from mrq.task import Task
from flaskapp.models import User
import json
import tempfile
import requests
import os
import re
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

        limit = int(params.get("limit", 90))
        username = params["source_data"]["username"].strip().replace("/", "").replace("@", "")

        user_search_url = "https://api.instagram.com/v1/users/search?q=%s&client_id=%s" % (
            username, app.config["SOCIAL_AUTH_INSTAGRAM_ID"]
        )

        user_search = get_json(user_search_url)

        if len(user_search.get("data", [])) == 0:
            return None

        user_id = None
        for apiuser in user_search["data"]:
            if apiuser["username"].lower() == username.lower():
                user_id = apiuser["id"]
                break

        if not user_id:
            print "User ID not found in the API, falling back to the profile page"

            # There may be too much users with this exact prefix.
            # This is a gaping hole in the Instagram API :/ Fallback to scraping!
            profile_page = requests.get("https://www.instagram.com/%s/" % username)
            if profile_page.status_code == 200:
                html = profile_page.content
                m = re.search(r"window\._sharedData = (.+?)\;\s*\<\/script\>", html)
                if m:
                    js_data = m.group(1)
                    data = json.loads(js_data)
                    user_id = data["entry_data"]["ProfilePage"][0]["user"]["id"]

        if not user_id:
            raise Exception("User not found on Instagram!")

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
            print "Downloading %s" % image["source"]
            fn = os.path.join(directory, "%s.jpg" % i)
            with open(fn, "wb") as f:
                f.write(requests.get(image["source"]).content)
            image["filepath"] = fn

        with open(os.path.join(directory, "images.json"), "wb") as f:
            json.dump(data, f)
