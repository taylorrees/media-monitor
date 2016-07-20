from json import load
from collect import Collect
from db import DB
from pprint import pprint


class Collect(Collect):
    def store(self, collection):
        # extend and alter store
        DB[collection].delete_many({})
        DB[collection].insert_many(self.members)


def statistics():
    """Get the number of users, tweets, original tweets, retweets
    and replies for all users, journalists, organisations and users
    external to the study."""

    # get sets of id_str's
    journalists = DB.journalists.distinct("id_str")
    organisations = DB.organisations.distinct("id_str")

    # used to collect results
    stats = {}

    # -- ALL --
    # -- All Accounts --
    # All tweets stored within the tweets collection.
    # This provides a base figure to work from.

    stats["all"]["retweets"] = DB.tweets.find({
        "retweeted_status": {"$exists": True}
    }).count()

    # -- JOI --
    # -- Journalists of Interest --
    # Those tweets created by the list of journalists
    # provided to the streaming follow parameter.

    stats["joi"]["retweets"] = DB.tweets.find({
        "user.id_str": {"$in": journalists},
        "retweeted_status": {"$exists": True}
    }).count()

    # -- OOI --
    # -- Organisations of Interest --
    # Those tweets created by the list of organisations
    # provided to the streaming follow parameter.

    stats["ooi"]["retweets"] = DB.tweets.find({
        "user.id_str": {"$in": organisations},
        "retweeted_status": {"$exists": True}
    }).count()

    # -- EXT --
    # -- External Accounts --
    # Those tweets created created by any user not
    # provided to the streaming follow parameter.

    stats["ext"]["retweets"] = DB.tweets.find({
        "user.id_str": {"$nin": (journalists + organisations)},
        "retweeted_status": {"$exists": True}
    }).count()
    
    return stats