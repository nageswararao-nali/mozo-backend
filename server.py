import settings
# from dotenv import load_dotenv, find_dotenv
# load_dotenv(find_dotenv())
import os
import json
from flask import Flask, request, jsonify
import base64
import urllib.request
from collections import ChainMap
# from flaskCelery import make_celery
import config
from responseCode import codes
from utilities import *
from flask_cors import CORS
# from werkzeug.utils import secure_filename
# from openpyxl import load_workbook
import simplejson
# import zipfile
from pathlib import Path
# import csv
# from io import StringIO
# from werkzeug.wrappers import Response
from functools import wraps
from bson import ObjectId
from flask_mail import Mail, Message

app = Flask(__name__)
app.config.from_object(config)

mail = Mail(app)
CORS(app)

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self,o)


def check_auth(token):
    return check_token(token)


def authenticate():
    message = {'error': "Authenticate Failed."}
    resp = jsonify(message)

    resp.status_code = 401

    return resp


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request.headers.get('Authorization'):
            return authenticate()
        elif not check_auth(request.headers.get('Authorization')):
            return authenticate()
        return f(*args, **kwargs)

    return decorated

@app.route('/api/v1/web-test', methods=['GET'])
def web_test():
    response = jsonify({"status": "Working"}), 200
    return response


@app.route('/api/v1/create-new-user', methods=['POST'])
@requires_auth
def create_new_user():
    try:
        req = request.get_json()
        print(req)
        if req:
            result = cognito_create_user(**req)
            if result == True:
                add_new_user_to_database(**req)
                response = jsonify(codes(200, 'User got created successfully')), 200
                return response
            else:
                return jsonify(codes(406, result)), 406
        else:
            return jsonify(codes(400, 'Bad Request')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'Bad Request')), 400

@app.route('/api/v1/login-with-facebook', methods=['POST'])
def login_with_facebook_req():
    try:
        req = request.get_json()
        if req:
            result = get_otp(req, True)
            if result:
                print(result)
                response = jsonify(codes(200, {"status": 'Success', "user": result})), 200
                return response
            else:
                return jsonify(codes(406, 'problem in sending otp')), 406
        else:
            return jsonify(codes(400, 'bad request')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'bad request')), 400

@app.route('/api/v1/get-all-users', methods=['GET'])
def get_all_users_request():
    try:
        result = get_all_users()
        if result:
            users_str = JSONEncoder().encode(result)
            users = json.loads(users_str)
            print(users)
            response = jsonify(codes(200, users)), 200
            return response
        else:
            return jsonify(codes(406, 'problem in getting users')), 406
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'bad request')), 400

@app.route('/api/v1/get-users', methods=['GET'])
def get_users_request():
    try:
        user_id = request.args.get("user_id")
        if user_id:
            result = get_users(user_id)
            print(result)
            if result or result == []:
                response = jsonify(codes(200, result)), 200
                return response
            else:
                return jsonify(codes(406, 'problem in getting users')), 406
        else:
            return jsonify(codes(406, 'User Id missing')), 406
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'bad request')), 400

@app.route('/api/v1/get-matches', methods=['GET'])
def get_matches_request():
    try:
        user_id = request.args.get("user_id")
        if user_id:
            result = get_matches(user_id)
            print(result)
            if result or result == []:
                response = jsonify(codes(200, result)), 200
                return response
            else:
                return jsonify(codes(406, 'problem in getting users')), 406
        else:
            return jsonify(codes(406, 'User Id missing')), 406
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'bad request')), 400

@app.route('/api/v1/login-otp', methods=['POST'])
def get_otp_request():
    try:
        req = request.get_json()
        if req:
            result = get_otp(req, False)
            if result:
                print("result")
                print(result)
                response = jsonify(codes(200, 'Success')), 200
                return response
            else:
                return jsonify(codes(406, 'problem in sending otp')), 406
        else:
            return jsonify(codes(400, 'bad request')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'bad request')), 400

@app.route('/api/v1/verify-otp', methods=['POST'])
def verify_otp_request():
    try:
        req = request.get_json()
        if req:
            result = verify_otp(req)
            if result:
                print(result)
                response = jsonify(codes(200, {"status": 'Success', "user": result})), 200
                return response
            else:
                return jsonify(codes(406, 'problem in login with otp')), 406
        else:
            return jsonify(codes(400, 'bad request')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'bad request')), 400

@app.route('/api/v1/update-user', methods=['PUT'])
def update_user_request():
    try:
        req = request.get_json()
        if req:
            result = update_user_data(req)
            if result:
                response = jsonify(codes(200, {"status": 'successfully updated the user info', "user": result})), 200
                return response
            else:
                return jsonify(codes(406, 'problem in updating user')), 406
        else:
            return jsonify(codes(400, 'bad request')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'bad request')), 400


