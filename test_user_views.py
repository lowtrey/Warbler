"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


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


class UserViewTestCase(TestCase):
    """Test views for users."""

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

        self.testuserthree = User.signup(username="testuserthree",
                                        email="testthree@test.com",
                                        password="testuserthree",
                                        image_url=None)

        self.testuser.following.append(self.testusertwo)
        self.testusertwo.following.append(self.testuser)

        db.session.commit()

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_follow(self):
        """Can a logged in user follow another user?"""

        with self.client as c:
            # Grab testuser id
            user_id = self.testuser.id

            # Mimic log in and follow
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuserthree.id

            response = c.post(f"/users/follow/{user_id}", follow_redirects=True)
            html = response.get_data(as_text=True)

            self.assertEqual(len(User.query.get(user_id).followers), 2)
            self.assertIn(self.testuser.username, html)
    
    def test_unfollow(self):
        """Can a logged in user unfollow another user?"""

        with self.client as c:
            user_id = self.testusertwo.id

            # Mimic log in and unfollow
            with c.session_transaction() as sess:
              sess[CURR_USER_KEY] = self.testuser.id

            response = c.post(f"/users/stop-following/{user_id}", follow_redirects=True)
            html = response.get_data(as_text=True)

            self.assertEqual(len(User.query.get(user_id).followers), 0)
            self.assertNotIn(self.testusertwo.username, html)

    def test_update(self):
        """Can a logged in user update their profile?"""

        with self.client as c:

            # Mimic log in and update
            with c.session_transaction() as sess:
              sess[CURR_USER_KEY] = self.testuser.id
            
            test_data = {
              "bio": "test bio",
              "email": "updateduser@test.com",
              "username": "updateduser",
              "password": "testuser",
              "image_url": None,
              "header_image_url": None
            }

            response = c.post(f"/users/{self.testuser.id}/update", data=test_data, follow_redirects=True)
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(test_data["username"], html)

    def test_delete(self):
        """Can a logged in user delete their profile?"""

        with self.client as c:

            # Mimic log in and delete
            with c.session_transaction() as sess:
              sess[CURR_USER_KEY] = self.testuserthree.id

            response = c.post("/users/delete")

            # Make sure it redirects
            self.assertEqual(response.status_code, 302)
            self.assertIsNone(User.query.get(self.testuserthree.id))
