from mrq.task import Task
from flaskapp.models import User
import json
import tempfile
import requests
import os


class FacebookAlbum(Task):

    def run(self, params):
        user = User.objects.get(id=params["user"])

        photos = user.get_facebook_photos(params["source_data"]["album"])

        limit = int(params.get("limit", 6))

        dump = {
            "images": photos[:limit]
        }

        tmpdir = tempfile.mkdtemp(prefix="imgfab")

        with open(tmpdir + "/images.json", "w") as f:
            json.dump(dump, f)

        return tmpdir


class DownloadImages(Task):

    def run(self, params):
        directory = params["directory"]

        with open(os.path.join(directory, "images.json"), "rb") as f:
            data = json.load(f)

        for i, image in enumerate(data["images"]):
            fn = os.path.join(directory, "%s.jpg" % i)
            with open(fn, "wb") as f:
                f.write(requests.get(data["images"]["source"]).content)
            image["filepath"] = fn

        with open(os.path.join(directory, "images.json"), "wb") as f:
            json.dump(data, f)
