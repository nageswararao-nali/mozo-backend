import random
import string
import boto3
from botocore.exceptions import ClientError
from pprint import pprint
from mongoOp import MONGO_OPERATION
from connection import CONNECTION_MONGODB, CONNECTION_S3
import os
import csv
# from flaskCelery import make_celery
# import docker
import base64
import json
import subprocess
from subprocess import Popen, PIPE
# from datetime import datetime
import datetime
import jwt
import math, random 
import requests
from bson.objectid import ObjectId
from flask import render_template

# from datetime import datetime, date

# from zipfile import ZipFile
# import shutil

# aws_access_key = os.getenv('AWS_ACCESS_KEY')
# aws_secret_key = os.getenv('AWS_SECRET_KEY')
fromEmail = "otp@mozo.app"
path = 'temp'
aws_access_key = ''
aws_secret_key = ''
sms_api_key = 'nn4K6NVEx060H6Wmqk8QBw'
sms_sender_id = 'MOZODT'
mozo_features = {
      "addFilters": False,
      "buzzCount": 0,
      "crushCount": 0,
      "hideAge": False,
      "hideDistance": False,
      "imageSharing": 0,
      "lastSwipe": False,
      "readTicks": False,
      "swipes": 0,
      "teleport": False,
      "voiceSharing": 0,
      "diamondCount": 0,
      "diamondReceivedCount": 0,
      "diamondSentCount": 0
    }
mozo_settings = {
    "sexual_orientation": "",
    "interested_in": "",
    "drinking": "",
    "smoking": "",
    "exercise": "",
    "religion": "",
    "pets": "",
    "age": "",
    "height": "",
    "type_of_relationship": "",
    "zodiac_sign": "",
    "education": "",
    "work": ""
}
mozo_filters = {
    "sexual_orientation": [],
    "interested_in": [],
    "drinking": [],
    "smoking": [],
    "exercise": [],
    "religion": [],
    "pets": [],
    "age": [],
    "height": "",
    "type_of_relationship": [],
    "zodiac_sign": [],
    "education": "",
    "work": ""
}


# mongoClient = CONNECTION_MONGODB().mongo_local_to_server_client()
mongoClient = CONNECTION_MONGODB().mongo_local_client()
s3Client = CONNECTION_S3().s3_client()

ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generateOTP() : 
  
    # Declare a digits variable   
    # which stores all digits  
    digits = "0123456789"
    OTP = "" 
  
   # length of password can be chaged 
   # by changing value in range 
    for i in range(6) : 
        OTP += digits[math.floor(random.random() * 10)] 
  
    return OTP 

def get_iso_format_datetime():
    return datetime.datetime.now().isoformat()

def get_token(mobile):
    encoded_jwt = jwt.encode({'mobile': mobile}, 'mozo-nag', algorithm='HS256')
    return encoded_jwt

def get_mobile_from_token(token):
    decoded_jwt = jwt.decode(token, 'mozo-nag', algorithm='HS256')
    return decoded_jwt

def get_iso_format_datetime():
    return datetime.datetime.now().isoformat()

def add_user_log_to_database(**userData):
    try:
        result = MONGO_OPERATION(mongoClient).save_user_log_data_in_mongo(**userData)
        if result:
            return True
        return False
    except Exception as e:
        print(e)
        return False


def get_user_logs_from_database():
    try:
        result = MONGO_OPERATION(mongoClient).get_user_logs_from_mongo()
        if result:
            return result
        return False
    except Exception as e:
        print(e)
        return False


def get_all_users_by_email_from_database(email_id):
    try:
        result = MONGO_OPERATION(mongoClient).get_all_users_by_email_from_mongo(email_id)
        if result:
            return result
        return result
    except Exception as e:
        print(e)
        return False

def get_all_users():
    print("get_all_users")
    try:
        result = MONGO_OPERATION(mongoClient).get_all_users_from_mongo()
        if result:
            return result
        return result
    except Exception as e:
        print(e)
        return False
def get_users(user_id):
    try:
        usersData = {}
        user_exists_result = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('_id', user_id)
        user_exists_result['_id'] = str(user_exists_result['_id'])
        usersData['loggedUserData'] = user_exists_result
        if user_exists_result:
            # print(user_exists_result)
            result = MONGO_OPERATION(mongoClient).get_users_on_localtion_from_mongo(user_exists_result)
            if result:
                usersData['usersList'] = result
                return usersData
            print("result")
            print(result)
            usersData['usersList'] = []
            return usersData
        else:
            return False
    except Exception as e:
        print(e)
        return False

