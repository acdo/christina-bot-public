import copy
import time

import discord
from pymongo import MongoClient
from cross_package_helpers import validate_names, get_image_url_cleanup
from tokens import MONGO_TOKEN

import battle_arena


def get_mongo_client():
    # noinspection PyPep8
    return MongoClient(MONGO_TOKEN)


def add_ba_counter(opp: str, img_url: str):
    print(f'Adding counter for {opp} to database.')
    client = get_mongo_client()
    opponent = battle_arena.get_opponent(client, opp)
    battle_arena.add_counter(opponent, img_url)
    print('Adding counter completed')
    return []


def get_opponent_collection(opp: str):
    print(f'Retrieving collection for {opp}')
    client = get_mongo_client()
    opp_formatted = opp.strip().lower()
    opponent = battle_arena.get_opponent(client, opp_formatted)
    return opponent


def get_ba_counters(opp: str):
    print(f'Retrieving counters for {opp}.')
    client = get_mongo_client()
    opp_formatted = opp.strip().lower()
    opp_names = opp_formatted.split()
    invalid_names = validate_names(opp_names)
    if len(invalid_names) != 0:
        print(f'Invalid names found, returning.')
        return True, invalid_names

    final_opp_names = ' '.join(opp_names)
    opponent = battle_arena.get_opponent(client, final_opp_names)
    counters = []
    cursor = opponent.find()
    for counter in cursor:
        counters.append(counter)
    print('Retrieved counters from database.')
    return False, counters


def url_cleanup():
    client = get_mongo_client()
    ba_database = client['BA']
    collection_names = ba_database.list_collection_names()
    counter = 0
    for name in collection_names:
        counter += 1
        collection = ba_database[name]
        print(f'Checking {name} ({counter}/64)')
        for doc in collection.find({}):
            if "discordapp" in doc['Image URL']:
                print(f'Now updating {doc}')
                new_doc = copy.copy(doc)
                new_url = get_image_url_cleanup(doc['Image URL'])
                new_doc['Image URL'] = new_url
                collection.replace_one(doc, new_doc)
                time.sleep(20)
