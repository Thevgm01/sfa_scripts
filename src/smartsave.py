import logging

from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pmc
from pymel.core.system import Path

log = logging.getLogger(__name__)


def maya_main_window():
    """Return the maya main window widget"""
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window), QtWidgets.QWidget)


class SmartSaveUI(QtWidgets.QDialog):
    """Smart Save UI Class"""

    def __init__(self):
        super(SmartSaveUI, self).__init__(parent=maya_main_window())
        self.setWindowTitle("Smart Save")
        self.setMinimumWidth(500)
        self.setMaximumHeight(200)
        self.setWindowFlags(self.windowFlags() ^
                            QtCore.Qt.WindowContextHelpButtonHint)
        self.create_ui()

    def create_ui(self):
        self.title_label = QtWidgets.QLabel("Smart Save")
        self.title_label.setStyleSheet("font: bold 20px")
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.title_label)
        self.setLayout(self.main_layout)


class SceneFile(object):
    """An abstract representation of a scene file."""

    def __init__(self, path_text=None):
        self.full_path = Path()
        self.folder_path = self.full_path
        self.descriptor = "main"
        self.task = None
        self.ver = 1
        self.ext = ".ma"
        if not path_text:
            scene = pmc.system.sceneName()
            if scene:
                path_text = pmc.system.sceneName()
            else:
                log.warning("Unable to initialize SceneFile object "
                            "from a new scene. Please specify a path.")
                return
        self._init_from_path(path_text)

    def _init_from_path(self, path_text):
        path = Path(path_text)
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
            log.warning("Missing directories in path. "
                        "Creating directories now...")
            self.folder_path.makedirs_p()
            return pmc.system.saveAs(self.path)

    def next_available_version(self):
        """Return the next available version number in the folder."""
        pattern = "{descriptor}_{task}_v*{ext}".format(
            descriptor=self.descriptor, task=self.task, ext=self.ext)
        matching_scenefiles = []
        for file_ in self.folder_path.files():
            if file_.name.fnmatch(pattern):
                matching_scenefiles.append(file_)
        if not matching_scenefiles:
            return 1
        matching_scenefiles.sort()
        latest_scenefile = matching_scenefiles[-1]
        latest_version = latest_scenefile.name.stripext().split("_v")[-1]
        return int(latest_version) + 1

    def increment_save(self):
        """Increments the version and saves the scene file.

        If the file already exists, increments the version number from
        the largest number in the directory.

        Returns:
            Path: The path to the scene file if successful"""
        self.ver = self.next_available_version()
        self.save()
