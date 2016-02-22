import pprint
import json, jsonpickle
from dotamatch import get_key
from dotamatch.history import MatchHistoryBySequenceNum
from dotamatch.players import PlayerSummaries
from dotamatch.heroes import Heroes
import schedule, time
from pymongo import MongoClient, ASCENDING

class Main():
    def __init__(self):
        self.client = MongoClient('localhost', 3001)
        self.db = self.client.meteor
        self.matches = self.db.matches
        self.preferences = self.db.preferences
        # Store key in ~/.steamapi
        self.key = get_key()

    def getMatches(self):
        sequence_num = self.preferences.find_one()["match_sequence_num"]
        history = MatchHistoryBySequenceNum(self.key)
        last_sequence_num = 0
        for match in history.matches(start_at_match_seq_num = sequence_num):
            last_sequence_num = match.match_seq_num
            mdict = match.__dict__
            mdict.pop("parent", None)
            try:
                self.matches.insert_one(mdict)
            except:
                print "Cannot insert match_id %d" % match.match_id

        # Update match_sequence_num
        self.preferences.update_one({"type": "settings"}, {"$set": {"match_sequence_num": last_sequence_num + 1}})


print "Welcome to the bot"
m = Main()
m.getMatches()
