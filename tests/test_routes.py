"""
Recommendations API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN

  While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_service.py:TestRecommendationService
"""

import os
import logging
from unittest import TestCase
# from unittest.mock import MagicMock, patch

from service import app
from service.models import db, init_db, Recommendation
from service.common import status  # HTTP Status Codes
from tests.factories import RecommendationFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/recommendations"

######################################################################
#  T E S T   S E R V I C E
######################################################################
class TestRecommendationService(TestCase):
    """Recommendation Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Recommendation).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    def _create_recommendations(self, count):
        """Factory method to create recommendations in bulk"""
        recommendations = []
        for _ in range(count):
            test_recommendation = RecommendationFactory()
            response = self.client.post(BASE_URL, json=test_recommendation.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test recommendation"
            )
            new_recommendation = response.get_json()
            test_recommendation.id = new_recommendation["id"]
            recommendations.append(test_recommendation)
        return recommendations

######################################################################
#  P L A C E   T E S T   C A S E S  &   S A D   P A T H S   H E R E
#Tip: Make sure to grab from both 'test cases' and 'sad paths'!
######################################################################

    def test_index(self):
        """It should call the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], "Recommendations REST API Service")

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/healthcheck")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["message"], "Healthy")

######################################################################
    #  RETRIEVE/GET A RECOMMENDATION (READ)
######################################################################

    def test_get_recommendation(self):
        """It should Get a single recommendation"""
        # get the id of a recommendation
        test_recommendation = self._create_recommendations(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["user_segment"], test_recommendation.user_segment)

    def test_get_recommendation_not_found(self):
        """It should not Get a recommendation thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

######################################################################
    #  ADD A RECOMMENDATION (CREATE)
######################################################################

    def test_create_recommendation_no_content_type(self):
        """It should not Create a recommendation with no content type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_recommendation_wrong_content_type(self):
        """It should not Create a recommendation with the wrong content type"""
        response = self.client.post(BASE_URL, data="hello", content_type="text/html")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

######################################################################
#  Update A RECOMMENDATION (Update)
######################################################################
    def test_update_recommendation(self):
	    """It should Update an existing recommendation"""
	    # create a recommendation to update
	    test_recommendation = RecommendationFactory()
	    response = self.client.post(BASE_URL, json=test_recommendation.serialize())
	    self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the recommendation
	    new_recommendation = response.get_json()
	    logging.debug(new_recommendation)
	    new_recommendation["user_segment"] = "unknown"
	    response = self.client.put(f"{BASE_URL}/{new_recommendation['id']}", json=new_recommendation)
	    self.assertEqual(response.status_code, status.HTTP_200_OK)
	    updated_recommendation = response.get_json()
	    self.assertEqual(updated_recommendation["user_segment"], "unknown")

    def test_update_recommendation_not_found(self):
        """It should Update a Recommendation and Return Not Found"""
        test_recommendation = RecommendationFactory()
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_recommendation = response.get_json()
        logging.debug(new_recommendation)
        new_recommendation["user_segment"] = "unknown"
        new_recommendation['id'] = 0
        response = self.client.put(f"{BASE_URL}/{new_recommendation['id']}", json=new_recommendation)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
