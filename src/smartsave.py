import logging

from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as cmds
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
        self.folder_layout = self._create_folder_ui()
        self.filename_layout = self._create_filename_ui()
        self.save_button_layout = self._create_save_button_ui()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addLayout(self.folder_layout)
        self.main_layout.addLayout(self.filename_layout)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.save_button_layout)
        self.setLayout(self.main_layout)

    def _create_folder_ui(self):
        default_folder = Path(cmds.workspace(rootDirectory=True, query=True))
        default_folder = default_folder / "scenes"
        self.folder_line_edit = QtWidgets.QLineEdit(default_folder)
        self.folder_browse_button = QtWidgets.QPushButton("...")
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.folder_line_edit)
        layout.addWidget(self.folder_browse_button)
        return layout

    def _create_filename_ui(self):
        self._create_filename_headers()
        self._create_filename_inputs()
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.descriptor_header_label, 0, 0)
        layout.addWidget(self.task_header_label, 0, 2)
        layout.addWidget(self.version_header_label, 0, 4)
        layout.addWidget(self.descriptor_line_edit, 1, 0)
        layout.addWidget(QtWidgets.QLabel("_"), 1, 1)
        layout.addWidget(self.task_line_edit, 1, 2)
        layout.addWidget(QtWidgets.QLabel("_v"), 1, 3)
        layout.addWidget(self.version_spinbox, 1, 4)
        layout.addWidget(self.extension_label, 1, 5)
        return layout

    def _create_filename_headers(self):
        self.descriptor_header_label = QtWidgets.QLabel("Descriptor")
        self.descriptor_header_label.setStyleSheet("font: bold")
        self.task_header_label = QtWidgets.QLabel("Task")
        self.task_header_label.setStyleSheet("font: bold")
        self.version_header_label = QtWidgets.QLabel("Version")
        self.version_header_label.setStyleSheet("font: bold")
        self.extension_label = QtWidgets.QLabel(".ma")

    def _create_filename_inputs(self):
        self.descriptor_line_edit = QtWidgets.QLineEdit("main")
        self.descriptor_line_edit.setMinimumWidth(100)
        self.task_line_edit = QtWidgets.QLineEdit("model")
        self.task_line_edit.setFixedWidth(50)
        self.version_spinbox = QtWidgets.QSpinBox()
        self.version_spinbox.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.PlusMinus)
        self.version_spinbox.setFixedWidth(50)
        self.version_spinbox.setValue(1)

    def _create_save_button_ui(self):
        self.save_button = QtWidgets.QPushButton("Save")
        self.save_increment_button = QtWidgets.QPushButton("Save Increment")
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.save_button)
        layout.addWidget(self.save_increment_button)
        return layout


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