def save_new_user(reqData):
    photos = [
        {
            "order": 1,
            "url": ""
        },
        {
            "order": 2,
            "url": ""
        },
        {
            "order": 3,
            "url": ""
        },
        {
            "order": 4,
            "url": ""
        },
        {
            "order": 5,
            "url": ""
        },
        {
            "order": 6,
            "url": ""
        },
        {
            "order": 7,
            "url": ""
        },
        {
            "order": 8,
            "url": ""
        }
    ]
    data = {}
    data['mobile'] = reqData['mobile'] if 'mobile' in reqData else ''
    data['otp'] = reqData['otp'] if 'otp' in reqData else ""
    data['last_otp_sent_time'] = get_iso_format_datetime()
    data['photos'] = photos
    data['about_me'] = ''
    data['profile_pic'] = ''
    data['dob'] = ''
    data['gender'] = ''
    data['work'] = ''
    data['education'] = ''
    data['height'] = ''
    data['sexual_orientation'] = ''
    data['interested_in'] = ''
    data['type_of_relationship'] = ''
    data['drinking'] = ''
    data['smoking'] = ''
    data['zodiac_sign'] = ''
    data['religion'] = ''
    data['pets'] = ''
    data['what_kind_of_person'] = []
    data['teleport_data'] = []
    data['instagram'] = False
    data['linked_in'] = False
    data['spotify'] = False
    data['show_age'] = True
    data['show_distance'] = True
    data['show_name'] = True
    data['age'] = ''
    data['distance'] = 50.0
    data['name'] = reqData['name'] if 'name' in reqData else ''
    data['privacy_policy'] = False
    data['terms_and_conditions'] = False
    data['licences'] = False
    data['hide_advertisements'] = False
    data['online'] = True
    data['is_subscribe'] = False
    data['isPhotoVerified'] = False
    data['isEmailVerified'] = False
    data['status'] = 1
    data['subscription_id'] = ''
    data['email'] = reqData['email'] if 'email' in reqData else ''
    data['lat_long'] = []
    data['last_update_time'] = get_iso_format_datetime()
    data['credits'] = mozo_features
    data['settings'] = mozo_settings
    data['filter'] = mozo_filters
    data['is_login'] = True
    result = MONGO_OPERATION(mongoClient).add_new_user(data)
    return result

def get_otp(reqData, isFacebookLogin):
    try:
        # otp = reqData['mobile'][-6:]
        if isFacebookLogin:
            user_exists_result = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('email', reqData['email'])
            if user_exists_result:
                update_data = {}
                update_data['last_otp_sent_time'] = get_iso_format_datetime()
                update_data['isEmailVerified'] = True
                update_data['is_login'] = True
                result = MONGO_OPERATION(mongoClient).update_user_data_in_mongo('email', reqData['email'], update_data)
            else:
                reqData['otp'] = ""
                token = get_token(reqData['email'])
                reqData['access_token'] = token
                reqData['isEmailVerified'] = True
                reqData['is_login'] = True
                result = save_new_user(reqData)
            user_data_result = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('email', reqData['email'])
            user_data_result['_id'] = str(user_data_result['_id'])
            return user_data_result
        else:
            # sms_url = 'http://sms.pearlsms.com/public/sms/send?sender=PLRSMS&smstype=TRANS&numbers=%s&apikey=%s&message=Your verification code is %s.' % (str(reqData['mobile']), sms_api_key, str(otp))
            
            # otp = generateOTP()
            # mobile = '91'+str(reqData['mobile'])
            # sms_url = 'http://cloud.smshostindia.in/api/mt/SendSMS?APIKey=%s&senderid=%s&channel=Trans&DCS=0&flashsms=0&number=%s&text=Your verification code is %s.&route=1' %(sms_api_key, sms_sender_id, mobile, str(otp))
            # print(sms_url)
            # response = requests.get(sms_url)
            # print(response)
            # print("response")
            # sms_res = response.json()

            otp = reqData['mobile'][-6:]
            sms_res = {'ErrorMessage': 'Done'}
            print(sms_res)
            if 'ErrorMessage' in sms_res and sms_res['ErrorMessage'] == 'Done':
                user_exists_result = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('mobile', reqData['mobile'])
                if user_exists_result:
                    update_data = {}
                    update_data['otp'] = otp
                    update_data['is_login'] = True
                    update_data['last_otp_sent_time'] = get_iso_format_datetime()
                    result = MONGO_OPERATION(mongoClient).update_user_data_in_mongo('mobile', reqData['mobile'], update_data)
                    return result
                else:
                    reqData['otp'] = otp
                    result = save_new_user(reqData)
                    return result
            else:
                return False
    except Exception as e:
        print("error from catch ", e)
        return False

