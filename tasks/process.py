from mrq.task import Task
from mrq.context import run_task
from mrq.job import queue_job, get_job_result
from flaskapp.models import User
import json
import tempfile
import shutil
import os
import time

# Creates end-to-end tasks


def wait_for_job(path, params):
    job_id = queue_job(path, params)

    while True:
        time.sleep(5)
        res = get_job_result(job_id)
        if res["status"] == "success":
            return res.get("result")
        elif res["status"] not in ["queued", "started", "interrupt"]:
            raise Exception("Job %s was in status %s" % (
                path, res.get("status")
            ))


class Create3dGallery(Task):

    def run(self, params):

        tmpdir = wait_for_job("tasks.gather_data.%s" % params["source_name"], {
            "user": params["user"],
            "source_data": params["source_data"],
            "limit": params.get("limit", 6)
        })

        # os.system("open %s" % tmpdir)

        wait_for_job("tasks.gather_data.DownloadImages", {
            "directory": tmpdir
        })

        wait_for_job("tasks.create_model.CreateModel", {
            "directory": tmpdir
        })

        sketchfab_data = wait_for_job("tasks.upload_to_sketchfab.UploadToSketchfab", {
            "directory": tmpdir
        })

        shutil.rmtree(tmpdir)

        return sketchfab_data
