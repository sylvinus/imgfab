##
# Uploading a model to Sketchfab is a two step process
#
# 1. Upload a model. If the upload is successful, the api will return
#    the model's id, and the model will be placed in the processing queue
#
# 2. Poll for the processing status
#    You can use your model id (see 1.) to poll the model processing status
#    The processing status can be one of the following:
#    - PENDING: the model is in the processing queue
#    - PROCESSING: the model is being processed
#    - SUCCESSED: the model has being sucessfully processed and can be view on sketchfab.com
#    - FAILED: the processing has failed. An error message detailing the reason for the failure
#              will be returned with the response
#
# HINTS
# - limit the rate at which you poll for the status (once every few seconds is more than enough)
##

from mrq.task import Task
import os
import requests
import json
from time import sleep
import random
from flaskapp.models import User


SKETCHFAB_DOMAIN = 'sketchfab.com'
SKETCHFAB_API_URL = 'https://api.{}/v2/models'.format(SKETCHFAB_DOMAIN)
SKETCHFAB_MODEL_URL = 'https://{}/models/'.format(SKETCHFAB_DOMAIN)

SKETCHFAB_API_KEY = os.getenv("SKETCHFAB_API_KEY")


class UploadToSketchfab(Task):

    sketchfab_api_key = SKETCHFAB_API_KEY

    def run(self, params):

        # Instamuseum uploads on user's accounts!
        if params["brand"] == "instamuseum":
            user = User.objects.get(id=params["user"])
            self.sketchfab_api_key = user.get_social_auth("sketchfab").extra_data['apiToken']

        directory = params["directory"]
        layout = params["layout"]

        rand = random.randint(100000000, 9999999999)

        zip_name = "export.zip"  # % rand

        model_file = os.path.join(directory, zip_name)
        source_file = os.path.join(directory, "export.blend")

        if os.path.isfile(model_file):
            os.remove(model_file)

        os.system("zip -j %s %s" % (
            model_file, source_file
        ))

        # Mandatory parameters

        # Optional parameters
        if params["brand"] == "instamuseum":
            instagram_username = params["source_data"]["username"].strip().replace("/", "")
            name = params.get("name", "Instamuseum for @%s" % instagram_username)
            description = params.get("description", "Created with http://www.instamuseum.com\nOriginal photos at https://www.instagram.com/%s" % instagram_username)
            password = ""  # requires a pro account
            private = 0  # requires a pro account
            tags = "instamuseum"  # space-separated list of tags
        else:
            name = params.get("name", "imgfab #%s" % rand)
            description = params.get("description", "Created with http://imgfab.io")
            password = ""  # requires a pro account
            private = 0  # requires a pro account
            tags = "imgfab"  # space-separated list of tags

        data = {
            'token': self.sketchfab_api_key,
            'name': name,
            'description': description,
            'tags': tags,
            'private': private,
            'password': password
        }

        f = open(model_file, 'rb')

        files = [
            ("modelFile", ("export.zip", f, "application/zip"))
        ]

        try:
            model_uid = self.upload(data, files)
            self.poll_processing_status(model_uid)
            self.set_3d_options(model_uid, layout)
        finally:
            f.close()

        return {
            "model_uid": model_uid,
            "model_url": SKETCHFAB_MODEL_URL + model_uid
        }

    def upload(self, data, files):
        """
        Upload a model to sketchfab
        """
        print 'Uploading ...'

        try:
            r = requests.post(SKETCHFAB_API_URL, data=data, files=files, verify=False)
        except requests.exceptions.RequestException as e:
            print "An error occured: {}".format(e)
            return

        result = r.json()

        if r.status_code != requests.codes.created:
            print "Upload failed with error: {}".format(result)
            return

        model_uid = result['uid']
        model_url = SKETCHFAB_MODEL_URL + model_uid
        print "Upload successful. Your model is being processed."
        print "Once the processing is done, the model will be available at: {}".format(model_url)

        return model_uid

    def poll_processing_status(self, model_uid):
        """
        Poll the Sketchfab API to query the processing status
        """
        polling_url = "{}/{}/status?token={}".format(SKETCHFAB_API_URL, model_uid, self.sketchfab_api_key)
        max_errors = 10
        errors = 0
        retry = 0
        max_retries = 50
        retry_timeout = 5  # seconds

        print "Start polling processing status for model {}".format(model_uid)

        while (retry < max_retries) and (errors < max_errors):
            print "Try polling processing status (attempt #{}) ...".format(retry)

            try:
                r = requests.get(polling_url)
            except requests.exceptions.RequestException as e:
                print "Try failed with error {}".format(e)
                errors += 1
                retry += 1
                continue

            result = r.json()

            if r.status_code != requests.codes.ok:
                print "Upload failed with error: {}".format(result['error'])
                errors += 1
                retry += 1
                continue

            processing_status = result['processing']
            if processing_status == 'PENDING':
                print "Your model is in the processing queue. Will retry in {} seconds".format(retry_timeout)
                print "Want to skip the line? Get a pro account! https://sketchfab.com/plans"
                retry += 1
                sleep(retry_timeout)
                continue
            elif processing_status == 'PROCESSING':
                print "Your model is still being processed. Will retry in {} seconds".format(retry_timeout)
                retry += 1
                sleep(retry_timeout)
                continue
            elif processing_status == 'FAILED':
                print "Processing failed: {}".format(result['error'])
                return
            elif processing_status == 'SUCCEEDED':
                model_url = SKETCHFAB_MODEL_URL + model_uid
                print "Processing successful. Check your model here: {}".format(model_url)
                return

            retry += 1

        print "Stopped polling after too many retries or too many errors"

    def set_3d_options(self, model_uid, layout):
        """ Fix camera starting point and lighting on the 3D model. """

        headers = {'content-type': 'application/json'}
        data = False

        if layout == "louvre":

            # TODO dump these options in a JSON file next to the model to better encapsulate specifics?
            data = {'options': {
                'camera': {
                    'position': [-0.5655142694766133, -0.17883883950099416, -0.5158722758070228],
                    'target': [-0.2785130611382468, -0.11043290142066092, -0.5412130323100272]
                },

                # Bryant park environment
                'environment': {
                    'backgroundExposure': 1,
                    'blur': 0.1,
                    'enable': True,
                    'exposure': 5.37483797816,
                    'rotation': 0,
                    'uid': 'e73867d210de4bc2b5eb261738cf3e79'
                }
            }}

        print "Sending", data
        if data:

            r = requests.patch(
                'https://api.sketchfab.com/v2/models/{}?token={}'.format(model_uid, self.sketchfab_api_key),
                headers=headers,
                data=json.dumps(data)
            )

            print "Sketchfab API returns", r.status_code