@app.route('/api/v1/get-user', methods=['GET'])
def get_user_request():
    try:
        user_id = request.args.get("user_id")
        if user_id:
            user = get_user_data(user_id)
            if user:
                response = jsonify(codes(200, {"status": 'Success', "user": user})), 200
                return response
            else:
                return jsonify(codes(406, 'problem in getting user details')), 406
        else:
            return jsonify(codes(400, 'bad request')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'bad request')), 400


# Subscriptions
@app.route('/api/v1/get-all-subscriptions', methods=['GET'])
def get_all_subscriptions_request():
    try:
        subscriptions = get_all_subscriptions()
        if subscriptions:
            response = jsonify(codes(200, subscriptions)), 200
            return response
        else:
            return jsonify(codes(406, 'problem in getting subscriptions')), 406
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'bad request')), 400

@app.route('/api/v1/add-subscription', methods=['POST'])
def save_subscription_request():
    try:
        req = request.get_json()
        print(req)
        if req:
            subscription = save_subscription(req)
            if subscription:
                response = jsonify(codes(200, {'status' :'Subscription got created successfully', 'subscription': subscription})), 200
                return response
            else:
                return jsonify(codes(406, result)), 406
        else:
            return jsonify(codes(400, 'Bad Request')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'Bad Request')), 400


@app.route('/api/v1/user-subscribe', methods=['POST'])
def user_subscribe_request():
    try:
        req = request.get_json()
        print(req)
        if req:
            user = user_subscribe(req)
            if user:
                response = jsonify(codes(200, {'status' :'User got subscription successfully', 'user': user})), 200
                return response
            else:
                return jsonify(codes(406, result)), 406
        else:
            return jsonify(codes(400, 'Bad Request')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'Bad Request')), 400

# @app.route('/api/v1/user-photos', methods=['POST'])
# def user_photos_request():
#     user_id = request.form['user_id']
#     if user_id:
#         try:
#             if request.method == 'POST':
#                 if 'file' not in request.files:
#                     return jsonify(codes(400, 'no file selected')), 400
#                 file = request.files['file']
#                 if file.filename == '':
#                     return jsonify(codes(400, 'no file selected')), 400
#                 if file and allowed_file(file.filename):
#                     filename = file.filename
#                     user = upload_user_photos_pic_to_s3(file, filename, user_id)
#                     if user:
#                         response = jsonify(codes(200, {'status' :'User photos added successfully', 'user': user})), 200
#                         return response
#                     else:
#                         return jsonify(codes(406, 'server is refusing your request')), 406
#                 else:
#                     return jsonify(codes(406, 'uploaded file is in invalid format')), 406
#         except Exception as e:
#             print(e)
#             return jsonify(codes(400, 'Bad Request')), 400
#     else:
#         return jsonify(codes(400, 'user_id missing')), 400

@app.route('/api/v1/user-photos', methods=['POST'])
def user_photos_request():
    try:
        req = request.get_json()
        if req:
            user = upload_user_photos_pic(req)
            if user:
                response = jsonify(codes(200, {'status' :'User photos added successfully', 'user': user})), 200
                return response
            else:
                return jsonify(codes(406, result)), 406
        else:
            return jsonify(codes(400, 'Bad Request')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'Bad Request')), 400

@app.route('/api/v1/message-attachments', methods=['POST'])
def message_attachment_request():
    try:
        req = request.get_json()
        if req:
            url = upload_message_attachment_pic(req)
            if url:
                response = jsonify(codes(200, {'status' :'message attachment uploaded successfully', 'url': url})), 200
                return response
            else:
                return jsonify(codes(406, result)), 406
        else:
            return jsonify(codes(400, 'Bad Request')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'Bad Request')), 400

@app.route('/api/v1/delete-user-photo', methods=['POST'])
def delete_user_photos_request():
    try:
        req = request.get_json()
        if req:
            user = delete_user_photo(req)
            if user:
                response = jsonify(codes(200, {'status' :'User photo deleted successfully', 'user': user})), 200
                return response
            else:
                return jsonify(codes(406, result)), 406
        else:
            return jsonify(codes(400, 'Bad Request')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'Bad Request')), 400

