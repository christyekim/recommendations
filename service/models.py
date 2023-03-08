"""
Models for Recommendations Service

All of the models are stored in this module

Models
------
Recommendation - A recommendation record for this service

Attributes:
-----------
product_id          (integer) - Foreign Key; from Products service
user_id             (integer) - Foreign Key; from Customers service
user_segment        (string)  - Segment Class; To identify user segment for above user
                                E.g., college student, pet owner, new parent, etc.
viewed_in_last7d    (boolean) - Recently viewed or not
bought_in_last30d   (boolean) - Recently bought or not
last_relevance_date (date)    - To see how recent the recommendation activity is
                                Out-of-date recommendations/relevance can be filtered out
recommendation_type (enum)    - Type of recommendation basis
"""
import logging
from enum import Enum
from datetime import date
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


# Function to initialize the database
def init_db(app):
    """ Initializes the SQLAlchemy app """
    Recommendation.init_db(app)


class DataValidationError(Exception):
    """ Used for an data validation error when deserializing """


class Type(Enum):
    """Enumeration of valid Recommendation Categories"""
    SIMILAR_PRODUCT = 1
    RECOMMENDED_FOR_YOU = 2
    UPGRADE = 3
    FREQ_BOUGHT_TOGETHER = 4
    ADD_ON = 5
    TRENDING = 6
    TOP_RATED = 7
    NEW_ARRIVAL = 8
    UNKNOWN = 15


class Recommendation(db.Model):
    """
    Class that represents a Recommendation
    """

    app = None

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)    # Primary Key: Recommendation ID
    product_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    user_segment = db.Column(db.String(63), nullable=False)
    viewed_in_last7d = db.Column(db.Boolean(), nullable=False, default=False)
    bought_in_last30d = db.Column(db.Boolean(), nullable=False, default=False)
    last_relevance_date = db.Column(db.Date(), nullable=False, default=date.today())
    recommendation_type = db.Column(
        db.Enum(Type), nullable=False, server_default=(Type.UNKNOWN.name)
    )

    ##################################################
    # INSTANCE METHODS
    ##################################################

    def __repr__(self):
        return f"<Recommendation id=[{self.id}]>"

    def create(self):
        """
        Creates a Recommendation to the database
        """
        logger.info("Creating id=[%s]", self.id)
        self.id = None  # pylint: disable=invalid-name
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Recommendation to the database
        """
        logger.info("Saving id=[%s]", self.id)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """ Removes a Recommendation from the data store """
        logger.info("Deleting id=[%s]", self.id)
        db.session.delete(self)
        db.session.commit()

    def serialize(self) -> dict:
        """ Serializes a Recommendation into a dictionary """
        return {
            "id": self.id,
            "product_id": self.product_id,
            "user_id": self.user_id,
            "user_segment": self.user_segment,
            "viewed_in_last7d": self.viewed_in_last7d,
            "bought_in_last30d": self.bought_in_last30d,
            "last_relevance_date": self.last_relevance_date.isoformat(),
            "recommendation_type": self.recommendation_type.name  # convert enum to string
        }

    def deserialize(self, data: dict):
        """
        Deserializes a Recommendation from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.product_id = data["product_id"]
            self.user_id = data["user_id"]
            self.user_segment = data["user_segment"]
            if isinstance(data["viewed_in_last7d"], bool):
                self.viewed_in_last7d = data["viewed_in_last7d"]
            else:
                raise DataValidationError(
                    "Invalid type for boolean [viewed_in_last7d]: "
                    + str(type(data["viewed_in_last7d"]))
                )
            if isinstance(data["bought_in_last30d"], bool):
                self.bought_in_last30d = data["bought_in_last30d"]
            else:
                raise DataValidationError(
                    "Invalid type for boolean [bought_in_last30d]: "
                    + str(type(data["bought_in_last30d"]))
                )
            self.last_relevance_date = date.fromisoformat(data["last_relevance_date"])
            self.recommendation_type = getattr(Type, data["recommendation_type"])
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError("Invalid Recommendation: missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Recommendation: body of request contained bad or no data; " + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def init_db(cls, app: Flask):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our SQLAlchemy tables

    @classmethod
    def all(cls) -> list:
        """ Returns all of the Recommendation in the database """
        logger.info("Processing all Recommendations")
        return cls.query.all()

    @classmethod
    def find(cls, by_id: int):
        """ Finds a Recommendation by its ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_or_404(cls, by_id: int):
        """ Finds a Recommendation by its ID or 404_NOT_FOUND if not found """
        logger.info("Processing lookup or 404 for id %s ...", by_id)
        return cls.query.get_or_404(by_id)

    @classmethod
    def find_by_product_id(cls, by_id: int) -> list:
        """ Returns all Recommendations for given Product ID """
        logger.info("Processing lookup for product id %s ...", by_id)
        return cls.query.filter(cls.product_id == by_id)

    @classmethod
    def find_by_user_id(cls, by_id: int) -> list:
        """ Returns all Recommendations for given User ID """
        logger.info("Processing lookup for user id %s ...", by_id)
        return cls.query.filter(cls.user_id == by_id)

    @classmethod
    def find_by_user_segment(cls, segment: str) -> list:
        """ Returns all Recommendations for given User Segment """
        logger.info("Processing lookup for user segment %s ...", segment)
        return cls.query.filter(cls.user_segment == segment)

    @classmethod
    def find_by_viewed_in_last7d(cls, viewed_in_last7d: bool = True) -> list:
        """ Returns all Recommendations viewed in last 7d """
        logger.info("Processing viewed_in_last7d lookup for %s ...", viewed_in_last7d)
        return cls.query.filter(cls.viewed_in_last7d == viewed_in_last7d)

    @classmethod
    def find_by_bought_in_last30d(cls, bought_in_last30d: bool = True) -> list:
        """ Returns all Recommendations bought in last 30d """
        logger.info("Processing bought_in_last30d lookup for %s ...", bought_in_last30d)
        return cls.query.filter(cls.bought_in_last30d == bought_in_last30d)

    @classmethod
    def find_by_last_relevance_date(cls, last_relevance_date: str) -> list:
        """ Returns all Recommendations by given last relevance date """
        logger.info("Processing lookup for last_relevance_date %s ...", last_relevance_date)
        return cls.query.filter(cls.last_relevance_date == date.fromisoformat(last_relevance_date))

    @classmethod
    def find_after_last_relevance_date(cls, last_relevance_date: str) -> list:
        """ Returns all Recommendations on or after given last relevance date """
        logger.info("Processing lookup after last_relevance_date %s ...", last_relevance_date)
        return cls.query.filter(cls.last_relevance_date >= date.fromisoformat(last_relevance_date))

    @classmethod
    def find_by_recommendation_type(cls, recommendation_type: Type = Type.UNKNOWN) -> list:
        """ Returns all Recommendations for given Type """
        logger.info("Processing lookup for recommendation type %s ...", recommendation_type)
        return cls.query.filter(cls.recommendation_type == recommendation_type)
