""" ==================================================================
Script Name: xNormalBatchBakerForMaya.py
by Tomas Poveda - 14/12/16
______________________________________________________________________
xNormal Batch Baker Tool for Maya
______________________________________________________________________
==================================================================="""

try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from shiboken2 import wrapInstance
except:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from shiboken import wrapInstance

import maya.OpenMayaUI as OpenMayaUI
import os
from functools import partial
import xNormal
reload(xNormal)
import subprocess

comtypesAvailable = True
try:
    import comtypes.client
except:
    comtypesAvailable = False

# Tool stylesheet
try:
    xNormalBatchBakerCss = os.path.join(os.path.dirname(os.path.relpath(__file__)), 'xNormalBatchBakerStyle.css')
except:
    xNormalBatchBakerCss = ''

import maya.cmds as cmds

global xNormalBatchBakerWindow

class xNormalBatchBaker(QMainWindow, object):

    def __init__(self):

        super(xNormalBatchBaker, self).__init__(_getMayaWindow())
        
        if xNormalBatchBakerCss != '':
            with open(xNormalBatchBakerCss) as styleSheetFile:
                self.setStyleSheet(styleSheetFile.read())

        winName = 'xNormalBatchBakerTool'

        if cmds.window(winName, exists=True):
            cmds.deleteUI(winName, window=True)
        elif cmds.windowPref(winName, exists=True):
            cmds.windowPref(winName, remove=True)

        self.setObjectName(winName)
        self.setWindowTitle('xNormal Batch Baker')
        self.setFixedSize(515, 800)

        self.setUI()

        cmds.select(clear=True)
        self._updateState()

        # Set Selected Items ScriptJob
        self.job = cmds.scriptJob(ct=['SomethingSelected', self._updateState])
        self.job2 = cmds.scriptJob(cf=['SomethingSelected', self._updateState])

        self.show()

    def closeEvent(self, event):
        try:
            cmds.scriptJob(kill=self.job, force=True)
            cmds.scriptJob(kill=self.job2, force=True)
        except:
            pass

    def setUI(self):

        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)

        self.mainLayout = QVBoxLayout(self.mainWidget)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.setSpacing(0)

        iconsPath = cmds.internalVar(userBitmapsDir=True) + '\\'

        # Logo
        self.logo = QLabel()
        self.logo.setAlignment(Qt.AlignCenter)
        self.logo.setPixmap(QPixmap(iconsPath + 'logoxNormal.png'))
        self.mainLayout.addWidget(self.logo)

        #Tab Widgets
        self.settingsTab = QWidget()
        self.meshesTab = QWidget()
        self.mapsTab = QWidget()
        self.bakeTab = QWidget()
        self.infoTab = QWidget()

        self.tabs = QTabWidget()
        self.tabs.addTab(self.settingsTab, '1. Meshes Settings')
        self.tabs.addTab(self.meshesTab, '2. Meshes List')
        self.tabs.addTab(self.mapsTab, '3. Maps Settings')
        self.tabs.addTab(self.bakeTab, '4. Bake Settings')
        self.tabs.addTab(self.infoTab, '5. Info Bake')
        self.mainLayout.addWidget(self.tabs)

        buttonsLayout = QHBoxLayout()
        self.mainLayout.addLayout(buttonsLayout)
        loadSettingsBtn = QPushButton('Load Settings')
        loadSettingsBtn.setEnabled(False)
        restoreDefBtn = QPushButton('Restore Default Settings')
        restoreDefBtn.setEnabled(False)
        saveSettingsBtn = QPushButton('Save Settings')
        buttonsLayout.addWidget(loadSettingsBtn)
        buttonsLayout.addWidget(restoreDefBtn)
        buttonsLayout.addWidget(saveSettingsBtn)

        self.tabs.setCurrentIndex(0)

        self.settingsTabUI()
        self.meshesTabUI()
        self.mapsTabUI()
        self.bakeTabUI()
        self.infoTabUI()

        # === SIGNALES === #
        saveSettingsBtn.clicked.connect(partial(self._saveSettings, separatedMeshes=False, createFile=True))


    def settingsTabUI(self):

        settingsMainLayout = QVBoxLayout()
        settingsMainLayout.setContentsMargins(5,5,5,5)
        settingsMainLayout.setSpacing(5)
        settingsMainLayout.setAlignment(Qt.AlignTop)

        settingsLayout = QVBoxLayout()
        settingsLayout.setContentsMargins(5, 5, 5, 5)
        settingsLayout.setSpacing(5)

        hpSettingsLayout = QVBoxLayout()
        hpSettingsLayout.setContentsMargins(5, 5, 5, 5)
        hpSettingsLayout.setSpacing(5)

        lpSettingsLayout = QVBoxLayout()
        lpSettingsLayout.setContentsMargins(5, 5, 5, 5)
        lpSettingsLayout.setSpacing(5)

        cageSettingsLayout = QVBoxLayout()
        cageSettingsLayout.setContentsMargins(5, 5, 5, 5)
        cageSettingsLayout.setSpacing(5)

        # ------- Meshes Settings Layout -------- #
        separatorLayout = QHBoxLayout()
        separatorLayout.setContentsMargins(0, 0, 0, 0)
        separatorLayout.setSpacing(0)
        prefixLayout = QHBoxLayout()
        prefixLayout.setContentsMargins(0, 0, 0, 0)
        prefixLayout.setSpacing(0)
        defMeshScaleLayout = QHBoxLayout()
        defMeshScaleLayout.setContentsMargins(0, 0, 0, 0)
        defMeshScaleLayout.setSpacing(0)
        hpSuffixLayout = QHBoxLayout()
        hpSuffixLayout.setContentsMargins(0, 0, 0, 0)
        hpSuffixLayout.setSpacing(0)
        hpMeshScaleLayout = QHBoxLayout()
        hpMeshScaleLayout.setContentsMargins(0, 0, 0, 0)
        hpMeshScaleLayout.setSpacing(0)
        hpIgnoreVtxColorLayout = QHBoxLayout()
        hpIgnoreVtxColorLayout.setContentsMargins(0, 0, 0, 0)
        hpIgnoreVtxColorLayout.setSpacing(0)
        lpSuffixLayout = QHBoxLayout()
        lpSuffixLayout.setContentsMargins(0, 0, 0, 0)
        lpSuffixLayout.setSpacing(0)
        lpMeshScaleLayout = QHBoxLayout()
        lpMeshScaleLayout.setContentsMargins(0, 0, 0, 0)
        lpMeshScaleLayout.setSpacing(0)
        lpMaxFrontalRayDstLayout = QHBoxLayout()
        lpMaxFrontalRayDstLayout.setContentsMargins(0, 0, 0, 0)
        lpMaxFrontalRayDstLayout.setSpacing(0)
        lpMinNearRayDstLayout = QHBoxLayout()
        lpMinNearRayDstLayout.setContentsMargins(0, 0, 0, 0)
        lpMinNearRayDstLayout.setSpacing(0)
        cageLayout = QHBoxLayout()
        cageLayout.setContentsMargins(0, 0, 0, 0)
        cageLayout.setSpacing(0)

        # ---------------------------------------------------------------------------------
        # ---------------------------------------------------------------------------------

        settingsGrp = QGroupBox('Meshes Settings')
        hpSettingsGrp = QGroupBox('High definition meshes settings (HP)')
        lpSettingsGrp = QGroupBox('Low definition meshes settings (LP')
        cageSettingsGrp = QGroupBox('Cage definition meshes settings (Cage)')

        separatorLbl = QLabel('Separator Character: ')

        self.separatorLine = QLineEdit()
        regExp = QRegExp("@|_")
        textValidator = QRegExpValidator(regExp, self.separatorLine)
        self.separatorLine.setValidator(textValidator)
        self.separatorLine.setMaxLength(1)
        self.separatorLine.setText('_')
        self.separatorLine.setMaximumWidth(20)
        self.separatorLine.setAlignment(Qt.AlignCenter)

        prefixLbl = QLabel('Prefix: ')
        self.prefixLine = QLineEdit()
        regEx = QRegExp("[a-zA-Z]+")
        textValidator = QRegExpValidator(regEx, self.prefixLine)
        self.prefixLine.setValidator(textValidator)

        defScaleLbl = QLabel('Default mesh scale: ')
        self.scaleSpinner = QDoubleSpinBox()
        self.scaleSpinner.setValue(1.0)
        self.scaleSpinner.setDecimals(3)
        self.scaleSpinner.setLocale(QLocale.English)

        hpSuffixLbl = QLabel('Suffix: ')
        self.hpSuffixLine = QLineEdit()
        hpRegEx = QRegExp("[a-zA-Z]+")
        hpSuffixValidator = QRegExpValidator(hpRegEx, self.hpSuffixLine)
        self.hpSuffixLine.setValidator(hpSuffixValidator)

        hpMeshScaleLbl = QLabel('Mesh scale: ')

        self.hpMeshScaleSpinner = QDoubleSpinBox()
        self.hpMeshScaleSpinner.setValue(1.0)
        self.hpMeshScaleSpinner.setDecimals(3)
        self.hpMeshScaleSpinner.setLocale(QLocale.English)

        hpIgnoreVtxColorLbl = QLabel('Ignore per vertex color: ')
        self.hpIgnoreVtxColorCbx = QCheckBox()

        lpSuffixLbl = QLabel('Suffix: ')
        self.lpSuffixLine = QLineEdit()
        lpRegEx = QRegExp("[a-zA-Z]+")
        lpSuffixValidator = QRegExpValidator(lpRegEx, self.lpSuffixLine)
        self.lpSuffixLine.setValidator(lpSuffixValidator)

        lpMeshScaleLbl = QLabel('Mesh scale: ')
        self.lpMeshScaleSpinner = QDoubleSpinBox()
        self.lpMeshScaleSpinner.setValue(1.0)
        self.lpMeshScaleSpinner.setDecimals(3)
        self.lpMeshScaleSpinner.setLocale(QLocale.English)

        lpMaxFrontalRayDstLbl = QLabel('Maximum frontal ray distance: ')
        self.lpMaxFrontalRayDstSpinner = QDoubleSpinBox()
        self.lpMaxFrontalRayDstSpinner.setValue(0.5)
        self.lpMaxFrontalRayDstSpinner.setDecimals(3)
        self.lpMaxFrontalRayDstSpinner.setLocale(QLocale.English)

        lpMinNearRayDstLbl = QLabel('Minimum rear ray distance: ')
        self.lpMinNearRayDstSpinner = QDoubleSpinBox()
        self.lpMinNearRayDstSpinner.setValue(0.5)
        self.lpMinNearRayDstSpinner.setDecimals(3)
        self.lpMinNearRayDstSpinner.setLocale(QLocale.English)

        cageSuffixLbl = QLabel('Suffix: ')
        self.cageSuffixLine = QLineEdit()

        settingsMainLayout.addWidget(settingsGrp)

        ########### BORRAR
        # self.prefixLine.setText('Dwarf')
        # self.hpSuffixLine.setText('HP')
        # self.lpSuffixLine.setText('LP')
        ###############

        settingsGrp.setLayout(settingsLayout)
        settingsLayout.addLayout(separatorLayout)
        settingsLayout.addLayout(prefixLayout)
        settingsLayout.addLayout(defMeshScaleLayout)
        separatorLayout.addSpacerItem(QSpacerItem(150, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        separatorLayout.addWidget(separatorLbl)
        separatorLayout.addWidget(self.separatorLine)
        separatorLayout.addSpacerItem(QSpacerItem(250, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        prefixLayout.addSpacerItem(QSpacerItem(224, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        prefixLayout.addWidget(prefixLbl)
        prefixLayout.addWidget(self.prefixLine)
        prefixLayout.addSpacerItem(QSpacerItem(200, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        defMeshScaleLayout.addSpacerItem(QSpacerItem(144, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        defMeshScaleLayout.addWidget(defScaleLbl)
        defMeshScaleLayout.addWidget(self.scaleSpinner)
        defMeshScaleLayout.addSpacerItem(QSpacerItem(200, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))

        settingsLayout.addWidget(hpSettingsGrp)
        hpSettingsGrp.setLayout(hpSettingsLayout)
        hpSettingsLayout.addLayout(hpSuffixLayout)
        hpSettingsLayout.addLayout(hpMeshScaleLayout)
        hpSettingsLayout.addLayout(hpIgnoreVtxColorLayout)
        hpSuffixLayout.addSpacerItem(QSpacerItem(218, 200, QSizePolicy.Maximum, QSizePolicy.Maximum))
        hpSuffixLayout.addWidget(hpSuffixLbl)
        hpSuffixLayout.addWidget(self.hpSuffixLine)
        hpSuffixLayout.addSpacerItem(QSpacerItem(200, 200, QSizePolicy.Maximum, QSizePolicy.Maximum))
        hpMeshScaleLayout.addSpacerItem(QSpacerItem(182, 200, QSizePolicy.Maximum, QSizePolicy.Maximum))
        hpMeshScaleLayout.addWidget(hpMeshScaleLbl)
        hpMeshScaleLayout.addWidget(self.hpMeshScaleSpinner)
        hpMeshScaleLayout.addSpacerItem(QSpacerItem(200, 200, QSizePolicy.Maximum, QSizePolicy.Maximum))
        hpIgnoreVtxColorLayout.addSpacerItem(QSpacerItem(108, 200, QSizePolicy.Maximum, QSizePolicy.Maximum))
        hpIgnoreVtxColorLayout.addWidget(hpIgnoreVtxColorLbl)
        hpIgnoreVtxColorLayout.addWidget(self.hpIgnoreVtxColorCbx)
        hpIgnoreVtxColorLayout.addSpacerItem(QSpacerItem(200, 200, QSizePolicy.Maximum, QSizePolicy.Maximum))

        settingsLayout.addWidget(lpSettingsGrp)
        lpSettingsGrp.setLayout(lpSettingsLayout)
        lpSettingsLayout.addLayout(lpSuffixLayout)
        lpSettingsLayout.addLayout(lpMeshScaleLayout)
        lpSettingsLayout.addLayout(lpMaxFrontalRayDstLayout)
        lpSettingsLayout.addLayout(lpMinNearRayDstLayout)
        lpSuffixLayout.addSpacerItem(QSpacerItem(218, 200, QSizePolicy.Maximum, QSizePolicy.Maximum))
        lpSuffixLayout.addWidget(lpSuffixLbl)
        lpSuffixLayout.addWidget(self.lpSuffixLine)
        lpSuffixLayout.addSpacerItem(QSpacerItem(200, 200, QSizePolicy.Maximum, QSizePolicy.Maximum))
        lpMeshScaleLayout.addSpacerItem(QSpacerItem(180, 200, QSizePolicy.Maximum, QSizePolicy.Maximum))
        lpMeshScaleLayout.addWidget(lpMeshScaleLbl)
        lpMeshScaleLayout.addWidget(self.lpMeshScaleSpinner)
        lpMeshScaleLayout.addSpacerItem(QSpacerItem(200, 200, QSizePolicy.Maximum, QSizePolicy.Maximum))
        lpMaxFrontalRayDstLayout.addSpacerItem(QSpacerItem(82, 200, QSizePolicy.Maximum, QSizePolicy.Maximum))
        lpMaxFrontalRayDstLayout.addWidget(lpMaxFrontalRayDstLbl)
        lpMaxFrontalRayDstLayout.addWidget(self.lpMaxFrontalRayDstSpinner)
        lpMaxFrontalRayDstLayout.addSpacerItem(QSpacerItem(200, 200, QSizePolicy.Maximum, QSizePolicy.Maximum))
        lpMinNearRayDstLayout.addSpacerItem(QSpacerItem(98, 200, QSizePolicy.Maximum, QSizePolicy.Maximum))
        lpMinNearRayDstLayout.addWidget(lpMinNearRayDstLbl)
        lpMinNearRayDstLayout.addWidget(self.lpMinNearRayDstSpinner)
        lpMinNearRayDstLayout.addSpacerItem(QSpacerItem(200, 200, QSizePolicy.Maximum, QSizePolicy.Maximum))

        cageSettingsGrp.setEnabled(False)
        settingsLayout.addWidget(cageSettingsGrp)
        cageSettingsGrp.setLayout(cageSettingsLayout)
        cageSettingsLayout.addLayout(cageLayout)
        cageLayout.addSpacerItem(QSpacerItem(215, 200, QSizePolicy.Maximum, QSizePolicy.Maximum))
        cageLayout.addWidget(cageSuffixLbl)
        cageLayout.addWidget(self.cageSuffixLine)
        cageLayout.addSpacerItem(QSpacerItem(210, 200, QSizePolicy.Maximum, QSizePolicy.Maximum))

        self.settingsTab.setLayout(settingsMainLayout)

    def meshesTabUI(self):

        meshesMainLayout = QVBoxLayout()
        meshesMainLayout.setContentsMargins(5, 5, 5, 5)
        meshesMainLayout.setSpacing(5)
        meshesMainLayout.setAlignment(Qt.AlignTop)

        meshesLayout = QVBoxLayout()
        meshesLayout.setContentsMargins(5, 5, 5, 5)
        meshesLayout.setSpacing(5)

        highDefLayout = QVBoxLayout()
        highDefLayout.setContentsMargins(5, 5, 5, 5)
        highDefLayout.setSpacing(5)

        lowDefLayout = QVBoxLayout()
        lowDefLayout.setContentsMargins(5, 5, 5, 5)
        lowDefLayout.setSpacing(5)

        # ------- Meshes List Layout ------- #

        highMeshesPathLayout = QHBoxLayout()
        highMeshesPathLayout.setContentsMargins(0, 0, 0, 0)
        highMeshesPathLayout.setSpacing(5)

        highListTopOptionsLayout = QHBoxLayout()
        highListTopOptionsLayout.setContentsMargins(0, 0, 0, 0)
        highListTopOptionsLayout.setSpacing(5)
        highListTopOptionsLayout.setAlignment(Qt.AlignLeft)

        highListLayout = QHBoxLayout()
        highListLayout.setContentsMargins(0, 0, 0, 0)
        highListLayout.setSpacing(5)
        highListLayout.setAlignment(Qt.AlignTop)

        highListBottomOptionsLayout = QHBoxLayout()
        highListBottomOptionsLayout.setContentsMargins(0, 0, 0, 0)
        highListBottomOptionsLayout.setSpacing(5)
        highListBottomOptionsLayout.setAlignment(Qt.AlignTop)

        lowListTopOptionsLayout = QHBoxLayout()
        lowListTopOptionsLayout.setContentsMargins(0, 0, 0, 0)
        lowListTopOptionsLayout.setSpacing(5)
        lowListTopOptionsLayout.setAlignment(Qt.AlignLeft)

        lowListLayout = QHBoxLayout()
        lowListLayout.setContentsMargins(0, 0, 0, 0)
        lowListLayout.setSpacing(5)
        lowListLayout.setAlignment(Qt.AlignTop)

        lowListBottomOptionsLayout = QHBoxLayout()
        lowListBottomOptionsLayout.setContentsMargins(0, 0, 0, 0)
        lowListBottomOptionsLayout.setSpacing(5)
        lowListBottomOptionsLayout.setAlignment(Qt.AlignTop)

        lowMeshesPathLayout = QHBoxLayout()
        lowMeshesPathLayout.setContentsMargins(0, 0, 0, 0)
        lowMeshesPathLayout.setSpacing(5)

        # ---------------------------------------------------------------------------------
        # ---------------------------------------------------------------------------------

        meshesListGrp = QGroupBox('Meshes List')
        highDefGrp = QGroupBox('High definition meshes')
        lowDefGrp = QGroupBox('Low definition meshes')

        highDefLbl = QLabel('High Poly Meshes Path')
        self.highDefLine = QLineEdit()
        # self.highDefLine.setText('F:\Dwarf\High Poly Models')
        self.highDefLine.setMinimumWidth(200)
        highDefSetPathBtn = QPushButton('...')

        self.highDefSelectAllBtn = QPushButton('Select All')
        self.highDefDeselectAllBtn = QPushButton('Deselect All')
        self.highDefToggleBakeBtn = QPushButton('Toggle Bake')
        self.highDefRemoveItemBtn = QPushButton('Remove Selected Items')
        self.highDefSelectAllBtn.setEnabled(False)
        self.highDefDeselectAllBtn.setEnabled(False)
        self.highDefToggleBakeBtn.setEnabled(False)
        self.highDefRemoveItemBtn.setEnabled(False)
        self.highDefRemoveItemBtn.setStyleSheet("QPushButton:enabled{background-color:rgb(165, 70, 70);}")

        highPolyList = []
        # highPolyList.append([True,'test'])
        # highPolyList.append([False, 'test2'])
        self.highMeshesTable = meshesTable(highPolyList, 'high', 0, 2)

        self.highDefUpdateBtn = QPushButton('Update High Poly Meshes')
        self.highDefClearBtn = QPushButton('Clear High Poly Meshes')
        self.highDefUpdateBtn.setEnabled(False)
        self.highDefClearBtn.setEnabled(False)

        self.lowDefSelectAllBtn = QPushButton('Select All')
        self.lowDefDeselectAllBtn = QPushButton('Deselect All')
        self.lowDefToggleBakeBtn = QPushButton('Toggle Bake')
        self.lowDefRemoveItemBtn = QPushButton('Remove Selected Items')
        self.lowDefSelectAllBtn.setEnabled(False)
        self.lowDefDeselectAllBtn.setEnabled(False)
        self.lowDefToggleBakeBtn.setEnabled(False)
        self.lowDefRemoveItemBtn.setEnabled(False)
        self.lowDefRemoveItemBtn.setStyleSheet("QPushButton:enabled{background-color:rgb(165, 70, 70);}")

        lowPolyList = []
        # lowPolyList.append([True, 'test', True, False])
        # lowPolyList.append([False, 'test2', False, True])
        self.lowMeshesTable = meshesTable(lowPolyList, 'low', 0, 4)

        self.lowDefAddSelectedBtn = QPushButton('Add selected')
        self.lowDefRemoveSelectedBtn = QPushButton('Remove selected')
        self.lowDefDetectHP = QPushButton('Detect High Poly Meshes')
        self.lowDefClearBtn = QPushButton('Clear All Meshes')
        self.lowDefAddSelectedBtn.setEnabled(False)
        self.lowDefRemoveSelectedBtn.setEnabled(False)
        self.lowDefDetectHP.setEnabled(False)
        self.lowDefClearBtn.setEnabled(False)

        lowDefLbl = QLabel('Low Poly Export Path: ')
        self.lowDefLine = QLineEdit()
        # self.lowDefLine.setText('F:\Dwarf\Low Poly Models')
        self.lowDefLine.setMinimumWidth(200)
        lowDefSetPathBtn = QPushButton('...')

        self.separateMeshesCbx = QCheckBox('Generate separated meshes maps')
        self.separateMeshesCbx.setChecked(True)

        meshesMainLayout.addWidget(meshesListGrp)

        meshesListGrp.setLayout(meshesLayout)

        meshesLayout.addWidget(highDefGrp)
        highDefGrp.setLayout(highDefLayout)
        highDefLayout.addLayout(highMeshesPathLayout)
        highDefLayout.addLayout(highListTopOptionsLayout)
        highDefLayout.addLayout(highListLayout)
        highDefLayout.addLayout(highListBottomOptionsLayout)
        highMeshesPathLayout.addSpacerItem(QSpacerItem(200, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        highMeshesPathLayout.addWidget(highDefLbl)
        highMeshesPathLayout.addWidget(self.highDefLine)
        highMeshesPathLayout.addWidget(highDefSetPathBtn)
        highMeshesPathLayout.addSpacerItem(QSpacerItem(200, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        highListTopOptionsLayout.addWidget(self.highDefSelectAllBtn)
        highListTopOptionsLayout.addWidget(self.highDefDeselectAllBtn)
        highListTopOptionsLayout.addWidget(self.highDefToggleBakeBtn)
        highListTopOptionsLayout.addWidget(self.highDefRemoveItemBtn)
        highListLayout.addWidget(self.highMeshesTable)
        highListBottomOptionsLayout.addSpacerItem(QSpacerItem(200, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        highListBottomOptionsLayout.addWidget(self.highDefUpdateBtn)
        highListBottomOptionsLayout.addWidget(self.highDefClearBtn)
        highListBottomOptionsLayout.addSpacerItem(QSpacerItem(200, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))

        meshesLayout.addWidget(lowDefGrp)
        lowDefGrp.setLayout(lowDefLayout)
        lowDefLayout.addLayout(lowListTopOptionsLayout)
        lowDefLayout.addLayout(lowListLayout)
        lowDefLayout.addLayout(lowListBottomOptionsLayout)
        lowDefLayout.addLayout(lowMeshesPathLayout)
        lowListTopOptionsLayout.addWidget(self.lowDefSelectAllBtn)
        lowListTopOptionsLayout.addWidget(self.lowDefDeselectAllBtn)
        lowListTopOptionsLayout.addWidget(self.lowDefToggleBakeBtn)
        lowListTopOptionsLayout.addWidget(self.lowDefRemoveItemBtn)
        lowListLayout.addWidget(self.lowMeshesTable)
        lowListBottomOptionsLayout.addWidget(self.lowDefAddSelectedBtn)
        lowListBottomOptionsLayout.addWidget(self.lowDefRemoveSelectedBtn)
        lowListBottomOptionsLayout.addWidget(self.lowDefDetectHP)
        lowListBottomOptionsLayout.addWidget(self.lowDefClearBtn)
        lowMeshesPathLayout.addSpacerItem(QSpacerItem(150, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        lowMeshesPathLayout.addWidget(lowDefLbl)
        lowMeshesPathLayout.addWidget(self.lowDefLine)
        lowMeshesPathLayout.addWidget(lowDefSetPathBtn)
        lowMeshesPathLayout.addSpacerItem(QSpacerItem(150, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))

        genSeparateLayout = QHBoxLayout()
        meshesLayout.addLayout(genSeparateLayout)
        genSeparateLayout.addSpacerItem(QSpacerItem(135, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        genSeparateLayout.addWidget(self.separateMeshesCbx)
        genSeparateLayout.addSpacerItem(QSpacerItem(100, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))

        self.meshesTab.setLayout(meshesMainLayout)

        # === SIGNALS === #
        highDefSetPathBtn.clicked.connect(partial(self.setPath, 'high'))
        self.highDefUpdateBtn.clicked.connect(partial(self.getModels, 'high'))
        self.highDefClearBtn.clicked.connect(partial(self.clearList, 'high'))
        self.highDefSelectAllBtn.clicked.connect(partial(self.selectAll, 'high'))
        self.highDefDeselectAllBtn.clicked.connect(partial(self.clearSelection, 'high'))
        self.highDefRemoveItemBtn.clicked.connect(partial(self.removeSelectedItems, 'high'))
        self.highDefToggleBakeBtn.clicked.connect(partial(self.toggleBake, 'high'))
        self.highMeshesTable.itemSelectionChanged.connect(self._updateState)

        lowDefSetPathBtn.clicked.connect(partial(self.setPath, 'low'))
        self.lowDefAddSelectedBtn.clicked.connect(partial(self.getModels, 'low'))
        self.lowDefClearBtn.clicked.connect(partial(self.clearList, 'low'))
        self.lowDefSelectAllBtn.clicked.connect(partial(self.selectAll, 'low'))
        self.lowDefDeselectAllBtn.clicked.connect(partial(self.clearSelection, 'low'))
        self.lowDefRemoveItemBtn.clicked.connect(partial(self.removeSelectedItems, 'low'))
        self.lowDefToggleBakeBtn.clicked.connect(partial(self.toggleBake, 'low'))
        self.lowDefDetectHP.clicked.connect(self.detectHP)
        self.lowMeshesTable.itemSelectionChanged.connect(self._updateState)

    def mapsTabUI(self):

        mapsMainLayout = QVBoxLayout()
        mapsMainLayout.setContentsMargins(5, 5, 5, 5)
        mapsMainLayout.setSpacing(5)
        mapsMainLayout.setAlignment(Qt.AlignTop)

        mapsLayout = QVBoxLayout()
        mapsLayout.setContentsMargins(5, 5, 5, 5)
        mapsLayout.setSpacing(5)

        mapsSettingsLayout = QVBoxLayout()
        mapsSettingsLayout.setContentsMargins(5, 5, 5, 5)
        mapsSettingsLayout.setSpacing(5)
        mapsSettingsLayout.setAlignment(Qt.AlignTop)

        self.mapsScrollArea = QScrollArea()
        self.mapsScrollArea.setFocusPolicy(Qt.NoFocus)
        self.mapsScrollArea.setWidgetResizable(True)
        self.mapsScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.mapsScrollArea.setContentsMargins(5,5,5,5)

        self.mapsSettingsScrollArea = QScrollArea()
        self.mapsSettingsScrollArea.setFocusPolicy(Qt.NoFocus)
        self.mapsSettingsScrollArea.setWidgetResizable(True)
        self.mapsSettingsScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.mapsSettingsScrollArea.setContentsMargins(5, 5, 5, 5)
        self.mapsSettingsScrollArea.setStyleSheet('background-color: rgb(70, 70, 70)')

        # ------- Maps Settings Layout ------- #
        buttonsLayout = QHBoxLayout()
        buttonsLayout.setContentsMargins(5, 5, 5, 5)
        buttonsLayout.setSpacing(5)
        normalMapLayout = QHBoxLayout()
        normalMapLayout.setContentsMargins(5, 5, 5, 5)
        normalMapLayout.setSpacing(5)
        heightMapLayout = QHBoxLayout()
        heightMapLayout.setContentsMargins(5, 5, 5, 5)
        heightMapLayout.setSpacing(5)
        bakeBaseTextureLayout = QHBoxLayout()
        bakeBaseTextureLayout.setContentsMargins(5, 5, 5, 5)
        bakeBaseTextureLayout.setSpacing(5)
        aoMapLayout = QHBoxLayout()
        aoMapLayout.setContentsMargins(5, 5, 5, 5)
        aoMapLayout.setSpacing(5)
        bentNormalMapLayout = QHBoxLayout()
        bentNormalMapLayout.setContentsMargins(5, 5, 5, 5)
        bentNormalMapLayout.setSpacing(5)
        prtPnLayout = QHBoxLayout()
        prtPnLayout.setContentsMargins(5, 5, 5, 5)
        prtPnLayout.setSpacing(5)
        convexityMapLayout = QHBoxLayout()
        convexityMapLayout.setContentsMargins(5, 5, 5, 5)
        convexityMapLayout.setSpacing(5)
        thicknessMapLayout = QHBoxLayout()
        thicknessMapLayout.setContentsMargins(5, 5, 5, 5)
        thicknessMapLayout.setSpacing(5)
        proximityLayout = QHBoxLayout()
        proximityLayout.setContentsMargins(5, 5, 5, 5)
        proximityLayout.setSpacing(5)
        cavityMapLayout = QHBoxLayout()
        cavityMapLayout.setContentsMargins(5, 5, 5, 5)
        cavityMapLayout.setSpacing(5)
        wireAndRayFailsLayout = QHBoxLayout()
        wireAndRayFailsLayout.setContentsMargins(5, 5, 5, 5)
        wireAndRayFailsLayout.setSpacing(5)
        directionLayout = QHBoxLayout()
        directionLayout.setContentsMargins(5, 5, 5, 5)
        directionLayout.setSpacing(5)
        radiosityLayout = QHBoxLayout()
        radiosityLayout.setContentsMargins(5, 5, 5, 5)
        radiosityLayout.setSpacing(5)
        bakeHPColorMapLayout = QHBoxLayout()
        bakeHPColorMapLayout.setContentsMargins(5, 5, 5, 5)
        bakeHPColorMapLayout.setSpacing(5)
        curvatureMapLayout = QHBoxLayout()
        curvatureMapLayout.setContentsMargins(5, 5, 5, 5)
        curvatureMapLayout.setSpacing(5)
        translucencyMapLayout = QHBoxLayout()
        translucencyMapLayout.setContentsMargins(5, 5, 5, 5)
        translucencyMapLayout.setSpacing(5)
        derivativeMapLayout = QHBoxLayout()
        derivativeMapLayout.setContentsMargins(5, 5, 5, 5)
        derivativeMapLayout.setSpacing(5)

        normalSettingsLayout = QVBoxLayout()
        normalSettingsLayout.setContentsMargins(5, 5, 5, 5)
        normalSettingsLayout.setSpacing(5)
        normalSwizzleLayout = QHBoxLayout()
        normalSwizzleLayout.setContentsMargins(5, 5, 5, 5)
        normalSwizzleLayout.setSpacing(5)
        normalTSLayout = QHBoxLayout()
        normalTSLayout.setContentsMargins(5, 5, 5, 5)
        normalTSLayout.setSpacing(5)
        normalBgColorLayout = QHBoxLayout()
        normalBgColorLayout.setContentsMargins(5, 5, 5, 5)
        normalBgColorLayout.setSpacing(5)
        normalDefLayout = QHBoxLayout()
        normalDefLayout.setContentsMargins(5, 5, 5, 5)
        normalDefLayout.setSpacing(5)

        heightSettingsLayout = QVBoxLayout()
        heightSettingsLayout.setContentsMargins(5, 5, 5, 5)
        heightSettingsLayout.setSpacing(5)
        heightBgColorLayout = QHBoxLayout()
        heightBgColorLayout.setContentsMargins(5, 5, 5, 5)
        heightBgColorLayout.setSpacing(5)
        heightNormalizationLayout = QHBoxLayout()
        heightNormalizationLayout.setContentsMargins(5, 5, 5, 5)
        heightNormalizationLayout.setSpacing(5)
        heightNormalNormLayout = QHBoxLayout()
        heightNormalNormLayout.setContentsMargins(5, 5, 5, 5)
        heightNormalNormLayout.setSpacing(5)

        bakeBaseSettingsLayout = QVBoxLayout()
        bakeBaseSettingsLayout.setContentsMargins(5, 5, 5, 5)
        bakeBaseSettingsLayout.setSpacing(5)
        bakeBaseTextureDrawColorLayout = QHBoxLayout()
        bakeBaseTextureDrawColorLayout.setContentsMargins(5, 5, 5, 5)
        bakeBaseTextureDrawColorLayout.setSpacing(5)
        bakeBaseBgColorLayout = QHBoxLayout()
        bakeBaseBgColorLayout.setContentsMargins(5, 5, 5, 5)
        bakeBaseBgColorLayout.setSpacing(5)

        aoBaseSettingsLayout = QVBoxLayout()
        aoBaseSettingsLayout.setContentsMargins(5, 5, 5, 5)
        aoBaseSettingsLayout.setSpacing(5)
        aoRaysLayout = QHBoxLayout()
        aoRaysLayout.setContentsMargins(5, 5, 5, 5)
        aoRaysLayout.setSpacing(5)
        aoDistributionLayout = QHBoxLayout()
        aoDistributionLayout.setContentsMargins(5,5,5,5)
        aoDistributionLayout.setSpacing(5)
        aoOccUnoccColorLayout = QHBoxLayout()
        aoOccUnoccColorLayout.setContentsMargins(5, 5, 5, 5)
        aoOccUnoccColorLayout.setSpacing(5)
        aoOccludedColorLayout = QHBoxLayout()
        aoOccludedColorLayout.setContentsMargins(5, 5, 5, 5)
        aoOccludedColorLayout.setSpacing(5)
        aoUnoccludedColorLayout = QHBoxLayout()
        aoUnoccludedColorLayout.setContentsMargins(5, 5, 5, 5)
        aoUnoccludedColorLayout.setSpacing(5)
        aoBiasSpreadLayout = QHBoxLayout()
        aoBiasSpreadLayout.setContentsMargins(5, 5, 5, 5)
        aoBiasSpreadLayout.setSpacing(5)
        aoBiasLayout = QVBoxLayout()
        aoBiasLayout.setContentsMargins(5, 5, 5, 5)
        aoBiasLayout.setSpacing(5)
        aoSpreadAngleLayout = QHBoxLayout()
        aoSpreadAngleLayout.setContentsMargins(5, 5, 5, 5)
        aoSpreadAngleLayout.setSpacing(5)
        aoAttenuationLayout = QHBoxLayout()
        aoAttenuationLayout.setContentsMargins(5, 5, 5, 5)
        aoAttenuationLayout.setSpacing(5)
        aoJitterBackfaceLayout = QHBoxLayout()
        aoJitterBackfaceLayout.setContentsMargins(5, 5, 5, 5)
        aoJitterBackfaceLayout.setSpacing(5)
        ao100OccLayout = QHBoxLayout()
        ao100OccLayout.setContentsMargins(5, 5, 5, 5)
        ao100OccLayout.setSpacing(5)
        aoBgColorLayout = QHBoxLayout()
        aoBgColorLayout.setContentsMargins(5, 5, 5, 5)
        aoBgColorLayout.setSpacing(5)

        bentNormalSettingsLayout = QVBoxLayout()
        bentNormalSettingsLayout.setContentsMargins(5, 5, 5, 5)
        bentNormalSettingsLayout.setSpacing(5)
        bentNormalRaysLayout = QHBoxLayout()
        bentNormalRaysLayout.setContentsMargins(5, 5, 5, 5)
        bentNormalRaysLayout.setSpacing(5)
        bentBiasSpreadLayout = QHBoxLayout()
        bentBiasSpreadLayout.setContentsMargins(5, 5, 5, 5)
        bentBiasSpreadLayout.setSpacing(5)
        bentBiasLayout = QHBoxLayout()
        bentBiasLayout.setContentsMargins(5, 5, 5, 5)
        bentBiasLayout.setSpacing(5)
        bentSpreadLayout = QHBoxLayout()
        bentSpreadLayout.setContentsMargins(5, 5, 5, 5)
        bentSpreadLayout.setSpacing(5)
        bentLimitJitterLayout = QHBoxLayout()
        bentLimitJitterLayout.setContentsMargins(5, 5, 5, 5)
        bentLimitJitterLayout.setSpacing(5)
        bentSwizzleLayout = QHBoxLayout()
        bentSwizzleLayout.setContentsMargins(5, 5, 5, 5)
        bentSwizzleLayout.setSpacing(5)
        bentTSLayout = QHBoxLayout()
        bentTSLayout.setContentsMargins(5, 5, 5, 5)
        bentTSLayout.setSpacing(5)
        bentDistributionLayout = QHBoxLayout()
        bentDistributionLayout.setContentsMargins(5, 5, 5, 5)
        bentDistributionLayout.setSpacing(5)
        bentBgColorLayout = QHBoxLayout()
        bentBgColorLayout.setContentsMargins(5, 5, 5, 5)
        bentBgColorLayout.setSpacing(5)

        prtSettingsLayout = QVBoxLayout()
        prtSettingsLayout.setContentsMargins(5, 5, 5, 5)
        prtSettingsLayout.setSpacing(5)
        prtRaysLayout = QHBoxLayout()
        prtRaysLayout.setContentsMargins(5, 5, 5, 5)
        prtRaysLayout.setSpacing(5)
        prtBiasSpreadLayout = QHBoxLayout()
        prtBiasSpreadLayout.setContentsMargins(5, 5, 5, 5)
        prtBiasSpreadLayout.setSpacing(5)
        prtBiasLayout = QHBoxLayout()
        prtBiasLayout.setContentsMargins(5, 5, 5, 5)
        prtBiasLayout.setSpacing(5)
        prtSpreadAngleLayout = QHBoxLayout()
        prtSpreadAngleLayout.setContentsMargins(5, 5, 5, 5)
        prtSpreadAngleLayout.setSpacing(5)
        prtLimitRayLayout = QHBoxLayout()
        prtLimitRayLayout.setContentsMargins(5, 5, 5, 5)
        prtLimitRayLayout.setSpacing(5)
        prtColorNormLayout = QHBoxLayout()
        prtColorNormLayout.setContentsMargins(5, 5, 5, 5)
        prtColorNormLayout.setSpacing(5)
        prtThresholdLayout = QHBoxLayout()
        prtThresholdLayout.setContentsMargins(5, 5, 5, 5)
        prtThresholdLayout.setSpacing(5)
        prtBgColorLayout = QHBoxLayout()
        prtBgColorLayout.setContentsMargins(5, 5, 5, 5)
        prtBgColorLayout.setSpacing(5)

        convexitySettingsLayout = QVBoxLayout()
        convexitySettingsLayout.setContentsMargins(5, 5, 5, 5)
        convexitySettingsLayout.setSpacing(5)
        convexityScaleLayout = QHBoxLayout()
        convexityScaleLayout.setContentsMargins(5, 5, 5, 5)
        convexityScaleLayout.setSpacing(5)
        convexityBgColorLayout = QHBoxLayout()
        convexityBgColorLayout.setContentsMargins(5, 5, 5, 5)
        convexityBgColorLayout.setSpacing(5)

        proximitySettingsLayout = QVBoxLayout()
        proximitySettingsLayout.setContentsMargins(5, 5, 5, 5)
        proximitySettingsLayout.setSpacing(5)
        proximityRaysSpreadLayout = QHBoxLayout()
        proximityRaysSpreadLayout.setContentsMargins(5, 5, 5, 5)
        proximityRaysSpreadLayout.setSpacing(5)
        proximityRaysLayout = QHBoxLayout()
        proximityRaysLayout.setContentsMargins(5, 5, 5, 5)
        proximityRaysLayout.setSpacing(5)
        proxmitySpreadAngleLayout = QHBoxLayout()
        proxmitySpreadAngleLayout.setContentsMargins(5, 5, 5, 5)
        proxmitySpreadAngleLayout.setSpacing(5)
        proximityLimitRadyDstLayout = QHBoxLayout()
        proximityLimitRadyDstLayout.setContentsMargins(5, 5, 5, 5)
        proximityLimitRadyDstLayout.setSpacing(5)
        proximityBgColorLayout = QHBoxLayout()
        proximityBgColorLayout.setContentsMargins(5, 5, 5, 5)
        proximityBgColorLayout.setSpacing(5)

        cavitySettingsLayout = QVBoxLayout()
        cavitySettingsLayout.setContentsMargins(5, 5, 5, 5)
        cavitySettingsLayout.setSpacing(5)
        cavityRaysJitterLayout = QHBoxLayout()
        cavityRaysJitterLayout.setContentsMargins(5, 5, 5, 5)
        cavityRaysJitterLayout.setSpacing(5)
        cavityRaysLayout = QHBoxLayout()
        cavityRaysLayout.setContentsMargins(5, 5, 5, 5)
        cavityRaysLayout.setSpacing(5)
        cavityJitterLayout = QHBoxLayout()
        cavityJitterLayout.setContentsMargins(5, 5, 5, 5)
        cavityJitterLayout.setSpacing(5)
        cavityRadiusLayout = QHBoxLayout()
        cavityRadiusLayout.setContentsMargins(5, 5, 5, 5)
        cavityRadiusLayout.setSpacing(5)
        cavityContrastLayout = QHBoxLayout()
        cavityContrastLayout.setContentsMargins(5, 5, 5, 5)
        cavityContrastLayout.setSpacing(5)
        cavityStepsLayout = QHBoxLayout()
        cavityStepsLayout.setContentsMargins(5, 5, 5, 5)
        cavityStepsLayout.setSpacing(5)
        cavityBgColorLayout = QHBoxLayout()
        cavityBgColorLayout.setContentsMargins(5, 5, 5, 5)
        cavityBgColorLayout.setSpacing(5)

        wireSettingsLayout = QVBoxLayout()
        wireSettingsLayout.setContentsMargins(5, 5, 5, 5)
        wireSettingsLayout.setSpacing(5)
        wireColorCWSeamLayout = QHBoxLayout()
        wireColorCWSeamLayout.setContentsMargins(5, 5, 5, 5)
        wireColorCWSeamLayout.setSpacing(5)
        wireColorLayout = QHBoxLayout()
        wireColorLayout.setContentsMargins(5, 5, 5, 5)
        wireColorLayout.setSpacing(5)
        wireCWLayout = QHBoxLayout()
        wireCWLayout.setContentsMargins(5, 5, 5, 5)
        wireCWLayout.setSpacing(5)
        wireSeamLayout = QHBoxLayout()
        wireSeamLayout.setContentsMargins(5, 5, 5, 5)
        wireSeamLayout.setSpacing(5)
        wireRenderRayFailsLayout = QHBoxLayout()
        wireRenderRayFailsLayout.setContentsMargins(5, 5, 5, 5)
        wireRenderRayFailsLayout.setSpacing(5)
        wireColorRayFailLayout = QHBoxLayout()
        wireColorRayFailLayout.setContentsMargins(5, 5, 5, 5)
        wireColorRayFailLayout.setSpacing(5)
        wireBgColorLayout = QHBoxLayout()
        wireBgColorLayout.setContentsMargins(5, 5, 5, 5)
        wireBgColorLayout.setSpacing(5)

        directionSettingsLayout = QVBoxLayout()
        directionSettingsLayout.setContentsMargins(5, 5, 5, 5)
        directionSettingsLayout.setSpacing(5)
        directionSwizzleLayout = QHBoxLayout()
        directionSwizzleLayout.setContentsMargins(5, 5, 5, 5)
        directionSwizzleLayout.setSpacing(5)
        directionTSLayout = QHBoxLayout()
        directionTSLayout.setContentsMargins(5, 5, 5, 5)
        directionTSLayout.setSpacing(5)
        directionBgColorLayout = QHBoxLayout()
        directionBgColorLayout.setContentsMargins(5, 5, 5, 5)
        directionBgColorLayout.setSpacing(5)
        directionNormLayout = QHBoxLayout()
        directionNormLayout.setContentsMargins(5, 5, 5, 5)
        directionNormLayout.setSpacing(5)

        radiositySettingsLayout = QVBoxLayout()
        radiositySettingsLayout.setContentsMargins(5, 5, 5, 5)
        radiositySettingsLayout.setSpacing(5)
        radiosityRaysLayout = QHBoxLayout()
        radiosityRaysLayout.setContentsMargins(5, 5, 5, 5)
        radiosityRaysLayout.setSpacing(5)
        radiosityDistributionLayout = QHBoxLayout()
        radiosityDistributionLayout.setContentsMargins(5, 5, 5, 5)
        radiosityDistributionLayout.setSpacing(5)
        radiosityBiasSpreadLayout = QHBoxLayout()
        radiosityBiasSpreadLayout.setContentsMargins(5, 5, 5, 5)
        radiosityBiasSpreadLayout.setSpacing(5)
        radiosityBiasLayout = QHBoxLayout()
        radiosityBiasLayout.setContentsMargins(5, 5, 5, 5)
        radiosityBiasLayout.setSpacing(5)
        radiositySpreadAngleLayout = QHBoxLayout()
        radiositySpreadAngleLayout.setContentsMargins(5, 5, 5, 5)
        radiositySpreadAngleLayout.setSpacing(5)
        radiosityLimitRayJitterLayout = QHBoxLayout()
        radiosityLimitRayJitterLayout.setContentsMargins(5, 5, 5, 5)
        radiosityLimitRayJitterLayout.setSpacing(5)
        radiosityAttenuationLayout = QHBoxLayout()
        radiosityAttenuationLayout.setContentsMargins(5, 5, 5, 5)
        radiosityAttenuationLayout.setSpacing(5)
        radiosityCoordinateLayout = QHBoxLayout()
        radiosityCoordinateLayout.setContentsMargins(5, 5, 5, 5)
        radiosityCoordinateLayout.setSpacing(5)
        radiosityContrastPureOccLayout = QHBoxLayout()
        radiosityContrastPureOccLayout.setContentsMargins(5, 5, 5, 5)
        radiosityContrastPureOccLayout.setSpacing(5)
        radiosityContrastLayout = QHBoxLayout()
        radiosityContrastLayout.setContentsMargins(5, 5, 5, 5)
        radiosityContrastLayout.setSpacing(5)
        radiosityPureOccLayout = QHBoxLayout()
        radiosityPureOccLayout.setContentsMargins(5, 5, 5, 5)
        radiosityPureOccLayout.setSpacing(5)
        radiosityBgColorLayout = QHBoxLayout()
        radiosityBgColorLayout.setContentsMargins(5, 5, 5, 5)
        radiosityBgColorLayout.setSpacing(5)

        bakeHPColorsSettingsLayout = QVBoxLayout()
        bakeHPColorsSettingsLayout.setContentsMargins(5, 5, 5, 5)
        bakeHPColorsSettingsLayout.setSpacing(5)
        bakeHPColorsBgLayout = QHBoxLayout()
        bakeHPColorsBgLayout.setContentsMargins(5, 5, 5, 5)
        bakeHPColorsBgLayout.setSpacing(5)

        curvatureSettingsLayout = QVBoxLayout()
        curvatureSettingsLayout.setContentsMargins(5, 5, 5, 5)
        curvatureSettingsLayout.setSpacing(5)
        curvatureRaysJitterLayout = QHBoxLayout()
        curvatureRaysJitterLayout.setContentsMargins(5, 5, 5, 5)
        curvatureRaysJitterLayout.setSpacing(5)
        curvatureSpreadBiasLayout = QHBoxLayout()
        curvatureSpreadBiasLayout.setContentsMargins(5, 5, 5, 5)
        curvatureSpreadBiasLayout.setSpacing(5)
        curvatureSpreadLayout = QHBoxLayout()
        curvatureSpreadLayout.setContentsMargins(5, 5, 5, 5)
        curvatureSpreadLayout.setSpacing(5)
        curvatureBiasLayout = QHBoxLayout()
        curvatureBiasLayout.setContentsMargins(5, 5, 5, 5)
        curvatureBiasLayout.setSpacing(5)
        curvatureAlgorithmLayout = QHBoxLayout()
        curvatureAlgorithmLayout.setContentsMargins(5, 5, 5, 5)
        curvatureAlgorithmLayout.setSpacing(5)
        curvatureDistributionLayout = QHBoxLayout()
        curvatureDistributionLayout.setContentsMargins(5, 5, 5, 5)
        curvatureDistributionLayout.setSpacing(5)
        curvatureSearchDstLayout = QHBoxLayout()
        curvatureSearchDstLayout.setContentsMargins(5, 5, 5, 5)
        curvatureSearchDstLayout.setSpacing(5)
        curvatureToneMappLayout = QHBoxLayout()
        curvatureToneMappLayout.setContentsMargins(5, 5, 5, 5)
        curvatureToneMappLayout.setSpacing(5)
        curvatureBgColorLayout = QHBoxLayout()
        curvatureBgColorLayout.setContentsMargins(5, 5, 5, 5)
        curvatureBgColorLayout.setSpacing(5)

        translucencySettingsLayout = QVBoxLayout()
        translucencySettingsLayout.setContentsMargins(5, 5, 5, 5)
        translucencySettingsLayout.setSpacing(5)
        translucencyRaysLayout = QHBoxLayout()
        translucencyRaysLayout.setContentsMargins(5, 5, 5, 5)
        translucencyRaysLayout.setSpacing(5)
        translucencyDistributionLayout = QHBoxLayout()
        translucencyDistributionLayout.setContentsMargins(5, 5, 5, 5)
        translucencyDistributionLayout.setSpacing(5)
        translucencyBiasAngleLayout = QHBoxLayout()
        translucencyBiasAngleLayout.setContentsMargins(5, 5, 5, 5)
        translucencyBiasAngleLayout.setSpacing(5)
        translucencyBiasLayout = QHBoxLayout()
        translucencyBiasLayout.setContentsMargins(5, 5, 5, 5)
        translucencyBiasLayout.setSpacing(5)
        translucencyAngleLayout = QHBoxLayout()
        translucencyAngleLayout.setContentsMargins(5, 5, 5, 5)
        translucencyAngleLayout.setSpacing(5)
        translucencyJitterSearchDstLayout = QHBoxLayout()
        translucencyJitterSearchDstLayout.setContentsMargins(5, 5, 5, 5)
        translucencyJitterSearchDstLayout.setSpacing(5)
        translucencyJitterLayout = QHBoxLayout()
        translucencyJitterLayout.setContentsMargins(5, 5, 5, 5)
        translucencyJitterLayout.setSpacing(5)
        translucencySearchDstLayout = QHBoxLayout()
        translucencySearchDstLayout.setContentsMargins(5, 5, 5, 5)
        translucencySearchDstLayout.setSpacing(5)
        translucencyBgColorLayout = QHBoxLayout()
        translucencyBgColorLayout.setContentsMargins(5, 5, 5, 5)
        translucencyBgColorLayout.setSpacing(5)

        derivativeSettingsLayout = QVBoxLayout()
        derivativeSettingsLayout.setContentsMargins(5, 5, 5, 5)
        derivativeSettingsLayout.setSpacing(5)
        derivativeBgColorLayout = QHBoxLayout()
        derivativeBgColorLayout.setContentsMargins(5, 5, 5, 5)
        derivativeBgColorLayout.setSpacing(5)

        # ---------------------------------------------------------------------------------
        # ---------------------------------------------------------------------------------

        mapsGrp = QGroupBox('Maps to render')
        mapsSettingsGrp = QGroupBox('Maps Settings')
        mapsSettingsGrp.setContentsMargins(5,5,5,5)
        mapsSettingsGrp.setFlat(True)
        self.normalMapSettingsGrp = QGroupBox('Normal map Settings')
        self.heightMapSettingsGrp = QGroupBox('Height map Settings')
        self.bakeBaseTextureSettingsGrp = QGroupBox('Bake Base map Settings')
        self.aoMapSettingsGrp = QGroupBox('Ambient occlusion map Settings')
        self.bentNormalMapSettingsGrp = QGroupBox('Bent Normal map Settings')
        self.prtPnMapSettingsGrp = QGroupBox('PRTpn map Settings')
        self.convexityMapSettingsGrp = QGroupBox('Convexity map Settings')
        self.thicknessMapSettingsGrp = QGroupBox('Thickness map Settings')
        self.proximityMapSettingsGrp = QGroupBox('Proximity map Settings')
        self.cavityMapSettingsGrp = QGroupBox('Cavity map Settings')
        self.wireframeAndRayFailsGrp = QGroupBox('Wireframe and Ray Fails map Settings')
        self.directionMapSettingsGrp = QGroupBox('Direction map Settings')
        self.radiosityMapSettingsGrp = QGroupBox('Radiosity Normal map Settings')
        self.bakeHPSettingsGrp = QGroupBox("Bake highpoly's vertex colors Settings")
        self.curvatureSettingsGrp = QGroupBox('Curvature map Settings')
        self.translucencyMapSettingsGrp = QGroupBox('Translucency map Settings')
        self.derivativeMapSettingsGrp = QGroupBox('Derivative map Settings')
        self.normalMapSettingsGrp.setVisible(False)
        self.heightMapSettingsGrp.setVisible(False)
        self.bakeBaseTextureSettingsGrp.setVisible(False)
        self.aoMapSettingsGrp.setVisible(False)
        self.bentNormalMapSettingsGrp.setVisible(False)
        self.prtPnMapSettingsGrp.setVisible(False)
        self.convexityMapSettingsGrp.setVisible(False)
        self.thicknessMapSettingsGrp.setVisible(False)
        self.proximityMapSettingsGrp.setVisible(False)
        self.cavityMapSettingsGrp.setVisible(False)
        self.wireframeAndRayFailsGrp.setVisible(False)
        self.directionMapSettingsGrp.setVisible(False)
        self.bakeHPSettingsGrp.setVisible(False)
        self.curvatureSettingsGrp.setVisible(False)
        self.translucencyMapSettingsGrp.setVisible(False)
        self.derivativeMapSettingsGrp.setVisible(False)
        self.radiosityMapSettingsGrp.setVisible(False)

        elems = []

        selectAllMapsBtn = QPushButton('Select All')
        clearAllMapsBtn = QPushButton('Clear All')

        self.normalMapCbx = QCheckBox('Normal map')
        normalMapBtn = QPushButton('...')
        normalMapBtn.setMaximumWidth(40)
        normalMapBtn.setCheckable(True)
        self.normalMapCbx.setChecked(True)

        self.heightMapCbx = QCheckBox('Height map')
        heightMapBtn = QPushButton('...')
        heightMapBtn.setMaximumWidth(40)
        heightMapBtn.setCheckable(True)

        self.bakeBaseTextureMapCbx = QCheckBox('Bake Base Texture map')
        bakeBaseTextureMapBtn = QPushButton('...')
        bakeBaseTextureMapBtn.setMaximumWidth(40)
        bakeBaseTextureMapBtn.setCheckable(True)
        bakeBaseTextureMapBtn.setEnabled(False)
        elems.append(self.bakeBaseTextureMapCbx)
        elems.append(bakeBaseTextureMapBtn)

        self.aoMapCbx = QCheckBox('Ambient occlusion map')
        aoMapBtn = QPushButton('...')
        aoMapBtn.setMaximumWidth(40)
        aoMapBtn.setCheckable(True)

        self.bentNormalMapCbx = QCheckBox('Bent Normal map')
        bentNormaMapBtn = QPushButton('...')
        bentNormaMapBtn.setMaximumWidth(40)
        bentNormaMapBtn.setCheckable(True)
        bentNormaMapBtn.setEnabled(False)
        elems.append(self.bentNormalMapCbx)
        elems.append(bentNormaMapBtn)

        self.prtPnMapCbx = QCheckBox('PRTpn map')
        prtPnMapBtn = QPushButton('...')
        prtPnMapBtn.setMaximumWidth(40)
        prtPnMapBtn.setCheckable(True)
        prtPnMapBtn.setEnabled(False)
        elems.append(self.prtPnMapCbx)
        elems.append(prtPnMapBtn)

        self.convexityMapCbx = QCheckBox('Convexity map')
        convexityMapBtn = QPushButton('...')
        convexityMapBtn.setMaximumWidth(40)
        convexityMapBtn.setCheckable(True)
        elems.append(self.convexityMapCbx)
        elems.append(convexityMapBtn)

        self.thicknessMapCbx = QCheckBox('Thickness map')
        thicknessMapBtn = QPushButton('...')
        thicknessMapBtn.setMaximumWidth(40)
        thicknessMapBtn.setCheckable(True)
        thicknessMapBtn.setEnabled(False)
        elems.append(self.thicknessMapCbx)
        elems.append(thicknessMapBtn)

        self.proximityMapCbx = QCheckBox('Proximity map')
        proximityMapBtn = QPushButton('...')
        proximityMapBtn.setMaximumWidth(40)
        proximityMapBtn.setCheckable(True)
        proximityMapBtn.setEnabled(False)
        elems.append(self.proximityMapCbx)
        elems.append(proximityMapBtn)

        self.cavityMapCbx = QCheckBox('Cavity map')
        cavityMapBtn = QPushButton('...')
        cavityMapBtn.setMaximumWidth(40)
        cavityMapBtn.setCheckable(True)
        cavityMapBtn.setEnabled(False)
        elems.append(self.cavityMapCbx)
        elems.append(cavityMapBtn)

        self.wireframeAndRayFailsMapCbx = QCheckBox("Wireframe and Ray Fails map")
        wireframeAndRayFailsMapBtn = QPushButton('...')
        wireframeAndRayFailsMapBtn.setMaximumWidth(40)
        wireframeAndRayFailsMapBtn.setCheckable(True)
        wireframeAndRayFailsMapBtn.setEnabled(False)
        elems.append(self.wireframeAndRayFailsMapCbx)
        elems.append(wireframeAndRayFailsMapBtn)

        self.directionMapCbx = QCheckBox('Direction map')
        directionMapBtn = QPushButton('...')
        directionMapBtn.setMaximumWidth(40)
        directionMapBtn.setCheckable(True)
        directionMapBtn.setEnabled(False)
        elems.append(self.directionMapCbx)
        elems.append(directionMapBtn)

        self.radiosityMapCbx = QCheckBox('Radiosity Normal map')
        radiosityMapBtn = QPushButton('...')
        radiosityMapBtn.setMaximumWidth(40)
        radiosityMapBtn.setCheckable(True)
        radiosityMapBtn.setEnabled(False)
        elems.append(self.radiosityMapCbx)
        elems.append(radiosityMapBtn)

        self.bakeHPColorMapCbx = QCheckBox("Bake highpoly's vertex colors")
        bakeHPColorMapBtn = QPushButton('...')
        bakeHPColorMapBtn.setMaximumWidth(40)
        bakeHPColorMapBtn.setCheckable(True)
        bakeHPColorMapBtn.setEnabled(False)
        elems.append(self.bakeHPColorMapCbx)
        elems.append(bakeHPColorMapBtn)

        self.curvatureMapCbx = QCheckBox('Curvature map')
        curvatureMapBtn = QPushButton('...')
        curvatureMapBtn.setMaximumWidth(40)
        curvatureMapBtn.setCheckable(True)
        curvatureMapBtn.setEnabled(False)
        elems.append(self.curvatureMapCbx)
        elems.append(curvatureMapBtn)

        self.translucencyMapCbx = QCheckBox('Translucency map')
        translucencyMapBtn = QPushButton('...')
        translucencyMapBtn.setMaximumWidth(40)
        translucencyMapBtn.setCheckable(True)
        translucencyMapBtn.setEnabled(False)
        elems.append(self.translucencyMapCbx)
        elems.append(translucencyMapBtn)

        self.derivativeMapCbx = QCheckBox('Derivative map')
        derivativeMapBtn = QPushButton('...')
        derivativeMapBtn.setMaximumWidth(40)
        derivativeMapBtn.setCheckable(True)
        derivativeMapBtn.setEnabled(False)
        elems.append(self.derivativeMapCbx)
        elems.append(derivativeMapBtn)
        #
        # for elem in elems:
        #     elem.setEnabled(False)

        # -----------------------------------------------------------------------

        normalSwizzleLbl = QLabel('Swizzle Coordinates: ')
        self.normalSwizzleXCmb = QComboBox()
        self.normalSwizzleYCmb = QComboBox()
        self.normalSwizzleZCmb = QComboBox()
        for axis in ['X', 'Y', 'Z']:
            for sign in ['+', '-']:
                self.normalSwizzleXCmb.addItem(axis + sign)
                self.normalSwizzleYCmb.addItem(axis + sign)
                self.normalSwizzleZCmb.addItem(axis + sign)
        self.normalTSCbx = QCheckBox('Tangent Space')
        normalBgColorLbl = QLabel('Background Color')
        self.normalBgColor = QColorLabel()
        normalDefBtn = QPushButton('Defaults')

        heightBgColorLbl = QLabel('Background Color')
        self.heightBgColor = QColorLabel()
        heightNormalizationLbl = QLabel('Normalization')
        self.heightNormalizationCmb = QComboBox()
        for norm in ['Interactive', 'Manual', 'Raw FP Values']:
            self.heightNormalizationCmb.addItem(norm)
        heightManualMinLbl = QLabel('Min: ')
        self.heightManualMinSpinner = QDoubleSpinBox()
        self.heightManualMinSpinner.setRange(-100000000, 100000000)
        self.heightManualMinSpinner.setDecimals(6)
        self.heightManualMinSpinner.setLocale(QLocale.English)
        heightManualMaxLbl = QLabel('Max: ')
        self.heightManualMaxSpinner = QDoubleSpinBox()
        self.heightManualMaxSpinner.setRange(-100000000, 100000000)
        self.heightManualMaxSpinner.setDecimals(6)
        self.heightManualMaxSpinner.setLocale(QLocale.English)
        heightDefBtn = QPushButton('Defaults')

        self.bakeBaseWriteObjIDCbx = QCheckBox('Write ObjectID if no texture')
        self.bakeBaseDrawColorCbx = QCheckBox('Draw using this color')
        self.bakeBaseDrawColor = QColorLabel()
        bakeBaseBgColorLbl = QLabel('Background color')
        self.bakeBaseBgColor = QColorLabel()
        bakeBaseDefBtn = QPushButton('Defaults')

        aoRaysLbl = QLabel('Rays')
        self.aoRaysSpinner = QSpinBox()
        self.aoRaysSpinner.setRange(0, 1000000)
        self.aoRaysSpinner.setLocale(QLocale.English)
        aoDistributionLbl = QLabel('Distribution')
        self.aoDistributionCmb = QComboBox()
        for dist in ['Uniform', 'Cosine', 'CosineSq']:
            self.aoDistributionCmb.addItem(dist)
        aoOccludedColorLbl = QLabel('Occluded color')
        self.aoOccludedColor = QColorLabel()
        aoUnoccludedColorLbl = QLabel('Unoccluded color')
        self.aoUnoccludedColor = QColorLabel()
        self.aoUnoccludedColor.setStyleSheet('background-color:rgb(255, 255, 255);')
        aoBiasLbl = QLabel('Bias')
        self.aoBiasSpinner = QDoubleSpinBox()
        self.aoBiasSpinner.setRange(0, 1)
        self.aoBiasSpinner.setDecimals(6)
        self.aoBiasSpinner.setLocale(QLocale.English)
        aoSpreadAngleLbl = QLabel('Spread Angle')
        self.aoSpreadAngleSpinner = QDoubleSpinBox()
        self.aoSpreadAngleSpinner.setRange(0.5, 179.50)
        self.aoSpreadAngleSpinner.setDecimals(2)
        self.aoSpreadAngleSpinner.setLocale(QLocale.English)
        self.aoLimitRayDstCbx = QCheckBox('Limit ray distance')
        aoAttenuationLbl = QLabel('Attenuation')
        self.aoAttenuationX = QDoubleSpinBox()
        self.aoAttenuationX.setRange(0, 1000)
        self.aoAttenuationX.setDecimals(6)
        self.aoAttenuationX.setLocale(QLocale.English)
        self.aoAttenuationY = QDoubleSpinBox()
        self.aoAttenuationY.setRange(0, 1000)
        self.aoAttenuationY.setDecimals(6)
        self.aoAttenuationY.setLocale(QLocale.English)
        self.aoAttenuationZ = QDoubleSpinBox()
        self.aoAttenuationZ.setRange(0, 1000)
        self.aoAttenuationZ.setDecimals(6)
        self.aoAttenuationZ.setLocale(QLocale.English)
        self.aoJitterCbx = QCheckBox('Jitter')
        self.aoIgnoreHitsCbx = QCheckBox('Ignore backface hits')
        self.aoAllow100OccCbx = QCheckBox('Allow 100% occlusion')
        aoBgColorLbl = QLabel('Background color')
        self.aoBgColor = QColorLabel()
        aoDefBtn = QPushButton('Defaults')

        bentRaysLbl = QLabel('Rays')
        bentRaysSpinner = QSpinBox()
        bentRaysSpinner.setValue(128)
        bentRaysSpinner.setRange(8, 1000000)
        bentRaysSpinner.setLocale(QLocale.English)
        bentBiasLbl = QLabel('Bias')
        bentBiasSpinner = QDoubleSpinBox()
        bentBiasSpinner.setRange(0, 1)
        bentBiasSpinner.setValue(0.08)
        bentBiasSpinner.setDecimals(6)
        bentBiasSpinner.setLocale(QLocale.English)
        bentSpreadAngleLbl = QLabel('Spread Angle')
        bentSpreadAngleSpinner = QDoubleSpinBox()
        bentSpreadAngleSpinner.setRange(0.5, 179.50)
        bentSpreadAngleSpinner.setValue(162.0)
        bentSpreadAngleSpinner.setDecimals(2)
        bentSpreadAngleSpinner.setLocale(QLocale.English)
        bentLimitRayDstCbx = QCheckBox('Limit ray distance')
        bentJitterCbx = QCheckBox('Jitter')
        bentSwizzleLbl = QLabel('Swizzle Coordinates')
        bentSwizzleXCmb = QComboBox()
        bentSwizzleYCmb = QComboBox()
        bentSwizzleZCmb = QComboBox()
        for axis in ['X', 'Y', 'Z']:
            for sign in ['+', '-']:
                bentSwizzleXCmb.addItem(axis + sign)
                bentSwizzleYCmb.addItem(axis + sign)
                bentSwizzleZCmb.addItem(axis + sign)
        bentSwizzleXCmb.setCurrentIndex(0)
        bentSwizzleYCmb.setCurrentIndex(2)
        bentSwizzleZCmb.setCurrentIndex(4)
        bentTSCbx = QCheckBox('Tangent space')
        bentDistributionLbl = QLabel('Distribution')
        bentDistributionCmb = QComboBox()
        for dist in ['Uniform', 'Cosine', 'CosineSq']:
            bentDistributionCmb.addItem(dist)
        bentDistributionCmb.setCurrentIndex(0)
        bentBgColorLbl = QLabel('Background color')
        bentBgColor = QLabel()
        bentBgColor.setStyleSheet('background-color: rgb(127, 127, 255);')
        bentDefBtn = QPushButton('Defaults')

        prtRaysLbl = QLabel('Rays')
        prtRaysSpinner = QSpinBox()
        prtRaysSpinner.setValue(128)
        prtRaysSpinner.setRange(8, 8192)
        prtRaysSpinner.setLocale(QLocale.English)
        prtBiasLbl = QLabel('Bias')
        prtBiasSpinner = QDoubleSpinBox()
        prtBiasSpinner.setRange(0, 1)
        prtBiasSpinner.setValue(0.08)
        prtBiasSpinner.setDecimals(6)
        prtBiasSpinner.setLocale(QLocale.English)
        prtSpreadAngleLbl = QLabel('Spread Angle')
        prtSpreadAngleSpinner = QDoubleSpinBox()
        prtSpreadAngleSpinner.setRange(0.5, 179.50)
        prtSpreadAngleSpinner.setValue(162.0)
        prtSpreadAngleSpinner.setDecimals(2)
        prtSpreadAngleSpinner.setLocale(QLocale.English)
        prtLimitRayDstCbx = QCheckBox('Limit ray distance')
        prtJitterCbx = QCheckBox('Jitter')
        prtColorNormCbx = QCheckBox('PRT Color Normalize')
        prtColorNormCbx.setChecked(True)
        prtThresholdLbl = QLabel('Threshold')
        prtThresholdSpinner = QDoubleSpinBox()
        prtThresholdSpinner.setRange(0, 1)
        prtThresholdSpinner.setValue(0.005)
        prtThresholdSpinner.setDecimals(6)
        prtThresholdSpinner.setLocale(QLocale.English)
        prtBgColorLbl = QLabel('Background color')
        prtBgColor = QLabel()
        prtBgColor.setStyleSheet('background-color:rgb(0,0,0);')
        prtDefBtn = QPushButton('Defaults')

        convexityScaleLbl = QLabel('Convexity scale')
        convexityScaleSpinner = QDoubleSpinBox()
        convexityScaleSpinner.setRange(0, 1)
        convexityScaleSpinner.setValue(1.0)
        convexityScaleSpinner.setDecimals(3)
        convexityScaleSpinner.setLocale(QLocale.English)
        convexityBgColorLbl = QLabel('Background color')
        convexityBgColor = QLabel()
        convexityBgColor.setStyleSheet('background-color:rgb(255,255,255);')
        convexityDefBtn = QPushButton('Defaults')

        proximityRaysLbl = QLabel('Rays')
        proximityRaysSpinner = QSpinBox()
        proximityRaysSpinner.setValue(128)
        proximityRaysSpinner.setRange(8, 8192)
        proximityRaysSpinner.setLocale(QLocale.English)
        proximitySpreadAngleLbl = QLabel('Spread Angle')
        proximitySpreadAngleSpinner = QDoubleSpinBox()
        proximitySpreadAngleSpinner.setRange(0.5, 179.50)
        proximitySpreadAngleSpinner.setValue(80.0)
        proximitySpreadAngleSpinner.setDecimals(2)
        proximitySpreadAngleSpinner.setLocale(QLocale.English)
        proximityLimitRayDst = QCheckBox('Limit ray distance')
        proximityLimitRayDst.setChecked(True)
        proximityBgColorLbl = QLabel('Background color')
        proximityBgColor = QLabel()
        proximityBgColor.setStyleSheet('background-color:rgb(25,255,255')
        proximityDefBtn = QPushButton('Defaults')

        cavityRaysLbl = QLabel('Rays')
        cavityRaysSpinner = QSpinBox()
        cavityRaysSpinner.setValue(128)
        cavityRaysSpinner.setRange(8, 8192)
        cavityRaysSpinner.setLocale(QLocale.English)
        cavityJitterCbx = QCheckBox('Jitter')
        cavityRadiusLbl = QLabel('Radius')
        cavityRadiusSpinner = QDoubleSpinBox()
        cavityRadiusSpinner.setValue(0.5)
        cavityRadiusSpinner.setDecimals(6)
        cavityRadiusSpinner.setRange(0, 100000000)
        cavityRadiusSpinner.setLocale(QLocale.English)
        cavityContrastLbl = QLabel('Contrast')
        cavityContrastSpinner = QDoubleSpinBox()
        cavityContrastSpinner.setValue(1.25)
        cavityContrastSpinner.setRange(0.001, 8)
        cavityContrastSpinner.setLocale(QLocale.English)
        cavityStepsLbl = QLabel('Steps')
        cavityStepsSpinner = QSpinBox()
        cavityStepsSpinner.setValue(4)
        cavityStepsSpinner.setSingleStep(4)
        cavityStepsSpinner.setRange(4, 128)
        cavityStepsSpinner.setLocale(QLocale.English)
        cavityBgColorLbl = QLabel('Background color')
        cavityBgColor = QLabel()
        cavityBgColor.setStyleSheet('background-color:rgb(255,255,255);')
        cavityDefBtn = QPushButton('Defaults')

        wireRenderWireCbx = QCheckBox('Render wireframe')
        wireRenderWireCbx.setChecked(True)
        wireColorLbl = QLabel('Color')
        wireColor = QLabel()
        wireColor.setStyleSheet('background-color:rgb(255,255,255);')
        wireCWLbl = QLabel('CW')
        wireCWColor = QLabel()
        wireCWColor.setStyleSheet('background-color:rgb(0,0,255);')
        wireSeamLbl = QLabel('Seam')
        wireSeamColor = QLabel()
        wireSeamColor.setStyleSheet('background-color:rgb(0,255,0);')
        wireRenderFailsCbx = QCheckBox('Render ray fails')
        wireRenderFailsCbx.setChecked(True)
        wireRayColorLbl = QLabel('Color')
        wireRayColor = QLabel()
        wireRayColor.setStyleSheet('background-color:rgb(255,0,0);')
        wireBgColorLbl = QLabel('Background color')
        wireBgColor = QLabel()
        wireBgColor.setStyleSheet('background-color:rgb(0,0,0);')
        wireDefBtn = QPushButton('Defaults')

        directionSwizzleLbl = QLabel('Swizzle Coordinates')
        directionSwizzleXCmb = QComboBox()
        directionSwizzleYCmb = QComboBox()
        directionSwizzleZCmb = QComboBox()
        for axis in ['X', 'Y', 'Z']:
            for sign in ['+', '-']:
                directionSwizzleXCmb.addItem(axis + sign)
                directionSwizzleYCmb.addItem(axis + sign)
                directionSwizzleZCmb.addItem(axis + sign)
        directionTSCbx = QCheckBox()
        directionBgLbl = QLabel('Background color')
        directionBgColor = QLabel()
        directionBgColor.setStyleSheet('background-color:rgb(0,0,0);')
        directionNormLbl = QLabel('Normalization')
        directionNormCmb = QComboBox()
        for norm in ['Interactive', 'Manual', 'Raw FP Values']:
            directionNormCmb.addItem(norm)
        directionNormCmb.setCurrentIndex(0)
        directionDefBtn = QPushButton('Defaults')

        radiosityRaysLbl = QLabel('Rays')
        radiosityRaysSpinner = QSpinBox()
        radiosityRaysSpinner.setRange(0, 1000000)
        radiosityRaysSpinner.setLocale(QLocale.English)
        radiosityRaysSpinner.setValue(128)
        radiosityEncodeOccCbx = QCheckBox('Encode occlusion')
        radiosityEncodeOccCbx.setChecked(True)
        radiosityDistributionLbl = QLabel('Distribution')
        radiosityDistributionCmb = QComboBox()
        for dist in ['Uniform', 'Cosine', 'CosineSq']:
            radiosityDistributionCmb.addItem(dist)
        radiosityDistributionCmb.setCurrentIndex(0)
        radiosityBiasLbl = QLabel('Bias')
        radiosityBiasSpinner = QDoubleSpinBox()
        radiosityBiasSpinner.setRange(0, 1)
        radiosityBiasSpinner.setValue(0.08)
        radiosityBiasSpinner.setDecimals(6)
        radiosityBiasSpinner.setLocale(QLocale.English)
        radiositySpreadAngleLbl = QLabel('Spread Angle')
        radiositySpreadAngleSpinner = QDoubleSpinBox()
        radiositySpreadAngleSpinner.setRange(0.5, 179.50)
        radiositySpreadAngleSpinner.setValue(162.0)
        radiositySpreadAngleSpinner.setDecimals(2)
        radiositySpreadAngleSpinner.setLocale(QLocale.English)
        radiosityLimitRayDstCbx = QCheckBox('Limit ray distance')
        radiosityJitterCbx = QCheckBox('Jitter')
        radiosityAttenuationLbl = QLabel('Attenuation')
        radiosityAttenuationX = QDoubleSpinBox()
        radiosityAttenuationX.setRange(0, 1000)
        radiosityAttenuationX.setDecimals(6)
        radiosityAttenuationX.setLocale(QLocale.English)
        radiosityAttenuationX.setValue(1.0)
        radiosityAttenuationY = QDoubleSpinBox()
        radiosityAttenuationY.setRange(0, 1000)
        radiosityAttenuationY.setDecimals(6)
        radiosityAttenuationY.setLocale(QLocale.English)
        radiosityAttenuationZ = QDoubleSpinBox()
        radiosityAttenuationZ.setRange(0, 1000)
        radiosityAttenuationZ.setDecimals(6)
        radiosityAttenuationZ.setLocale(QLocale.English)
        radiosityCoordinatesLbl = QLabel('Coordinate System')
        radiosityCoordianteCmb = QComboBox()
        for coord in ['OpenGL', 'Direct3D', 'Ali B']:
            radiosityCoordianteCmb.addItem(coord)
        radiosityCoordianteCmb.setCurrentIndex(2)
        radiosityContrastLbl = QLabel('Contrast')
        radiosityContrastSpinner = QDoubleSpinBox()
        radiosityContrastSpinner.setRange(0.05, 50)
        radiosityContrastSpinner.setDecimals(6)
        radiosityContrastSpinner.setValue(1)
        radiosityContrastSpinner.setLocale(QLocale.English)
        radiosityAllowPureAOCbx = QCheckBox('Allow pure occlusion')
        radiosityBgColorLbl = QLabel('Background color')
        radiosityBgColor = QLabel()
        radiosityBgColor.setStyleSheet('background-color:rgb(0,0,0);')
        radiosityDefBtn = QPushButton('Defaults')

        bakeHPColorLbl = QLabel('Background color')
        bakeHPColor = QLabel()
        bakeHPColor.setStyleSheet('background-color:rgb(255,255,255')
        bakeHPDefBtn = QPushButton('Defaults')

        curvatureRaysLbl = QLabel('Rays')
        curvatureRaysSpinner = QSpinBox()
        curvatureRaysSpinner.setRange(0, 1000000)
        curvatureRaysSpinner.setLocale(QLocale.English)
        curvatureRaysSpinner.setValue(128)
        curvatureEncodeOccCbx = QCheckBox('Jitter')
        curvatureSpreadAngleLbl = QLabel('Spread Angle')
        curvatureSpreadAngleSpinner = QDoubleSpinBox()
        curvatureSpreadAngleSpinner.setRange(0.5, 179.50)
        curvatureSpreadAngleSpinner.setValue(162.0)
        curvatureSpreadAngleSpinner.setDecimals(2)
        curvatureSpreadAngleSpinner.setLocale(QLocale.English)
        curvatureBiasLbl = QLabel('Bias')
        curvatureBiasSpinner = QDoubleSpinBox()
        curvatureBiasSpinner.setRange(0, 1)
        curvatureBiasSpinner.setValue(0.0001)
        curvatureBiasSpinner.setDecimals(10)
        curvatureBiasSpinner.setLocale(QLocale.English)
        curvatureAlgorithmLbl = QLabel('Algorithm')
        curvatureAlgorithmCmb = QComboBox()
        for algorithm in ['Average', 'Gaussian']:
            curvatureAlgorithmCmb.addItem(algorithm)
        curvatureAlgorithmCmb.setCurrentIndex(0)
        curvatureDistributionCmb = QComboBox()
        for dist in ['Uniform', 'Cosine', 'CosineSq']:
            curvatureDistributionCmb.addItem(dist)
        curvatureDistributionCmb.setCurrentIndex(1)
        curvatureSearchDstLbl = QLabel('Search distance')
        curvatureSearchDstSpinner = QDoubleSpinBox()
        curvatureSearchDstSpinner.setRange(0, 10000000)
        curvatureSearchDstSpinner.setValue(1.0)
        curvatureSearchDstSpinner.setDecimals(10)
        curvatureSearchDstSpinner.setLocale(QLocale.English)
        curvatureToneMapLbl = QLabel('Tone mapping')
        curvatureToneMpCmb = QComboBox()
        for toneMap in ['Monocrome', 'Two colors', 'Three colors']:
            curvatureToneMpCmb.addItem(toneMap)
        curvatureToneMpCmb.setCurrentIndex(2)
        curvatureSmoothCbx = QCheckBox('Smoothing')
        curvatureSmoothCbx.setChecked(True)
        curvatureBgColorLbl = QLabel('Background color')
        curvatureBgColor = QLabel()
        curvatureBgColor.setStyleSheet('background-color:rgb(0,0,0);')
        curvatureDefBtn = QPushButton('Defaults')

        translucencyRaysLbl = QLabel('Rays')
        translucencyRaysSpinner = QSpinBox()
        translucencyRaysSpinner.setRange(0, 1000000)
        translucencyRaysSpinner.setLocale(QLocale.English)
        translucencyRaysSpinner.setValue(128)
        translucencyDistributionCmb = QComboBox()
        for dist in ['Uniform', 'Cosine', 'CosineSq']:
            translucencyDistributionCmb.addItem(dist)
        translucencyDistributionCmb.setCurrentIndex(0)
        translucencyBiasLbl = QLabel('Bias')
        translucencyBiasSpinner = QDoubleSpinBox()
        translucencyBiasSpinner.setRange(0, 1)
        translucencyBiasSpinner.setValue(0.0005)
        translucencyBiasSpinner.setDecimals(6)
        translucencyBiasSpinner.setLocale(QLocale.English)
        translucencySpreadAngleLbl = QLabel('Spread Angle')
        translucencySpreadAngleSpinner = QDoubleSpinBox()
        translucencySpreadAngleSpinner.setRange(0.5, 179.50)
        translucencySpreadAngleSpinner.setValue(162.0)
        translucencySpreadAngleSpinner.setDecimals(2)
        translucencySpreadAngleSpinner.setLocale(QLocale.English)
        translucencyEncodeOccCbx = QCheckBox('Jitter')
        translucencySearchDstLbl = QLabel('Search distance')
        translucencySearchDstSpinner = QDoubleSpinBox()
        translucencySearchDstSpinner.setRange(0, 10000000)
        translucencySearchDstSpinner.setValue(1.0)
        translucencySearchDstSpinner.setDecimals(10)
        translucencySearchDstSpinner.setLocale(QLocale.English)
        translucencyBgColorLbl = QLabel('Background color')
        translucencyBgColor = QLabel()
        translucencyBgColor.setStyleSheet('background-color:rgb(0,0,0);')
        translucencyDefBtn = QPushButton('Defaults')

        derivativeBgColorLbl = QLabel('Background color')
        derivativeBgColor = QLabel()
        derivativeBgColor.setStyleSheet('background-color:rgb(127,127,0);')

        mapsMainLayout.addLayout(buttonsLayout)
        mapsMainLayout.addWidget(self.mapsScrollArea)
        self.mapsScrollArea.setWidget(mapsGrp)
        mapsGrp.setLayout(mapsLayout)

        mapsMainLayout.addWidget(self.mapsSettingsScrollArea)
        self.mapsSettingsScrollArea.setWidget(mapsSettingsGrp)
        mapsSettingsGrp.setLayout(mapsSettingsLayout)

        mapsLayout.addLayout(normalMapLayout)
        mapsLayout.addLayout(heightMapLayout)
        mapsLayout.addLayout(bakeBaseTextureLayout)
        mapsLayout.addLayout(aoMapLayout)
        mapsLayout.addLayout(bentNormalMapLayout)
        mapsLayout.addLayout(prtPnLayout)
        mapsLayout.addLayout(convexityMapLayout)
        mapsLayout.addLayout(thicknessMapLayout)
        mapsLayout.addLayout(proximityLayout)
        mapsLayout.addLayout(cavityMapLayout)
        mapsLayout.addLayout(wireAndRayFailsLayout)
        mapsLayout.addLayout(directionLayout)
        mapsLayout.addLayout(radiosityLayout)
        mapsLayout.addLayout(bakeHPColorMapLayout)
        mapsLayout.addLayout(curvatureMapLayout)
        mapsLayout.addLayout(translucencyMapLayout)
        mapsLayout.addLayout(derivativeMapLayout)

        buttonsLayout.addSpacerItem(QSpacerItem(120, 0, QSizePolicy.Fixed, QSizePolicy.Fixed))
        buttonsLayout.addWidget(selectAllMapsBtn)
        buttonsLayout.addWidget(clearAllMapsBtn)
        buttonsLayout.addSpacerItem(QSpacerItem(120, 0, QSizePolicy.Fixed, QSizePolicy.Fixed))

        normalMapLayout.addWidget(self.normalMapCbx)
        normalMapLayout.addWidget(normalMapBtn)
        heightMapLayout.addWidget(self.heightMapCbx)
        heightMapLayout.addWidget(heightMapBtn)
        bakeBaseTextureLayout.addWidget(self.bakeBaseTextureMapCbx)
        bakeBaseTextureLayout.addWidget(bakeBaseTextureMapBtn)
        aoMapLayout.addWidget(self.aoMapCbx)
        aoMapLayout.addWidget(aoMapBtn)
        bentNormalMapLayout.addWidget(self.bentNormalMapCbx)
        bentNormalMapLayout.addWidget(bentNormaMapBtn)
        prtPnLayout.addWidget(self.prtPnMapCbx)
        prtPnLayout.addWidget(prtPnMapBtn)
        convexityMapLayout.addWidget(self.convexityMapCbx)
        convexityMapLayout.addWidget(convexityMapBtn)
        thicknessMapLayout.addWidget(self.thicknessMapCbx)
        thicknessMapLayout.addWidget(thicknessMapBtn)
        proximityLayout.addWidget(self.proximityMapCbx)
        proximityLayout.addWidget(proximityMapBtn)
        cavityMapLayout.addWidget(self.cavityMapCbx)
        cavityMapLayout.addWidget(cavityMapBtn)
        wireAndRayFailsLayout.addWidget(self.wireframeAndRayFailsMapCbx)
        wireAndRayFailsLayout.addWidget(wireframeAndRayFailsMapBtn)
        directionLayout.addWidget(self.directionMapCbx)
        directionLayout.addWidget(directionMapBtn)
        radiosityLayout.addWidget(self.radiosityMapCbx)
        radiosityLayout.addWidget(radiosityMapBtn)
        bakeHPColorMapLayout.addWidget(self.bakeHPColorMapCbx)
        bakeHPColorMapLayout.addWidget(bakeHPColorMapBtn)
        curvatureMapLayout.addWidget(self.curvatureMapCbx)
        curvatureMapLayout.addWidget(curvatureMapBtn)
        translucencyMapLayout.addWidget(self.translucencyMapCbx)
        translucencyMapLayout.addWidget(translucencyMapBtn)
        derivativeMapLayout.addWidget(self.derivativeMapCbx)
        derivativeMapLayout.addWidget(derivativeMapBtn)

        mapsSettingsLayout.addWidget(self.normalMapSettingsGrp)
        self.normalMapSettingsGrp.setLayout(normalSettingsLayout)
        normalSettingsLayout.addLayout(normalSwizzleLayout)
        normalSettingsLayout.addLayout(normalTSLayout)
        normalSettingsLayout.addLayout(normalBgColorLayout)
        normalSwizzleLayout.addWidget(normalSwizzleLbl)
        normalSwizzleLayout.addWidget(self.normalSwizzleXCmb)
        normalSwizzleLayout.addWidget(self.normalSwizzleYCmb)
        normalSwizzleLayout.addWidget(self.normalSwizzleZCmb)
        normalTSLayout.addWidget(self.normalTSCbx)
        normalBgColorLayout.addWidget(normalBgColorLbl)
        normalBgColorLayout.addWidget(self.normalBgColor)
        normalSettingsLayout.addWidget(normalDefBtn)

        mapsSettingsLayout.addWidget(self.heightMapSettingsGrp)
        self.heightMapSettingsGrp.setLayout(heightSettingsLayout)
        heightSettingsLayout.addLayout(heightBgColorLayout)
        heightSettingsLayout.addLayout(heightNormalizationLayout)
        heightSettingsLayout.addLayout(heightNormalNormLayout)
        heightBgColorLayout.addWidget(heightBgColorLbl)
        heightBgColorLayout.addWidget(self.heightBgColor)
        heightNormalizationLayout.addWidget(heightNormalizationLbl)
        heightNormalizationLayout.addWidget(self.heightNormalizationCmb)
        heightNormalNormLayout.addWidget(heightManualMinLbl)
        heightNormalNormLayout.addWidget(self.heightManualMinSpinner)
        heightNormalNormLayout.addWidget(heightManualMaxLbl)
        heightNormalNormLayout.addWidget(self.heightManualMaxSpinner)
        heightSettingsLayout.addWidget(heightDefBtn)

        mapsSettingsLayout.addWidget(self.bakeBaseTextureSettingsGrp)
        self.bakeBaseTextureSettingsGrp.setLayout(bakeBaseSettingsLayout)
        bakeBaseSettingsLayout.addWidget(self.bakeBaseWriteObjIDCbx)
        bakeBaseSettingsLayout.addLayout(bakeBaseTextureDrawColorLayout)
        bakeBaseSettingsLayout.addLayout(bakeBaseBgColorLayout)
        bakeBaseTextureDrawColorLayout.addWidget(self.bakeBaseDrawColorCbx)
        bakeBaseTextureDrawColorLayout.addWidget(self.bakeBaseDrawColorCbx)
        bakeBaseBgColorLayout.addWidget(bakeBaseBgColorLbl)
        bakeBaseBgColorLayout.addWidget(self.bakeBaseBgColor)
        bakeBaseSettingsLayout.addWidget(bakeBaseDefBtn)

        mapsSettingsLayout.addWidget(self.aoMapSettingsGrp)
        self.aoMapSettingsGrp.setLayout(aoBaseSettingsLayout)
        aoBaseSettingsLayout.addLayout(aoRaysLayout)
        aoBaseSettingsLayout.addLayout(aoDistributionLayout)
        aoBaseSettingsLayout.addLayout(aoOccUnoccColorLayout)
        aoOccUnoccColorLayout.addLayout(aoOccludedColorLayout)
        aoOccUnoccColorLayout.addLayout(aoUnoccludedColorLayout)
        aoBaseSettingsLayout.addLayout(aoBiasSpreadLayout)
        aoBiasSpreadLayout.addLayout(aoBiasLayout)
        aoBiasSpreadLayout.addLayout(aoSpreadAngleLayout)
        aoBaseSettingsLayout.addWidget(self.aoLimitRayDstCbx)
        aoBaseSettingsLayout.addLayout(aoAttenuationLayout)
        aoBaseSettingsLayout.addLayout(aoJitterBackfaceLayout)
        aoBaseSettingsLayout.addWidget(self.aoAllow100OccCbx)
        aoBaseSettingsLayout.addLayout(aoBgColorLayout)
        aoRaysLayout.addWidget(aoRaysLbl)
        aoRaysLayout.addWidget(self.aoRaysSpinner)
        aoDistributionLayout.addWidget(aoDistributionLbl)
        aoDistributionLayout.addWidget(self.aoDistributionCmb)
        aoOccludedColorLayout.addWidget(aoOccludedColorLbl)
        aoOccludedColorLayout.addWidget(self.aoOccludedColor)
        aoUnoccludedColorLayout.addWidget(aoUnoccludedColorLbl)
        aoUnoccludedColorLayout.addWidget(self.aoUnoccludedColor)
        aoBiasLayout.addWidget(aoBiasLbl)
        aoBiasLayout.addWidget(self.aoBiasSpinner)
        aoSpreadAngleLayout.addWidget(aoSpreadAngleLbl)
        aoSpreadAngleLayout.addWidget(self.aoSpreadAngleSpinner)
        aoAttenuationLayout.addWidget(aoAttenuationLbl)
        aoAttenuationLayout.addWidget(self.aoAttenuationX)
        aoAttenuationLayout.addWidget(self.aoAttenuationY)
        aoAttenuationLayout.addWidget(self.aoAttenuationZ)
        aoJitterBackfaceLayout.addWidget(self.aoJitterCbx)
        aoJitterBackfaceLayout.addWidget(self.aoIgnoreHitsCbx)
        aoBgColorLayout.addWidget(aoBgColorLbl)
        aoBgColorLayout.addWidget(self.aoBgColor)
        aoBaseSettingsLayout.addWidget(aoDefBtn)

        mapsSettingsLayout.addWidget(self.bentNormalMapSettingsGrp)
        self.bentNormalMapSettingsGrp.setLayout(bentNormalSettingsLayout)
        bentNormalSettingsLayout.addLayout(bentNormalRaysLayout)
        bentNormalSettingsLayout.addLayout(bentBiasSpreadLayout)
        bentBiasSpreadLayout.addLayout(bentBiasLayout)
        bentBiasSpreadLayout.addLayout(bentSpreadLayout)
        bentBiasSpreadLayout.addLayout(bentLimitJitterLayout)
        bentNormalSettingsLayout.addLayout(bentSwizzleLayout)
        bentNormalSettingsLayout.addLayout(bentTSLayout)
        bentNormalSettingsLayout.addLayout(bentDistributionLayout)
        bentNormalSettingsLayout.addLayout(bentBgColorLayout)
        bentNormalRaysLayout.addWidget(bentRaysLbl)
        bentNormalRaysLayout.addWidget(bentRaysSpinner)
        bentBiasLayout.addWidget(bentBiasLbl)
        bentBiasLayout.addWidget(bentBiasSpinner)
        bentSpreadLayout.addWidget(bentSpreadAngleLbl)
        bentSpreadLayout.addWidget(bentSpreadAngleSpinner)
        bentSwizzleLayout.addWidget(bentSwizzleLbl)
        bentSwizzleLayout.addWidget(bentSwizzleXCmb)
        bentSwizzleLayout.addWidget(bentSwizzleYCmb)
        bentSwizzleLayout.addWidget(bentSwizzleZCmb)
        bentTSLayout.addWidget(bentTSCbx)
        bentDistributionLayout.addWidget(bentDistributionLbl)
        bentDistributionLayout.addWidget(bentDistributionCmb)
        bentBgColorLayout.addWidget(bentBgColorLbl)
        bentBgColorLayout.addWidget(bentBgColor)

        mapsSettingsLayout.addWidget(self.prtPnMapSettingsGrp)
        self.prtPnMapSettingsGrp.setLayout(prtSettingsLayout)
        prtSettingsLayout.addLayout(prtRaysLayout)
        prtSettingsLayout.addLayout(prtBiasSpreadLayout)
        prtSettingsLayout.addLayout(prtBiasLayout)
        prtSettingsLayout.addLayout(prtSpreadAngleLayout)
        prtSettingsLayout.addLayout(prtLimitRayLayout)
        prtSettingsLayout.addLayout(prtColorNormLayout)
        prtSettingsLayout.addLayout(prtThresholdLayout)
        prtSettingsLayout.addLayout(prtBgColorLayout)
        prtRaysLayout.addWidget(prtRaysLbl)
        prtRaysLayout.addWidget(prtRaysSpinner)
        prtBiasLayout.addWidget(prtBiasLbl)
        prtBiasLayout.addWidget(prtBiasSpinner)
        prtSpreadAngleLayout.addWidget(prtSpreadAngleLbl)
        prtSpreadAngleLayout.addWidget(prtSpreadAngleSpinner)
        prtLimitRayLayout.addWidget(prtLimitRayDstCbx)
        prtLimitRayLayout.addWidget(prtJitterCbx)
        prtThresholdLayout.addWidget(prtThresholdLbl)
        prtThresholdLayout.addWidget(prtThresholdSpinner)
        prtBgColorLayout.addWidget(prtBgColorLbl)
        prtBgColorLayout.addWidget(prtBgColor)
        prtSettingsLayout.addWidget(prtDefBtn)

        mapsSettingsLayout.addWidget(self.convexityMapSettingsGrp)
        self.convexityMapSettingsGrp.setLayout(convexitySettingsLayout)
        convexitySettingsLayout.addLayout(convexityScaleLayout)
        convexitySettingsLayout.addLayout(convexityBgColorLayout)
        convexityScaleLayout.addWidget(convexityScaleLbl)
        convexityScaleLayout.addWidget(convexityScaleSpinner)
        convexityBgColorLayout.addWidget(convexityBgColorLbl)
        convexityBgColorLayout.addWidget(convexityBgColor)
        convexitySettingsLayout.addWidget(convexityDefBtn)

        mapsSettingsLayout.addWidget(self.proximityMapSettingsGrp)
        self.proximityMapSettingsGrp.setLayout(proximitySettingsLayout)
        proximitySettingsLayout.addLayout(proximityRaysSpreadLayout)
        proximityRaysSpreadLayout.addLayout(proximityRaysLayout)
        proximitySettingsLayout.addLayout(proximityLimitRadyDstLayout)
        proximitySettingsLayout.addLayout(proximityBgColorLayout)
        proximityRaysLayout.addWidget(proximityRaysLbl)
        proximityRaysLayout.addWidget(proximityRaysSpinner)
        proximityRaysLayout.addWidget(proximitySpreadAngleLbl)
        proximityRaysLayout.addWidget(proximitySpreadAngleSpinner)
        proximityLimitRadyDstLayout.addWidget(proximityLimitRayDst)
        proximityBgColorLayout.addWidget(proximityBgColorLbl)
        proximityBgColorLayout.addWidget(proximityBgColor)
        proximitySettingsLayout.addWidget(proximityDefBtn)

        mapsSettingsLayout.addWidget(self.cavityMapSettingsGrp)
        self.cavityMapSettingsGrp.setLayout(cavitySettingsLayout)
        cavitySettingsLayout.addLayout(cavityRaysLayout)
        cavityRaysLayout.addLayout(cavityJitterLayout)
        cavitySettingsLayout.addLayout(cavityRadiusLayout)
        cavitySettingsLayout.addLayout(cavityContrastLayout)
        cavitySettingsLayout.addLayout(cavityStepsLayout)
        cavitySettingsLayout.addLayout(cavityBgColorLayout)
        cavityRaysLayout.addWidget(cavityRaysLbl)
        cavityRaysLayout.addWidget(cavityRaysSpinner)
        cavityJitterLayout.addWidget(cavityJitterCbx)
        cavityRadiusLayout.addWidget(cavityRadiusLbl)
        cavityRadiusLayout.addWidget(cavityRadiusSpinner)
        cavityContrastLayout.addWidget(cavityContrastLbl)
        cavityContrastLayout.addWidget(cavityContrastSpinner)
        cavityStepsLayout.addWidget(cavityStepsLbl)
        cavityStepsLayout.addWidget(cavityStepsSpinner)
        cavityBgColorLayout.addWidget(cavityBgColorLbl)
        cavityBgColorLayout.addWidget(cavityBgColor)
        cavitySettingsLayout.addWidget(cavityDefBtn)

        mapsSettingsLayout.addWidget(self.wireframeAndRayFailsGrp)
        self.wireframeAndRayFailsGrp.setLayout(wireSettingsLayout)
        wireSettingsLayout.addWidget(wireRenderWireCbx)
        wireSettingsLayout.addLayout(wireColorCWSeamLayout)
        wireColorCWSeamLayout.addLayout(wireColorLayout)
        wireColorCWSeamLayout.addLayout(wireCWLayout)
        wireColorCWSeamLayout.addLayout(wireSeamLayout)
        wireSettingsLayout.addWidget(wireRenderFailsCbx)
        wireSettingsLayout.addLayout(wireColorRayFailLayout)
        wireSettingsLayout.addLayout(wireBgColorLayout)
        wireColorLayout.addWidget(wireColorLbl)
        wireColorLayout.addWidget(wireColor)
        wireCWLayout.addWidget(wireCWLbl)
        wireCWLayout.addWidget(wireCWColor)
        wireSeamLayout.addWidget(wireSeamLbl)
        wireSeamLayout.addWidget(wireSeamColor)
        wireColorRayFailLayout.addWidget(wireRayColorLbl)
        wireColorRayFailLayout.addWidget(wireRayColor)
        wireBgColorLayout.addWidget(wireBgColorLbl)
        wireBgColorLayout.addWidget(wireBgColor)
        wireSettingsLayout.addWidget(wireDefBtn)

        mapsSettingsLayout.addWidget(self.directionMapSettingsGrp)
        self.directionMapSettingsGrp.setLayout(directionSettingsLayout)

        mapsSettingsLayout.addWidget(self.radiosityMapSettingsGrp)
        self.radiosityMapSettingsGrp.setLayout(radiositySettingsLayout)

        mapsSettingsLayout.addWidget(self.bakeHPSettingsGrp)
        self.bakeHPSettingsGrp.setLayout(bakeHPColorsSettingsLayout)

        mapsSettingsLayout.addWidget(self.curvatureSettingsGrp)
        self.curvatureSettingsGrp.setLayout(curvatureSettingsLayout)

        mapsSettingsLayout.addWidget(self.translucencyMapSettingsGrp)
        self.translucencyMapSettingsGrp.setLayout(translucencySettingsLayout)

        mapsSettingsLayout.addWidget(self.derivativeMapSettingsGrp)
        self.derivativeMapSettingsGrp.setLayout(derivativeSettingsLayout)

        self.mapsTab.setLayout(mapsMainLayout)

        for type in ['normal', 'height', 'bakeBase', 'ao']:
            self._setDefault(type)

        # === SIGNALS === #
        normalMapBtn.clicked.connect(partial(self._toggleSettings, 'normal'))
        heightMapBtn.clicked.connect(partial(self._toggleSettings, 'height'))
        aoMapBtn.clicked.connect(partial(self._toggleSettings, 'ao'))

    def bakeTabUI(self):

        bakeMainLayout = QVBoxLayout()
        bakeMainLayout.setContentsMargins(5, 5, 5, 5)
        bakeMainLayout.setSpacing(5)
        bakeMainLayout.setAlignment(Qt.AlignTop)

        bakeLayout = QVBoxLayout()
        bakeLayout.setContentsMargins(5, 5, 5, 5)
        bakeLayout.setSpacing(5)

        outputLayout = QVBoxLayout()
        outputLayout.setContentsMargins(5, 5, 5, 5)
        outputLayout.setSpacing(5)

        renderSettingsLayout = QVBoxLayout()
        renderSettingsLayout.setContentsMargins(5, 5, 5, 5)
        renderSettingsLayout.setSpacing(5)

        # ------- Maps Settings Layout ------- #

        outputFileLayout = QHBoxLayout()
        outputFileLayout.setContentsMargins(0, 0, 0, 0)
        outputFileLayout.setSpacing(5)
        bakeExportLayout = QHBoxLayout()
        bakeExportLayout.setContentsMargins(0, 0, 0, 0)
        bakeExportLayout.setSpacing(25)
        bakePathExportLayout = QHBoxLayout()
        bakePathExportLayout.setContentsMargins(0, 0, 0, 0)
        bakePathExportLayout.setSpacing(5)
        bakeFormatExportLayout = QHBoxLayout()
        bakeFormatExportLayout.setContentsMargins(0, 0, 0, 0)
        bakeFormatExportLayout.setSpacing(5)
        sizeLayout = QHBoxLayout()
        sizeLayout.setContentsMargins(0, 0, 0, 0)
        sizeLayout.setSpacing(15)
        edgeBucketLayout = QHBoxLayout()
        edgeBucketLayout.setContentsMargins(0, 0, 0, 0)
        edgeBucketLayout.setSpacing(5)
        edgeLayout = QHBoxLayout()
        edgeLayout.setContentsMargins(0, 0, 0, 0)
        edgeLayout.setSpacing(5)
        bucketSizeLayout = QHBoxLayout()
        bucketSizeLayout.setContentsMargins(0, 0, 0, 0)
        bucketSizeLayout.setSpacing(0)
        extrasRenderLayout = QHBoxLayout()
        extrasRenderLayout.setContentsMargins(10, 10, 10, 10)
        extrasRenderLayout.setSpacing(5)
        closesHitLayout = QHBoxLayout()
        closesHitLayout.setContentsMargins(0, 0, 0, 0)
        closesHitLayout.setSpacing(5)
        discardLayout = QHBoxLayout()
        discardLayout.setContentsMargins(0, 0, 0, 0)
        discardLayout.setSpacing(5)
        rendererLayout = QVBoxLayout()
        rendererLayout.setContentsMargins(0, 0, 0, 0)
        rendererLayout.setSpacing(5)
        antialiasingLayout = QVBoxLayout()
        antialiasingLayout.setContentsMargins(0, 0, 0, 0)
        antialiasingLayout.setSpacing(5)
        fileOverwriteLayout = QHBoxLayout()
        fileOverwriteLayout.setContentsMargins(0, 0, 0, 0)
        fileOverwriteLayout.setSpacing(5)

        # ---------------------------------------------------------------------------------
        # ---------------------------------------------------------------------------------

        bakeGrp = QGroupBox('Baking Options')
        outputGrp = QGroupBox('Output Settings')
        renderGrp = QGroupBox('Render Settings')

        outputFileLbl = QLabel('Output file name: ')
        self.outputFileLine = QLineEdit()
        self.outputFileLine.setEnabled(False)
        # self.outputFileLine.setText('$prefix' + self.separatorLine.text() + '$name')
        self.outputFileLine.setMinimumWidth(100)
        self.outputFileLine.setMaximumWidth(200)
        matTypeLbl = QLabel('_$matType')
        outputInfoBtn = QPushButton('>')
        clearOutputInfoBtn = QPushButton('Clear')
        outputInfoBtn.setMinimumWidth(25)
        clearOutputInfoBtn.setMinimumWidth(35)

        bakeExportLbl = QLabel('Baking export path: ')
        self.bakeExportLine = QLineEdit()
        # self.bakeExportLine.setText('F:\Dwarf\Exports')
        self.bakeExportLine.setMinimumWidth(164)
        bakeExportBtn = QPushButton('...')
        bakeExportBtn.setMinimumWidth(25)
        bakeExportFormatLbl = QLabel('Format')
        self.bakeExportFormatCmb = QComboBox()
        #for format in ['BMP', 'JPG', 'PNG', 'HDR', 'TGA', 'TIFF', 'RAW', 'WebP', 'DDS', 'OpenEXR']:
        for format in ['BMP', 'JPG', 'PNG', 'TGA', 'TIFF', 'RAW']:
            self.bakeExportFormatCmb.addItem(format)
            self.bakeExportFormatCmb.setCurrentIndex(1)
        self.bakeExportFormatCmb.setMaximumWidth(80)

        sizeLbl = QLabel('Size: ')
        self.sizeWCmb = QComboBox()
        self.sizeWCmb.setMinimumWidth(100)
        self.sizeHCmb = QComboBox()
        self.sizeHCmb.setMinimumWidth(100)
        val = 16
        while val < (32768+1):
            self.sizeWCmb.addItem(str(val))
            self.sizeHCmb.addItem(str(val))
            val *= 2
            self.sizeWCmb.setCurrentIndex(6)
            self.sizeHCmb.setCurrentIndex(6)

        edgeLbl = QLabel('Edge padding: ')
        self.edgeSpinBox = QSpinBox()
        self.edgeSpinBox.setMaximumWidth(80)
        self.edgeSpinBox.setValue(16)
        bucketSizeLbl = QLabel('Bucket Size: ')
        self.bucketSizeCmb = QComboBox()

        val = 16
        while val < (512+1):
            self.bucketSizeCmb.addItem(str(val))
            val *= 2

        self.bucketSizeCmb.setMaximumWidth(80)
        self.bucketSizeCmb.setCurrentIndex(1)

        self.closesHitCbx = QCheckBox('Closests hit if fails')
        self.discardCbx = QCheckBox('Discard back-faces hits')

        rendererLbl = QLabel('Renderer')
        self.rendererCmb = QComboBox()
        for render in ['Optix/CUDA renderer', 'Default bucket renderer', 'OpenRL map renderer']:
            self.rendererCmb.addItem(render)
            self.rendererCmb.setCurrentIndex(1)

        antialiasingLbl = QLabel('Antialiasing')
        self.antialiasingCmb = QComboBox()
        for aa in ['1x', '2x', '4x']:
            self.antialiasingCmb.addItem(aa)

            self.fileOverwriteCbx = QCheckBox('Overwrite existing file')
            self.fileOverwriteCbx.setChecked(True)

        bakeMainLayout.addWidget(bakeGrp)

        bakeGrp.setLayout(bakeLayout)

        bakeLayout.addWidget(outputGrp)
        outputGrp.setLayout(outputLayout)
        outputLayout.addLayout(outputFileLayout)
        outputLayout.addLayout(bakeExportLayout)
        bakeExportLayout.addLayout(bakePathExportLayout)
        bakeExportLayout.addLayout(bakeFormatExportLayout)

        outputFileLayout.addSpacerItem(QSpacerItem(70, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        outputFileLayout.addWidget(outputFileLbl)
        outputFileLayout.addWidget(self.outputFileLine)
        outputFileLayout.addWidget(matTypeLbl)
        outputFileLayout.addWidget(outputInfoBtn)
        outputFileLayout.addWidget(clearOutputInfoBtn)
        outputFileLayout.addSpacerItem(QSpacerItem(200, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        bakePathExportLayout.addSpacerItem(QSpacerItem(55, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        bakePathExportLayout.addWidget(bakeExportLbl)
        bakePathExportLayout.addWidget(self.bakeExportLine)
        bakePathExportLayout.addWidget(bakeExportBtn)
        bakePathExportLayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        bakeFormatExportLayout.addWidget(bakeExportFormatLbl)
        bakeFormatExportLayout.addWidget(self.bakeExportFormatCmb)
        bakeFormatExportLayout.addSpacerItem(QSpacerItem(55, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))

        bakeLayout.addWidget(renderGrp)
        renderGrp.setLayout(renderSettingsLayout)
        renderSettingsLayout.addLayout(sizeLayout)
        renderSettingsLayout.addLayout(edgeBucketLayout)
        edgeBucketLayout.addLayout(edgeLayout)
        edgeBucketLayout.addLayout(bucketSizeLayout)
        renderSettingsLayout.addLayout(extrasRenderLayout)
        extrasRenderLayout.addLayout(closesHitLayout)
        extrasRenderLayout.addLayout(discardLayout)
        renderSettingsLayout.addLayout(rendererLayout)
        renderSettingsLayout.addLayout(antialiasingLayout)
        renderSettingsLayout.addLayout(fileOverwriteLayout)

        sizeLayout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        sizeLayout.addWidget(sizeLbl)
        sizeLayout.addWidget(self.sizeWCmb)
        sizeLayout.addWidget(self.sizeHCmb)
        sizeLayout.addSpacerItem(QSpacerItem(215, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        edgeLayout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        edgeLayout.addWidget(edgeLbl)
        edgeLayout.addWidget(self.edgeSpinBox)
        edgeLayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        bucketSizeLayout.addWidget(bucketSizeLbl)
        bucketSizeLayout.addWidget(self.bucketSizeCmb)
        bucketSizeLayout.addSpacerItem(QSpacerItem(200, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        closesHitLayout.addWidget(self.closesHitCbx)
        discardLayout.addSpacerItem(QSpacerItem(200, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        discardLayout.addWidget(self.discardCbx)
        rendererLayout.addWidget(rendererLbl)
        rendererLayout.addWidget(self.rendererCmb)
        antialiasingLayout.addWidget(antialiasingLbl)
        antialiasingLayout.addWidget(self.antialiasingCmb)
        fileOverwriteLayout.addSpacerItem(QSpacerItem(2, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        fileOverwriteLayout.addWidget(self.fileOverwriteCbx)

        self.bakeTab.setLayout(bakeMainLayout)

        # === SIGNALS === #
        outputInfoBtn.clicked.connect(self._showNamingConventions)
        bakeExportBtn.clicked.connect(partial(self.setPath, 'output'))
        self.outputFileLine.textChanged.connect(self._updateState)

    def infoTabUI(self):

        infoMainLayout = QVBoxLayout()
        infoMainLayout.setContentsMargins(5,5,5,5)
        infoMainLayout.setSpacing(5)
        infoMainLayout.setAlignment(Qt.AlignTop)

        infoLayout = QVBoxLayout()
        infoLayout.setContentsMargins(5,5,5,5)
        infoLayout.setSpacing(5)

        bakeMapsLayout = QVBoxLayout()
        bakeMapsLayout.setContentsMargins(5,5,5,5)
        bakeMapsLayout.setSpacing(5)

        appsLayout = QVBoxLayout()
        appsLayout.setContentsMargins(5, 5, 5, 5)
        appsLayout.setSpacing(5)

        # -------- Info Layout -------- #

        xNormalLayout = QHBoxLayout()
        xNormalLayout.setContentsMargins(0,0,0,0)
        xNormalLayout.setSpacing(5)

        # ---------------------------------------------------------------------------------
        # ---------------------------------------------------------------------------------

        bakeMapsGrp = QGroupBox('Bake maps')
        appsGrp = QGroupBox('Apps Setup')
        appsGrp.setContentsMargins(5,5,5,5)

        infoMainLayout.addLayout(infoLayout)
        infoLayout.addWidget(bakeMapsGrp)
        bakeMapsGrp.setLayout(bakeMapsLayout)
        bakeMapsLayout.addWidget(appsGrp)
        appsGrp.setLayout(appsLayout)

        xNormalLbl = QLabel('xNormal App Path: ')
        self.xNormalLine = QLineEdit()
        self.xNormalLine.setText('C:/Program Files/S.Orgaz/xNormal 3.19.2/x64/xNormal.exe')
        xNormalBtn = QPushButton('...')
        self.autoNormalGenCbx = QCheckBox('Auto generate Maps (Photoshop Required)')
        self.autoNormalGenCbx.setChecked(True)

        self.bakeMapsBtn = QPushButton('Bake Maps')

        appsLayout.addLayout(xNormalLayout)
        xNormalLayout.addWidget(xNormalLbl)
        xNormalLayout.addWidget(self.xNormalLine)
        xNormalLayout.addWidget(xNormalBtn)
        appsLayout.addWidget(self.autoNormalGenCbx)

        bakeMapsLayout.addWidget(self.bakeMapsBtn)

        self.infoTab.setLayout(infoMainLayout)

        # === SIGNALS === #
        xNormalBtn.clicked.connect(partial(self.setPath, 'xNormal'))
        self.bakeMapsBtn.clicked.connect(self._bakeMaps)


    def _getModelsToBake(self):
        validHpMeshes = []
        validLpMeshes = []
        for row in range(self.highMeshesTable.rowCount()):
            hpMeshIsChecked = bool(self.highMeshesTable.item(row, 0))
            if hpMeshIsChecked:
                hpMesh = self.highMeshesTable.item(row, 1)
                hpMeshName = self._getBaseName(hpMesh.text())
                for lpRow in range(self.lowMeshesTable.rowCount()):
                    lpMeshIsChecked = bool(self.lowMeshesTable.item(lpRow, 0))
                    if lpMeshIsChecked:
                        lpMesh = self.lowMeshesTable.item(lpRow, 1)
                        lpMeshName = self._getBaseName(lpMesh.text())
                        if lpMeshName == hpMeshName:
                            validLpMeshes.append(lpMesh.text())
                            validHpMeshes.append(hpMesh.text())
        return validLpMeshes, validHpMeshes


    def _saveSettings(self, separatedMeshes=False, index=0, createFile=True):

        xNormalTypes = ['_normals', '_heights']

        # Get valid models to bake
        validLpMeshes, validHpMeshes = self._getModelsToBake()
        highMeshesOptions = []
        lowMeshesOptions = []
        genTextures = []

        if separatedMeshes:
            highConfig = xNormal.high_mesh_options(self.highDefLine.text() + '/' + validHpMeshes[index],
                                                   scale=self.scaleSpinner.value(),
                                                   ignore_per_vertex_colors=self.hpIgnoreVtxColorCbx.isChecked())
            lowConfig = xNormal.low_mesh_options(self.lowDefLine.text() + '/' + validLpMeshes[index] + '.OBJ',
                                                 scale=self.scaleSpinner.value(),
                                                 forward_ray_dist=self.lpMaxFrontalRayDstSpinner.value(),
                                                 backward_ray_dist=self.lpMinNearRayDstSpinner.value())
            highMeshesOptions.append(highConfig)
            lowMeshesOptions.append(lowConfig)

            mapName = self.bakeExportLine.text() + '/' + self._getOutputName(mesh=self._getBaseName(validHpMeshes[index])) + '.' + self.bakeExportFormatCmb.currentText().lower()

            for type in xNormalTypes:
                splitMap = mapName.split('.')
                newMap = splitMap[0] + type + '.' + splitMap[1]
                count = 0

                if not self.fileOverwriteCbx.isChecked():
                    while(os.path.exists(newMap)):

                        newMap = splitMap[0] + '_' + str(count) + type + '.' + splitMap[1]
                        mapName = self.bakeExportLine.text() + '/' + self._getOutputName(mesh=self._getBaseName(validHpMeshes[index])) + '_' + str(count) + '.' + self.bakeExportFormatCmb.currentText().lower()
                        count += 1

            genTextures.append(os.path.abspath(mapName))

        else:
            for i, hp in enumerate(validHpMeshes):
                highConfig = xNormal.high_mesh_options(self.highDefLine.text() + '/' + hp,
                                                       scale=self.scaleSpinner.value(),
                                                       ignore_per_vertex_colors=self.hpIgnoreVtxColorCbx.isChecked())
                lowConfig = xNormal.low_mesh_options(self.lowDefLine.text() + '/' + validLpMeshes[i] + '.OBJ',
                                                     scale=self.scaleSpinner.value(),
                                                     forward_ray_dist=self.lpMaxFrontalRayDstSpinner.value(),
                                                     backward_ray_dist=self.lpMinNearRayDstSpinner.value())
                highMeshesOptions.append(highConfig)
                lowMeshesOptions.append(lowConfig)
            mapName = self.bakeExportLine.text() + '/' + self.outputFileLine.text() + '.' + self.bakeExportFormatCmb.currentText().lower()
            genTextures.append(os.path.abspath(mapName))

        normalColor = self.normalBgColor.palette().color(QPalette.Background)
        ## QCOLOR normalColor

        if mapName != '':
            genConfig = xNormal.generation_options(mapName,
                   width=int(self.sizeWCmb.currentText()),
                   height=int(self.sizeHCmb.currentText()),
                   edge_padding=self.edgeSpinBox.value(),
                   bucket_size=int(self.bucketSizeCmb.currentText()),
                   gen_normals=self.normalMapCbx.isChecked(),
                   tangent_space=self.normalTSCbx.isChecked(),
                   closest_if_fails=self.closesHitCbx.isChecked(),
                   discard_backface_hits=self.discardCbx.isChecked(),
                   normals_x=self.normalSwizzleXCmb.currentText(),
                   normals_y=self.normalSwizzleYCmb.currentText(),
                   normals_z=self.normalSwizzleZCmb.currentText(),
                   gen_heights=self.heightMapCbx.isChecked(),
                   heights_tonemap=self.heightNormalizationCmb.currentText(),
                   heights_min=self.heightManualMinSpinner.value(),
                   heights_max=self.heightManualMaxSpinner.value(),
                   gen_ao=self.aoMapCbx.isChecked(),
                   ao_rays=self.aoRaysSpinner.value(),
                   ao_distribution=self.aoDistributionCmb.currentText(),
                   ao_bias=self.aoBiasSpinner.value(),
                   ao_pure_occlude=self.aoAllow100OccCbx.isChecked(),
                   ao_limit_ray_distance=self.aoLimitRayDstCbx.isChecked(),
                   ao_atten_const=self.aoAttenuationX.value(),
                   ao_atten_linear=self.aoAttenuationY.value(),
                   ao_atten_quadratic=self.aoAttenuationZ.value(),
                   ao_jitter=self.aoJitterCbx.isChecked(),
                   ao_ignore_backfaces=self.aoIgnoreHitsCbx.isChecked()
                                                   )
            config = xNormal.config(highMeshesOptions, lowMeshesOptions, genConfig)

            if createFile and not separatedMeshes:
                saveFile = QFileDialog.getSaveFileName(self, 'Save .XML xNormal Settings')
                if self.pathIsValid(saveFile):
                    file = open(saveFile, 'w')
                    file.write(config)
                    file.close()
                    print 'xNormalBatchBaker: xNormal Settings saved correctly!'

        return config, genTextures

    def _getCheckedBakes(self):
        exportedBakes = []
        if self.normalMapCbx.isChecked():
            exportedBakes.append('_normals')
        if self.heightMapCbx.isChecked():
            exportedBakes.append('_heights')
        if self.aoMapCbx.isChecked():
            exportedBakes.append('_occlusion')
        return exportedBakes

    def _bakeMaps(self):

        # Check if xNormal is already running
        tlcall = 'TASKLIST', '/FI', 'imagename eq xNormal.exe'
        tlproc = subprocess.Popen(tlcall, shell=True, stdout=subprocess.PIPE)
        tlout = tlproc.communicate()[0].strip().split('\r\n')
        if len(tlout) > 1 and 'xNormal.exe' in tlout[-1]:
            cmds.error('xNormalBatchBaker: xNormal is running, close it before bake maps')
            return

        # Set xNormal Path
        xNormal.path = self.xNormalLine.text()

        genTextures = []

        if self.separateMeshesCbx.isChecked():

            # Export low poly meshes
            self.exportLowMeshes()

            validLpMeshes, validHpMeshes = self._getModelsToBake()
            genTextures = []

            for i in range(len(validHpMeshes)):
                config, txt = self._saveSettings(separatedMeshes=True, index=i, createFile=False)
                genTextures.append(txt)
                xNormal.run_config(config)
        else:
            print 'xNormalBatchBaker: NOT IMPLEMENTED YET'
            return

        finalTextures = []
        pathFiles = [f for f in os.listdir(self.bakeExportLine.text()) if os.path.isfile(os.path.join(self.bakeExportLine.text(), f))]

        exportedTypes = self._getCheckedBakes()

        for type in exportedTypes:
            for file in genTextures:
                file = self._getFileBaseName(file[0]) + type + '.' + self.bakeExportFormatCmb.currentText().lower()
                for txt in pathFiles:
                    txt = self._getFileBaseName(txt)
                    if txt in file:
                        finalTextures.append(os.path.abspath(file))

        print finalTextures

        finalMaps = {}
        finalMaps['_normals'] = []
        finalMaps['_heights'] = []
        finalMaps['_occlusion'] = []
        for map in finalTextures:
            if '_normals' in map:
                finalMaps['_normals'].append(map)
            elif '_heights' in map:
                finalMaps['_heights'].append(map)
            elif '_occlusion' in map:
                finalMaps['_occlusion'].append(map)

        # If the user wants auto generate maps
        if self.autoNormalGenCbx.isChecked() and comtypesAvailable:

            psApp = comtypes.client.CreateObject('Photoshop.Application')

            # Save the current preferences
            startRulerUnits = psApp.Preferences.RulerUnits
            startTypeUnits = psApp.Preferences.TypeUnits
            startDisplayDialogs = psApp.DisplayDialogs

            # Set the default unity to pixels
            psApp.Preferences.RulerUnits = 1
            psApp.Preferences.TypeUnits = 1

            # Display no dialogs when opening files
            psApp.DisplayDialogs = 3

            # Close all the open documents
            for i in range(psApp.Documents.Count):
                psApp.ActiveDocument.Close()

            # Create new document to merge all the samples into
            docWidth = int(self.sizeWCmb.currentText())
            docHeight = int(self.sizeHCmb.currentText())
            newDoc = psApp.Documents.Add(docWidth, docHeight, 72, "newTexture", 2, 1, 1)

            checkedTypes = self._getCheckedBakes()

            for type in reversed(checkedTypes):
                self._openTypeInPsAndSave(psApp, newDoc, finalMaps[type], type)

            # Reset application preferences
            psApp.Preferences.RulerUnits = startRulerUnits
            psApp.Preferences.TypeUnits = startTypeUnits
            psApp.DisplayDialogs = startDisplayDialogs

            # Save Document as PSD
            if self.prefixLine.text() != '':
                docName = os.path.abspath(self.bakeExportLine.text() + '/' + self.prefixLine.text() + '_MAPS.psd')
            else:
                docName = os.path.abspath(self.bakeExportLine.text() + '/' + 'EXPORTED_MAPS.psd')
            psdOptions = comtypes.client.CreateObject('Photoshop.PhotoshopSaveOptions')
            psdOptions.annotations = False
            psdOptions.alphaChannels = True
            psdOptions.layers = True
            psdOptions.spotColors = True
            psdOptions.embedColorProfile = True
            psApp.activeDocument.SaveAs(docName, psdOptions)

            for layerSet in psApp.activeDocument.LayerSets:
                layerSet.Visible = True

    def _openTypeInPsAndSave(self, psApp, doc, maps, type):

        # Create new group
        newLayerSet = doc.LayerSets.Add()
        newLayerSet.name = self._getGroupName(type)

        # Create background layer
        bgLayer = newLayerSet.ArtLayers.Add()
        bgLayer.name = self._getGroupName(type) + '_BG'

        # Fill the layer with the appropiate color
        psApp.activeDocument.selection.selectAll
        psApp.activeDocument.selection.Fill(self._getBgColor(type))

        # Load generated maps
        for map in maps:
            psApp.Open(map)
            docName = psApp.ActiveDocument.Name

            # Flatthen document so we get everything and then copy
            psApp.ActiveDocument.flatten()
            psApp.ActiveDocument.Selection.SelectAll()
            psApp.ActiveDocument.Selection.Copy()

            # Don't sae anything we did
            psApp.ActiveDocument.Close(2)

            # Paste content into the original document
            psApp.ActiveDocument.Paste()

            # Change layer name
            psApp.ActiveDocument.ActiveLayer.Name = docName

        # Sets Layers blending mode to Overlay
        for i in range(1, newLayerSet.Layers.Count):
            layer = newLayerSet.Layers(i)
            layer.BlendMode = self._getBlendMode(type)

        self._saveDocument(psApp, type)

        newLayerSet.Visible = False

    def _saveDocument(self, psApp, type):

        docExt = self.bakeExportFormatCmb.currentText().lower()
        savePath = self.bakeExportLine.text()

        if self.prefixLine.text() != '':
            name = os.path.abspath(savePath + '/' + self.prefixLine.text() + '_' + self._getGroupName(type) + '_MAP.' + docExt)
        else:
            name = os.path.abspath(savePath + '/' + self._getGroupName(type) + '_MAP.' + docExt)

        print 'SAVE DOCUMENT INFO'
        print '-------------------'
        print type
        print docExt
        print savePath
        print name

        if docExt == 'bmp':
            options = comtypes.client.CreateObject('Photoshop.BMPSaveOptions')
            PsBMPBitsPerPixels = 24
            options.AlphaChannels = False
            options.Depth = PsBMPBitsPerPixels
        elif docExt == 'jpg':
            options = comtypes.client.CreateObject('Photoshop.JPEGSaveOptions')
            options.Quality = 12
        elif docExt == 'png':
            options = comtypes.client.CreateObject('Photoshop.PNGSaveOptions')
        elif docExt == 'tga':
            options = comtypes.client.CreateObject('Photoshop.TargaSaveOptions')
            PsTargaBitsPerPixels = 24
            options.Resolution = PsTargaBitsPerPixels
            options.AlphaChannels = False
            options.RLECompression = False
        elif docExt == 'tiff':
            options = comtypes.client.CreateObject('Photoshop.TiffSaveOptions')
            options.AlphaChannels = False
            options.Annotations = False
            options.Layers = False
            options.Transparency = False
        elif docExt == 'raw':
            options = comtypes.client.CreateObject('Photoshop.RawSaveOptions')
            options.AlphaChannels = False

        # When working with tgas we have to flatten the active document first
        if docExt == 'tga':
            savedState = psApp.activeDocument.activeHistoryState
            psApp.activeDocument.flatten()
            psApp.activeDocument.Copy()
            if savePath != '':
                psApp.activeDocument.SaveAs(name, options)
            psApp.activeDocument.ActiveHistoryState = savedState
        else:
            if savePath != '':
                print 'SAVING DOCUMENT ...'
                psApp.activeDocument.SaveAs(name, options)

    def _getGroupName(self, type):
        if type == '_normals':
            return 'NORMAL'
        elif type == '_heights':
            return 'HEIGHT'
        elif type == '_occlusion':
            return 'AO'

    def _getBgColor(self, type):
        bgColor = comtypes.client.CreateObject('Photoshop.SolidColor')
        if type == '_normals':
            bgColor.rgb.red = 128
            bgColor.rgb.green = 128
            bgColor.rgb.blue = 255
        elif type == '_heights':
            bgColor.rgb.red = 0
            bgColor.rgb.green = 0
            bgColor.rgb.blue = 0
        elif type == '_occlusion':
            bgColor.rgb.red = 255
            bgColor.rgb.green = 255
            bgColor.rgb.blue = 255
        return bgColor

    def _getBlendMode(self, type):
        blendMode = 0
        if type == '_normals':
            blendMode = 12
        elif type == '_heights':
            blendMode = 2
        elif type == '_occlusion':
            blendMode = 5
        return blendMode


    def _getFileBaseName(self, file):
        return file.split('.')[0].split('/')[-1]

    def _showNamingConventions(self):
        namingDialog(self).show()

    def _updateState(self):

        if self.pathIsValid(self.highDefLine.text()):
            self.highDefUpdateBtn.setEnabled(True)
        else:
            self.highDefUpdateBtn.setEnabled(False)

        if self.highMeshesTable.rowCount() > 0:
            self.highDefClearBtn.setEnabled(True)
            self.highDefSelectAllBtn.setEnabled(True)
            self.highDefDeselectAllBtn.setEnabled(True)
        else:
            self.highDefClearBtn.setEnabled(False)
            self.highDefSelectAllBtn.setEnabled(False)
            self.highDefDeselectAllBtn.setEnabled(False)

        if len(self.highMeshesTable.selectedItems()) > 0:
            self.highDefRemoveItemBtn.setEnabled(True)
            self.highDefToggleBakeBtn.setEnabled(True)
        else:
            self.highDefRemoveItemBtn.setEnabled(False)
            self.highDefToggleBakeBtn.setEnabled(False)

        # --------------------------------------------------------------

        if self.xNormalLine.text() != '' and self.pathIsValid(self.bakeExportLine.text()) and self.outputFileLine.text() != '' and self.highMeshesTable.rowCount() > 0 and self.lowMeshesTable.rowCount() > 0:
            # xNormal App validation
            if os.path.isfile(self.xNormalLine.text()):
                self.bakeMapsBtn.setEnabled(True)
        else:
            self.bakeMapsBtn.setEnabled(False)

        # --------------------------------------------------------------

        if self.pathIsValid(self.lowDefLine.text()):
            self.lowDefAddSelectedBtn.setEnabled(True)
        else:
            self.lowDefAddSelectedBtn.setEnabled(False)

        sel = cmds.ls(selection=True, type='transform')
        if len(sel) > 0:
            lowMeshItems = []
            if self.lowMeshesTable.rowCount() > 0:
                for row in range(self.lowMeshesTable.rowCount()):
                    lowMeshItems.append(self.lowMeshesTable.item(row, 1).text())

            if(self.lowMeshesTable.rowCount()) > 0:
                self.lowDefRemoveSelectedBtn.setEnabled(True)
            else:
                self.lowDefRemoveSelectedBtn.setEnabled(False)
                self.lowDefAddSelectedBtn.setEnabled(True)

            for obj in sel:
                if obj in lowMeshItems:
                    self.lowDefAddSelectedBtn.setEnabled(False)
                    self.lowDefRemoveSelectedBtn.setEnabled(True)
                else:
                    self.lowDefAddSelectedBtn.setEnabled(True)
                    self.lowDefRemoveSelectedBtn.setEnabled(False)
        else:
            self.lowDefAddSelectedBtn.setEnabled(False)
            self.lowDefRemoveSelectedBtn.setEnabled(False)

        if self.lowMeshesTable.rowCount() > 0:
            self.lowDefClearBtn.setEnabled(True)
            self.lowDefSelectAllBtn.setEnabled(True)
            self.lowDefDeselectAllBtn.setEnabled(True)
            self.lowDefDetectHP.setEnabled(True)
        else:
            self.lowDefClearBtn.setEnabled(False)
            self.lowDefSelectAllBtn.setEnabled(False)
            self.lowDefDeselectAllBtn.setEnabled(False)
            self.lowDefDetectHP.setEnabled(False)

        if len(self.lowMeshesTable.selectedItems()) > 0:
            self.lowDefRemoveItemBtn.setEnabled(True)
            self.lowDefToggleBakeBtn.setEnabled(True)
        else:
            self.lowDefRemoveItemBtn.setEnabled(False)
            self.lowDefToggleBakeBtn.setEnabled(False)

        # Check if we can bake
        if self.separatorLine.text != '' and self.prefixLine.text() != '' and self.hpSuffixLine.text() != '' and self.highDefLine.text() != '' and self.highMeshesTable.rowCount() > 0 and self.lowMeshesTable.rowCount() > 0 and self.lowDefLine.text() != '' and len(self._getCheckedBakes()) > 0 and self.outputFileLine.text() != '' and self.bakeExportLine.text() != '':
            self.bakeMapsBtn.setEnabled(True)
        else:
            self.bakeMapsBtn.setEnabled(False)

    def pathIsValid(self, path):
        if path != '':
            if os.path.exists(path):
                return True
        return False

    def _setDefault(self, type=''):
        if type == 'normal':
            self.normalSwizzleXCmb.setCurrentIndex(1)
            self.normalSwizzleYCmb.setCurrentIndex(2)
            self.normalSwizzleZCmb.setCurrentIndex(4)
            self.normalTSCbx.setChecked(True)
            self.normalBgColor.setStyleSheet("background-color:rgb(128, 128, 255);")
        elif type == 'height':
            self.heightBgColor.setStyleSheet('background-color:rgb(0,0,0);')
            self.heightNormalizationCmb.setCurrentIndex(0)
            self.heightManualMinSpinner.setValue(-100.0)
            self.heightManualMaxSpinner.setValue(-100.0)
        elif type == 'bakeBase':
            self.bakeBaseWriteObjIDCbx.setChecked(False)
            self.bakeBaseDrawColorCbx.setChecked(True)
            self.bakeBaseDrawColor.setStyleSheet('background-color:rgb(255, 0, 0);')
            self.bakeBaseBgColor.setStyleSheet('background-color:rgb(0, 0, 0);')

        elif type == 'ao':
            self.aoRaysSpinner.setValue(128)
            self.aoDistributionCmb.setCurrentIndex(0)
            self.aoOccludedColor.setStyleSheet('background-color:rgb(0,0,0);')
            self.aoUnoccludedColor.setStyleSheet('background-color:rgb(255, 255, 255);')
            self.aoBiasSpinner.setValue(0.08)
            self.aoSpreadAngleSpinner.setValue(162.0)
            self.aoLimitRayDstCbx.setChecked(False)
            self.aoAttenuationX.setValue(1.0)
            self.aoAttenuationY.setValue(0.0)
            self.aoAttenuationZ.setValue(0.0)
            self.aoJitterCbx.setChecked(False)
            self.aoIgnoreHitsCbx.setChecked(False)
            self.aoAllow100OccCbx.setChecked(True)
            self.aoBgColor.setStyleSheet('background-color:rgb(255,255,255);')

    def _toggleSettings(self, type):
        if type == 'normal':
            self.normalMapSettingsGrp.setVisible(not self.normalMapSettingsGrp.isVisible())
        elif type == 'height':
            self.heightMapSettingsGrp.setVisible(not self.heightMapSettingsGrp.isVisible())
        elif type == 'ao':
            self.aoMapSettingsGrp.setVisible(not self.aoMapSettingsGrp.isVisible())
        elif type == 'convexity':
            self.convexityMapSettingsGrp.setVisible(not self.convexityMapSettingsGrp.isVisible())
        elif type == 'thickness':
            self.thicknessMapSettingsGrp.setVisible(not self.thicknessMapSettingsGrp.isVisible())
        elif type == 'cavity':
            self.cavityMapSettingsGrp.setVisible(not self.cavityMapSettingsGrp.isVisible())
        elif type == 'bakeHP':
            self.bakeHPSettingsGrp.setVisible(not self.bakeHPSettingsGrp.isVisible())
        elif type == 'curavture':
            self.curvatureSettingsGrp.setVisible(not self.curvatureSettingsGrp.isVisible())
        elif type == 'translucency':
            self.translucencyMapSettingsGrp.setVisible(not self.translucencyMapSettingsGrp.isVisible())

    def setPath(self, type):
        if type == 'high':
            file = str(QFileDialog.getExistingDirectory(self, 'Select Directory where HP meshes are stored'))
            if file != '':
                self.highDefLine.setText(file)
                self.getModels('high')
        elif type == 'low':
            file = str(QFileDialog.getExistingDirectory(self, 'Select Directory where LP meses will be stored'))
            if file != '':
                self.lowDefLine.setText(file)
        elif type == 'output':
            file = str(QFileDialog.getExistingDirectory(self, 'Select Directory where output maps will be stored'))
            if file != '':
                self.bakeExportLine.setText(file)
        elif type == 'xNormal':
            file = str(QFileDialog.getOpenFileName(self, 'Select xNormal App .EXE')[0])
            if file != '':
                self.xNormalLine.setText(file)
        self._updateState()

    def getModels(self, type):

        if type == 'high':
            if self.pathIsValid(self.highDefLine.text()):
                self.highMeshesTable.clearData()
                for file in os.listdir(self.highDefLine.text()):
                    if file.endswith((('.fbx', '.obj', '.FBX', '.OBJ'))):
                        self.addToList(file, type='high')
        elif type == 'low':
            self.lowMeshesTable.clearData()
            sel = cmds.ls(selection=True, type='transform')
            for obj in sel:
                self.addToList(obj, type='low')
        self._updateState()
        self.detectHP()

    def addToList(self, item, type):
        if type == 'high':
            itemToAdd = [True, item]
            self.highMeshesTable.addItem(itemToAdd)
        elif type == 'low':
            itemToAdd = [True, item, False, False]
            self.lowMeshesTable.addItem(itemToAdd)
        self._updateState()

    def clearList(self, type):
        if type == 'high':
            self.highMeshesTable.clearData()
        elif type == 'low':
            self.lowMeshesTable.clearData()
        self._updateState()
        self.detectHP()

    def removeItem(self, row, type):
        if type == 'high':
            self.highMeshesTable.removeRow(row)
        elif type == 'low':
            self.lowMeshesTable.removeRow(row)
        self._updateState()
        self.detectHP()

    def removeSelectedItems(self, type):
        if type == 'high':
            for row in range(len(self.highMeshesTable.selectedItems()), -1, -1):
                self.highMeshesTable.removeRow(row)
        elif type == 'low':
            for row in range(len(self.lowMeshesTable.selectedItems()), -1, -1):
                self.lowMeshesTable.removeRow(row)
        self._updateState()
        self.detectHP()

    def selectAll(self, type):
        if type == 'high':
            self.highMeshesTable.selectAll()
        elif type == 'low':
            self.lowMeshesTable.selectAll()
        self._updateState()

    def clearSelection(self, type):
        if type == 'high':
            self.highMeshesTable.clearSelection()
        elif type == 'low':
            self.lowMeshesTable.clearSelection()
        self._updateState()

    def exportLowMeshes(self):
        if self.lowMeshesTable.rowCount() > 0:
            for row in range(self.lowMeshesTable.rowCount()):
                meshName = self.lowMeshesTable.item(row, 1).text()
                cmds.select(meshName)
                if len(cmds.ls(sl=True)) > 0:
                    cmds.file(self.lowDefLine.text() + '//' + meshName + '.obj', force=True, type='OBJexport', options="materials=0, smoothing=1, normals=1", exportSelected=True)

    def toggleBake(self, type):
        if type == 'high':
            for item in self.highMeshesTable.selectedItems():
                widget = self.highMeshesTable.cellWidget(item.row(), 0)
                cbx = widget.findChild(QCheckBox)
                if cbx:
                    cbx.setChecked(not cbx.isChecked())
        elif type == 'low':
            for item in self.lowMeshesTable.selectedItems():
                widget = self.lowMeshesTable.cellWidget(item.row(), 0)
                cbx = widget.findChild(QCheckBox)
                if cbx:
                    cbx.setChecked(not cbx.isChecked())

    def detectHP(self):
        lowMeshItems = []
        lowMeshCheckedItems = []
        if self.lowMeshesTable.rowCount() > 0:
            for row in range(self.lowMeshesTable.rowCount()):
                lowMeshItems.append(self.lowMeshesTable.item(row, 1))
                lowMeshCheckedItems.append(self.lowMeshesTable.item(row, 2))

        highMeshItems = []
        if self.highMeshesTable.rowCount() > 0:
            for row in range(self.highMeshesTable.rowCount()):
                highMeshItems.append(self.highMeshesTable.item(row, 1))

        if self.highMeshesTable.rowCount() > 0:
            for hpMesh in highMeshItems:
                hpMeshName = self._getBaseName(hpMesh.text())
                for i, lpMesh in enumerate(lowMeshItems):
                    lpMeshName = self._getBaseName(lpMesh.text())
                    if hpMeshName == lpMeshName:
                        lowMeshCheckedItems[i].setText('Yes')
                        greenBrush = QBrush(QColor(75, 165, 90))
                        lowMeshCheckedItems[i].setBackground(greenBrush)
                        break
        else:
            for lpMesh in lowMeshCheckedItems:
                lpMesh.setText('No')
                redBrush = QBrush(QColor(165, 70, 70))
                lpMesh.setBackground(redBrush)

    def _getBaseName(self, name):
        finalName = ''
        tokens = name.split(self.separatorLine.text())

        # No suffix or prefix
        if len(tokens) == 1:
            finalName = tokens[0]
        else:
            if len(tokens) == 2:
                if tokens[0] == self.prefixLine.text():
                    finalName = tokens[1]
                else:
                    finalName = tokens[0]
            else:
                finalName = tokens[1]
        return finalName

    def _getOutputName(self, mesh=''):
        name = self.outputFileLine.text()
        if name != '':
            splitName = name.split(self.separatorLine.text())
            finalNames = []
            finalName = ''
            for n in splitName:
                finalNames.append(n.split('$')[1])

            for i,n in enumerate(finalNames):
                if n != '':
                    if i == 0:
                        name = self._changeOut(n, mesh)
                    else:
                        name = name + '_' + self._changeOut(n, mesh)

        return name

    def _changeOut(self, type, mesh=''):
      if type == 'hpMesh':
          return self.highDefLine.text()
      elif type == 'lpMesh':
          return self.lowDefLine.text()
      elif type == 'prefix':
          return self.prefixLine.text()
      elif type == 'name':
          if mesh is None:
              return ''
          else:
            return mesh

class meshesTable(QTableWidget, object):
    def __init__(self, data=[], type='high', *args):
        QTableWidget.__init__(self, *args)
        self.data = data
        self.setData()
        self.type = type
        try:
            self.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        except:
            self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        if self.type == 'low':
            self.setHorizontalHeaderLabels(('Bake', 'Name', 'High Poly Exists?', 'Cage Exists?'))
        else:
            self.setHorizontalHeaderLabels(('Bake', 'Name'))

    def setData(self):
        row = 0
        for item in self.data:
            column = 0
            for value in item:
                newItem = QTableWidgetItem()
                newItem.setTextAlignment(Qt.AlignCenter)
                if column == 0:
                    newItem = QWidget()
                    l = QHBoxLayout()
                    l.setAlignment(Qt.AlignCenter)
                    cbx = QCheckBox()
                    cbx.setChecked(True)
                    l.addWidget(cbx)
                    newItem.setLayout(l)
                    self.setCellWidget(row, column, newItem)
                else:
                    if column == 2:
                        if str(value) == 'True':
                            value = 'Yes'
                        else:
                            value = 'No'
                    elif column == 3:
                        if str(value) == 'True':
                            value = 'Nombre malla'
                        else:
                            value = 'No'
                    else:
                        value = str(value)
                        newItem.setText(value)
                        self.setItem(row, column, newItem)
                column += 1
            row += 1

    def updateData(self, data):
        self.data = data
        self.setData()

    def clearData(self):
        for row in range(self.rowCount(), -1, -1):
            self.removeRow(row)

    def addItem(self, item):

        rowPos = self.rowCount()
        self.insertRow(rowPos)

        newItem = QTableWidgetItem()
        newItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        newItem.setTextAlignment(Qt.AlignCenter)
        newItem.setText(str(item[1]))

        itemCbx = QWidget()
        l = QHBoxLayout()
        l.setAlignment(Qt.AlignCenter)
        cbx = QCheckBox()
        cbx.setChecked(True)
        l.addWidget(cbx)
        itemCbx.setLayout(l)

        self.setCellWidget(rowPos, 0, itemCbx)
        self.setItem(rowPos, 0, QTableWidgetItem())
        self.setItem(rowPos, 1, newItem)

        if self.type == 'low':
            if str(item[2]) == 'True':
                value = 'Yes'
            else:
                value = 'No'
            newItem = QTableWidgetItem()
            newItem.setTextAlignment(Qt.AlignCenter)
            newItem.setText(value)
            self.setItem(rowPos, 2, newItem)

            if str(value) == 'True':
                value = 'Nombre malla'
            else:
                value = 'No'
            newItem.setText(value)
            self.setItem(rowPos, 3, newItem)

class namingDialog(QDialog, object):
    def __init__(self, parent=None):
        super(namingDialog, self).__init__(parent)
        self.setWindowTitle('Naming Conventions')

        mainLayout = QVBoxLayout()
        prefixLayout = QHBoxLayout()
        nameLayout = QHBoxLayout()
        lpLayout = QHBoxLayout()
        hpLayout = QHBoxLayout()
        matTypeLayout = QHBoxLayout()

        prefixLbl = QLabel('$prefix: Mesh Prefix')
        nameLbl = QLabel('$name: Name of the Mesh')
        lpLbl = QLabel('$lpMesh: Low-Poly Mesh Name')
        hpLbl = QLabel('$hpMesh: High-Poly Mesh Name')
        mapLbl = QLabel('$mapType: Map Type Name')
        prefixBtn = QPushButton('>')
        nameBtn = QPushButton('>')
        lpBtn = QPushButton('>')
        hpBtn = QPushButton('>')
        mapBtn = QPushButton('>')
        prefixBtn.setMaximumWidth(50)
        nameBtn.setMaximumWidth(50)
        lpBtn.setMaximumWidth(50)
        hpBtn.setMaximumWidth(50)
        mapBtn.setMaximumWidth(50)

        mainLayout.addLayout(prefixLayout)
        mainLayout.addLayout(nameLayout)
        mainLayout.addLayout(lpLayout)
        mainLayout.addLayout(hpLayout)
        mainLayout.addLayout(matTypeLayout)

        prefixLayout.addWidget(prefixLbl)
        prefixLayout.addWidget(prefixBtn)
        nameLayout.addWidget(nameLbl)
        nameLayout.addWidget(nameBtn)
        lpLayout.addWidget(lpLbl)
        lpLayout.addWidget(lpBtn)
        hpLayout.addWidget(hpLbl)
        hpLayout.addWidget(hpBtn)
        matTypeLayout.addWidget(mapLbl)
        matTypeLayout.addWidget(mapBtn)

        self.setLayout(mainLayout)

        # === SIGNALS === #
        prefixBtn.clicked.connect(partial(self.addNaming, 'prefix'))
        nameBtn.clicked.connect(partial(self.addNaming, 'name'))
        lpBtn.clicked.connect(partial(self.addNaming, 'lp'))
        hpBtn.clicked.connect(partial(self.addNaming, 'hp'))
        mapBtn.clicked.connect(partial(self.addNaming, 'mapType'))

    def addNaming(self, type):

        if type == 'prefix':
            name = '$prefix'
        if type == 'name':
            name = '$name'
        if type == 'lp':
            name = '$lpMesh'
        elif type == 'hp':
            name = '$hpMesh'
        elif type == 'mapType':
            name = '$mapType'

        if self.parent().outputFileLine.text() == '':
            self.parent().outputFileLine.setText(name)
        else:
            self.parent().outputFileLine.setText(self.parent().outputFileLine.text() + self.parent().separatorLine.text() + name)
        pass

class QColorLabel(QLabel, object):
    def __init__(self, parent=None):
        super(QColorLabel, self).__init__(parent)

    def mousePressEvent(self, event):
        self.setColor()

    def setColor(self):
        color = QColorDialog.getColor()
        self.setStyleSheet('background-color:rgb('+str(color.red())+','+str(color.green())+','+str(color.blue())+');')

def _getMayaWindow():

    """
    Return the Maya main window widget as a Python object
    @return: Maya main window
    """

    ptr = OpenMayaUI.MQtUtil.mainWindow()
    if ptr is not None:
        return wrapInstance(long(ptr), QMainWindow)
        
xNormalBatchBaker()