# @app.route('/api/v1/user-profile-pic', methods=['POST'])
# def user_profile_pic_request():
#     user_id = request.form['user_id']
#     if user_id:
#         try:
#             if request.method == 'POST':
#                 if 'file' not in request.files:
#                     return jsonify(codes(400, 'no file selected')), 400
#                 file = request.files['file']
#                 # print(file)
#                 for ab in file:
#                     print(ab)
#                     print(file[ab])
#                 if file.filename == '':
#                     return jsonify(codes(400, 'no file selected')), 400
#                 if file and allowed_file(file.filename):
#                     filename = file.filename
#                     result = upload_user_profile_pic_to_s3(file, filename, user_id)
#                     if result:
#                         response = jsonify(codes(200, {'status' :'User profile pic added successfully', 'user': result})), 200
#                         return response
#                     else:
#                         return jsonify(codes(406, 'server is refusing your request')), 406
#                 else:
#                     return jsonify(codes(406, 'uploaded file is in invalid format')), 406
#         except Exception as e:
#             print(e)
#             return jsonify(codes(400, 'Bad Request')), 400
#     else:
#         return jsonify(codes(400, 'user_id missing')), 400

@app.route('/api/v1/user-profile-pic', methods=['POST'])
def user_profile_pic_request():
    try:
        req = request.get_json()
        print(req)
        if req:
            user = upload_user_profile_pic(req)
            if user:
                response = jsonify(codes(200, {'status' :'User profile pic added successfully', 'user': user})), 200
                return response
            else:
                return jsonify(codes(406, result)), 406
        else:
            return jsonify(codes(400, 'Bad Request')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'Bad Request')), 400


@app.route('/api/v1/user-interest', methods=['POST'])
def user_interest_request():
    try:
        req = request.get_json()
        fromUser = req['fromUser']
        toUser = req['toUser']
        if fromUser and toUser:
            result = user_interest(req)
            if result:
                response = jsonify(codes(200, result)), 200
                return response
            else:
                return jsonify(codes(406, result)), 406
        else:
            return jsonify(codes(400, 'data missing')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'Bad Request')), 400

@app.route('/api/v1/respond-user-interest', methods=['POST'])
def respond_user_interest_request():
    try:
        req = request.get_json()
        interestId = req['interest_id']
        if interestId:
            result = respond_user_interest(req)
            if result:
                response = jsonify(codes(200, {'status' :'successfully updated your interest', 'success': True})), 200
                return response
            else:
                return jsonify(codes(406, result)), 406
        else:
            return jsonify(codes(400, 'data missing')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'Bad Request')), 400

# messages
@app.route('/api/v1/send-message', methods=['POST'])
def send_message_request():
    try:
        req = request.get_json()
        fromUser = req['fromUser']
        toUser = req['toUser']
        if fromUser and toUser:
            result = send_message(req)
            if result:
                response = jsonify(codes(200, {'status' :'message sent successfully', 'message': result})), 200
                return response
            else:
                return jsonify(codes(406, result)), 406
        else:
            return jsonify(codes(400, 'data missing')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'Bad Request')), 400

@app.route('/api/v1/update-message', methods=['POST'])
def update_message_request():
    try:
        req = request.get_json()
        messageId = req['message_id']
        if messageId:
            result = update_message(req)
            if result:
                response = jsonify(codes(200, {'status' :'message updated successfully', 'message': result})), 200
                return response
            else:
                return jsonify(codes(406, result)), 406
        else:
            return jsonify(codes(400, 'data missing')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'Bad Request')), 400

@app.route('/api/v1/sent-messages-list', methods=['POST'])
def sent_messages_list_request():
    try:
        req = request.get_json()
        fromUser = req['user_id']
        if req and fromUser:
            messages = send_messages_list(req, 'message')
            if messages or messages == []:
                response = jsonify(codes(200, {'status' :'sent messages list', 'messages': messages})), 200
                return response
            else:
                return jsonify(codes(406, messages)), 406
        else:
            return jsonify(codes(400, 'data missing')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'Bad Request')), 400

@app.route('/api/v1/received-messages-list', methods=['POST'])
def received_messages_list_request():
    try:
        req = request.get_json()
        fromUser = req['user_id']
        if req and fromUser:
            messages = received_messages_list(req, 'message')
            if messages or messages == []:
                response = jsonify(codes(200, {'status' :'received messages list', 'messages': messages})), 200
                return response
            else:
                return jsonify(codes(406, messages)), 406
        else:
            return jsonify(codes(400, 'data missing')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'Bad Request')), 400

@app.route('/api/v1/sent-buzz-list', methods=['POST'])
def sent_buzz_list_request():
    try:
        req = request.get_json()
        fromUser = req['user_id']
        if req and fromUser:
            messages = send_messages_list(req, 'buzz')
            if messages or messages == []:
                response = jsonify(codes(200, {'status' :'sent buzz list', 'buzz': messages})), 200
                return response
            else:
                return jsonify(codes(406, messages)), 406
        else:
            return jsonify(codes(400, 'data missing')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'Bad Request')), 400

