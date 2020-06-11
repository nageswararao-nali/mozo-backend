from pymongo import MongoClient
import urllib.parse
import boto3
from boto3.dynamodb.conditions import Key, Attr

class CONNECTION_MONGODB:
    """[Class holds the mongodb connection.]
    """

    def __init__(self):
        # username = urllib.parse.quote_plus('BluesinqAdmin')
        # password = urllib.parse.quote_plus('Bluesinq2015awsdkl;123')
        username = urllib.parse.quote_plus('Mozoadmin')
        password = urllib.parse.quote_plus('Mozo1986')
        self.client1 = MongoClient(
            'mongodb://%s:%s@localhost:21778/' % (username, password), connect=True)
        self.client2 = MongoClient(
            'mongodb://%s:%s@localhost:21778/' % (username, password), connect=False)
        self.local_toserver_client = MongoClient(
            'mongodb://18.222.230.151:21778/', connect=True)
        self.local_client = MongoClient(
            'mongodb://localhost:27017/', connect=True)
        # self.db = self.client['bluesinq_EC2_DB']

    def mongo_client_1(self):
        return self.client1

    def mongo_client_2(self):
        return self.client2

    def mongo_local_client(self):
        return self.local_client

    def mongo_local_to_server_client(self):
        return self.local_toserver_client

class CONNECTION_S3:
    """[Class holds the S3 connection.]
    """

    def __init__(self):
        self.s3 = boto3.client('s3',
                                    aws_access_key_id='AKIAZ6OGIW7X6MO3QBWM',
                                    aws_secret_access_key='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',
                                    region_name='ap-south-1')

    def s3_client(self):
        return self.s3

