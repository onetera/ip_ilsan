# -*- coding: utf-8 -*-


#***********************************************************************************************
#***    External imports.
#***********************************************************************************************
import sys
import os
import glob



#***********************************************************************************************
#***    Module classes and definitions.
#***********************************************************************************************
DEVEL = True if os.path.isdir( '/home/d10218' ) else False



class Constants():
    
    if 'linux' in sys.platform :
        if DEVEL:
             applicationDirectory = '/home/d10218/work/ipipeline/'
        else :
            applicationDirectory = "/lustre/INHouse/MAYA/common/file/ipipeline/"
    else:
        applicationDirectory = "//10.0.200.100/_lustre_INHouse/MAYA/common/file/ipipeline/"    
  
    frameworkUIFile = sorted( glob.glob( applicationDirectory+"ui/ipipeline_GUI*.ui" ) )[-1]        
    deptTreeUI = sorted( glob.glob( applicationDirectory+"ui/deptTree_*.ui" ) )[-1]
    ldapAddress = '10.0.99.10'
    wdSQLaddress = '10.0.201.15'
        
    DI_animTransfer = applicationDirectory+"Gui/DI_animTransfer/DI_animTransfer02.ui"
    DI_animTransferAlone = applicationDirectory+"Gui/DI_animTransfer/DI_animTransferAlone.ui"
    
    bookmark_ui = sorted( glob.glob( applicationDirectory + "components/addons/bookmarks/ui/*.ui" ))[-1]
    
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
    print Constants().frameworkUIFile
    
