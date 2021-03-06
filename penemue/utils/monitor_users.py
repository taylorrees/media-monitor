from twython import Twython
from time import time

from .config import db
from .limiter import limiter
from credentials import app_key
from credentials import app_secret
from credentials import auth_token
from credentials import auth_secret


@limiter("users/lookup")
def lookup(user_id):
    """Twitter api wrapper to enforce rate limit."""
    # rate limited
    cr = [app_key, app_secret, auth_token, auth_secret]
    twitter = Twython(*cr)
    return twitter.lookup_user(user_id=user_id)


class MonitorUsers(object):

    def __init__(self):
        self.users = [user for user in db.users.find()]

    def __archive(self):
        """Archive all current users."""
        # archive current users
        db.archive.insert({
            "timestamp": time(),
            "document_type": "users",
            "data": self.users
        })

    def __store(self):
        """Store the users to the database."""
        # overwite existing users
        db.users.remove({})
        db.users.insert_many(self.users)

    def __collect(self):
        """Make calls to twitter api to collect profiles."""
        # collect profiles of all users
        user_ids = [user["id_str"] for user in self.users]
        updated = []

        for i in range(0, len(self.users), 100):
            # take batches of 100 ids
            j = i + 100
            user_id = user_ids[i:j]
            updated += lookup(user_id)


    def update(self):
        """Update existing user profiles."""

        print("Update Users")
        print("\t 1. Archiving")
        self.__archive()
        print("\t 2. Collecting")
        self.__collect()
        print("\t 3. Storing")
        self.__store()
