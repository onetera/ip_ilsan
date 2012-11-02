#encoding=utf-8
#!/usr/bin/env python

#-------------------------------------------------------------------------------
#
#   RenderMan TD
#
#       Sanghun Kim, masin77@gmail.com
#
#-------------------------------------------------------------------------------

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

try :
	from pymel.all import *
	standAlone = False
except ImportError :
	standAlone = True

		
import os, sys
import string, json, fnmatch

import cacheFileLoader
#reload(cacheFileLoader)
#-------------------------------------------------------------------------------
#
#   MrGo Production
#
#-------------------------------------------------------------------------------
# Import Tool
imp_basePath = os.path.dirname(__file__)
imp_uifile = os.path.join(imp_basePath, "ui", "show_mrgo_import.ui")
class mrgoImport_UI(QDialog):
	def __init__(self, parent=None):
		QDialog.__init__(self, parent)
		uic.loadUi(imp_uifile, self)

		# icon
		self.communicate_icon = QIcon()
		self.communicate_icon.addFile(os.path.join(imp_basePath, 'resources', 'communicate.gif'))

		# Hide Widget
		self.anim_fdlist.hide()
		self.geo_fdlist.hide()
		self.zfur_fdlist.hide()
		self.cam_fdlist.hide()

		# Directory
		self.currentDirectory = ''
		self.directory_current()
		self.directory_setup()
		self.path_label.setText(' Path : %s' % self.currentDirectory)

		# File Tree
		self.file_model = QFileSystemModel()
		self.file_model.setRootPath(QDir.rootPath())
		self.treeView.setModel(self.file_model)
		self.treeView.hideColumn(1)
		self.treeView.hideColumn(2)
		self.treeView.hideColumn(3)
		self.treeView.setHeaderHidden(True)
		self.treeView.setRootIndex(self.file_model.index(self.currentDirectory))

		# Global value
		self.anim_item_row = -1
		self.geo_item_row = -1
		self.zfur_item_row = -1
		self.cam_item_row = -1

		# Button Icon
		self.anim_inout_pushButton.setIcon(self.communicate_icon)
		self.geo_inout_pushButton.setIcon(self.communicate_icon)
		self.zfur_inout_pushButton.setIcon(self.communicate_icon)
		self.cam_inout_pushButton.setIcon(self.communicate_icon)

		# Button Command Bind
		self.shot_comboBox.activated.connect(self.directory_change)
		self.anim_inout_pushButton.clicked.connect(self.anim_inout_process)
		self.geo_inout_pushButton.clicked.connect(self.geo_inout_process)
		self.zfur_inout_pushButton.clicked.connect(self.zfur_inout_process)
		self.cam_inout_pushButton.clicked.connect(self.cam_inout_process)
		# ListWidget Command Bind
		self.anim_list.itemClicked.connect(self.anim_click_process)
		self.anim_list.itemDoubleClicked.connect(self.anim_dclick_process)
		self.geo_list.itemClicked.connect(self.geo_click_process)
		self.geo_list.itemDoubleClicked.connect(self.geo_dclick_process)
		self.zfur_list.itemClicked.connect(self.zfur_click_process)
		self.zfur_list.itemDoubleClicked.connect(self.zfur_dclick_process)
		self.cam_list.itemClicked.connect(self.cam_click_process)
		self.cam_list.itemDoubleClicked.connect(self.cam_dclick_process)

		self.import_pushButton.clicked.connect(self.import_process)
	
	def directory_change(self):
		citem = str(self.shot_comboBox.currentText())
		bpath = os.path.dirname(self.currentDirectory)
		self.currentDirectory = os.path.abspath(bpath + '/' + citem)
		#
		self.path_label.setText(' Path : %s' % self.currentDirectory)
		self.treeView.setRootIndex(self.file_model.index(self.currentDirectory))
		self.directory_setup()
	
	def directory_current(self):
		currentPath = sceneName()
		if currentPath:
			proj = os.path.dirname(os.path.dirname(currentPath))
		else:
			proj = os.path.dirname(workspace(q=True, rd=True))
		self.currentDirectory = os.path.abspath(proj + '/../../')
	
	def directory_setup(self):
		self.shot_comboBox.clear()
		self.shot_comboBox.addItems(['', '..'])
		bpath = os.path.dirname(self.currentDirectory)
		for i in os.listdir(bpath):
			if os.path.isdir(os.path.join(bpath, i)):
				self.shot_comboBox.addItem(i)

	def anim_inout_process(self):
		focus = self.anim_list.hasFocus()
		if focus:
			currentRow = self.anim_list.currentRow()
			if int(currentRow) > -1:
				self.anim_list.takeItem(currentRow)
				self.anim_fdlist.takeItem(currentRow)
		else:
			currentItem = str(self.file_model.filePath(self.treeView.currentIndex()))
			if os.path.isfile(currentItem):
				if currentItem.split('.')[-1] == 'anim':
					self.anim_list.addItem(os.path.basename(currentItem))
					self.anim_fdlist.addItem(os.path.dirname(currentItem))
	def anim_click_process(self):
		currentRow = self.anim_list.currentRow()
		if self.anim_item_row == currentRow:
			self.anim_list.setCurrentRow(-1)
			self.anim_item_row = -1
		else:
			self.anim_item_row = currentRow
	def anim_dclick_process(self):
		currentRow = self.anim_list.currentRow()
		self.anim_list.takeItem(currentRow)
		self.anim_fdlist.takeItem(currentRow)

	def geo_inout_process(self):
		focus = self.geo_list.hasFocus()
		if focus:
			currentRow = self.geo_list.currentRow()
			if int(currentRow) > -1:
				self.geo_list.takeItem(currentRow)
				self.geo_fdlist.takeItem(currentRow)
		else:
			currentItem = str(self.file_model.filePath(self.treeView.currentIndex()))
			if os.path.isdir(currentItem):
				self.geo_list.addItem(os.path.basename(currentItem))
				self.geo_fdlist.addItem(os.path.dirname(currentItem))
	def geo_click_process(self):
		currentRow = int(self.geo_list.currentRow())
		if self.geo_item_row == currentRow:
			self.geo_list.setCurrentRow(-1)
			self.geo_item_row = -1
		else:
			self.geo_item_row = currentRow
	def geo_dclick_process(self):
		currentRow = self.geo_list.currentRow()
		self.geo_list.takeItem(currentRow)
		self.geo_fdlist.takeItem(currentRow)
	
	def zfur_inout_process(self):
		pass
	def zfur_click_process(self):
		pass
	def zfur_dclick_process(self):
		pass

	def cam_inout_process(self):
		focus = self.cam_list.hasFocus()
		if focus:
			currentRow = self.cam_list.currentRow()
			if int(currentRow) > -1:
				self.cam_list.takeItem(currentRow)
				self.cam_fdlist.takeItem(currentRow)
		else:
			currentItem = str(self.file_model.filePath(self.treeView.currentIndex()))
			if os.path.isfile(currentItem):
				ext = currentItem.split('.')[-1]
				if ext == 'mb' or ext == 'ma':
					self.cam_list.addItem(os.path.basename(currentItem))
					self.cam_fdlist.addItem(os.path.dirname(currentItem))
	def cam_click_process(self):
		currentRow = int(self.cam_list.currentRow())
		if self.cam_item_row == currentRow:
			self.cam_list.setCurrentRow(-1)
			self.cam_item_row = -1
		else:
			self.cam_item_row = currentRow
	def cam_dclick_process(self):
		currentRow = self.cam_list.currentRow()
		self.cam_list.takeItem(currentRow)
		self.cam_fdlist.takeItem(currentRow)
	
	def import_process(self):
		# anim file
		anim_filenames = []
		for i in range(int(self.anim_list.count())):
			file = str(self.anim_list.item(i).text())
			path = str(self.anim_fdlist.item(i).text())
			anim_filenames.append(os.path.join(path, file))
		# geo cache
		geo_dirnames = []
		for i in range(int(self.geo_list.count())):
			file = str(self.geo_list.item(i).text())
			path = str(self.geo_fdlist.item(i).text())
			geo_dirnames.append(os.path.join(path, file))
		# cam file
		cam_filenames = []
		for i in range(int(self.cam_list.count())):
			file = str(self.cam_list.item(i).text())
			path = str(self.cam_fdlist.item(i).text())
			cam_filenames.append(os.path.join(path, file))
		#print anim_filenames, geo_dirnames, cam_filenames
		if anim_filenames:
			mrgo_animImport(anim_filenames[0])
		hidden_file = '/show/mrgo/assets/char/mrgo/render/pub/script/mrgo.hide'
		if geo_dirnames:
			for i in geo_dirnames:
				mrgo_GeoCacheFile(hidden_file, i)
		if cam_filenames:
			for i in cam_filenames:
				importFile(i, options='v=0', loadReferenceDepth='all')
		mrgoImportWindow.close()

