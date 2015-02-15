from mrq.task import Task
import os


class CreateModel(Task):

    def run(self, params):

        blender_path = os.getenv("BLENDER_PATH", "/Applications/Blender/blender.app/Contents/MacOS/blender")
        blender_script = os.path.abspath(os.path.join(__file__, '../../blender_script.py'))

        export_file = os.path.join(params["directory"], "export.blend")
        if os.path.isfile(export_file):
            os.remove(export_file)

        os.system("%s --debug --background --python %s -- %s" % (
          blender_path, blender_script, params["directory"]
        ))

        # os.system("open %s" % export_file)
