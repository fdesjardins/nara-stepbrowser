#!/usr/bin/env python

import os

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QFileDialog

import networkx as NX


class GraphHierarchy(object):
    def __init__(self, parent = None):
		
        self.parent = parent

        #Dialog for step directory if not set
        if self.parent.step_path == None:
            filedialog = QtGui.QFileDialog()
            tmp = filedialog.getExistingDirectory(None, 'Open Directory', '')
            self.parent.set_step_path(str(tmp))

        #self.parent = stepBrowser
        os.chdir(self.parent.step_path)
        dirlist = os.listdir(self.parent.step_path)

        #Store STEP file locations
        self.allStepFilePaths = []
        for root, dirs, files in os.walk(self.parent.step_path):
            #print root, dirs, files
            for f in files:
                if self.isStepFilename(f):
                    self.allStepFilePaths.append(os.path.join(root, f))

        
        #print "len(allStepFilePaths) = ", len(self.allStepFilePaths)
        #print
        #print "allStepFilePaths = ", self.allStepFilePaths

        dirlist = os.listdir(self.parent.step_path)
        xref_str = "APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT"
        doc_str = "DOCUMENT_FILE"
        Gh = NX.Graph()
        Gd = NX.DiGraph()

        for f in dirlist:
            if os.path.isfile(os.path.join(self.parent.step_path, f)) and self.isStepFilename(f):
                #print(f)
                for line in open(f):
                    if xref_str in line:
                        line_parts = line.split("'")
                        if len(line_parts) > 2:
                            xref_name = line_parts[1]

                            try:
                                (xref_name for xref_name in dirlist).next()
                                print(f, " -> ", xref_name)
                                Gh.add_edge(f, xref_name, weight=1.0)
                                Gd.add_edge(f, xref_name, weight=1.0)
                            except:
                                print("File ", f, " references xref ", xref_name, ", but that xref does not exist.")

        all_nodes = Gh.nodes()                    
        scaled_node_size = lambda(node) : NX.degree(Gh, node) * 700
        position = NX.spring_layout(Gh)    
        NX.draw_networkx_nodes(Gd, position, ax=self.parent.axes, node_size=map(scaled_node_size, all_nodes), alpha=0.5)
        NX.draw_networkx_edges(Gd, position, ax=self.parent.axes, width=1.0, alpha=1.0, edge_color="red")
        NX.draw_networkx_labels(Gd, position, ax=self.parent.axes, fontsize = 14)

    
    def isStepFilename(self, fname):
        out = map(fname.endswith, ['.stp','.STP','.step','.STEP'])
        if any(out) == True: return True
        return False

        #return fname.endswith('.stp') or f.endswith('.STP') or f.endswith('.step') or f.endswith('.STEP')
