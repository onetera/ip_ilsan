try:
    reload(sys.modules['constants'])
    reload(sys.modules['Core.iPipelineInfo'])
    reload(sys.modules['Core.iPipelineActions'])
    reload(sys.modules['Core.iPipelineInit'])
    reload(sys.modules['Core.iPipelineUtility'])
    reload(sys.modules['Gui.Functions.assistantFunctions'])
    reload(sys.modules['Custom.secondary'])
    reload(sys.modules['Custom.DI_animTransfer'])
    reload(sys.modules['nuke'])
    reload(ipipeline)
except:
    print "couldn't python sript"

import sys
if not '/lustre/INHouse/MAYA_DEV/common/file/ipipeline' in sys.path:
    sys.path.append('/lustre/INHouse/MAYA_DEV/common/file/ipipeline')
import ipipeline
ipipeline.pipeline()