def logout(reqDaata):
    try:
        if reqData['user_id']:
            MONGO_OPERATION(mongoClient).update_user_data_in_mongo('_id', reqData['user_id'], {'is_login': False})
            return True
        else:
            return False

    except Exception as e:
        print(e)
        return False

def verify_otp(reqData):
    try:
        user_exists_result = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('mobile', reqData['mobile'])
        if user_exists_result:
            print(user_exists_result)
            mobile = user_exists_result['mobile']
            otp = user_exists_result['otp']
            if mobile == reqData['mobile'] and otp == reqData['otp']:
                token = get_token(reqData['mobile'])
                MONGO_OPERATION(mongoClient).update_user_data_in_mongo('mobile', reqData['mobile'], {'access_token': token})
                user_exists_result['_id'] = str(user_exists_result['_id'])
                user_exists_result['access_token'] = token
                return user_exists_result
            else:
                return False
        else:
            return False

    except Exception as e:
        print(e)
        return False
def calculate_age(born):
    today = datetime.date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
def zodiac_sign(day, month): 
    astro_sign = ""
    print(day, month)
    if month == 12: 
        astro_sign = 'Sagittarius' if (day < 21) else 'Capricorn'
          
    elif month == 1: 
        astro_sign = 'Capricorn' if (day < 19) else 'Aquarius'
          
    elif month == 2: 
        astro_sign = 'Aquarius' if (day < 18) else 'Pisces'
          
    elif month == 3: 
        astro_sign = 'Pisces' if (day < 20) else 'Aries'
          
    elif month == 4: 
        astro_sign = 'Aries' if (day < 19) else 'Taurus'
          
    elif month == 5: 
        astro_sign = 'Taurus' if (day < 20) else 'Gemini'
          
    elif month == 6: 
        astro_sign = 'Gemini' if (day < 20) else 'Cancer'
          
    elif month == 7: 
        astro_sign = 'Cancer' if (day < 22) else 'Leo'
          
    elif month == 8: 
        astro_sign = 'Leo' if (day < 22) else 'Virgo'
          
    elif month == 9: 
        astro_sign = 'Virgo' if (day < 22) else 'Libra'
          
    elif month == 10: 
        astro_sign = 'Libra' if (day < 22) else 'Scorpio'
          
    elif month == 11: 
        astro_sign = 'Scorpio' if (day < 21) else 'Sagittarius'
          
    return astro_sign 

def update_user_data(reqData):
    try:
        if('dob' in reqData):
            dobData = reqData['dob'].split("T")[0]
            date_of_birth = datetime.datetime.strptime(dobData, "%Y-%m-%d")
            age = calculate_age(date_of_birth)
            reqData['age'] = age
            zodiac_sign_data = zodiac_sign(date_of_birth.day, date_of_birth.month)
            reqData['zodiac_sign'] = zodiac_sign_data
        user_data = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('_id', reqData['user_id'])
        if user_data:
            reqData['last_update_time'] = get_iso_format_datetime()
            if('dob' in reqData):
                user_data['settings']['age'] = age
                user_data['settings']['zodiac_sign'] = zodiac_sign_data
                reqData['settings'] = user_data['settings']
            result = MONGO_OPERATION(mongoClient).update_user_data_in_mongo('_id', reqData['user_id'], reqData)
            if result:
                user_data = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('_id', reqData['user_id'])
                user_data['_id'] = str(user_data['_id'])
                return user_data
            else:
                return False
        else:
            return False
    except Exception as e:
        print(e)
        return False

