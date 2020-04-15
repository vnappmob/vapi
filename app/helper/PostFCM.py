"""[summary]
This helper aim to post Firebase Cloud Messaging
Returns:
    [response] -- [description]
"""
from flask import current_app
import requests


def post_fcm(data):
    headers = {
        'Authorization': 'key=' + current_app.config['VPRICE_FCM_KEY'],
        'Content-Type': 'application/json'
    }

    return requests.post(
        'https://fcm.googleapis.com/fcm/send',
        headers=headers,
        data=data.encode('utf-8')
    )
