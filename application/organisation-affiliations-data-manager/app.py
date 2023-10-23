from chalice import Chalice
from chalicelib import service


app = Chalice(app_name="organisation-affiliations-data-manager")


@app.route("/organisation_affiliations", methods=["GET"])
def get_organisationaffiliations():
    print("Get organisationaffiliations record...")
    oa_id = app.current_request.query_params["id"]
    print("Get oa_id record..." + oa_id)
    response = service.get_record_by_id(oa_id)
    return {"statusCode": 200, "body": response}


@app.route("/organisation_affiliations", methods=["POST"])
def create_organisationaffiliations():
    request = app.current_request.json_body
    data = {
        "id": request["id"],
        "healthcareService": request["healthcareservice"],
    }
    print(data)
    service.add_record(data)

    return {"statusCode": 200, "body": "Item Added Successfully"}


@app.route("/organisation_affiliations", methods=["PUT"])
def update_organisationaffiliations():
    #    request = app.current_request.json_body  // Required to get request from the API Gateway once it's set up.
    print("Updating organisation_affiliations record...")
    request = app.current_request.json_body
    service.update_record(
        request["id"], request["HospitalName"], request["HospitalLocation"]
    )
    return {"statusCode": 200, "body": "Item Updated Successfully"}


@app.route("/organisation_affiliations", methods=["DELETE"])
def delete_organisationaffiliations():
    #    request = app.current_request.json_body  // Required to get request from the API Gateway once it's set up.
    print("Delete healthcareservice record...")
    request = app.current_request.json_body
    oa_id = request["id"]
    service.delete_record(oa_id)

    return {"statusCode": 200, "body": "Item Deleted Successfully"}
