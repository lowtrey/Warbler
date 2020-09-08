"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="testtwo@test.com",
            username="testusertwo",
            password="HASHED_PASSWORD_TWO"
        )

        db.session.add(u)
        db.session.add(u2)
        db.session.commit()

        self.client = app.test_client()
        self.user_one = u
        self.user_two = u2

    def test_user_model(self):
        """Does basic model work?"""

        # Users should have no messages & no followers
        self.assertEqual(len(self.user_one.messages), 0)
        self.assertEqual(len(self.user_one.followers), 0)
        self.assertEqual(len(self.user_two.messages), 0)
        self.assertEqual(len(self.user_two.followers), 0)
    
    def test_repr(self):
        """Does the repr method work as expected?"""

        repr_one = f"<User #{self.user_one.id}: {self.user_one.username}, {self.user_one.email}>"
        repr_two = f"<User #{self.user_two.id}: {self.user_two.username}, {self.user_two.email}>"
  
        self.assertEqual(repr(self.user_one), repr_one)
        self.assertEqual(repr(self.user_two), repr_two)
    
    def test_is_following(self):
        """Does the is_following method work as expected?"""

        self.assertFalse(self.user_one.is_following(self.user_two))
        self.assertFalse(self.user_two.is_following(self.user_one))

        # Have Users Follow Each Other & Test
        self.user_one.following.append(self.user_two)
        self.user_two.following.append(self.user_one)

        db.session.commit()

        self.assertTrue(self.user_one.is_following(self.user_two))
        self.assertTrue(self.user_two.is_following(self.user_one))
    
    def test_is_followed_by(self):
        """Does the is_followed-by method work as expected?"""

        self.assertFalse(self.user_one.is_followed_by(self.user_two))
        self.assertFalse(self.user_two.is_followed_by(self.user_one))

        # Have Users Follow Each Other & Test
        self.user_one.following.append(self.user_two)
        self.user_two.following.append(self.user_one)
        
        db.session.commit()

        self.assertTrue(self.user_one.is_followed_by(self.user_two))
        self.assertTrue(self.user_two.is_followed_by(self.user_one))