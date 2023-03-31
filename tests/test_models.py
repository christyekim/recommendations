"""
Test cases for Recommendation Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_recommendations.py:TestRecommendationModel

"""
import os
import logging
import unittest
from datetime import date
from werkzeug.exceptions import NotFound
from service.models import Recommendation, Type, DataValidationError, db
from service import app
from tests.factories import RecommendationFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  Recommendation   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods


class TestRecommendationModel(unittest.TestCase):
    """ Test Cases for Recommendation Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Recommendation.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.session.query(Recommendation).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_recommendation(self):
        """It should Create a Recommendation and assert that it exists"""
        date_today = date.today().isoformat()
        rec = Recommendation(
            product_id=123, user_id=456, user_segment="Millenial Female Pet Owner",
            viewed_in_last7d=True, bought_in_last30d=False,
            last_relevance_date=date_today, recommendation_type=Type.TRENDING)
        self.assertEqual(str(rec), "<Recommendation id=[None]>")
        self.assertTrue(rec is not None)
        self.assertEqual(rec.id, None)
        self.assertEqual(rec.product_id, 123)
        self.assertEqual(rec.user_id, 456)
        self.assertEqual(rec.user_segment, "Millenial Female Pet Owner")
        self.assertEqual(rec.viewed_in_last7d, True)
        self.assertEqual(rec.bought_in_last30d, False)
        self.assertEqual(rec.last_relevance_date, date_today)
        self.assertEqual(rec.recommendation_type, Type.TRENDING)
        rec = Recommendation(
            product_id=123, user_id=456, user_segment="Millenial Female Pet Owner",
            viewed_in_last7d=False, bought_in_last30d=False,
            last_relevance_date=date_today, recommendation_type=Type.UPGRADE)
        self.assertEqual(rec.viewed_in_last7d, False)
        self.assertEqual(rec.recommendation_type, Type.UPGRADE)

    def test_add_a_recommendation(self):
        """It should Create a Recommendation and add it to the database"""
        recs = Recommendation.all()
        self.assertEqual(recs, [])
        rec = Recommendation(
            product_id=123, user_id=456, user_segment="Millenial Female Pet Owner",
            viewed_in_last7d=True, bought_in_last30d=False,
            last_relevance_date=date.today().isoformat(), recommendation_type=Type.TRENDING)
        self.assertTrue(rec is not None)
        self.assertEqual(rec.id, None)
        rec.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(rec.id)
        recs = Recommendation.all()
        self.assertEqual(len(recs), 1)

    def test_read_a_recommendation(self):
        """It should Read a Recommendation"""
        rec = RecommendationFactory()
        logging.debug(rec)
        rec.id = None
        rec.create()
        self.assertIsNotNone(rec.id)
        # Fetch it back
        found_rec = Recommendation.find(rec.id)
        self.assertEqual(found_rec.id, rec.id)
        self.assertEqual(found_rec.user_segment, rec.user_segment)
        self.assertEqual(found_rec.recommendation_type,
                         rec.recommendation_type)

    def test_update_a_recommendation(self):
        """It should Update a Recommendation"""
        rec = RecommendationFactory()
        logging.debug(rec)
        rec.id = None
        rec.create()
        logging.debug(rec)
        self.assertIsNotNone(rec.id)
        # Change it an save it
        rec.user_segment = "z3r0"
        original_id = rec.id
        rec.update()
        self.assertEqual(rec.id, original_id)
        self.assertEqual(rec.user_segment, "z3r0")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        recs = Recommendation.all()
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0].id, original_id)
        self.assertEqual(recs[0].user_segment, "z3r0")

    def test_update_no_id(self):
        """It should Not Update a Recommendation with no ID"""
        rec = RecommendationFactory()
        logging.debug(rec)
        rec.id = None
        self.assertRaises(DataValidationError, rec.update)

    def test_delete_a_recommendation(self):
        """It should Delete a Recommendation"""
        rec = RecommendationFactory()
        rec.create()
        self.assertEqual(len(Recommendation.all()), 1)
        # delete the rec and make sure it isn't in the database
        rec.delete()
        self.assertEqual(len(Recommendation.all()), 0)

    def test_list_all_recommendations(self):
        """It should List all Recommendations in the database"""
        recs = Recommendation.all()
        self.assertEqual(recs, [])
        # Create 5 Recommendations
        for _ in range(5):
            rec = RecommendationFactory()
            rec.create()
        # See if we get back 5 recs
        recs = Recommendation.all()
        self.assertEqual(len(recs), 5)

    def test_serialize_a_recommendation(self):
        """It should serialize a Recommendation"""
        rec = RecommendationFactory()
        data = rec.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], rec.id)
        self.assertIn("product_id", data)
        self.assertEqual(data["product_id"], rec.product_id)
        self.assertIn("user_id", data)
        self.assertEqual(data["user_id"], rec.user_id)
        self.assertIn("user_segment", data)
        self.assertEqual(data["user_segment"], rec.user_segment)
        self.assertIn("viewed_in_last7d", data)
        self.assertEqual(data["viewed_in_last7d"], rec.viewed_in_last7d)
        self.assertIn("bought_in_last30d", data)
        self.assertEqual(data["bought_in_last30d"], rec.bought_in_last30d)
        self.assertIn("last_relevance_date", data)
        self.assertEqual(date.fromisoformat(
            data["last_relevance_date"]), rec.last_relevance_date)
        self.assertIn("recommendation_type", data)
        self.assertEqual(data["recommendation_type"],
                         rec.recommendation_type.name)

    def test_deserialize_a_recommendation(self):
        """It should deserialize a Recommendation"""
        data = RecommendationFactory().serialize()
        rec = Recommendation()
        rec.deserialize(data)
        self.assertNotEqual(rec, None)
        self.assertEqual(rec.id, None)
        self.assertEqual(rec.product_id, data["product_id"])
        self.assertEqual(rec.user_id, data["user_id"])
        self.assertEqual(rec.user_segment, data["user_segment"])
        self.assertEqual(rec.viewed_in_last7d, data["viewed_in_last7d"])
        self.assertEqual(rec.bought_in_last30d, data["bought_in_last30d"])
        self.assertEqual(rec.last_relevance_date,
                         date.fromisoformat(data["last_relevance_date"]))
        self.assertEqual(rec.recommendation_type.name,
                         data["recommendation_type"])

    def test_deserialize_missing_data(self):
        """It should not deserialize a Recommendation with missing data"""
        data = {"id": 1, "user_segment": "z3r0", "viewed_in_last7d": True}
        rec = Recommendation()
        self.assertRaises(DataValidationError, rec.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        rec = Recommendation()
        self.assertRaises(DataValidationError, rec.deserialize, data)

    def test_deserialize_bad_viewed_in_last7d(self):
        """It should not deserialize a bad viewed_in_last7d attribute"""
        test_recommendation = RecommendationFactory()
        data = test_recommendation.serialize()
        data["viewed_in_last7d"] = "true"
        rec = Recommendation()
        self.assertRaises(DataValidationError, rec.deserialize, data)

    def test_deserialize_bad_bought_in_last30d(self):
        """It should not deserialize a bad bought_in_last30d attribute"""
        test_recommendation = RecommendationFactory()
        data = test_recommendation.serialize()
        data["bought_in_last30d"] = "false"
        rec = Recommendation()
        self.assertRaises(DataValidationError, rec.deserialize, data)

    def test_deserialize_bad_recommendation_type(self):
        """It should not deserialize a bad recommendation_type attribute"""
        test_recommendation = RecommendationFactory()
        data = test_recommendation.serialize()
        data["recommendation_type"] = "manual"  # wrong case
        rec = Recommendation()
        self.assertRaises(DataValidationError, rec.deserialize, data)

    def test_find_recommendation(self):
        """It should Find a Recommendation by ID"""
        recs = RecommendationFactory.create_batch(5)
        for rec in recs:
            rec.create()
        logging.debug(recs)
        # make sure they got saved
        self.assertEqual(len(Recommendation.all()), 5)
        # find the 2nd rec in the list
        rec = Recommendation.find(recs[1].id)
        self.assertIsNot(rec, None)
        self.assertEqual(rec.id, recs[1].id)
        self.assertEqual(rec.product_id, recs[1].product_id)
        self.assertEqual(rec.user_id, recs[1].user_id)
        self.assertEqual(rec.user_segment, recs[1].user_segment)
        self.assertEqual(rec.viewed_in_last7d, recs[1].viewed_in_last7d)
        self.assertEqual(rec.bought_in_last30d, recs[1].bought_in_last30d)
        self.assertEqual(rec.last_relevance_date, recs[1].last_relevance_date)
        self.assertEqual(rec.recommendation_type, recs[1].recommendation_type)

    def test_find_recommendation_or_404(self):
        """It should Find a Recommendation by ID or return 404_NOT_FOUND if not found"""
        recs = RecommendationFactory.create_batch(3)
        for rec in recs:
            rec.create()
        logging.debug(recs)
        # make sure they got saved
        self.assertEqual(len(Recommendation.all()), 3)
        # find the 2nd rec in the list
        rec = Recommendation.find_or_404(recs[1].id)
        self.assertIsNot(rec, None)
        self.assertEqual(rec.id, recs[1].id)
        self.assertEqual(rec.product_id, recs[1].product_id)
        self.assertEqual(rec.user_id, recs[1].user_id)
        self.assertEqual(rec.user_segment, recs[1].user_segment)
        self.assertEqual(rec.viewed_in_last7d, recs[1].viewed_in_last7d)
        self.assertEqual(rec.bought_in_last30d, recs[1].bought_in_last30d)
        self.assertEqual(rec.last_relevance_date, recs[1].last_relevance_date)
        self.assertEqual(rec.recommendation_type, recs[1].recommendation_type)

    def test_find_recommendation_or_404_not_found(self):
        """It should return 404_NOT_FOUND for ID not found"""
        self.assertRaises(NotFound, Recommendation.find_or_404, 0)

    def test_find_by_product_id(self):
        """It should Find Recommendations by Product ID"""
        recs = RecommendationFactory.create_batch(5)
        for rec in recs:
            rec.create()
        product_id = recs[0].product_id
        count = len([rec for rec in recs if rec.product_id == product_id])
        found = Recommendation.find_by_product_id(product_id)
        self.assertEqual(found.count(), count)
        for rec in found:
            self.assertEqual(rec.product_id, product_id)

    def test_find_by_user_id(self):
        """It should Find Recommendations by User ID"""
        recs = RecommendationFactory.create_batch(5)
        for rec in recs:
            rec.create()
        user_id = recs[0].user_id
        count = len([rec for rec in recs if rec.user_id == user_id])
        found = Recommendation.find_by_user_id(user_id)
        self.assertEqual(found.count(), count)
        for rec in found:
            self.assertEqual(rec.user_id, user_id)

    def test_find_by_user_segment(self):
        """It should Find a Recommendation by User Segment"""
        recs = RecommendationFactory.create_batch(10)
        for rec in recs:
            rec.create()
        user_segment = recs[0].user_segment
        count = len([rec for rec in recs if rec.user_segment == user_segment])
        found = Recommendation.find_by_user_segment(user_segment)
        self.assertEqual(found.count(), count)
        for rec in found:
            self.assertEqual(rec.user_segment, user_segment)

    def test_find_by_viewed_in_last7d(self):
        """It should Find Recommendations by viewed_in_last7d"""
        recs = RecommendationFactory.create_batch(10)
        for rec in recs:
            rec.create()
        viewed_in_last7d = recs[0].viewed_in_last7d
        count = len(
            [rec for rec in recs if rec.viewed_in_last7d == viewed_in_last7d])
        found = Recommendation.find_by_viewed_in_last7d(viewed_in_last7d)
        self.assertEqual(found.count(), count)
        for rec in found:
            self.assertEqual(rec.viewed_in_last7d, viewed_in_last7d)

    def test_find_by_bought_in_last30d(self):
        """It should Find Recommendations by bought_in_last30d"""
        recs = RecommendationFactory.create_batch(10)
        for rec in recs:
            rec.create()
        bought_in_last30d = recs[0].bought_in_last30d
        count = len(
            [rec for rec in recs if rec.bought_in_last30d == bought_in_last30d])
        found = Recommendation.find_by_bought_in_last30d(bought_in_last30d)
        self.assertEqual(found.count(), count)
        for rec in found:
            self.assertEqual(rec.bought_in_last30d, bought_in_last30d)

    def test_find_by_recommendation_type(self):
        """It should Find Recommendations by recommendation_type"""
        recs = RecommendationFactory.create_batch(10)
        for rec in recs:
            rec.create()
        recommendation_type = recs[0].recommendation_type
        count = len(
            [rec for rec in recs if rec.recommendation_type == recommendation_type])
        found = Recommendation.find_by_recommendation_type(recommendation_type)
        self.assertEqual(found.count(), count)
        for rec in found:
            self.assertEqual(rec.recommendation_type, recommendation_type)

    def test_find_by_last_relevance_date(self):
        """It should Find Recommendations by last_relevance_date"""
        recs = RecommendationFactory.create_batch(10)
        for rec in recs:
            rec.create()
        last_relevance_date = recs[0].last_relevance_date.isoformat()
        count = len(
            [rec for rec in recs if rec.last_relevance_date.isoformat() == last_relevance_date])
        found = Recommendation.find_by_last_relevance_date(last_relevance_date)
        self.assertEqual(found.count(), count)
        for rec in found:
            self.assertEqual(
                rec.last_relevance_date.isoformat(), last_relevance_date)

    def test_find_after_last_relevance_date(self):
        """It should Find Recommendations after last_relevance_date"""
        recs = RecommendationFactory.create_batch(10)
        for rec in recs:
            rec.create()
        last_relevance_date = recs[0].last_relevance_date.isoformat()
        count = len(
            [rec for rec in recs if rec.last_relevance_date.isoformat() >= last_relevance_date])
        found = Recommendation.find_after_last_relevance_date(
            last_relevance_date)
        self.assertEqual(found.count(), count)
        for rec in found:
            self.assertGreaterEqual(
                rec.last_relevance_date.isoformat(), last_relevance_date)