def get_user_data(user_id):
    try:
        user_data = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('_id', user_id)
        if user_data:
            # user_interests_Count = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('_id', user_id)
            user_buzz_Count = MONGO_OPERATION(mongoClient).get_today_buzz_sent_count(user_id)
            user_likes_Count = MONGO_OPERATION(mongoClient).get_today_like_sent_count(user_id)
            total_count = user_buzz_Count + user_likes_Count
            user_data['_id'] = str(user_data['_id'])
            user_data['likesCount'] = total_count
            return user_data
        else:
            return False
    except Exception as e:
        print("problem in getting user data")
        print(e)
        return False

def get_subscription_data(subscription_id):
    try:
        subscripiton_data = MONGO_OPERATION(mongoClient).get_subscription_from_mongo('_id', subscription_id)
        if subscripiton_data:
            return subscripiton_data
        else:
            return False
    except Exception as e:
        print(e)
        return False

def user_subscribe(reqData):
    try:
        user_data = get_user_data(reqData['user_id'])
        sub_data = get_subscription_data(reqData['subscription_id'])
        if user_data and sub_data:
            valid_upto = datetime.datetime.now() + datetime.timedelta(days=30)
            data = {}
            data['user_id'] = reqData['user_id']
            data['subscription_id'] = reqData['subscription_id']
            data['subscripiton_date'] = get_iso_format_datetime()
            data['subscripiton_expires'] = valid_upto
            data['status'] = 1

            sub_result = MONGO_OPERATION(mongoClient).user_subscribe(data)
            if sub_result:
                if 'credits' not in user_data:
                    user_data['credits'] = mozo_features
                credits_data = user_data['credits']
                credits_data['crushCount'] = credits_data['crushCount'] + sub_data['crushCount']
                credits_data['buzzCount'] = credits_data['buzzCount'] + sub_data['buzzCount']
                credits_data['addFilters'] = sub_data['addFilters']
                credits_data['hideAge'] = sub_data['hideAge']
                credits_data['hideDistance'] = sub_data['hideDistance']
                credits_data['imageSharing'] = credits_data['imageSharing'] + sub_data['imageSharing']
                credits_data['lastSwipe'] = sub_data['lastSwipe']
                credits_data['readTicks'] = sub_data['readTicks']
                credits_data['teleport'] = sub_data['teleport']
                credits_data['swipes'] = credits_data['swipes'] + sub_data['swipes']
                credits_data['voiceSharing'] = credits_data['voiceSharing'] + sub_data['voiceSharing']
                result = MONGO_OPERATION(mongoClient).update_user_data_in_mongo('_id', reqData['user_id'], {'is_subscribe': True, 'subscription_id': reqData['subscription_id'], 'credits': credits_data})
                if result:
                    user_data = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('_id', reqData['user_id'])
                    del user_data['access_token']
                    del user_data['otp']
                    user_data['_id'] = str(user_data['_id'])
                    return user_data
                else:
                    return False
            else:
                print("problem in saving user subscription")
                print(data)
                return False  
        else:
            return {'message': 'User or Subscription not found'} 
    except Exception as e:
        print(e)
        return False

# Subscriptions
def get_all_subscriptions():
    print("get_all_subscriptions")
    try:
        result = MONGO_OPERATION(mongoClient).get_all_subscriptions_from_mongo()
        if result:
            return result
        return result
    except Exception as e:
        print(e)
        return False

def save_subscription(reqData):
    try:
        reqData['created_time'] = get_iso_format_datetime()
        reqData['last_update_time'] = get_iso_format_datetime()
        result = MONGO_OPERATION(mongoClient).save_new_subscription(reqData)
        return result        
    except Exception as e:
        print(e)
        return False

def upload_user_photos_pic_to_s3(file, filename, user_id):
    try:
        print(filename)
        print(file)
        source_file = os.path.join(path, filename)
        file.save(source_file)
        try:
            response = s3Client.upload_file(source_file, 'user-photo-pics', 'photos/' + user_id + '/' + filename)
            user_data = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('_id', user_id)
            if user_data:
                update_data = {}
                if user_data['photos'] is None:
                    print("am in ifffff")
                    update_data['photos'] = []
                else:
                    update_data['photos'] = user_data['photos']
                update_data['photos'].append(filename)
                update_data['last_update_time'] = get_iso_format_datetime()
                print(update_data)
                result = MONGO_OPERATION(mongoClient).update_user_data_in_mongo('_id', user_id, update_data)
                if result:
                    user_data = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('_id', user_id)
                    user_data['_id'] = str(user_data['_id'])
                    print(user_data)
                    return user_data
                else:
                    return False
            else:
                return False
        except Exception as e:
            print("problem in uploading file", e)
            return False
        os.remove(source_file)
        return True
    except Exception as e:
        print(e)
        return False

