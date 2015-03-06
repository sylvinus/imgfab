from mrq.task import Task
from flaskapp.models import User
import json
import tempfile
import requests
import os
from flaskapp import settings


def get_json(url):
    return json.loads(requests.get(url).content)


class FacebookAlbum(Task):

    def connect(self):
        from flaskapp.app import app

    def run(self, params):

        self.connect()

        user = User.objects.get(id=params["user"])

        photos = user.get_facebook_photos(params["source_data"]["album"])

        limit = int(params.get("limit", 6))

        dump = {
            "images": photos[:limit],
            "layout": params["layout"]
        }

        tmpdir = tempfile.mkdtemp(prefix="imgfab")

        with open(tmpdir + "/images-sources.json", "w") as f:
            json.dump(dump, f)

        return tmpdir


class InstagramFeed(Task):

    def run(self, params):

        from flaskapp.app import app
        # from instagram.client import InstagramAPI

        # api = InstagramAPI(client_id=app.config["SOCIAL_AUTH_INSTAGRAM_ID"], client_secret=app.config["SOCIAL_AUTH_INSTAGRAM_SECRET"])

        # search = api.user_search(params["source_data"]["username"])
        # print search

        # media = api.user_recent_media(params["source_data"]["username"], 90, None)
        # print media

        limit = 90

        user_search = get_json("https://api.instagram.com/v1/users/search?q=%s&client_id=%s" % (
            params["source_data"]["username"], app.config["SOCIAL_AUTH_INSTAGRAM_ID"]
        ))

        if len(user_search.get("data", [])) == 0:
            return None

        user_id = user_search["data"][0]["id"]

        # TODO pagination, we might not get only images...
        media = get_json("https://api.instagram.com/v1/users/%s/media/recent?client_id=%s&count=%s" % (
            user_id, app.config["SOCIAL_AUTH_INSTAGRAM_ID"], limit * 5
        ))

        photos = [
            {"source": x["images"]["standard_resolution"]["url"]}
            for x in media.get("data", [])
            if x.get("images") and x["type"] == "image"
        ]

        print "Found %s photos" % len(photos)

        dump = {
            "images": photos[:limit],
            "layout": params["layout"]
        }

        tmpdir = tempfile.mkdtemp(prefix="imgfab")

        with open(tmpdir + "/images-sources.json", "w") as f:
            json.dump(dump, f)

        return tmpdir


class DownloadImages(Task):

    def run(self, params):
        directory = params["directory"]

        with open(os.path.join(directory, "images-sources.json"), "rb") as f:
            data = json.load(f)

        for i, image in enumerate(data["images"]):
            fn = os.path.join(directory, "%s.jpg" % i)
            with open(fn, "wb") as f:
                f.write(requests.get(image["source"]).content)
            image["filepath"] = fn

        with open(os.path.join(directory, "images.json"), "wb") as f:
            json.dump(data, f)
