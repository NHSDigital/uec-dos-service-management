from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import os
import gzip
import time
import boto3

import json

result_file = "/tmp/location_compare_gp_results.txt"
result_file_handle = open(result_file, "w")
dubious_services = set()
dubious_services_group_map = {}

s3 = boto3.resource("s3")


def lambda_handler(event, context):
    # Get a list of ods codes from file in s3 bucket
    json_content = read_dos_locations(os.getenv("GP_LOCATION_JSON_FILE"))

    log("Comparing DoS location details with ODS API...")
    process_count = perform_comparision(json_content)
    generate_summary_report(process_count)
    upload_results_to_s3()

    return {"statusCode": 200, "body": json.dumps("Success")}


def read_dos_locations(location_file):
    content_object = s3.Object(os.getenv("S3_DATA_BUCKET"), location_file)
    file_content = content_object.get()["Body"].read().decode("utf-8")
    json_content = json.loads(file_content)

    return json_content


def log_ods_location_details(fhir_organisation):
    log("ODS odscode:" + str(fhir_organisation.get("id")))
    log("ODS name:" + str(fhir_organisation.get("name")))
    log("ODS address: ")

    lines = fhir_organisation.get("address")[0].get("line")
    if lines is not None:
        ods_line_count = 1
        for line in lines:
            log("ODS Address line " + str(ods_line_count) + ": " + line)
            ods_line_count += 1

    log("ODS city:" + str(fhir_organisation.get("address")[0].get("city")))
    log("ODS district:" + str(fhir_organisation.get("address")[0].get("district")))
    log("ODS postalCode:" + str(fhir_organisation.get("address")[0].get("postalCode")))
    log("ODS country:" + str(fhir_organisation.get("address")[0].get("country")))

    log("ODS telecom:")
    ods_public_phone = "None"
    telecoms = fhir_organisation.get("telecom")
    if telecoms is not None:
        for telecom in telecoms:
            if telecom is not None:
                for value in telecom:
                    ods_public_phone = telecom[value]
                    log(ods_public_phone)


def log_dos_location_details(organisations):
    log("DoS ODS: " + str(organisations.get("providedBy")))
    log("DoS Name: " + str(organisations.get("name")))
    log("DoS Public Name: " + str(organisations.get("publicName")))

    dos_address = str(organisations.get("address"))
    dos_address_lines = dos_address.split("$")
    dos_line_count = 1
    for dos_address_line in dos_address_lines:
        log("DoS Address Line " + str(dos_line_count) + ": " + dos_address_line)
        dos_line_count += 1

    log("DoS Town: " + str(organisations.get("town")))
    log("DoS Postcode: " + str(organisations.get("postcode")))
    log("DoS public phone: " + str(organisations.get("publicphone")))


def call_ods_api(dos_service_type, dos_ods_code):
    odscode = dos_ods_code
    fhir_organisation = None

    # Take first 5 chars of ODS codes for Pharamacy service types
    if dos_service_type in (13, 132, 134):
        if len(dos_ods_code) > 5:
            odscode = dos_ods_code[:5]

    url = os.getenv("BASE_URL") + odscode

    req = Request(url)
    req.add_header("Authorization", "Bearer " + os.getenv("TOKEN"))
    req.add_header("Accept-encoding", "gzip")

    try:
        response = urlopen(req)
    except HTTPError as error:
        log("ODS API call failed with error code - %s." % error.status)
        log(str(error.status) + ":" + str(error.reason))
    except URLError as error:
        log("ODS API call failed with error code - %s." % error.status)
        log(error.reason)
    except TimeoutError:
        log("Request timed out")
    else:
        content = gzip.decompress(response.read())
        fhir_organisation = json.loads(content.decode("utf-8"))

    return fhir_organisation


def compare_location_details(dos_location, ods_location):
    dos_ods_code = str(dos_location.get("providedBy"))
    dos_name = str(dos_location.get("name"))
    # dos_public_name = str(dos_location.get("publicName"))
    dos_address = str(dos_location.get("address"))
    dos_address_lines = dos_address.split("$")
    dos_postcode = str(dos_location.get("postcode"))
    ods_address_lines = ods_location.get("address")[0].get("line")
    # Compare service names
    compare(dos_ods_code, "Name", dos_name, str(ods_location.get("name")))

    # compare(dos_ods_code, "Public Name", dos_public_name, str(ods_location.get('name')))

    #  Compare service address lines
    i = 1
    x = 1
    for dos_address_line in dos_address_lines:
        if i <= len(ods_address_lines):
            compare(
                dos_ods_code,
                "Address line " + str(i),
                dos_address_line,
                ods_address_lines[i - 1],
            )
        else:
            # No more entries in ODS address so now check city and district
            if x == 1:
                compare(
                    dos_ods_code,
                    "City (line " + str(i) + ")",
                    dos_address_line,
                    str(ods_location.get("address")[0].get("city")),
                )
            if x == 2:
                compare(
                    dos_ods_code,
                    "District (line " + str(i) + ")",
                    dos_address_line,
                    str(ods_location.get("address")[0].get("district")),
                )
            if x == 3:
                compare(
                    dos_ods_code,
                    "Country (line " + str(i) + ")",
                    dos_address_line,
                    str(ods_location.get("address")[0].get("country")),
                )
            x += 1
        i += 1

    # Compare postcode
    compare(
        dos_ods_code,
        "Postcode",
        dos_postcode,
        str(ods_location.get("address")[0].get("postalCode")),
    )

    log("-------------------------------------------------------")