def upload_user_profile_pic_to_s3(file, filename, user_id):
    try:
        print(filename)
        print(file)
        source_file = os.path.join(path, filename)
        file.save(source_file)
        try:
            response = s3Client.upload_file(source_file, 'user-photo-pics', 'profile/' + user_id + '/' + filename)
            user_data = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('_id', user_id)
            if user_data:
                update_data = {}
                update_data['profile_pic']= filename
                update_data['last_update_time'] = get_iso_format_datetime()
                print(update_data)
                result = MONGO_OPERATION(mongoClient).update_user_data_in_mongo('_id', user_id, update_data)
                if result:
                    user_data = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('_id', user_id)
                    user_data['_id'] = str(user_data['_id'])
                    print(user_data)
                    return user_data
                else:
                    return False
            else:
                return False
        except Exception as e:
            print("problem in uploading file", e)
            return False
        os.remove(source_file)
        return True
    except Exception as e:
        print(e)
        return False

def upload_user_profile_pic(reqData):
    try:
        user_id = reqData['user_id']
        image = reqData['image']
        image = image[image.find(",")+1:]
        imageFile = base64.b64decode(image)
        s3Path = 'https://user-photo-pics.s3.ap-south-1.amazonaws.com/'
        filename = 'profile/' + user_id + '/' + user_id + '.jpg'
        response = s3Client.put_object(Bucket='user-photo-pics', Key=filename, Body=imageFile)
        print(response)
        # response = s3Client.upload_file(source_file, 'user-photo-pics', 'profile/' + user_id + '/' + filename)
        user_data = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('_id', user_id)
        if user_data:
            update_data = {}
            update_data['profile_pic']= s3Path + filename
            update_data['last_update_time'] = get_iso_format_datetime()
            print(update_data)
            result = MONGO_OPERATION(mongoClient).update_user_data_in_mongo('_id', user_id, update_data)
            if result:
                user_data = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('_id', user_id)
                user_data['_id'] = str(user_data['_id'])
                print(user_data)
                return user_data
            else:
                return False
        else:
            return False
        return True
    except Exception as e:
        print("e")
        print(e)
        return False

def upload_user_photos_pic(reqData):
    try:
        user_id = reqData['user_id']
        filename = reqData['filename']
        image = reqData['image']
        image = image[image.find(",")+1:]
        imageFile = base64.b64decode(image)
        s3Path = 'https://user-photo-pics.s3.ap-south-1.amazonaws.com/'
        s3filename = 'photos/' + user_id + '/' + filename + '.jpg'
        response = s3Client.put_object(Bucket='user-photo-pics', Key=s3filename, Body=imageFile)
        user_data = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('_id', user_id)
        print(user_data)
        if user_data:
            update_data = {}
            if user_data['photos'] is None:
                print("am in ifffff")
                photos = [
                    {
                        "order": 1,
                        "url": ""
                    },
                    {
                        "order": 2,
                        "url": ""
                    },
                    {
                        "order": 3,
                        "url": ""
                    },
                    {
                        "order": 4,
                        "url": ""
                    },
                    {
                        "order": 5,
                        "url": ""
                    },
                    {
                        "order": 6,
                        "url": ""
                    },
                    {
                        "order": 7,
                        "url": ""
                    },
                    {
                        "order": 8,
                        "url": ""
                    }
                ]
                update_data['photos'] = photos
            else:
                update_data['photos'] = user_data['photos']
            # update_data['photos'].append(s3Path + s3filename)
            for photo in update_data['photos']:
                if photo['order'] == reqData['order']:
                    photo['url'] = s3Path + s3filename

            print(update_data)
            update_data['last_update_time'] = get_iso_format_datetime()
            result = MONGO_OPERATION(mongoClient).update_user_data_in_mongo('_id', user_id, update_data)
            if result:
                user_data = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('_id', user_id)
                user_data['_id'] = str(user_data['_id'])
                print(user_data)
                return user_data
            else:
                return False
        else:
            return False
        return True
    except Exception as e:
        print(e)
        return False

