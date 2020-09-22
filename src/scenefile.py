# {path} = {folder_path}/{descriptor}_{task}_{v###}.{ext}

from pathlib import Path


class SceneFile(object):
    """An abstract representation of a scene file."""

    def __init__(self, path):
        self.folder_path = Path()
        self.descriptor = "main"
        self.task = None
        self.ver = 1
        self.ext = ".ma"
        self._init_from_path(path)

    def _init_from_path(self, path):
        path = Path(path)
        self.folder_path = path.parent
        self.ext = path.suffix
        self.descriptor, self.task, ver_str = path.stem.split("_")
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


scene_file = SceneFile("C:/spaceship_model_v031.ma")