def mrgoImportTool():
	global mrgoImportWindow
	mrgoImportWindow = mrgoImport_UI()
	mrgoImportWindow.show()

#-------------------------------------------------------------------------------
#
#	MrGo anim-file import
#
#-------------------------------------------------------------------------------
keydata = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
init_zero = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
init_one = ['sx', 'sy', 'sz']
def mrgo_animImport(filename):
	if ls(sl=True):
		if not pluginInfo('animImportExport', l=True, q=True):
			loadPlugin('animImportExport')
		# initialize
		for i in ls(sl=True):
			for d in i.connections(type='animCurve'):
				delete(d)
			for x in init_zero:
				i.setAttr(x, 0)
			for x in init_one:
				i.setAttr(x, 1)
		try:
			importFile(filename, options='targetTime=4;copies=1;option=replace;pictures=0;connect=0;',
					   loadReferenceDepth='all')
		except: pass

#-------------------------------------------------------------------------------
#
#	MrGo Geometry Cache import & Hide Object
#
#-------------------------------------------------------------------------------
# Dialog
def mrgo_CacheDialog():
	# anim data
	if ls(sl=True):
		if not pluginInfo('animImportExport', l=True, q=True):
			loadPlugin('animImportExport')
		animfile = fileDialog2(fileMode=1, caption='Select Anim File',
							   ds=2, fileFilter='*.anim', okc='Select')
		if animfile:
			# initialize
			for i in ls(sl=True):
				for d in i.connection(type='animCurve'):
					delete(d)
				for x in init_zero:
					i.setAttr(x, 0)
				for x in init_one:
					i.setAttr(x, 1)
			try:
				importFile(animfile[0], options='targetTime=4;copies=1;option=replace;pictures=0;connect=0;',
						   loadReferenceDepth='all')
			except: pass
	filename = fileDialog2(fileMode=3, caption='Select GeoCache Directory',
						   ds=2, okc='Select')
	if filename:
		hidden_file = '/show/mrgo/assets/char/mrgo/render/pub/script/mrgo.hide'
		mrgo_GeoCacheFile(hidden_file, filename[0])