def perform_comparision(json_content):
    count = 0

    for organisations in json_content.get("odscodes"):
        if count >= 100:
            break

        count += 1

        log("Organisation Count: " + str(count))
        log_dos_location_details(organisations)

        fhir_organisation = call_ods_api(
            str(organisations.get("type")), str(organisations.get("providedBy"))
        )
        if fhir_organisation is None:
            continue

        log_ods_location_details(fhir_organisation)

        compare_location_details(organisations, fhir_organisation)

        if count % 20 == 0:
            time.sleep(2)

    return count


def log(message):
    print(message)
    result_file_handle.write(message + "\n")


def upload_results_to_s3():
    result_file_handle.close()

    # Upload file to S3
    s3.Bucket(os.getenv("S3_DATA_BUCKET")).upload_file(
        result_file, "location_compare_results/location_compare_gp_results.txt"
    )


def generate_summary_report(process_count):
    log("--- Summary Report ---")
    log("Number of services okay: " + str(process_count - len(dubious_services)))
    log("Number of dubious services: " + str(len(dubious_services)))
    log("Total number of services checked: " + str(process_count))

    log("--- Dubious Services Groups ---")
    for dubious_services_group in dubious_services_group_map:
        log(
            "Dubious Group: "
            + dubious_services_group
            + " : Count: "
            + str(len(dubious_services_group_map[dubious_services_group]))
        )
        for dubious_service in dubious_services_group_map[dubious_services_group]:
            log("Service: " + dubious_service)


def compare(odscode, name, value_1, value_2):
    # Rule 1: Don't worry if we have a None value; we will source the data from the source where it is not None
    if str(value_1) != "None" and str(value_2) != "None":
        if not filter(value_1) in filter(value_2) and not filter(value_2) in filter(
            value_1
        ):
            log(
                "!!!! DUBIOUS "
                + str(name)
                + " - DoS value different from ODS value: "
                + str(value_1)
                + " : "
                + str(value_2)
            )
            dubious_services.add(odscode)
            # Add group to list if it doesn't exist
            if str(name) not in dubious_services_group_map:
                dubious_services_group_map[str(name)] = set()

            # Add service to group set
            dubious_services_group_map[str(name)].add(odscode)


# Filtering rules!
def filter(value):
    filtered_value = value.upper()

    # Punctuation filters
    filtered_value = filtered_value.replace("-", "")
    filtered_value = filtered_value.replace("'S", "")
    filtered_value = filtered_value.replace(" ", "")
    filtered_value = filtered_value.replace("/", "")
    filtered_value = filtered_value.replace(".", "")
    filtered_value = filtered_value.replace(",", "")
    filtered_value = filtered_value.replace("()", "")
    filtered_value = filtered_value.replace(";", "")
    filtered_value = filtered_value.replace(":", "")

    # Commonly used abbreviation filters
    filtered_value = filtered_value.replace("&", "AND")
    filtered_value = filtered_value.replace("PARK", "PK")
    filtered_value = filtered_value.replace("LANE", "LN")
    filtered_value = filtered_value.replace("ROAD", "RD")
    filtered_value = filtered_value.replace("STREET", "ST")
    filtered_value = filtered_value.replace("CLOSE", "CL")
    filtered_value = filtered_value.replace("LIMITED", "LTD")
    filtered_value = filtered_value.replace("CENTRE", "CTR")
    filtered_value = filtered_value.replace("CNTR", "CTR")
    filtered_value = filtered_value.replace("MEDICAL", "MED")
    filtered_value = filtered_value.replace("COMMUNITY", "COMM")
    filtered_value = filtered_value.replace("HOSPITAL", "HOSP")
    filtered_value = filtered_value.replace("HEALTH", "HLTH")

    # Synonym filters
    filtered_value = filtered_value.replace("CHEMISTS", "CHEMIST")
    filtered_value = filtered_value.replace("PHARMACY", "CHEMIST")

    return filtered_value
