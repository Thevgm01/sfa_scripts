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
        self.setWindowFlags(self.windowFlags() ^
                            QtCore.Qt.WindowContextHelpButtonHint)
        self.scenefile = SceneFile()
        self.create_ui()
        self.create_connections()
        self.resize(500, 100)
        self.setMaximumWidth(700)
        self.setMaximumHeight(250)

    def create_ui(self):
        self.title_label = QtWidgets.QLabel("Smart Save")
        self.title_label.setStyleSheet("font: bold 20px")
        self.folder_layout = self._create_folder_ui()
        self.filename_layout = self._create_filename_ui()
        self.successful_save = QtWidgets.QLabel("")
        self.save_button_layout = self._create_save_button_ui()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addLayout(self.folder_layout)
        self.main_layout.addLayout(self.filename_layout)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.successful_save)
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
        self.descriptor_line_edit = QtWidgets.QLineEdit(
            self.scenefile.descriptor)
        self.descriptor_line_edit.setMinimumWidth(100)
        self.task_line_edit = QtWidgets.QLineEdit(self.scenefile.task)
        self.task_line_edit.setFixedWidth(50)
        self.version_spinbox = QtWidgets.QSpinBox()
        self.version_spinbox.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.PlusMinus)
        self.version_spinbox.setFixedWidth(50)
        # self.version_spinbox.setValue(self.scenefile.version)
        # done in create_connections
        self.version_spinbox.setMinimum(1)
        self.version_spinbox.setMaximum(999)

    def _create_save_button_ui(self):
        self.save_button = QtWidgets.QPushButton("Save")
        self.save_increment_button = QtWidgets.QPushButton("Save Increment")
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.save_button)
        layout.addWidget(self.save_increment_button)
        return layout

    def create_connections(self):
        """Connects Signals and Slots"""
        self.folder_browse_button.clicked.connect(self._browse_folder)
        self.save_button.clicked.connect(self._save_file)
        self.save_increment_button.clicked.connect(self._save_increment)
        self.version_spinbox.valueChanged.connect(
            self._add_version_spinbox_padding)
        self.version_spinbox.setValue(self.scenefile.version)

    @QtCore.Slot()
    def _browse_folder(self):
        """Opens a dialog box to browse through folders"""
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            parent=self,
            caption="Select folder",
            dir=self.folder_line_edit.text(),
            options=QtWidgets.QFileDialog.ShowDirsOnly |
                    QtWidgets.QFileDialog.DontResolveSymlinks)
        self.folder_line_edit.setText(folder)

    @QtCore.Slot()
    def _save_file(self):
        """Saves the scene"""
        self._set_scenefile_properties_from_ui()
        self._update_successful_save(self.scenefile.save())

    @QtCore.Slot()
    def _save_increment(self):
        """Save an increment of the scene"""
        self._set_scenefile_properties_from_ui()
        self._update_successful_save(self.scenefile.save_increment())
        self.version_spinbox.setValue(self.scenefile.version)

    def _set_scenefile_properties_from_ui(self):
        self.scenefile.folder_path = self.folder_line_edit.text()
        self.scenefile.descriptor = self.descriptor_line_edit.text()
        self.scenefile.task = self.task_line_edit.text()
        self.scenefile.version = self.version_spinbox.value()
        self.scenefile.extension = self.extension_label.text()

    def _update_successful_save(self, value):
        if value:
            self.successful_save.setText(
                self.scenefile.filename + " saved successfully!")
        else:
            self.successful_save.setText(
                "Error: Could not save " + self.scenefile.filename)

    @QtCore.Slot()
    def _add_version_spinbox_padding(self, value):
        if value >= 100:
            self.version_spinbox.setPrefix("")
        elif value >= 10:
            self.version_spinbox.setPrefix("0")
        else:
            self.version_spinbox.setPrefix("00")


class SceneFile(object):
    """An abstract representation of a scene file."""

    def __init__(self, path_text=None):
        if path_text:
            self._init_from_path(path_text)
        else:
            scene = pmc.system.sceneName()
            if scene:
                self._init_from_path(scene)
            else:
                log.info("Unable to initialize SceneFile object "
                         "from open scene. Initializing with "
                         "default values.")
                self._folder_path = Path(cmds.workspace(
                    query=True,
                    rootDirectory=True)) / "scenes"
                self.descriptor = "main"
                self.task = "model"
                self.version = 1
                self.extension = ".ma"

    def _init_from_path(self, path_text):
        path = Path(path_text)
        self.folder_path = path.parent
        self.extension = path.ext
        self.descriptor, self.task, ver_str = path.name.stripext().split("_")
        self.version = int(ver_str.split("v")[-1])

    @property
    def folder_path(self):
        return self._folder_path

    @folder_path.setter
    def folder_path(self, value):
        self._folder_path = Path(value)

    @property
    def filename(self):
        pattern = "{descriptor}_{task}_v{ver:03d}{ext}"
        return pattern.format(descriptor=self.descriptor,
                              task=self.task,
                              ver=self.version,
                              ext=self.extension)

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
            descriptor=self.descriptor, task=self.task, ext=self.extension)
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

    def save_increment(self):
        """Increments the version and saves the scene file.

        If the file already exists, increments the version number from
        the largest number in the directory.

        Returns:
            Path: The path to the scene file if successful"""
        self.version = self.next_available_version()
        return self.save()
