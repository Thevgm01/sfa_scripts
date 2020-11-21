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
        self.resize(100, 500)
        self.setMaximumWidth(700)
        self.setMaximumHeight(500)

    def create_ui(self):
        self.title_label = QtWidgets.QLabel("Scatterer")
        self.title_label.setStyleSheet("font: bold 20px")
        self.description_label = QtWidgets.QLabel(
            "Click on the object(s) (or vertices) that you want to scatter "
            "to, then click on the \"Set Target(s)\" button. Repeat for the "
            "sources that you want to scatter with. Change any settings, then "
            "click the \"Scatter\" button.")
        self.description_label.setWordWrap(True)
        self.vector_array = self._create_vector_array_ui()
        self.alignment_button = QtWidgets.QCheckBox("Align instances to "
                                                    "surface normals")
        self.scatter_density_layout = self._create_scatter_density_spinbox()
        self.scatter_buttons_layout = self._create_scatter_buttons()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.description_label)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.vector_array)
        self.main_layout.addWidget(self.alignment_button)
        self.main_layout.addLayout(self.scatter_density_layout)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.scatter_buttons_layout)
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

    def _create_scatter_density_spinbox(self):
        self.scatter_density_spinbox = self._create_vector_component_spinbox()
        self.scatter_density_spinbox.setMinimum(0)
        self.scatter_density_spinbox.setMaximum(1)
        self.scatter_density_label = QtWidgets.QLabel("Fraction of vertices "
                                                      "to scatter")

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.scatter_density_spinbox)
        layout.addWidget(self.scatter_density_label)
        layout.addStretch()
        return layout

    def _create_scatter_buttons(self):
        self.set_scatter_targets_button = \
            QtWidgets.QPushButton("Set Target(s)")
        self.select_scatter_targets_button = \
            QtWidgets.QPushButton("Select Target(s)")

        self.set_scatter_sources_button = \
            QtWidgets.QPushButton("Set Source(s)")
        self.select_scatter_sources_button = \
            QtWidgets.QPushButton("Select Source(s)")

        self.targets_selected_label = QtWidgets.QLabel("0 targets selected")
        self.targets_selected_label.setAlignment(QtCore.Qt.AlignCenter)
        self.sources_selected_label = QtWidgets.QLabel("0 sources selected")
        self.sources_selected_label.setAlignment(QtCore.Qt.AlignCenter)

        self.scatter_button = QtWidgets.QPushButton("Scatter")
        self.undo_button = QtWidgets.QPushButton("Undo")

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.set_scatter_targets_button, 0, 0)
        layout.addWidget(self.select_scatter_targets_button, 1, 0)

        layout.addWidget(self.set_scatter_sources_button, 0, 1)
        layout.addWidget(self.select_scatter_sources_button, 1, 1)

        layout.addWidget(self.targets_selected_label, 2, 0)
        layout.addWidget(self.sources_selected_label, 2, 1)

        layout.addWidget(self.scatter_button, 3, 0)
        layout.addWidget(self.undo_button, 3, 1)
        return layout

    def create_connections(self):
        """Connects Signals and Slots"""
        self.set_scatter_targets_button.clicked.connect(
            self._set_scatter_targets)
        self.select_scatter_targets_button.clicked.connect(
            self.scatterer.select_scatter_targets)

        self.set_scatter_sources_button.clicked.connect(
            self._set_scatter_sources)
        self.select_scatter_sources_button.clicked.connect(
            self.scatterer.select_scatter_sources)

        self.scatter_button.clicked.connect(self._scatter)
        self.undo_button.clicked.connect(self.scatterer.delete_scatters)
        return

    def _set_scatter_targets(self):
        self.scatterer.set_scatter_targets()
        self.targets_selected_label.setText(
            str(len(self.scatterer.scatter_targets)) + " targets selected")

    def _set_scatter_sources(self):
        self.scatterer.set_scatter_sources()
        self.sources_selected_label.setText(
            str(len(self.scatterer.scatter_sources)) + " sources selected")

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
        self.scatter_density_spinbox.setValue(self.scatterer.scatter_density)

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
        self.scatterer.scatter_density = self.scatter_density_spinbox.value()


def random_between_two_vectors(vec1, vec2):
    result = [0, 0, 0]
    result[0] = random.uniform(vec1[0], vec2[0])
    result[1] = random.uniform(vec1[1], vec2[1])
    result[2] = random.uniform(vec1[2], vec2[2])
    return result


class Scatterer(object):

    def __init__(self):
        self.scatter_targets = []
        self.scatter_sources = []
        self.scatter_instances = []
        self.alignment = True
        self.scatter_density = 1

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

    def set_scatter_targets(self):
        self.scatter_targets = pmc.ls(os=True, fl=True)

    def add_scatter_targets(self):
        self.scatter_targets.extend(pmc.ls(os=True, fl=True))

    def select_scatter_targets(self):
        pmc.select(self.scatter_targets)

    def set_scatter_sources(self):
        self.scatter_sources = pmc.ls(os=True, fl=True)

    def add_scatter_sources(self):
        self.scatter_sources.extend(pmc.ls(os=True, fl=True))

    def select_scatter_sources(self):
        pmc.select(self.scatter_sources)

    def scatter(self):
        all_vertexes = []
        self.scatter_instances.append([])

        for target in self.scatter_targets:
            if type(target) == pmc.general.MeshVertex:
                all_vertexes.append(target)
            else:
                all_vertexes.extend(target.vtx)

        vertexes = range(len(all_vertexes))
        random.shuffle(vertexes)
        vertexes = vertexes[:int(self.scatter_density * len(vertexes))]

        for i in vertexes:
            vertex = all_vertexes[i]

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

            new_instance = pmc.instance(random.choice(self.scatter_sources))
            self.scatter_instances[-1].append(new_instance)

            position = pmc.pointPosition(vertex, w=True)
            pmc.move(position[0], position[1], position[2],
                     new_instance, a=True, ws=True)

            if self.alignment:
                pmc.normalConstraint(vertex, new_instance)
                pmc.normalConstraint(vertex, new_instance, rm=True)

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

    def delete_scatters(self):
        if len(self.scatter_instances) > 0:
            pmc.delete(self.scatter_instances.pop(-1))
