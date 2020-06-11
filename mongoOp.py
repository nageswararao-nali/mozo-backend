from datetime import datetime
from datetime import date
from pprint import pprint
import jwt
from bson.objectid import ObjectId
import pymongo
from math import sin, cos, sqrt, atan2, radians

def get_iso_format_datetime():
    return datetime.now().isoformat()

def get_token(email):
    encoded_jwt = jwt.encode({'email': email}, 'hitachi', algorithm='HS256')
    return encoded_jwt

def get_email_from_token(token):
    decoded_jwt = jwt.decode(token, 'hitachi', algorithm='HS256')
    return decoded_jwt

class MONGO_OPERATION():
    def __init__(self, mongoClient):
        self.client = mongoClient['mozo_db']

    def save_user_data_in_mongo(self, **userData):
        try:
            userData['creationTime'] = get_iso_format_datetime()
            userData['lastUpdationTime'] = get_iso_format_datetime()
            userData['token'] = get_token(userData['emailId'])
            collection = self.client.usersDetail
            collection.update_one({'_id': userData['emailId']}, {'$set': userData}, upsert=True)
            return True
        except Exception as e:
            print(e)
            return False

    def update_user_token_in_mongo(self, email_id):
        try:
            collection = self.client.usersDetail
            token = get_token(email_id)
            print(token)
            collection.update_one({'_id': email_id}, {'$set': {'token': token}})
            return True
        except Exception as e:
            print(e)
            return False

    def get_user_token_in_mongo(self, email_id):
        try:
            collection = self.client.usersDetail
            result = collection.find_one({'_id': email_id}, {'token': 1, '_id': 0})
            return result
        except Exception as e:
            print(e)
            return False

    def delete_user_data_from_mongo(self, email_id):
        try:
            collection = self.client.usersDetail
            collection.remove({'_id': email_id})
            return True
        except Exception as e:
            print(e)
            return False

    def get_user_data_from_mongo(self, email_id):
        try:
            collection = self.client.usersDetail
            result = collection.find_one({'_id': email_id})
            return result
        except Exception as e:
            print(e)
            return False

    def get_all_users_from_mongo(self):
        print("get_all_users_from_mongo mongo op")
        try:
            collection = self.client.users
            output = []
            for data in collection.find({}):
                if 'access_token' in data:
                    del data['access_token']
                if 'otp' in data:
                    del data['otp']
                output.append(data)
            return output
        except Exception as e:
            print(e)
            return False


    def check_user_exists_from_mongo(self, key, value):
        try:
            collection = self.client.users
            if key == "_id":
                value = ObjectId(value)
            result = collection.find_one({key: value})
            return result
        except Exception as e:
            print("problem in getting user from db")
            print(e)
            return False

    def get_user_details(self, key, value, projectData):
        try:
            collection = self.client.users
            if key == "_id":
                value = ObjectId(value)
            result = collection.find_one({key: value}, projectData)
            return result
        except Exception as e:
            print("problem in getting user from db")
            print(e)
            return False

    def check_buzz_sent(self, fromUser, toUser):
        try:
            collection = self.client.user_messages
            output = []
            count = collection.find({'fromUser': fromUser, 'toUser': toUser, 'status': {"$nin": [4, 5]}, "messageType": { "$regex" : 'buzz' , "$options" : "i"}}).count()
            return count
        except Exception as e:
            print(e)
            return False

    def get_today_buzz_sent_count(self, fromUser):
        try:
            today = date.today()
            today_date = datetime(today.year, today.month, today.day, 0, 0, 0).isoformat()
            print(today_date)
            collection = self.client.user_messages
            output = []
            count = collection.find({'fromUser': fromUser, "messageType": { "$regex" : 'buzz' , "$options" : "i"}, "sentTime":{"$gte": today_date}}).count()
            return count
        except Exception as e:
            print(e)
            return False

    def get_today_like_sent_count(self, fromUser):
        try:
            today = date.today()
            today_date = datetime(today.year, today.month, today.day, 0, 0, 0).isoformat()
            print(today_date)
            collection = self.client.user_interests
            output = []
            query = {'fromUser': fromUser, "sentTime":{"$gte": today_date}, '$or': [{"interestType": { "$regex" : 'super_like' , "$options" : "i"}}, {"interestType": { "$regex" : 'like' , "$options" : "i"}}] }
            count = collection.find(query).count()
            return count
        except Exception as e:
            print(e)
            return False

    def check_interest_exist(self, fromUser, toUser):
        try:
            collection = self.client.user_interests
            output = []
            query = {'fromUser': fromUser, 'toUser': toUser }
            print(query)
            for data in collection.find(query):
                output.append(data)
            return output
        except Exception as e:
            print(e)
            return False

    def check_message_exist(self, fromUser, toUser):
        try:
            collection = self.client.user_messages
            output = []
            query = {'fromUser': fromUser, 'toUser': toUser }
            print(query)
            for data in collection.find(query):
                output.append(data)
            return output
        except Exception as e:
            print(e)
            return False

    def check_like_exist(self, fromUser, toUser):
        try:
            collection = self.client.user_interests
            output = []
            query = {'fromUser': fromUser, 'toUser': toUser, 'status': 0, '$or': [{"interestType": { "$regex" : 'super_like' , "$options" : "i"}}, {"interestType": { "$regex" : 'like' , "$options" : "i"}}] }
            print(query)
            for data in collection.find(query):
                output.append(data)
            return output
        except Exception as e:
            print(e)
            return False

    def update_interest_status(self, fromUser, toUser):
        try:
            collection = self.client.user_interests
            output = []
            query = {'$or': [{"fromUser": fromUser, 'toUser': toUser}, {"fromUser": toUser, 'toUser': fromUser}] }
            print(query)
            for data in collection.update(query, {'$set': {'status': 6}}):
                output.append(data)
            return output
        except Exception as e:
            print(e)
            return False

    def check_crush_sent(self, fromUser, toUser):
        try:
            collection = self.client.user_interests
            output = []
            count = collection.find({'fromUser': fromUser, 'toUser': toUser, 'status': 0, "interestType": { "$regex" : 'super_like' , "$options" : "i"}}).count()
            return count
        except Exception as e:
            print(e)
            return False

    def get_users_on_localtion_from_mongo(self, userDetails):
        try:
            print("datetime")
            print(date.today())
            earthRadius = 6371.0
            maxDistance = userDetails['distance'] if userDetails['distance'] else 50.0
            max_distance_radians = maxDistance / earthRadius
            output = []
            collection = self.client.users
            # collection.create_index([("lat_long", pymongo.GEO2D)])
            user_id = userDetails['_id']
            # lat_long.append(maxDistance)
            query = {
                "lat_long": {
                    "$nearSphere": userDetails['lat_long'],
                    "$maxDistance": max_distance_radians
                }
            }
            print(query)
            for data in collection.find(query):
                if user_id == data['_id']:
                    continue
                if (userDetails['interested_in'] == 'Male' and (data['gender'] == 'Man' or data['gender'] == 'Other')) or (userDetails['interested_in'] == 'Female' and (data['gender'] == 'Female' or data['gender'] == 'Other')) or (userDetails['interested_in'] == 'Other' and (data['gender'] == 'Man' or data['gender'] == 'Female')):
                    continue;
                isValidUser = True
                if 'filter' in userDetails:
                    print(userDetails['filter'])
                    for filterData in userDetails['filter']:
                        # if filterData in userDetails['filter'] and 'filter' in data and filterData in data['filter'] and userDetails['filter'][filterData] != "" and userDetails[filterData] in data['filter'][filterData]:
                        # print(filterData)
                        # print(userDetails['filter'][filterData])
                        # print(data)

                        # if userDetails['settings'][filterData] != "": 
                        #     print(userDetails['settings'][filterData])
                        #     if filterData in data['filter']:
                        #         print(filterData)
                        #         print("***")
                        #         if isinstance(data['filter'][filterData], list) and (userDetails['settings'][filterData] not in data['filter'][filterData]):
                        #             print("here")
                        #             isValidUser = False
                        #         else:
                        #             if userDetails['settings'][filterData] != data['filter'][filterData]:
                        #                 isValidUser = False
                        #     else:
                        #         isValidUser = False
                        # print(len(userDetails['filter'][filterData]))
                        if userDetails['filter'][filterData] != "" and len(userDetails['filter'][filterData]) != 0: 
                            # print(userDetails['filter'][filterData], " ---")
                            if filterData in data['settings']:
                                # print(filterData, "---", userDetails['filter'][filterData])
                                # print(data['settings'][filterData])
                                # print("***")
                                if isinstance(userDetails['filter'][filterData], list) and (data['settings'][filterData] not in userDetails['filter'][filterData]):
                                    # print("here")
                                    isValidUser = False
                                else:
                                    if userDetails['filter'][filterData] != data['settings'][filterData]:
                                        isValidUser = False
                            else:
                                isValidUser = False
                    is_interest_exist = self.check_interest_exist(str(user_id), str(data['_id']))
                    if(is_interest_exist and len(is_interest_exist) > 0):
                        isValidUser = False

                    is_message_exist = self.check_message_exist(str(user_id), str(data['_id']))
                    if(is_message_exist and len(is_message_exist) > 0):
                        isValidUser = False

                    if isValidUser == False:
                        continue
                    else:
                        R = 6373.0

                        lat1 = radians(userDetails['lat_long'][1])
                        lon1 = radians(userDetails['lat_long'][0])
                        lat2 = radians(data['lat_long'][1])
                        lon2 = radians(data['lat_long'][0])

                        dlon = lon2 - lon1
                        dlat = lat2 - lat1

                        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
                        c = 2 * atan2(sqrt(a), sqrt(1 - a))

                        distance = R * c

                        data['user_distance'] = round(distance, 1)

                        buzzCount = self.check_buzz_sent(str(user_id), str(data['_id']))
                        if buzzCount:
                            data['isBuzzSent'] = True
                        else:
                            data['isBuzzSent'] = False
                        buzzCount = self.check_crush_sent(str(data['_id']), str(user_id))
                        if buzzCount:
                            data['isCrush'] = True
                        else:
                            data['isCrush'] = False
                        
                data['_id'] = str(data['_id'])
                output.append(data)
            # print(output)
            return output
        except Exception as e:
            print("problem in getting user from db")
            print(e)
            return False

    def add_new_user(self, data):
        try:
            collection = self.client.users
            print(data)
            collection.insert(data)
            return True
        except Exception as e:
            print(e)
            return False

    def update_user_data_in_mongo(self, where_key, where_value, update_data):
        try:
            collection = self.client.users
            if where_key == "_id":
                where_value = ObjectId(where_value)
            collection.update_one({where_key: where_value}, {'$set': update_data})
            return True
        except Exception as e:
            print(e)
            return False

    def user_subscribe(self, data):
        try:
            collection = self.client.user_subscriptions
            x = collection.insert(data)
            return data
        except Exception as e:
            print(e)
            return False

