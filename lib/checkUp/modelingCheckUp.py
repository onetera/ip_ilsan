# -*- coding: utf-8 -*-

##################################
# author : Hong joo Ahn
#
# mail : 
#
# Usage : 
#
# Description :
#
#



try : 
    import maya.cmds as mc
    MAYA = 1
except :
    MAYA = 0
        
import string


class modelingCheckUp:
    def __init__(self):
        #pass
        #self.loop = []
        self.listT = set(mc.ls(type='transform'))
        self.cameraList = mc.ls(type='camera')
        self.cameraList = set([ mc.listRelatives(x,p=1)[0] for x in self.cameraList])
        self.listT = list(self.listT.difference(self.cameraList))
        self.value = ''
        self.num = ''
        self.rpPos = []
        self.spPos = []
        self.rOrder = []
        
    def scale(self,obj):
        self.value = mc.getAttr('%s.sx'%obj) +\
        mc.getAttr('%s.sy'%obj) +\
        mc.getAttr('%s.sz'%obj)
        
        return self.value
    
    def freeze(self,obj):
        self.value = mc.getAttr('%s.tx'%obj) +\
        mc.getAttr('%s.ty'%obj) +\
        mc.getAttr('%s.tz'%obj) +\
        mc.getAttr('%s.rx'%obj) +\
        mc.getAttr('%s.ry'%obj) +\
        mc.getAttr('%s.rz'%obj)
        
        return self.value
    
    def axis(self,obj):
        self.rpPos = mc.xform(obj,q=1,ws=1,rp=1)
        self.spPos = mc.xform(obj,q=1,ws=1,sp=1)
        
        self.Epos = list(set(self.rpPos).union(set(self.spPos)))
        self.checkP = reduce(lambda x,y: x+y,self.Epos,0)
        
        return self.checkP
        
        
    def history(self,obj):        
        hisL = mc.listHistory(obj,leaf=1)
        shapeL = mc.listRelatives(obj,s=1)[0]
        hisL = [ x for x in hisL if x != shapeL ]
        self.num = len(hisL) # if hisL != [] else ''
            
        return self.num
        
    def loop_check(self,typ):
        
        for x in self.listT:
            if typ == "scale":
                self.val = self.scale(x)
                if self.val != 3:
                    print '%s is not default scale value. you should check up!'%x
                    return False
                
            if typ == "axis":
                self.pivotScaleRo = self.axis(x)
                if self.pivotScaleRo != 0:
                    print '%s is not located 0 0 0.. you should check up pivots locations!'%x
                    return False
                
            if typ == "history":
                self.checkNum = self.history(x)
                if self.checkNum != 0:
                    print '%s has history. you should check up!'%x
                    return False
        
        return True

    def allModCheck(self):
        self.loop_check('scale')
        self.loop_check('axis')
        self.loop_check('history')


if __name__ == '__main__':
    xx = modelingCheckUp()
    xx.loop_check('scale')
    xx.loop_check('axis')
    xx.loop_check('history')