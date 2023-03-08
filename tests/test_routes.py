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
    #  P L A C E   T E S T   C A S E S   H E R E
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
