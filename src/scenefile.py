from pymel.core.system import Path
#from pathlib import Path


class SceneFile(object):
    """An abstract representation of a scene file."""

    def __init__(self, path_text):
        self.full_path = Path()
        self.folder_path = self.full_path
        self.descriptor = "main"
        self.task = None
        self.ver = 1
        self.ext = ".ma"
        self._init_from_path(path_text)

    def _init_from_path(self, path):
        path = Path(path)
        self.full_path = path
        self.folder_path = path.parent
        self.ext = path.ext
        self.descriptor, self.task, ver_str = path.name.stripext().split("_")
        self.ver = int(ver_str.split("v")[-1])

    @property
    def filename(self):
        pattern = "{descriptor}_{task}_v{ver:03d}{ext}"
        return pattern.format(descriptor=self.descriptor,
                              task=self.task,
                              ver=self.ver,
                              ext=self.ext)

    @property
    def path(self):
        return self.folder_path / self.filename


input_string = "C:\\maya_projects\\spaceship_model_v031.ma"
scene_file = SceneFile(input_string)

table = [["Input string", input],
         ["Full path", str(scene_file.full_path)],
         ["Folder path", str(scene_file.folder_path)],
         ["Filename", scene_file.filename],
         ["Descriptor", scene_file.descriptor],
         ["Task", scene_file.task],
         ["Version", scene_file.ver],
         ["Extension", scene_file.ext]]
for header, value in table:
    print('%-15s %s' % (header, value))