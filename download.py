import pprint, os
import json, jsonpickle
from dotamatch import get_key
from dotamatch.history import MatchHistoryBySequenceNum
from dotamatch.players import PlayerSummaries
from dotamatch.heroes import Heroes
import schedule, time
from pymongo import MongoClient, ASCENDING

class Main():
    def __init__(self):
        self.client = MongoClient(os.environ['DOKKU_MONGO_DOTA2STATS_PORT_27017_TCP_ADDR'], 27017)
        self.db = self.client.dota2stats
        self.matches = self.db.matches
        self.preferences = self.db.preferences
        # Store key in ~/.steamapi
        self.key = get_key()
        self.matches.create_index([("match_id", ASCENDING)], unique=True)

    def getMatches(self):
        sequence_num = self.preferences.find_one()["match_sequence_num"]
        history = MatchHistoryBySequenceNum(self.key)
        last_sequence_num = 0
        for match in history.matches(start_at_match_seq_num = sequence_num):
            last_sequence_num = match.match_seq_num
            match.herolist = []
            match.interpret_version = 0
            for player in match.players:
                match.herolist.append(player["hero_id"])
            mdict = match.__dict__
            mdict.pop("parent", None)
            try:
                self.matches.insert_one(mdict)
                print "Insert match_id %d into db" % match.match_id
            except:
                print "Cannot insert match_id %d" % match.match_id

        # Update match_sequence_num
        self.preferences.update_one({"type": "settings"}, {"$set": {"match_sequence_num": last_sequence_num + 1}})


print "Starting the bot to grab matches data from DotA API"
m = Main()
schedule.every(1).minutes.do(m.getMatches)

while True:
    schedule.run_pending()
    time.sleep(1)
