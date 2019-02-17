from pymongo import MongoClient   # Imports MongoClient from pymongo
from pprint import pprint         # Imports pprint from pprint

'''
Class mainly used to connect to
the Mongodb database and a
collection.
'''
class HumongousDB:

    '''
    Initializes client, database,
    collection and cursor all to
    None.
    '''
    def __init__(self):
        self.client = None
        self.database = None
        self.collection = None
        self.cursor = None

    '''
    Initializes connection with Mongodb
    '''
    def init_connection(self):
        self.client =  MongoClient()

    '''
    Close connection with mongodb
    '''
    def close_connection(self):
        self.client.close()

    '''
    Takes in a name and initializes self.database
    with the name given.
    '''
    def init_database(self,name):
        self.database = self.client[name]

    '''
    Takes in a name and initializes self.connection
    with the name given. This can only be done if
    self.database is initialized.
    '''
    def init_collection(self,name):
        self.collection = self.database[name]

    '''
    Clears self.collection
    '''
    def clear_collection(self):
        self.collection.delete_many({})

    '''
    Prints the contents of self.collection
    '''
    def print_collection(self):
        self.cursor = self.collection.find({})
        for data in self.cursor:
            pprint(data)

    '''
    Insert a single data to the self.collection.
    '''
    def insert_token(self,data):
        self.collection.insert(data)



    '''
    Prints various statistics of the 'Bookkeeping' collection.
    '''
    def print_collection_stats(self):
        print(self.database.command("collstats", "Images"))

    '''
    Takes in a query and returns postings based on the input query.
    '''
    def retrieve(self,query):
        return self.collection.find({"Token":query})