def upload_message_attachment_pic(reqData):
    try:
        user_id = reqData['user_id']
        filename = reqData['filename']
        image = reqData['image']
        image = image[image.find(",")+1:]
        imageFile = base64.b64decode(image)
        s3Path = 'https://user-photo-pics.s3.ap-south-1.amazonaws.com/'
        s3filename = 'message/' + user_id + '/' + filename + '.jpg'
        response = s3Client.put_object(Bucket='user-photo-pics', Key=s3filename, Body=imageFile)
        return s3Path + s3filename
    except Exception as e:
        print(e)
        return False


def delete_user_photo(reqData):
    try:
        user_id = reqData['user_id']
        order = reqData['order']
        user_data = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('_id', user_id)
        print(user_data)
        if user_data:
            update_data = {}
            update_data['photos'] = user_data['photos']
            # update_data['photos'].append(s3Path + s3filename)
            for photo in update_data['photos']:
                if photo['order'] == reqData['order']:
                    photo['url'] = ""

            print(update_data)
            update_data['last_update_time'] = get_iso_format_datetime()
            result = MONGO_OPERATION(mongoClient).update_user_data_in_mongo('_id', user_id, update_data)
            if result:
                user_data = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('_id', user_id)
                user_data['_id'] = str(user_data['_id'])
                print(user_data)
                return user_data
            else:
                return False
        else:
            return False
        return True
    except Exception as e:
        print(e)
        return False

def user_interest(reqData):
    try:
        interest_data = {
            'fromUser': reqData['fromUser'],
            'toUser': reqData['toUser'],
            'interestType': reqData['interestType'], # like, super_like,
            'status': 0, # 0 - requested, 1- request expired, 2 - responded, 3-4-5 are timer updates, 6- got message
            'isAccept': False,
            'respondType': '',
            'reason': '',
            'interestAcceptTime': '',
            'interestTime': get_iso_format_datetime()
        }
        is_like_exist = MONGO_OPERATION(mongoClient).check_like_exist(reqData['toUser'], reqData['fromUser'])
        if len(is_like_exist):
            like_data = is_like_exist[0]
            update_data = {
                'isAccept': True if reqData['interestType'].lower() == 'like' or reqData['interestType'].lower() == 'super_like' else False,
                'respondType': reqData['interestType'],
                'status': 2,
                'reason': reqData['reason'] if 'reason' in reqData else '',
                'interestAcceptTime': get_iso_format_datetime()
            }
            result = MONGO_OPERATION(mongoClient).update_interest('_id', str(like_data['_id']), update_data)
            fromUserData = MONGO_OPERATION(mongoClient).get_user_details('_id', reqData['fromUser'], {"name": 1, "photos": 1})
            toUserData = MONGO_OPERATION(mongoClient).get_user_details('_id', reqData['toUser'], {"name": 1, "photos": 1})
            fromUserData['_id'] = str(fromUserData['_id'])
            toUserData['_id'] = str(toUserData['_id'])
            return {'isMatched': True, 'success': True, 'fromUser': fromUserData, 'toUser': toUserData}
        else:
            is_from_like_exist = MONGO_OPERATION(mongoClient).check_like_exist(reqData['fromUser'], reqData['toUser'])
            if len(is_from_like_exist):
                f_like_data = is_from_like_exist[0]
                update_data = {
                    'interestTime': get_iso_format_datetime()
                }
                result = MONGO_OPERATION(mongoClient).update_interest('_id', str(f_like_data['_id']), update_data)
                return {'isMatched': False, 'success': True}
            else:
                result = MONGO_OPERATION(mongoClient).add_new_interest(interest_data)
                if reqData['interestType'].lower() == 'crush':
                    updateDebitCount(reqData['fromUser'], 'crushCount')
                if result:
                    return {'isMatched': False, 'success': True}
                else:
                    return {'isMatched': False, 'success': False}
    except Exception as e:
        print(e)
        return {'isMatched': False, 'success': False}

def respond_user_interest(reqData):
    try:
        print(reqData)
        update_data = {
            'isAccept': True if reqData['respondType'] == 'accept' else False,
            'respondType': reqData['respondType'],
            'reason': reqData['reason'] if 'reason' in reqData else '',
            'interestAcceptTime': get_iso_format_datetime()
        }
        print(update_data)
        result = MONGO_OPERATION(mongoClient).update_interest('_id', reqData['interest_id'], update_data)
        if result:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