# Subscripitons 
    def get_all_subscriptions_from_mongo(self):
        print("get_all_subsctiptions_from_mongo mongo op")
        try:
            collection = self.client.subscriptions
            output = []
            for data in collection.find({}):
                data['_id'] = str(data['_id'])
                output.append(data)
            return output
        except Exception as e:
            print(e)
            return False

    def save_new_subscription(self, data):
        try:
            collection = self.client.subscriptions
            x = collection.insert(data)
            return data
        except Exception as e:
            print(e)
            return False
    
    def get_subscription_from_mongo(self, key, value):
        try:
            collection = self.client.subscriptions
            if key == '_id':
                value = ObjectId(value)
            result = collection.find_one({key: value})
            return result
        except Exception as e:
            print(e)
            return False

# User interested users
    def add_new_interest(self, data):
        try:
            collection = self.client.user_interests
            x = collection.insert(data)
            return data
        except Exception as e:
            print(e)
            return False

    def update_interest(self, where_key, where_value, update_data):
        try:
            collection = self.client.user_interests
            if where_key == "_id":
                where_value = ObjectId(where_value)
            collection.update_one({where_key: where_value}, {'$set': update_data})
            return True
        except Exception as e:
            print(e)
            return False

    def update_message(self, where_key, where_value, update_data):
        try:
            collection = self.client.user_messages
            if where_key == "_id":
                where_value = ObjectId(where_value)
            collection.update_one({where_key: where_value}, {'$set': update_data})
            return True
        except Exception as e:
            print(e)
            return False

    def get_likes_count(self, user_id):
        try:
            collection = self.client.user_interests
            countData = collection.find({"toUser": user_id, 'isAccept': False, '$or':[{"interestType":{ "$regex" : 'like' , "$options" : "i"}}, { "interestType" : {"$regex" : 'super_like' , "$options" : "i"}}] }).count()
            return {'count': countData}
        except Exception as e:
            print(e)
            return False

