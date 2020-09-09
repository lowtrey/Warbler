"""Message model tests."""

import os
from app import app
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

db.drop_all()
db.create_all()

class MessageModelTestCase(TestCase):
  """Test views for Messages"""

  def setUp(self):
    """Create test client, add sample data."""

    User.query.delete()
    Message.query.delete()
    Follows.query.delete()

    user_one = User.signup(
        email="test@test.com",
        username="testuser",
        password="HASHED_PASSWORD",
        image_url="https://www.testimage.com"
    )

    user_two = User.signup(
        email="testtwo@test.com",
        username="testusertwo",
        password="HASHED_PASSWORD_TWO",
        image_url="https://www.testimage.com"
    )

    message_one = Message(text="test message one")
    message_two = Message(text="test message two")
    message_three = Message(text="test message three")
    message_four = Message(text="test message four")
    message_five = Message(text="test message five")
    message_six = Message(text="test message six")

    user_one.messages.extend([message_one, message_two, message_three])
    user_two.messages.extend([message_four, message_five, message_six])

    db.session.commit()

    self.client = app.test_client()
    self.user_one = user_one
    self.user_two = user_two
    self.message_one = message_one
    self.message_four = message_four

  def test_message_model(self):
    """Does basic model work?"""
    
    # Each user should have 3 messages
    self.assertEqual(len(self.user_one.messages), 3)
    self.assertEqual(len(self.user_two.messages), 3)

  def test_relationship(self):
    """Does the user relationship work as expected?"""

    self.assertIs(self.message_one.user, self.user_one)
    self.assertIs(self.message_four.user, self.user_two)

  # def test_message_creation(self):
  #   """Is an error raised for non-nullable values?"""

  #   with self.assertRaises(exc.IntegrityError):
  #     invalid_message = Message(text=None)

  #     db.session.add(invalid_message)
  #     # self.assertRaises(IntegrityError, db.session.commit)