def updateDebitCount(user_id, creditParam):
    try:
        user_data = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('_id', user_id)
        user_data['credits'][creditParam] = user_data['credits'][creditParam] - 1
        result = MONGO_OPERATION(mongoClient).update_user_data_in_mongo('_id', user_id, user_data)
        return True
    except Exception as e:
        return False

def updateCreditCount(user_id, creditParam):
    try:
        user_data = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('_id', user_id)
        user_data['credits'][creditParam] = user_data['credits'][creditParam] + 1
        result = MONGO_OPERATION(mongoClient).update_user_data_in_mongo('_id', user_id, user_data)
        return True
    except Exception as e:
        return False

def send_message(reqData):
    try:
        message_data = {
            'fromUser': reqData['fromUser'],
            'toUser': reqData['toUser'],
            'messageType': reqData['messageType'], # message, buzz, diamond
            'message': reqData['message'],
            'status': 0,  # 0 - new message, 1 - stage1, 2 - stage2, 3 - stage3, 4 - inactive, 5 - reject
            'attachments': reqData['attachments'] if 'attachments' in reqData  else '', 
            'sentTime': get_iso_format_datetime(),
            'lastUpdateTime': get_iso_format_datetime()
        }
        result = MONGO_OPERATION(mongoClient).add_message(message_data)
        if reqData['messageType'].lower() == 'buzz':
            updateDebitCount(reqData['fromUser'], 'buzzCount')
        elif reqData['messageType'].lower() == 'diamond':
            updateDebitCount(reqData['fromUser'], 'diamondCount')
            updateCreditCount(reqData['toUser'], 'diamondCount')
            updateCreditCount(reqData['fromUser'], 'diamondSentCount')
            updateCreditCount(reqData['toUser'], 'diamondReceivedCount')
        else:
            result1 = MONGO_OPERATION(mongoClient).update_interest_status(reqData['fromUser'], reqData['toUser'])

         
        if result:
            result['_id'] = str(result['_id'])
            return result
        else:
            return False
    except Exception as e:
        print(e)
        return False

def update_message(reqData):
    try:
        print(reqData)
        update_data = {
            'messageType': reqData['messageType'] if 'messageType' in reqData else 'buzz' ,
            'reason': reqData['reason'] if 'reason' in reqData else '',
            'status': reqData['status'] if 'status' in reqData else 4
        }
        if 'status' in reqData and reqData['status'] == 0:
            # like
            message = MONGO_OPERATION(mongoClient).get_message(reqData['message_id'])
            if message:
                interest_data = {
                    'fromUser': message['fromUser'],
                    'toUser': message['toUser'],
                    'interestType': 'like', # like, super_like,
                    'status': 6, # 0 - requested, 1- request expired, 2 - responded, 3-4-5 are timer updates, 6- got message
                    'isAccept': True,
                    'respondType': 'like',
                    'reason': '',
                    'interestAcceptTime': get_iso_format_datetime(),
                    'interestTime': get_iso_format_datetime()
                }
                result1 = MONGO_OPERATION(mongoClient).add_new_interest(interest_data)
        
        if 'status' in reqData and reqData['status'] == 5:
            #reject
            message = MONGO_OPERATION(mongoClient).get_message(reqData['message_id'])
            if message:
                interest_data = {
                    'fromUser': message['fromUser'],
                    'toUser': message['toUser'],
                    'interestType': 'like', # like, super_like,
                    'status': 1, # 0 - requested, 1- request expired, 2 - responded, 3-4-5 are timer updates, 6- got message
                    'isAccept': False,
                    'respondType': '',
                    'reason': '',
                    'interestAcceptTime': '',
                    'interestTime': get_iso_format_datetime()
                }
                result1 = MONGO_OPERATION(mongoClient).add_new_interest(interest_data)

        print(update_data)
        result = MONGO_OPERATION(mongoClient).update_message('_id', reqData['message_id'], update_data)
        if result:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False
def send_messages_list(reqData, messageType):
    try:
        result = MONGO_OPERATION(mongoClient).get_send_messages(reqData['user_id'], messageType)
        if result:
            return result
        else:
            return []
    except Exception as e:
        print(e)
        return False

def all_messages_list(reqData):
    try:
        result = MONGO_OPERATION(mongoClient).get_all_messages(reqData['user_id'])
        if result:
            return result
        else:
            return []
    except Exception as e:
        print(e)
        return False

