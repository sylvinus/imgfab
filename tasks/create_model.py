from mrq.task import Task
import os


class CreateModel(Task):

    def run(self, params):

        blender_path = os.getenv("BLENDER_PATH", "/Applications/Blender/blender.app/Contents/MacOS/blender")
        blender_script = os.path.abspath(os.path.join(__file__, '../../blender_script.py'))

        export_file = os.path.join(params["directory"], "export.blend")
        if os.path.isfile(export_file):
            os.remove(export_file)

        cmdline = "%s --debug --background --python %s -- %s" % (
          blender_path, blender_script, params["directory"]
        )

        if params.get("localdebug"):
            print "Calling blender with:"
            print cmdline

        os.system(cmdline)

        if params.get("localdebug"):
            os.system("open %s" % export_file)
