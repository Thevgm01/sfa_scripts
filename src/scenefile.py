import logging

import pymel.core as pmc
from pymel.core.system import Path

log = logging.getLogger(__name__)

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

    def save(self):
        """Saves the scene file.

        Returns
            Path: The path to the scene file if successful
        """
        try:
            return pmc.system.saveAs(self.path)
        except RuntimeError as err:
            log.warning("Missing directories in path. Creating directories now...")
            self.folder_path.makedirs_p()
            return pmc.system.saveAs(self.path)

