from mrq.task import Task
from mrq.context import run_task
from mrq.job import queue_job, get_job_result
import json
import tempfile
import shutil
import os
import time

# Creates end-to-end tasks


def wait_for_job(path, params, **kwargs):
    job_id = queue_job(path, params, **kwargs)

    while True:
        time.sleep(5)
        res = get_job_result(job_id)
        if res["status"] == "success":
            return res.get("result")
        elif res["status"] not in ["queued", "started", "interrupt"]:
            raise Exception("Job %s was in status %s" % (
                path, res.get("status")
            ))


# mrq-run tasks.process.Create3dGallery '{"localdebug":1, "source_name": "InstagramFeed", "layout": "louvre", "source_data": {"username": "nineinchnails"}}'
class Create3dGallery(Task):

    def run(self, params):

        layout = params.get("layout", "cube")
        brand = params.get("brand", "imgfab")

        limit = params.get("limit", {
            "cube": 6,
            "wall": 90,
            "louvre": 12,
            "artgallery": 12
        }.get(layout, 10))

        localdebug = params.get("localdebug")

        subtask = wait_for_job
        if localdebug:
            def subtask(*args, **kwargs):
                kwargs.pop("queue", None)
                return run_task(*args, **kwargs)

        tmpdir = subtask("tasks.gather_data.%s" % params["source_name"], {
            "user": params.get("user"),
            "source_data": params["source_data"],
            "limit": limit,
            "layout": layout
        })

        if localdebug:
            os.system("open %s" % tmpdir)

        subtask("tasks.gather_data.DownloadImages", {
            "directory": tmpdir
        })

        subtask("tasks.create_model.CreateModel", {
            "directory": tmpdir,
            "layout": layout,
            "localdebug": localdebug
        })

        if not localdebug:

            sketchfab_data = subtask("tasks.upload_to_sketchfab.UploadToSketchfab", {
                "directory": tmpdir,
                "source_data": params["source_data"],
                "layout": layout,
                "brand": brand,
                "user": params.get("user")
            })

            shutil.rmtree(tmpdir)

            return sketchfab_data
