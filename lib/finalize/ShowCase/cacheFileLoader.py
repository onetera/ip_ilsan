#encoding=utf-8
#!/usr/bin/env python

#-------------------------------------------------------------------------------
#
#   RenderMan TD
#
#       Sanghun Kim, masin77@gmail.com
#
#-------------------------------------------------------------------------------
try :
	from pymel.all import *
	standAlone = False
except :
	standAlone = True
	print 'Module import error'
import os
import re
from xml.dom import minidom

#-------------------------------------------------------------------------------
#
#	Extra
#
#-------------------------------------------------------------------------------
def findTargetMesh(shapename):
	mesh = shapename
	if not objExists(mesh):
		if len(shapename.split(':')) > 1:
			mesh = shapename.split(':')[-1]
		if len(shapename.split('Deformed')) > 1:
			mesh = shapename.split('Deformed')[0]
	if objExists(mesh):
		return mesh


#-------------------------------------------------------------------------------
#
#	Maya Geometry Cachefile
#
#-------------------------------------------------------------------------------
class MayaGeoCacheFile:
	def __init__(self):
		self.m_fileName = ''
		self.m_baseDir = ''
		self.m_baseName = ''
		self.m_cacheType = ''
		self.m_cacheStartTime = 0
		self.m_cacheEndTime = 0
		self.m_timePerFrame = 0
		self.m_frameOffset = 10
		self.m_version = .0
		self.m_channels = {}
		self.m_selectedMesh = ''
	
	def dimport(self, fileName):
		self.m_fileName = fileName
		self.m_baseDir = os.path.dirname(fileName)
		self.m_baseName = os.path.splitext(os.path.basename(fileName))[0]
		self.parseDescriptionFile()

		for shape in self.m_channels:
			if self.m_selectedMesh:
				shapename = self.m_selectedMesh
			else:
				shapename = findTargetMesh(shape)
			if shapename:
				cacheNode = ''
				for h in listHistory(shapename):
					if h.type() == 'cacheFile':
						cacheNode = h
				if cacheNode:
					try:
						self.setCacheAttributes(cacheNode)
					except: pass
				else:
					try:
						self.connectCacheNode(shapename)
					except: pass
	
	def connectCacheNode(self, shapename):
		switch = mel.eval('createHistorySwitch("%s", false)' % shapename)
		cacheNode = cacheFile(dir=self.m_baseDir, f=self.m_baseName,
							  ia='%s.inp[0]' % switch, attachFile=True)
		setAttr('%s.playFromCache' % switch, 1)

	def setCacheAttributes(self, cacheNode):
		cacheNode.setAttr('cachePath', self.m_baseDir, type='string')
		cacheNode.setAttr('cacheName', self.m_baseName, type='string')
		startFrame = self.m_cacheStartTime/self.m_timePerFrame
		endFrame = self.m_cacheEndTime/self.m_timePerFrame
		cacheNode.setAttr('startFrame', startFrame)
		cacheNode.setAttr('sourceStart', startFrame)
		cacheNode.setAttr('sourceEnd', endFrame)
		cacheNode.setAttr('originalStart', startFrame)
		cacheNode.setAttr('originalEnd', endFrame)
	
	def parseDescriptionFile(self):
		xml = minidom.parse(self.m_fileName)
		root = xml.getElementsByTagName("Autodesk_Cache_File")
		allNodes = root[0].childNodes
		for node in allNodes:
			if node.nodeName == 'cacheType':
				self.m_cacheType = node.attributes.item(0).nodeValue
			if node.nodeName == 'time':
				timeRange = node.attributes.item(0).nodeValue.split('-')
				self.m_cacheStartTime = int(timeRange[0])
				self.m_cacheEndTime = int(timeRange[-1])
			if node.nodeName == 'cacheTimePerFrame':
				self.m_timePerFrame = int(node.attributes.item(0).nodeValue)
			if node.nodeName == 'cacheVersion':
				self.m_version = float(node.attributes.item(0).nodeValue)
			if node.nodeName == 'Channels':
				channels = self.parseChannels(node.childNodes)
	
	def parseChannels(self, channels):
		for ch in channels:
			if re.compile("channel").match(ch.nodeName) != None:
				channelName = ''
				channelType = ''
				channelInterp = ''
				sampleType = ''
				sampleRate = 0
				startTime = 0
				endTime = 0

				for index in range(0, ch.attributes.length):
					attrName = ch.attributes.item(index).nodeName
					if attrName == 'ChannelName':
						channelName = ch.attributes.item(index).nodeValue
					if attrName == 'ChannelType':
						channelType = ch.attributes.item(index).nodeValue
					if attrName == 'ChannelInterpretation':
						channelInterp = ch.attributes.item(index).nodeValue
					if attrName == 'SamplingType':
						sampleType = ch.attributes.item(index).nodeValue
					if attrName == 'SamplingRate':
						sampleRate = ch.attributes.item(index).nodeValue
					if attrName == 'StartTime':
						startTime = ch.attributes.item(index).nodeValue
					if attrName == 'EndTime':
						endTime = ch.attributes.item(index).nodeValue

				self.m_channels[channelName] = (channelType, channelInterp, sampleType,
											    sampleRate, startTime, endTime)