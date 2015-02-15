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


SKETCHFAB_DOMAIN = 'sketchfab.com'
SKETCHFAB_API_URL = 'https://api.{}/v2/models'.format(SKETCHFAB_DOMAIN)
SKETCHFAB_MODEL_URL = 'https://{}/models/'.format(SKETCHFAB_DOMAIN)

YOUR_API_TOKEN = os.getenv("SKETCHFAB_API_KEY")

from mrq.task import Task
import os
import requests
from time import sleep
import random


class UploadToSketchfab(Task):

    def run(self, params):

        directory = params["directory"]

        rand = random.randint(100000000, 9999999999)

        zip_name = "export-%s.zip" % rand
        model_file = "%s/%s" % zip_name

        os.system("zip %s %s/export.blend" % (
            model_file, directory
        ))

        # Mandatory parameters

        # Optional parameters
        name = params.get("name", "imgfab #%s" % rand)
        description = params.get("description", "http://imgfab.io")
        password = ""  # requires a pro account
        private = 0  # requires a pro account
        tags = "imgfab gallery"  # space-separated list of tags

        data = {
            'token': YOUR_API_TOKEN,
            'name': name,
            'description': description,
            'tags': tags,
            'private': private,
            'password': password
        }

        f = open(model_file, 'rb')

        files = {
            'modelFile': f
        }

        try:
            model_uid = self.upload(data, files)
            self.poll_processing_status(model_uid)
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
        polling_url = "{}/{}/status?token={}".format(SKETCHFAB_API_URL, model_uid, YOUR_API_TOKEN)
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