def mrgo_GeoCacheFile(hiddenfile, cacheDir):
	# mesh hide
	hideMesh = []
	if os.path.exists(hiddenfile):
		f = open(hiddenfile, 'r')
		info = f.read()
		f.close()
		hideMesh = json.loads(info)

	# cache directory
	cacheMesh = []
	cacheStartTime = 0;
	cacheEndTime = 0;
	timePerFrame = 0;
	xml_files = []
	for i in os.listdir(cacheDir):
		if fnmatch.fnmatch(i, '*.xml'):
			xml_files.append(os.path.join(cacheDir, i))
	if xml_files:
		for f in xml_files:
			cacheClass = cacheFileLoader.MayaGeoCacheFile()
			cacheClass.dimport(f)
			cacheStartTime = cacheClass.m_cacheStartTime;
			cacheEndTime = cacheClass.m_cacheEndTime;
			timePerFrame = cacheClass.m_timePerFrame;
			for i in cacheClass.m_channels:
				spn = cacheFileLoader.findTargetMesh(i)
				if spn:
					cacheMesh.append(spn)
	#print cacheMesh
	for m in hideMesh:
		if objExists(m):
			node = PyNode(m)
			if m in cacheMesh:
				node.firstParent().setAttr('visibility', 1)
			else:
				node.firstParent().setAttr('visibility', 0)
	# playbackoption set
	playbackOptions(ast = cacheStartTime / timePerFrame)
	playbackOptions(min = 101)
	playbackOptions(max = cacheEndTime / timePerFrame - 1)
	playbackOptions(aet = cacheEndTime / timePerFrame)
