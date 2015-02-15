from mongoengine import StringField, EmailField, BooleanField
from flask.ext.login import UserMixin
import requests
import json

from mongoengine import Document
from social.apps.flask_app.me.models import FlaskStorage


class User(Document, UserMixin):
    username = StringField(max_length=200)
    password = StringField(max_length=200, default='')
    name = StringField(max_length=100)
    fullname = StringField(max_length=100)
    first_name = StringField(max_length=100)
    last_name = StringField(max_length=100)
    email = EmailField()
    active = BooleanField(default=True)

    def facebook_api(self, path, fields=None):

        url = "https://graph.facebook.com/v2.2%s" % path
        params = {
            'access_token': self.get_social_auth("facebook").extra_data['access_token']
        }
        if fields:
            params["fields"] = ",".join(fields)

        res = requests.get(url, params=params)

        if res.status_code != 200:
            raise Exception("Status was %s" % res.status_code)

        return json.loads(res.content)

    def get_facebook_albums(self):

        return self.facebook_api("/me/albums", fields=["id", "name"])

    def get_facebook_photos(self, album_id):

        return self.facebook_api("/%s/photos" % album_id, fields=[
            "id", "created_time", "from", "height", "width", "name", "source"
        ])

    def get_social_auth(self, provider):

        return FlaskStorage.user.get_social_auth_for_user(self, provider=provider).get()

    def is_active(self):
        return self.active
