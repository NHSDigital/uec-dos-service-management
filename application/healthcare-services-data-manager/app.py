from chalice import Chalice
from chalicelib import service

app = Chalice(app_name="healthcare-services-data-manager")


@app.route("/healthcare_services", methods=["GET"])
def get_healthcareservice():
    hs_id = app.current_request.query_params["id"]
    print("Get hs_id record..." + hs_id)
    response = service.get_record_by_id(hs_id)
    return {"statusCode": 200, "body": response}


@app.route("/healthcare_services", methods=["POST"])
def create_healthcareservice():
    request = app.current_request.json_body
    data = {
        "id": request["id"],
        "hospitalName": request["hospitalname"],
        "hospitalLocation": request["hospitallocation"],
    }

    print(data)
    service.add_record(data)

    return {"statusCode": 200, "body": "Item Added Successfully"}


@app.route("/healthcare_services", methods=["PUT"])
def update_healthcareservices():
    #    request = app.current_request.json_body  // Required to get request from the API Gateway once it's set up.
    print("Updating healthcare_service record...")
    request = app.current_request.json_body
    service.update_record(
        request["id"], request["HospitalName"], request["HospitalLocation"]
    )
    return {"statusCode": 200, "body": "Item Updated Successfully"}


@app.route("/healthcare_services", methods=["DELETE"])
def delete_healthcareservices():
    #    request = app.current_request.json_body  // Required to get request from the API Gateway once it's set up.
    print("Delete healthcareservice record...")
    request = app.current_request.json_body
    hs_id = request["id"]
    service.delete_record(hs_id)

    return {"statusCode": 200, "body": "Item Deleted Successfully"}
