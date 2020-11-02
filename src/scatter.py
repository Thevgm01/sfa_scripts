import logging
import random

from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import pymel.core as pmc

log = logging.getLogger(__name__)


def maya_main_window():
    """Return the maya main window widget"""
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window), QtWidgets.QWidget)


class ScatterUI(QtWidgets.QDialog):
    """Smart Save UI Class"""

    def __init__(self):
        super(ScatterUI, self).__init__(parent=maya_main_window())
        self.setWindowTitle("Scatterer")
        self.setWindowFlags(self.windowFlags() ^
                            QtCore.Qt.WindowContextHelpButtonHint)
        self.scatterer = Scatterer()
        self.create_ui()
        self.create_connections()
        self.resize(500, 100)
        self.setMaximumWidth(700)
        self.setMaximumHeight(250)

    def create_ui(self):
        self.title_label = QtWidgets.QLabel("Scatterer")
        self.title_label.setStyleSheet("font: bold 20px")
        # self.folder_layout = self._create_folder_ui()
        # self.filename_layout = self._create_filename_ui()
        # self.successful_save = QtWidgets.QLabel("")
        self.scatter_button = QtWidgets.QPushButton("Scatter")
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.title_label)
        # self.main_layout.addLayout(self.folder_layout)
        # self.main_layout.addLayout(self.filename_layout)
        # self.main_layout.addStretch()
        self.main_layout.addWidget(self.scatter_button)
        # self.main_layout.addLayout(self.save_button_layout)
        self.setLayout(self.main_layout)

    def create_connections(self):
        """Connects Signals and Slots"""
        self.scatter_button.clicked.connect(self._scatter)
        return

    def _scatter(self):
        self._set_scatter_properties_from_ui()
        self.scatterer.scatter()
        return

    def _set_scatter_properties_from_ui(self):
        return
        # self.scatterer.folder_path = self.folder_line_edit.text()
        # self.scatterer.descriptor = self.descriptor_line_edit.text()
        # self.scatterer.task = self.task_line_edit.text()
        # self.scatterer.version = self.version_spinbox.value()
        # self.scatterer.extension = self.extension_label.text()


def random_between_two_vectors(vec1, vec2):
    result = [0, 0, 0]
    result[0] = random.uniform(vec1[0], vec2[0])
    result[1] = random.uniform(vec1[1], vec2[1])
    result[2] = random.uniform(vec1[2], vec2[2])
    return result


class Scatterer(object):

    def __init__(self):
        self.selected_objects = []
        self.scatter_density = 1
        self.random_scale_min = [1, 1, 1]
        self.random_scale_max = [1, 1, 1]
        self.random_rotation_min = [0, 0, 0]
        self.random_rotation_max = [0, 0, 0]
        self.random_position_min = [-1, -1, -1]
        self.random_position_max = [1, 1, 1]

    def scatter(self):
        self.selected_objects = []

        # Get objects currently selected
        self.selected_objects = pmc.ls(os=True)
        scatter_target = self.selected_objects[0]
        scatter_source = self.selected_objects[1]

        for vertex in scatter_target.vtx:
            # Get the average normal of the vertex
            # pmc.select(vertex, r=True)
            # a = pmc.polyNormalPerVertex(q=True, xyz=True)
            # num_normals = len(a) / 3
            # average_normal = [0, 0, 0]
            # i = 0
            # while i < len(a):
            #     average_normal[i % 3] += a[i] / num_normals
            #     i += 1
            # # print(average_normal)

            new_instance = pmc.instance(scatter_source)
            position = pmc.pointPosition(vertex, w=True)
            pmc.move(position[0], position[1], position[2],
                     new_instance, a=True, ws=True)

            # pmc.normalConstraint(scatter_target, new_instance)
            # pmc.normalConstraint(scatter_target, new_instance, rm=True)

            scale = random_between_two_vectors(
                self.random_scale_min, self.random_scale_max)
            rotation = random_between_two_vectors(
                self.random_rotation_min, self.random_rotation_max)
            position = random_between_two_vectors(
                self.random_position_min, self.random_position_max)

            pmc.scale(new_instance,
                      scale[0], scale[1], scale[2],
                      r=True)
            pmc.rotate(new_instance,
                       rotation[0], rotation[1], rotation[2],
                       r=True)
            pmc.move(position[0], position[1], position[2],
                     new_instance,
                     r=True)

        # hello = cmds.polyListComponentConversion(tv=True)
        # print(hello[0])

        # vertices = cmds.polyEvaluate(scatter_target, v=True)
        # i = 0
        # while i < vertices:
        #     print(scatter_target.vtx)
        #     i += 1
        #print(cmds.filterExpand(selectionMask=31))
        #self.scatterTargetsVertices.append(vertices)

        return
