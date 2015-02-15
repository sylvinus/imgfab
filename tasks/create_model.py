from mrq.task import Task
import os


class CreateModel(Task):

    def run(self, params):

        blender_path = "/Applications/Blender/blender.app/Contents/MacOS/blender"
        blender_script = os.path.abspath(os.path.join(__file__, '../../blender_script.py'))

        #  -b
        os.system("%s -P %s -d -- %s" % (
          blender_path, blender_script, params["directory"]
        ))
