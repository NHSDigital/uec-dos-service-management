The ODS comparator is a temporary Lambda function that can be run to compare Organisation location data
from the ODS API with service addresses stored in DoS.

To use it:

1. Order a clone of the live DoS DB
2. Log into the clone with DBeaver
3. Run the appropriate SQL statement in scripts/sql/aurora_extract_scripts/ods-vs-dos-compare.sql - This will generate a JSON
  output
4. Copy the JSON output into a results.json file and upload the file into the nhse-uec-sm-dev-databucket S3 bucket
5. Open AWS in a browser and find the ODS Location Comparator Lambda function
6. Navigate to the Environment variables for this Lambda and set:
    a. The Base path URL to the ODS API endpoint
    b. The authentication access token for authentication for the ODS endpoint API
    c. The DOS_LOCATIONS_JSON_FILE to the name of the results.json file uploaded into the S3 bucket in step 4
7. Run the Lambda. The Lambda will output results of any discrepencies to the screen and will also write all logging and stats
  to the nhse-uec-sm-dev-databucket S3 bucket in location_compare_results/location_compare_results.txt
