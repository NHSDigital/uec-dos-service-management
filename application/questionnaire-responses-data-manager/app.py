from chalice import Chalice
from chalicelib import service


app = Chalice(app_name="questionnaire-responses-data-manager")


@app.route("/questionnaire_responses", methods=["GET"])
def get_questionnaireresponses():
    print("Get questionnaire_responses record...")
    qr_id = app.current_request.query_params["id"]
    print("Get qr_id record..." + qr_id)
    response = service.get_record_by_id(qr_id)
    return {"statusCode": 200, "body": response}


@app.route("/questionnaire_responses", methods=["POST"])
def create_questionnaireresponses():
    request = app.current_request.json_body
    data = {
        "id": request["id"],
        "name": request["name"],
    }
    print(data)
    service.add_record(data)

    return {"statusCode": 200, "body": "Item Added Successfully"}


@app.route("/questionnaire_responses", methods=["PUT"])
def update_questionnaireresponses():
    #    request = app.current_request.json_body  // Required to get request from the API Gateway once it's set up.
    print("Updating questionnaireresponses record...")
    request = app.current_request.json_body
    service.update_record(
        request["id"], request["HospitalName"], request["HospitalLocation"]
    )
    return {"statusCode": 200, "body": "Item Updated Successfully"}


@app.route("/questionnaire_responses", methods=["DELETE"])
def delete_questionnaireresponses():
    #    request = app.current_request.json_body  // Required to get request from the API Gateway once it's set up.
    print("Delete questionnaireresponses record...")
    request = app.current_request.json_body
    qr_id = request["id"]
    service.delete_record(qr_id)

    return {"statusCode": 200, "body": "Item Deleted Successfully"}
