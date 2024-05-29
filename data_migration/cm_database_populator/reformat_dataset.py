#!/usr/bin/python
# -*- coding: utf-8 -*-

###############################################
# File       : reformatDataset.py             #
# Ticket     : DR-794                         #
# Date       : 2024-05-02                     #
# Author     : Tom Leyman                     #
###############################################

import itertools
import json
import logging
import os
import shutil
import pandas as pd
from typing import Dict, List, Optional
from common import common_functions


class DatasetReformatter:
    """
    A class used to reformat datasets by generating new IDs for FHIR based CM/DoS entities
    while preserving the existing ID mappings and guaranteeing no duplicates.
    """

    def __init__(self):
        """
        Initialize instance attributes for the DatasetReformatter class.
        """
        print("Working in " + os.getcwd())
        try:
            with open("reformat_dataset_config.json") as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error reading config file: {e}")
            raise
        self.id_dict = {}
        self.df_dict = {}
        self.workbook = config["workbook"]
        self.backup_file = config["backup_file"]
        self.log_file = config["log_file"]
        self.dataset_sheets_columns = config["dataset_sheets_columns"]
        self.last_id = common_functions.generate_unique_id()
        self.testing = config.get("testing", False)
        self.spinner = itertools.cycle(["-", "/", "|", "\\"])

        # Check if backup file already exists
        # and if not, create a backup
        print("Working in " + os.getcwd())
        if not os.path.exists(self.backup_file):
            shutil.copy2(self.workbook, self.backup_file)

        # Remove the old log file
        removed = self.remove_old_log_file(self.log_file)

        # Set up the logger - logging level can be changed to DEBUG for more
        # detailed output
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # Create a file handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)

        # Create a console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Create a formatter and add it to the handlers
        formatter = logging.Formatter("%(asctime)s - %(message)s")
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add the handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # Log the start of the process
        if removed:
            self.log(f"Old log file {self.log_file} removed.")
        else:
            self.log(f"Log file {self.log_file} does not exist. It will be created.")
        self.log("Working in " + os.getcwd())
        self.log("Workbook path is " + self.workbook + "\n")

    def log(self, message: str, level: str = "") -> None:
        """
        Log a message at the specified level.
        """
        levels = {
            "": self.logger.info,
            "Warning": self.logger.warning,
            "Error": self.logger.error,
        }
        log_message = f"{level} {message}"
        levels[level](log_message)

    def show_progress_spinner(self):
        """
        Show a progress spinner while the process is running.
        """
        print(next(self.spinner), end="\r", flush=True)

    def generate_unique_id(self, prefix: str = "") -> str:
        """
        Generate a unique ID from common_functions.generate_unique_id.
        The value is UTC based and is guaranteed to be unique
        by comparing against the last generated ID.

        Returns:
        A unique ID string.
        """
        dupe = False
        new_id = self.last_id
        while new_id == self.last_id:
            if dupe:
                self.show_progress_spinner()
            new_id = common_functions.generate_unique_id()
            dupe = True
        self.last_id = new_id
        if prefix != "":
            new_id = str(prefix + str(new_id))
        return new_id

    def replace_old_ids_with_new_ids(
        self,
        df: pd.DataFrame,
        id_column: str,
        id_dict: Dict[str, str],
        prefix: str = "",
    ) -> None:
        """
        Replace old IDs in the DataFrame with new ones and update the id_dict.
        """
        if id_column not in df.columns:
            raise ValueError(f"Error: '{id_column}' column not found in DataFrame")
        unique_ids = df[id_column].unique()
        new_ids = {
            old_id: str(self.generate_unique_id(prefix))
            for old_id in unique_ids
            if old_id not in id_dict
        }

        self.log(f"Generated {len(new_ids)} new IDs for column {id_column}")

        id_dict.update(new_ids)
        df[id_column] = df[id_column].replace(new_ids)

    def map_old_ids_to_new_ids(
        self, df: pd.DataFrame, id_column: str, id_dict: Dict[str, str]
    ) -> None:
        """
        Map old IDs in the DataFrame to new ones using the id_dict.
        """
        if id_column not in df.columns:
            raise ValueError(f"Error: '{id_column}' column not found in DataFrame")
        # Update the mapped column in the sheet's DataFrame

        df[id_column] = df[id_column].map(id_dict).fillna(df[id_column])
        self.log(
            f"Mapped {len(df[id_column])} rows to {len(df[id_column].unique())} IDs in column {id_column}"
        )

    def update_workbook_with_new_data(
        self, workbook: str, sheet: str, df: pd.DataFrame
    ) -> None:
        """
        Update the specified sheet in the workbook with the new data.
        """
        if self.testing:
            self.log(f"Testing Mode. Skipping update {sheet} with new IDs")
        else:
            try:
                with pd.ExcelWriter(
                    workbook, engine="openpyxl", mode="a", if_sheet_exists="replace"
                ) as writer:
                    df.to_excel(writer, sheet_name=sheet, index=False)
                    self.log(f"Updated {sheet} with new IDs")
            except Exception as e:
                self.log(f"An error occurred while updating {sheet}: {str(e)}", "Error")
                self.log(
                    f"{workbook} may be corrupt. See backup in working directory.",
                    "Error",
                )
                raise

    def remove_old_log_file(self, log_file: str) -> bool:
        """
        Remove the old log file if it exists.

        Returns:
        True if the file was removed, False otherwise.
        """
        removed = False
        if os.path.exists(log_file):
            os.remove(log_file)
            removed = True
        return removed

    def load_data_from_excel_sheet(
        self, workbook: str, sheet: str
    ) -> Optional[pd.DataFrame]:
        """
        Load data from an Excel sheet into a pandas DataFrame.
        """
        try:
            df = pd.read_excel(workbook, sheet)
        except FileNotFoundError:
            self.log(f"File not found: {workbook}, Sheet: {sheet}", "Error")
            raise
        df = df.dropna(how="all")
        if df.empty:
            self.log(f"\nNo entries in {sheet}. Stopping process.", "Warning")
            return None
        return df

    def generate_and_replace_new_ids(
        self,
        df: pd.DataFrame,
        id_column: str,
        id_dict: Dict[str, str],
        prefix: str = "",
    ) -> pd.DataFrame:
        """
        Generate new IDs for the DataFrame.
        """
        current_id_dict_size = len(id_dict)
        current_df_size = len(df)
        self.replace_old_ids_with_new_ids(df, id_column, id_dict, prefix)
        new_ids_generated = len(id_dict) - current_id_dict_size
        if new_ids_generated != current_df_size:
            self.log("Not all IDs have been replaced.", "Error")
            raise ValueError("Not all IDs have been replaced.")
        return df

    def map_columns_to_new_ids(
        self, df: pd.DataFrame, map_columns: List[str], id_dict: Dict[str, str]
    ) -> pd.DataFrame:
        """
        Map columns in the DataFrame to new IDs.
        """
        for column in map_columns:
            if column in df.columns:
                self.map_old_ids_to_new_ids(df, column, id_dict)
                self.log(f"Column {column} updated.")
            else:
                raise ValueError(
                    f"Column '{column}' not found in DataFrame. Verify column names and re-run. No data written."
                )
        return df

    def process_excel_sheet(
        self,
        workbook: str,
        data_sheet: str,
        dataset_sheets_columns: Dict[str, Dict[str, str]],
        id_dict: Dict[str, str],
        df_dict: Dict[str, pd.DataFrame],
    ) -> None:
        """
        Process an Excel sheet: load data, generate new IDs, map old IDs to new ones.
        """

        # Get the sheet details from the dataset_sheets_columns dictionary
        sheet = dataset_sheets_columns[data_sheet]["sheet"]
        generate_column = dataset_sheets_columns[data_sheet]["generate_column"]
        map_columns = dataset_sheets_columns[data_sheet]["map_columns"]
        prefix = dataset_sheets_columns[data_sheet].get("id_prefix", "")
        # Load the data from the sheet into a DataFrame

        df = self.load_data_from_excel_sheet(workbook, sheet)
        # Start processing the sheet

        self.log(f"Starting processing of sheet: {sheet}")
        if df is not None:
            # If data was loaded, generate and replace new IDs

            df = self.generate_and_replace_new_ids(df, generate_column, id_dict, prefix)
            # Map old IDs to new ones

            df = self.map_columns_to_new_ids(df, map_columns, id_dict)
            # Store the processed DataFrame in the df_dict dictionary

            df_dict[data_sheet] = df
            # Log the completion of processing the sheet
            self.log(f"{data_sheet} ID prefix:{prefix}")
            self.log(f"Finished processing of {data_sheet}\n")
        else:
            # If no data was loaded, log that we are skipping the processing of
            # this sheet

            self.log(f"No data found in sheet: {sheet}, skipping processing\n ")
        self.prefix = ""

    def process_all_excel_sheets(
        self,
        workbook: str,
        dataset_sheets_columns: Dict[str, Dict[str, str]],
        id_dict: Dict[str, str],
        df_dict: Dict[str, pd.DataFrame],
    ) -> None:
        """
        Process all Excel sheets in the workbook.
        """
        for data_sheet in dataset_sheets_columns:
            self.process_excel_sheet(
                workbook, data_sheet, dataset_sheets_columns, id_dict, df_dict
            )
            # Check if all defined sheets have been processed
        if len(self.df_dict) != len(self.dataset_sheets_columns):
            self.log("Not all defined sheets have been processed.", "Warning")

    def write_new_data_to_all_sheets(
        self,
        workbook: str,
        dataset_sheets_columns: Dict[str, Dict[str, str]],
        df_dict: Dict[str, pd.DataFrame],
    ) -> None:
        """
        Write the new data to all sheets in the workbook.
        """
        for sheet in df_dict.keys():
            self.log(f"Writing {sheet} to {workbook}")
            self.log("Updating workbook... Please wait.")
            self.update_workbook_with_new_data(
                workbook, dataset_sheets_columns[sheet]["sheet"], df_dict[sheet]
            )
            self.log(f"{sheet} updated in {workbook}. Moving on\n")

    def main(self) -> None:
        """
        Main execution of the script.
        Updates all IDs and retains the mapping to the old IDs.
        """

        # Generate new IDs for each sheet
        self.log(
            "\n******************************************\n"
            + "***** Generating and mapping new IDs *****\n"
            + "******************************************\n"
        )
        self.process_all_excel_sheets(
            self.workbook, self.dataset_sheets_columns, self.id_dict, self.df_dict
        )
        # Log discovered sheets

        self.log(f"{len(self.df_dict)} sheets found")
        for sheet in self.df_dict.keys():
            self.log(f"{self.dataset_sheets_columns[sheet]['sheet']}")
        # All new IDs have been generated and stored in id_dict
        # ID generation and mapping complete
        # Write the data back to the spreadsheet

        self.log(
            "\n***************************\n"
            + "***** Writing new IDs *****\n"
            + "***************************\n"
        )
        self.write_new_data_to_all_sheets(
            self.workbook, self.dataset_sheets_columns, self.df_dict
        )
        # All sheets have been updated with new IDs and mappings updated

        self.log(
            "\n****************************\n"
            + "***** Process complete *****\n"
            + "****************************\n"
        )


if __name__ == "__main__":
    reformatter = DatasetReformatter()
    reformatter.main()
