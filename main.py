#!/usr/bin/env python

import sys
sys.path.append("./src")
from stepBrowser import *

if __name__=='__main__':
    app = QApplication(sys.argv)
    form = StepBrowser(app)
    form.show()
    app.exec_()
	