# Messages
    def add_message(self, data):
        try:
            collection = self.client.user_messages
            x = collection.insert(data)
            return data
        except Exception as e:
            print(e)
            return False

    def get_send_messages(self, user_id, messageType):
        try:
            collection = self.client.user_messages
            output = []
            for data in collection.find({'fromUser': user_id, "messageType": { "$regex" : messageType , "$options" : "i"}}).sort([('sentTime', -1)]):
                data['_id'] = str(data['_id'])
                output.append(data)
            return output
        except Exception as e:
            print(e)
            return False

    def get_received_messages(self, user_id, messageType):
        try:
            collection = self.client.user_messages
            output = []
            for data in collection.find({'toUser': user_id, "messageType": { "$regex" : messageType , "$options" : "i"}}).sort([('sentTime', -1)]):
                data['_id'] = str(data['_id'])
                output.append(data)
            return output
        except Exception as e:
            print(e)
            return False

    def get_all_messages(self, user_id):
        try:
            output = []
            collection = self.client.user_messages
            messages = {
                "messages": [],
                "buzz": []
            }
            for data in collection.find({'$or':[{'fromUser': user_id}, {'toUser': user_id}] }).sort([('sentTime', -1)]):
                output.append(data)
            userIds = {}
            for userData in output:
                if userData['fromUser'] not in userIds:
                    user = self.get_user_details('_id', userData['fromUser'], {"name": 1, "photos": 1})
                    userIds[userData['fromUser']] = user
                    userIds[userData['fromUser']]['_id'] = str(user['_id'])
                if userData['toUser'] not in userIds:
                    user = self.get_user_details('_id', userData['toUser'], {"name": 1, "photos": 1})
                    userIds[userData['toUser']] = user
                    userIds[userData['toUser']]['_id'] = str(user['_id'])

            for data in output:
                data['_id'] = str(data['_id'])
                data['fromUser'] = userIds[data['fromUser']]
                data['toUser'] = userIds[data['toUser']]
                if data['messageType'].lower() == "message":
                    messages['messages'].append(data)
                if data['messageType'].lower() == "buzz" and str(data['toUser']['_id']) == user_id:
                    messages['buzz'].append(data)
            if len(messages['messages']):
                final_messages = []
                for data in messages['messages']:
                    isExists = False
                    if len(final_messages):
                        for f_message in final_messages:
                            if (str(data['fromUser']['_id']) == str(f_message['fromUser']['_id']) and str(data['toUser']['_id']) == str(f_message['toUser']['_id'])) or (str(data['fromUser']['_id']) == str(f_message['toUser']['_id']) and str(data['toUser']['_id']) == str(f_message['fromUser']['_id'])):
                                isExists = True
                        if isExists:
                            continue
                        else:
                            final_messages.append(data)
                    else:
                        final_messages.append(data)
                messages['messages'] = final_messages
            return messages
        except Exception as e:
            print("problem in fetching messges")
            print(e)
            return False

    def get_all_matches(self, user_id):
        try:
            output = []
            interests = []
            collection = self.client.user_interests
            query = {
                '$and': [
                    {'$or':[{'fromUser': user_id}, {'toUser': user_id}]}, 
                    {'$or':[{"interestType":{ "$regex" : 'like' , "$options" : "i"}}, { "interestType" : {"$regex" : 'super_like' , "$options" : "i"}}]}
                ], 
                'isAccept': True
            }
            # print(user_id)
            # print(query)
            # for data in collection.find({'$or':[{'fromUser': user_id}, {'toUser': user_id}], 'isAccept': True, '$or':[{"interestType":{ "$regex" : 'like' , "$options" : "i"}}, { "interestType" : {"$regex" : 'super_like' , "$options" : "i"}}] }).sort([('sentTime', -1)]):
            for data in collection.find(query).sort([('sentTime', -1)]):
                output.append(data)
            userIds = {}
            print(output)
            for userData in output:
                if userData['fromUser'] not in userIds and str(userData['fromUser']) != user_id:
                    user = self.get_user_details('_id', userData['fromUser'], {"name": 1, "photos": 1})
                    user['_id'] = str(user['_id'])
                    user['status'] = userData['status']
                    interests.append(user)
                    userIds[userData['fromUser']] = 1
                if userData['toUser'] not in userIds and str(userData['toUser']) != user_id:
                    user = self.get_user_details('_id', userData['toUser'], {"name": 1, "photos": 1})
                    user['_id'] = str(user['_id'])
                    user['status'] = userData['status']
                    interests.append(user)
                    userIds[userData['toUser']] = 1
            return interests
        except Exception as e:
            print("problem in fetching matches")
            print(e)
            return False

    def get_all_user_chat_messages(self, fromUser, toUser):
        try:
            collection = self.client.user_messages
            output = []
            for data in collection.find({'$or':[{'fromUser': fromUser, 'toUser': toUser}, {'fromUser': toUser, 'toUser': fromUser}] }).sort([('sentTime', 1)]):
                data['_id'] = str(data['_id'])
                output.append(data)
            return output
        except Exception as e:
            print(e)
            return False

    def get_user_interests(self, user_id, interestType):
        try:
            collection = self.client.user_interests
            output = []
            for data in collection.find({'toUser': user_id, 'isAccept': False, '$or':[{"interestType":{ "$regex" : 'like' , "$options" : "i"}}, { "interestType" : {"$regex" : 'super_like' , "$options" : "i"}}] }):
                data['_id'] = str(data['_id'])
                output.append(data)
            return output
        except Exception as e:
            print(e)
            return False

    def get_users_by_mobile_numbers(self, user_ids):
        try:
            collection = self.client.users
            output = []
            print("user ids in mongo")
            print(user_ids)
            for data in collection.find({"_id": {"$in": user_ids}}):
                if 'access_token' in data:
                    del data['access_token']
                del data['otp']
                data['_id'] = str(data['_id'])
                output.append(data)
            return output
        except Exception as e:
            print(e)
            return False