@app.route('/api/v1/all-user-messages', methods=['POST'])
def all_user_messages_list_request():
    try:
        req = request.get_json()
        fromUser = req['user_id']
        if req and 'user_id' in req:
            messages = all_messages_list(req)
            if messages or messages == []:
                response = jsonify(codes(200, {'status' :'all messages list', 'messages': messages})), 200
                return response
            else:
                return jsonify(codes(406, messages)), 406
        else:
            return jsonify(codes(400, 'data missing')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'Bad Request')), 400

@app.route('/api/v1/user-chat-messages', methods=['POST'])
def all_user_chat_messages_list_request():
    try:
        req = request.get_json()
        fromUser = req['fromUser']
        toUser = req['toUser']
        if req and fromUser and toUser:
            messages = all_user_char_messages_list(req)
            if messages or messages == []:
                response = jsonify(codes(200, {'status' :'all messages list', 'messages': messages})), 200
                return response
            else:
                return jsonify(codes(406, messages)), 406
        else:
            return jsonify(codes(400, 'data missing')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'Bad Request')), 400

@app.route('/api/v1/received-buzz-list', methods=['POST'])
def received_buzz_list_request():
    try:
        req = request.get_json()
        fromUser = req['user_id']
        if req and fromUser:
            messages = received_messages_list(req, 'buzz')
            if messages or messages == []:
                response = jsonify(codes(200, {'status' :'received buzz list', 'buzz': messages})), 200
                return response
            else:
                return jsonify(codes(406, messages)), 406
        else:
            return jsonify(codes(400, 'data missing')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'Bad Request')), 400


@app.route('/api/v1/liked-users', methods=['POST'])
def received_likes_list_request():
    try:
        req = request.get_json()
        fromUser = req['user_id']
        if req and fromUser:
            users = received_likes_list(req)
            if users or users == []:
                response = jsonify(codes(200, {'status' :'received likes list', 'users': users})), 200
                return response
            else:
                return jsonify(codes(406, users)), 406
        else:
            return jsonify(codes(400, 'data missing')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'Bad Request')), 400

@app.route('/api/v1/get-likes-count', methods=['POST'])
def get_likes_count_request():
    try:
        req = request.get_json()
        fromUser = req['user_id']
        if req and fromUser:
            likesCount = get_likes_count(req)
            if likesCount:
                response = jsonify(codes(200, {'status' :'received likes count', 'likes': likesCount})), 200
                return response
            else:
                return jsonify(codes(406, {'success': False})), 406
        else:
            return jsonify(codes(400, 'data missing')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'Bad Request')), 400

@app.route('/api/v1/send-otp-to-email', methods=['POST'])
def send_otp_to_email_request():
    try:
        req = request.get_json()
        if 'email' in req and 'user_id' in req:
            sendMail = send_otp_to_email(req, mail, Message)
            print(sendMail)
            if sendMail:
                response = jsonify(codes(200, {'status' :'OTP send successfully', 'success': True})), 200
                return response
            else:
                return jsonify(codes(406, {'success': False})), 406
        else:
            return jsonify(codes(400, 'data missing')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'Bad Request')), 400

@app.route('/api/v1/send-verification-email', methods=['POST'])
def send_verification_email_request():
    try:
        req = request.get_json()
        if 'email' in req and 'user_id' in req:
            sendMail = send_verification_email(req, mail, Message)
            print(sendMail)
            if sendMail:
                response = jsonify(codes(200, {'status' :'Email send successfully', 'success': True})), 200
                return response
            else:
                return jsonify(codes(406, {'success': False})), 406
        else:
            return jsonify(codes(400, 'data missing')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'Bad Request')), 400


@app.route('/api/v1/verify-email-otp', methods=['POST'])
def verify_email_otp_request():
    try:
        req = request.get_json()
        if 'otp' in req and 'user_id' in req:
            verifyOtp = verify_email_otp(req)
            if verifyOtp:
                response = jsonify(codes(200, {'status' :'OTP Verified successfully', 'success': True})), 200
                return response
            else:
                return jsonify(codes(406, {'success': False})), 406
        else:
            return jsonify(codes(400, 'data missing')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'Bad Request')), 400

@app.route('/api/v1/verify-email', methods=['GET'])
def verify_email_request():
    try:
        user_id = request.args.get("user_id")
        if user_id:
            verifyOtp = verify_email(user_id)
            if verifyOtp:
                response = jsonify(codes(200, {'status' :'OTP Verified successfully', 'success': True})), 200
                return response
            else:
                return jsonify(codes(406, {'success': False})), 406
        else:
            return jsonify(codes(400, 'data missing')), 400
    except Exception as e:
        print(e)
        return jsonify(codes(400, 'Bad Request')), 400


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=8844)

