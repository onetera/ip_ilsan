import os
import ConfigParser
#from Core.iPipelineInfo import iPipelineInfo

#class Logs:
#    def __init__(self , tab , level1 = '', level2='', level3='', subjectName='' , folder = 'devFolder'):
#        self.inifile = self.getFileName( tab , level1 , level2 , level3 , folder )
#        print self.inifile
        
def Logs( name , num ,  date , time , shot , sframe , eframe , mayafile , preview , comment ):
    filepath = mayafile[:-2]+'ini'
#    f = open(filepath , 'w')
    config = ConfigParser.RawConfigParser()
    config.add_section("publish")
    config.set( "publish" , "author" , unicode(name ).encode('euc-kr') )
    config.set( "publish" , "number" , num )
    config.set( "publish" , "date" , unicode(date ).encode('euc-kr'))
    config.set( "publish" , "time" , time )
    config.set( "publish" , "shot" , shot )
    config.set( "publish" , "startframe" , int(sframe ))
    config.set( "publish" , "endframe" , int(eframe ))
    config.set( "publish" , "mayafile" , mayafile )
    config.set( "publish" , "preview" , preview )
    config.set( "publish" , "comment" , unicode(comment ).encode('euc-kr') )
    configFile = open(filepath, "w")
    config.write(configFile) 
    configFile.close() 
     
    
def wconf():
    config = ConfigParser.ConfigParser() 
    config.add_section("SECTION") 
    config.set("SECTION", "OPTION", "VALUE") 
    configFile = open("/home/d10218/config.ini", "w") 
    config.write(configFile) 
    configFile.close() 
        
def readconf():        
    config = ConfigParser.ConfigParser() 
    config.read("/home/d10218/config.ini") 
    print config.get("SECTION", "OPTION")
             
if __name__ == '__main__':
    wconf()
    