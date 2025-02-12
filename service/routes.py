"""
Recommendations Service

Paths:
------
GET /recommendations - Returns a list all of the Recommendations
GET /recommendations/{id} - Returns the Recommendation with a given id number
POST /recommendations - creates a new Recommendation record in the database
PUT /recommendations/{id} - updates a Recommendation record in the database
DELETE /recommendations/{id} - deletes a Recommendation record in the database
"""

#from flask import Flask, make_response
from flask import jsonify, request, url_for, abort
from service.common import status  # HTTP Status Codes
from service.models import Recommendation

# Import Flask application
from . import app

######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/healthcheck")
def healthcheck():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Recommendations REST API Service",
            version="1.0",
            paths=url_for("list_recommendations", _external=True),
        ),
        status.HTTP_200_OK,
    )

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )

######################################################################
#  R E S T   A P I   E N D P O I N T S
#@everyone - add your code below here!
######################################################################

######################################################################
# LIST ALL RECOMMENDATIONS (LIST)
######################################################################
@app.route("/recommendations", methods=["GET"])
def list_recommendations():
    """Returns all of the Recommendations"""
    app.logger.info("Request for recommendation list")
    recommendations = []
 #   rec_id = request.args.get("id")
    user_segment = request.args.get("user_segment")
    if user_segment:
        recommendations = Recommendation.find_by_user_segment(user_segment)
    else:
        recommendations = Recommendation.all()

    results = [recommendation.serialize() for recommendation in recommendations]
    app.logger.info("Returning %d recommendations", len(results))
    return jsonify(results), status.HTTP_200_OK

######################################################################
# RETRIEVE A RECOMMENDATION (READ)
######################################################################
@app.route("/recommendations/<int:rec_id>", methods=["GET"])
def get_recommendation(rec_id):
    """
    Retrieve a single recommendation
    This endpoint will return a recommendation based on it's id
    """
    app.logger.info("Request for recommendation with id: %s", rec_id)
    recommendation = Recommendation.find(rec_id)
    if not recommendation:
        abort(status.HTTP_404_NOT_FOUND, f"recommendation with id '{rec_id}' was not found.")

    app.logger.info("Returning recommendation: %s", recommendation.user_segment)
    return jsonify(recommendation.serialize()), status.HTTP_200_OK

######################################################################
# ADD A NEW RECOMMENDATION (CREATE)
######################################################################
@app.route("/recommendations", methods=["POST"])
def create_recommendation():
    """
    Creates a recommendation
    This endpoint will create a recommendation based the data in the body that is posted
    """
    app.logger.info("Request to create a recommendation")
    check_content_type("application/json")
    recommendation = Recommendation()
    recommendation.deserialize(request.get_json())
    recommendation.create()
    message = recommendation.serialize()
    location_url = url_for("get_recommendation", rec_id=recommendation.id, _external=True)

    app.logger.info("Recommendation with ID [%s] created.", recommendation.id)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}

######################################################################
# DELETE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:rec_id>", methods=["DELETE"])
def delete_recommendation(rec_id):
    """
    Delete a recommendation
    This endpoint will delete a recommendation based the id specified in the path
    """
    app.logger.info("Request to delete recommendation with id: %s", rec_id)
    recommendation = Recommendation.find(rec_id)
    if recommendation:
        recommendation.delete()

    app.logger.info("Recommendation with ID [%s] delete complete.", rec_id)
    return "", status.HTTP_204_NO_CONTENT

######################################################################
# UPDATE AN EXISTING recommendation
######################################################################
@app.route("/recommendations/<int:rec_id>", methods=["PUT"])
def update_recommendations(rec_id):
    """
    Update a recommendation

    This endpoint will update a recommendation based the body that is posted
    """
    app.logger.info("Request to update recommendation with id: %s", rec_id)
    check_content_type("application/json")

    recommendation = Recommendation.find(rec_id)
    if not recommendation:
        abort(status.HTTP_404_NOT_FOUND, f"recommendation with id '{rec_id}' was not found.")

    recommendation.deserialize(request.get_json())
    recommendation.id = rec_id
    recommendation.update()

    app.logger.info("recommendation with ID [%s] updated.", recommendation.id)
    return jsonify(recommendation.serialize()), status.HTTP_200_OK
