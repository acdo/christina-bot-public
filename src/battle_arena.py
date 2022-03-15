import discord
from pymongo import MongoClient, collection
from datetime import datetime


def get_opponent(client: MongoClient, opp_team: str):
    db = client['BA']
    return db[opp_team]


def add_counter(opponent: collection, img_url: str):
    print(f'Adding team and counter to database.')
    counter_item = {
        'Image URL': img_url,
        'Upvotes': 0,
        'Downvotes': 0,
        'Upvoters': [],
        'Downvoters': [],
        'Timestamp': datetime.now()
    }
    _id = opponent.insert_one(counter_item)
    item_id = _id.inserted_id
    print(f'Added counter to database with id {item_id}.')
