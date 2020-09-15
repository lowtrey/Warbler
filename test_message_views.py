"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testusertwo = User.signup(username="testusertwo",
                                        email="testtwo@test.com",
                                        password="testusertwo",
                                        image_url=None)

        db.session.commit()

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_add_message(self):
        """Can a logged in user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can run
            # the rest of our tests

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_delete_message(self):
        """Can a logged in user delete a message?"""
        
        message = Message(text="Hello")
        self.testuser.messages.append(message)
        db.session.commit()

        # Grab the message ID
        message_id = self.testuser.messages[0].id

        with self.client as c:
            # Mimic logged in user
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Make sure it redirects
            resp = c.post(f"/messages/{message_id}/delete", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIsNone(Message.query.get(message.id))
            self.assertEqual(len(User.query.get(self.testuser.id).messages), 0)

    def test_delete_message_unauthorized(self):
        """Can user delete another user's message?"""

        message = Message(text="Hello again")
        self.testusertwo.messages.append(message)
        db.session.commit()

        # Grab the message ID
        message_id = self.testusertwo.messages[0].id

        with self.client as c:
            # Mimic logged in user (not message owner)
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Make sure it redirects
            response = c.post(f"/messages/{message_id}/delete", follow_redirects=True)
            html = response.get_data(as_text=True)  

            self.assertEqual(response.status_code, 200) 
            self.assertIn("Access unauthorized.", html)

    def test_message_logged_out(self):
        """Can a logged out user add or delete a message?"""

        with self.client as c:
            add_response = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            add_html = add_response.get_data(as_text=True)

            # Make sure it redirects
            self.assertEqual(add_response.status_code, 200)
            self.assertIn("Access unauthorized.", add_html)


            delete_response = c.post("/messages/1/delete", follow_redirects=True)
            delete_html = delete_response.get_data(as_text=True)

            # Make sure it redirects
            self.assertEqual(delete_response.status_code, 200)
            self.assertIn("Access unauthorized.", delete_html)