def get_matches(user_id):
    try:
        result = MONGO_OPERATION(mongoClient).get_all_matches(user_id)
        if result:
            return result
        else:
            return []
    except Exception as e:
        print(e)
        return False

def all_user_char_messages_list(reqData):
    try:
        result = MONGO_OPERATION(mongoClient).get_all_user_chat_messages(reqData['fromUser'], reqData['toUser'])
        if result:
            return result
        else:
            return []
    except Exception as e:
        print(e)
        return False

def received_messages_list(reqData, messageType):
    try:
        result = MONGO_OPERATION(mongoClient).get_received_messages(reqData['user_id'], messageType)
        if result:
            return result
        else:
            return []
    except Exception as e:
        print(e)
        return False

def received_likes_list(reqData):
    try:
        user_interests_docs = MONGO_OPERATION(mongoClient).get_user_interests(reqData['user_id'], 'LIKE')
        if user_interests_docs and len(user_interests_docs):
            # return result
            user_ids = []
            for user_interest in user_interests_docs:
                user_ids.append(ObjectId(user_interest['fromUser']))
            print("user_ids")
            print(user_ids)
            interested_users = MONGO_OPERATION(mongoClient).get_users_by_mobile_numbers(user_ids)
            if interested_users:
                return interested_users
            else:
                return []
        else:
            return []
    except Exception as e:
        print(e)
        return False

def get_likes_count(reqData):
    try:
        result = MONGO_OPERATION(mongoClient).get_likes_count(reqData['user_id'])
        if result:
            return result
        else:
            return []
    except Exception as e:
        print(e)
        return False

def send_otp_to_email(reqData, mail, message):
    try:
        otp = generateOTP()
        user_exists_result = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('_id', reqData['user_id'])
        if user_exists_result:
            userName = user_exists_result['name'] if user_exists_result['name'] else 'User'
            msg = message("Mozo - Email Verification",
              sender=fromEmail,
              recipients=[reqData['email']])
            print(msg)
            msg.body = "Dear " + user_exists_result['name'] + "!\nYour OTP is " + str(otp) + ", Please use this OTP to verify your email address"           
            mail.send(msg)
            update_data = {}
            update_data['otp'] = otp
            update_data['last_otp_sent_time'] = get_iso_format_datetime()
            result = MONGO_OPERATION(mongoClient).update_user_data_in_mongo('_id', reqData['user_id'], update_data)
            return result
        else:
            return False
    except Exception as e:
        print(e)
        # print(str(e))
        return False
def send_verification_email(reqData, mail, message):
    try:
        otp = generateOTP()
        user_exists_result = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('_id', reqData['user_id'])
        if user_exists_result:
            userName = user_exists_result['name'] if user_exists_result['name'] else 'User'
            msg = message("Mozo - Email Verification",
              sender=fromEmail,
              recipients=[reqData['email']])
            # print(msg)
            link = 'http://18.222.230.151:8844/api/v1/verify-email?user_id='+reqData['user_id']
            # msg.body = "Dear " + user_exists_result['name'] + "!\nYour OTP is " + str(otp) + ", Please use this OTP to verify your email address"           
            msg.html = render_template('email.html', username=user_exists_result['name'], link=link)
            mail.send(msg)
            update_data = {}
            update_data['otp'] = otp
            update_data['last_otp_sent_time'] = get_iso_format_datetime()
            result = MONGO_OPERATION(mongoClient).update_user_data_in_mongo('_id', reqData['user_id'], update_data)
            return result
        else:
            return False
    except Exception as e:
        print("problem in sending email")
        print(e)
        # print(str(e))
        return False

def verify_email_otp(reqData):
    try:
        user_exists_result = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('_id', reqData['user_id'])
        if user_exists_result:
            otp = user_exists_result['otp']
            if otp == reqData['otp']:
                MONGO_OPERATION(mongoClient).update_user_data_in_mongo('_id', reqData['user_id'], {'isEmailVerified': True})
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        print(e)
        return False

def verify_email(user_id):
    try:
        user_exists_result = MONGO_OPERATION(mongoClient).check_user_exists_from_mongo('_id', user_id)
        if user_exists_result:
            MONGO_OPERATION(mongoClient).update_user_data_in_mongo('_id', reqData['user_id'], {'isEmailVerified': True})
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


