#!/usr/bin/env python

'''
Breadcrumb style address bar.
Author: Forrest Desjardins
'''

import os

from PyQt4 import QtGui
from PyQt4.QtGui import QWidget, QLabel, QStatusBar
from PyQt4.QtGui import QPushButton


class BrowserAddressBar(QtGui.QWidget):
	def __init__(self, parent = None):
		self.parent = parent
		QtGui.QWidget.__init__(self, parent)
		
		self.widgets = []
		
		hbox = QtGui.QHBoxLayout()
		self.layout = hbox
		self.setLayout(hbox)
		
		
	def set_address(self, address):
		'''Creates "crumbs" from address, and updates the layout'''
		
		if address == None:
			return 0;
		else:
			addr_lst = self.split_address('.'+address)
			addr_lst.reverse()
			
		#Interleave buttons and labels, with a stretch on the end
		crumbs = []	
		for x in addr_lst:
			crumbs.append( QPushButton(x) )
			crumbs.append( QLabel("/") )
			
		self.update_layout(crumbs)
			
			
	def update_layout(self, crumbs):
		'''Removes existing address bar crumbs, and adds new ones'''
		
		for x in self.widgets:
			self.layout.removeWidget(x)
					
		self.widgets = crumbs
		for x in crumbs:
			self.layout.addWidget(x)
			
		self.layout.addStretch()
			
		
	def split_address(self, address, out = []):
		'''Recursively splits a path using os.path.split, returning a string.'''
		
		(rest,head) = os.path.split(address)
		
		#print head, rest
		
		if rest=='' or rest==None:
			out.append(head)
			return out
		else:
			out.append(head)
			return self.split_address(rest, out)
			
