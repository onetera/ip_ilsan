# -*- coding: utf-8 -*-

"""
**constants.py**

**Platform:**
    Linux, Mac Os X.

**Description:**
    Constants Module

**Others:**

"""

#***********************************************************************************************
#***    External imports.
#***********************************************************************************************
import sys
import os
#***********************************************************************************************
#***    Module attributes.
#***********************************************************************************************
__author__ = "Seo Jungwook"
__copyright__ = "Copyright (C) 2011 - Seo Jungwook"
__maintainer__ = "Seo Jungwook"
__email__ = "rndvfx@gmail.com"
__status__ = "Production"

#***********************************************************************************************
#***    Module classes and definitions.
#***********************************************************************************************
test = 0



class Constants():
    """
    This class is the **Constants** class.
    """
    
    debugMode = False
    applicationName = "iPipeline v0.2.7.1"
#    if sys.platform == "darwin":
#        applicationDirectory = "/Users/higgsdecay/work/release/ipipeline/"
    if 'linux' in sys.platform :
        if test == 1:
             applicationDirectory = '/home/idea/work/ipipeline/'
        else :
            applicationDirectory = "/lustre/INHouse/MAYA/common/file/ipipeline/"
    else:
        applicationDirectory = "//10.0.200.100/_lustre_INHouse/MAYA/common/file/ipipeline/"
    
    frameworkUIFile = applicationDirectory+"ui/ipipeline_GUI07.ui"
    DI_animTransfer = applicationDirectory+"Gui/DI_animTransfer/DI_animTransfer02.ui"
    DI_animTransferAlone = applicationDirectory+"Gui/DI_animTransfer/DI_animTransferAlone.ui"
    
    nukeTemplaeFile = applicationDirectory+"templates/master.nk"
    workspaceDirectory = applicationDirectory+"templates/workspace"
    lutFile = applicationDirectory+"templates/default_lut.cube"
    codecFile = applicationDirectory+"templates/codec.txt"
    workcodeFile = applicationDirectory+"templates/workcode.xml"
    DI_ani = applicationDirectory+"mel/animation"
    DI_finalize = applicationDirectory+"mel/finalize"
    
    tractor = '/lustre/INHouse/Tractor/tractor-blade/tractor-spool.py'
    tractorHome = 'http://10.0.99.20/tractor/dashboard'
    engine_ip = '10.0.99.20'


if __name__ == '__main__' : 
    print os.path.isfile('/hsme/idea/work/develop.py')
    
