import copy
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
        self.setMaximumHeight(500)

    def create_ui(self):
        self.title_label = QtWidgets.QLabel("Scatterer")
        self.title_label.setStyleSheet("font: bold 20px")
        self.description_label = QtWidgets.QLabel(
            "First click on the object you want to scatter objects onto. "
            "Then hold shift and click on the object that you want to "
            "scatter. Change any of the settings you want to, then click "
            "the \"Scatter\" button.")
        self.description_label.setWordWrap(True)
        self.vector_array = self._create_vector_array_ui()
        self.alignment_button = QtWidgets.QCheckBox("Align instances to "
                                                    "surface normals")
        self.scatter_button = QtWidgets.QPushButton("Scatter")
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.description_label)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.vector_array)
        self.main_layout.addWidget(self.alignment_button)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.scatter_button)
        self.setLayout(self.main_layout)
        self._set_ui_properties_from_scatter()

    def _create_vector_array_ui(self):
        w, h = 3, 6
        self.spinbox_array = [[0 for x in range(w)] for y in range(h)]

        layout = QtWidgets.QGridLayout()

        layout.addWidget(QtWidgets.QLabel("Scale Minimum"), 0, 0)
        layout.addWidget(QtWidgets.QLabel("Scale Maximum"), 1, 0)
        layout.addWidget(QtWidgets.QLabel("Rotation Minimum"), 2, 0)
        layout.addWidget(QtWidgets.QLabel("Rotation Maximum"), 3, 0)
        layout.addWidget(QtWidgets.QLabel("Position Minimum"), 4, 0)
        layout.addWidget(QtWidgets.QLabel("Position Maximum"), 5, 0)

        i = 0
        while i < 6:
            j = 0
            while j < 3:
                spinbox = \
                    self._create_vector_component_spinbox()
                self.spinbox_array[i][j] = spinbox
                layout.addWidget(spinbox, i, j * 2 + 3)
                j += 1

            layout.addWidget(QtWidgets.QLabel("X"), i, 2)
            layout.addWidget(QtWidgets.QLabel("Y"), i, 4)
            layout.addWidget(QtWidgets.QLabel("Z"), i, 6)

            i += 1

        layout.setColumnStretch(10, 100)

        return layout

    def _create_vector_component_spinbox(self):
        spinbox = QtWidgets.QDoubleSpinBox()
        spinbox.setSingleStep(0.1)
        spinbox.setMinimum(-1000)
        spinbox.setMaximum(1000)
        spinbox.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.PlusMinus)
        spinbox.setFixedWidth(50)
        spinbox.setValue(0)
        return spinbox

    def create_connections(self):
        """Connects Signals and Slots"""
        self.scatter_button.clicked.connect(self._scatter)
        return

    def _scatter(self):
        self._set_scatter_properties_from_ui()
        self.scatterer.scatter()
        self._set_scatter_properties_from_ui()
        return

    def _set_ui_properties_from_scatter(self):
        i = 0
        while i < len(self.spinbox_array):
            j = 0
            while j < len(self.spinbox_array[i]):
                self.spinbox_array[i][j].setValue(
                    self.scatterer.attribute_array[i][j])
                j += 1
            i += 1

        self.alignment_button.setChecked(self.scatterer.alignment)

    def _set_scatter_properties_from_ui(self):
        i = 0
        while i < len(self.spinbox_array):
            j = 0
            while j < len(self.spinbox_array[i]):
                self.scatterer.attribute_array[i][j] = \
                    self.spinbox_array[i][j].value()
                j += 1
            i += 1

        self.scatterer.alignment = self.alignment_button.checkState()


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
        self.alignment = True
        self.scatter_percentage = 1

        # Scale Min    X Y Z
        # Scale Max    X Y Z
        # Rotation Min X Y Z
        # Rotation Max X Y Z
        # Position Min X Y Z
        # Position Max X Y Z
        w, h = 3, 6
        self.attribute_array = [[0 for x in range(w)] for y in range(h)]
        self.attribute_array[0] = [1, 1, 1]
        self.attribute_array[1] = [1, 1, 1]

    def scatter(self):
        self.selected_objects = []

        # Get objects currently selected
        self.selected_objects = pmc.ls(os=True)
        scatter_target = self.selected_objects[0]
        scatter_sources = self.selected_objects[1:]

        vertexes = range(len(scatter_target.vtx))
        random.shuffle(vertexes)
        vertexes = vertexes[:int(self.scatter_percentage * len(vertexes))]

        for i in vertexes:
            vertex = scatter_target.vtx[i]

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

            new_instance = pmc.instance(random.choice(scatter_sources))
            position = pmc.pointPosition(vertex, w=True)
            pmc.move(position[0], position[1], position[2],
                     new_instance, a=True, ws=True)

            if self.alignment:
                pmc.normalConstraint(scatter_target, new_instance)
                pmc.normalConstraint(scatter_target, new_instance, rm=True)

            scale = random_between_two_vectors(
                self.attribute_array[0], self.attribute_array[1])
            rotation = random_between_two_vectors(
                self.attribute_array[2], self.attribute_array[3])
            position = random_between_two_vectors(
                self.attribute_array[4], self.attribute_array[5])

            pmc.scale(new_instance,
                      scale[0], scale[1], scale[2],
                      r=True)
            pmc.rotate(new_instance,
                       rotation[0], rotation[1], rotation[2],
                       r=True)
            pmc.move(position[0], position[1], position[2],
                     new_instance,
                     r=True, os=True, wd=True)

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
