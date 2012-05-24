from xml.dom import minidom, Node
try :
    import maya.cmds as cmds
    MAYA = 1 
except : 
    MAYA = 0


class layerManager:
    def __init__(self):
        if MAYA:
            self.layerData = self.outLayer()
        else :
            self.layerData = [[u'addptofgjth', [u'pSphere1']], [u'layer1', [u'pSphere1']], [u'layer3', [u'pSphere1']]]
            
            
    def outLayer(self):
        layers = [ x for x in cmds.ls(type="displayLayer" ) if x!= 'defaultLayer' ]
        layerData = []
        for x in layers:
            layerData.append( [ x , cmds.editDisplayLayerMembers( x , q=1) ] )
        return layerData
          
          
    def layer2XMl(self):
        doc  = minidom.Document()
        dom = doc.createComment( 'XML Layer Information')        
        root = doc.createElement( 'root' )
        doc.appendChild( root )
        
        for x in self.layerData:
            layer = doc.createElement( x[0] )
            root.appendChild( layer )
            for n in x[1]:
                elem = doc.createElement( n )
                layer.appendChild( elem )
        return doc.toprettyxml( indent='\t' ,newl='\n', encoding = 'utf-8')

    def writeXML(self , xmlpath ):
        self.layerData = self.outLayer()
        xml = self.layer2XMl()
        f = file( xmlpath , 'w+' )
        f.write( xml )
        f.close()
        print xmlpath
        print 'writed layML file'
        

    def xml2layer(self , theFile ):
        f = file( theFile )
        xmldoc = minidom.parse( f )
        f.close()         
#        layers = [ x.nodeName for x in xmldoc.childNodes[0].childNodes if x.nodeType == 1 ]
        layerNodes = [ x for x in xmldoc.childNodes[0].childNodes if x.nodeType == 1 ]
        layerData = [ [ x.nodeName , [ n.nodeName for n in x.childNodes if n.nodeType ==1 ] ] for x in layerNodes ]
        return layerData
    
    def constructLayer(self , theFile ):
        layers = [ x for x in cmds.ls(type="displayLayer" ) if x!= 'defaultLayer' ]
        if layers != []:
            cmds.delete( layers ) 
        self.layerData = self.xml2layer( theFile )
        print 'self.layerData : ' , self.layerData 
        for x in self.layerData :
            cmds.select( x[1] )
            print x[0]
            cmds.createDisplayLayer(n=x[0])            
            cmds.select(d=1)
        
if __name__ == '__main__' :
     
    lm = layerManager()
    theFile = '/home/idea/work/nnn.xml'
    lm.writeXML( theFile )
#    print lm.xml2layer( theFile )
#    lm.constructLayer()
