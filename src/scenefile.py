# {path} = {folder_path}/{descriptor}_{task}_{v###}.{ext}

class SceneFile(object):
    """An abstract representation of a scene file."""
    def __init__(self, folder_path, descriptor, task, ver, ext):
        self.folder_path = folder_path
        self.descriptor = descriptor
        self.task = task
        self.ver = ver
        self.ext = ext

scene_file = SceneFile("C:\\", "tank", "model", "v001", ".ma")
print(scene_file.descriptor)