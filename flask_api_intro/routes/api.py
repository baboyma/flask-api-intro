from flask import Blueprint, request, jsonify

bp_api = Blueprint('api', __name__)

# The endpoint of our flask app
@bp_api.route("/api/text", methods=["GET", "POST"])
def handle_request():
    # The GET endpoint
    if request.method == "GET":
        return "This is the GET Endpoint of flask API."

    # The POST endpoint
    if request.method == "POST":
        # accesing the passed payload
        payload = request.get_json()
        # capitalizing the text
        cap_text = payload['text'].upper()
        # Creating a proper response
        response = {'cap-text'.upper(): cap_text}
        # return the response as JSON
        return jsonify(response)
