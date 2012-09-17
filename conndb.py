# -*- coding: utf-8 -*-

import os

try :
    import MySQLdb
except ImportError:    
        os.system('./lustre/INHouse/CentOS/bin/mysql_inst.exe')
        import MySQLdb
        
import time
import re


if 'd10218' in os.getenv('LOGNAME'):
    mysqlhost = 'localhost'
else :
    mysqlhost = '10.0.201.15'
theLogFile = '/lustre/INHouse/INI/'



class DBhandler:
    def dbConn(self):
        if 'd10218' in os.getenv('LOGNAME'):     
            self.db = MySQLdb.connect(host = mysqlhost , user = 'root' , passwd='studio77' , db= 'wd' , charset='utf8')
        else :
            self.db = MySQLdb.connect(host = mysqlhost , user = 'idea' , passwd='idea' ,port=3366, db= 'wd' , charset='utf8')
#        self.db = MySQLdb.connect(host = '10.0.201.15' , user = 'idea' , passwd='idea' ,port=3366, db= 'wd' , charset='utf8')
        self.cr = self.db.cursor()
        return True
        
    def dbclose(self):
        if self.db.open:
            self.db.close()
        
        
            
    def getFetch(self , query ): 
        self.dbConn()                         
        self.cr.execute(query )
        data = self.cr.fetchall()
        self.cr.close()
        self.dbclose()               
        return list( data )
    
    

class tableInfo( DBhandler ):
    def __init__(self , table ): 
        self.table = table
        self.logs = ''
        self.querytext = ''           
    
    def getlastid(self):
        self.dbConn()
        lastid =  self.cr.lastrowid if self.cr.lastrowid != None else ''
        self.dbclose()
        return str( lastid )    
        
    def query(self , query ):
        '''여러 아이템을 리턴하는 값들과 통일하기 위해 lastid를 리스트로 리턴 시킴.
        '''
        self.dbConn()
        self.querytext = query
        self.cr.execute(query )
        self.db.commit()
        lastid =  self.cr.lastrowid if self.cr.lastrowid != None else ''
        self.dbclose()
        lasetid = int(lastid) if type(lastid) == type(1L) else lastid
        return [ lastid ]
     

    def getAttr(self ):
        self.dbConn()
        temp = []
        for x in self.getFetch('desc %s' % self.table ):
            if not 'auto_increment' in x and not 'status' in x :
#            if not 'auto_increment' in x and not 'timestamp' in  x  and not 'status' in x :                
                temp.append( x[0] )        
        return temp  

    def register(self , *arg ):
        self.dbConn()
        attr = self.getAttr()
        print 'attr = ' , attr
        setAttr = len(arg)*'%s,'
        setValues = len(arg)*'"%s",'        
        query = 'insert into %s ('+setAttr[:-1]+') values('+setValues[:-1]+')'           
        format = tuple( [self.table]+attr + list(arg) )
        query = query % format  
        self.querytext = query              
        lastid = self.query( query )        
        return  lastid 
        
    def update(self , id , **keys ):         
#        value = value.replace('\'' , '"')        
        values = ''
        for x in keys:
            values += x + '="' + str(keys[x]) + '",'
        query = "UPDATE %(table)s SET %(values)s WHERE id = %(id)s " % {'table':self.table , 'id':id , 'values':values[:-1] }
        print query
        self.querytext = query       
        self.query( query )
        return [ id ] 
        
             
    def search(self , col, **options):
        if 'repetition' in options.keys():
            repetition = ' distinct '
        else : 
            repetition = ''
        
        txt1 = 'select ' 
        txt2 = ' from %s ' % self.table
        query = txt1 + repetition + col + txt2  
        if type([]) in [ type(x) for x in options.values()] or None:
            return []         
        if options != {} and not '' in options.values():
            query += ' where '
            for key in options:
                query += key +"=\'" + str(options[key]) + "\' AND "
            query = query[:-4]
            self.querytext = query                                                                 
        fetchList = self.getFetch(query)        
        if fetchList == []:            
            return []
        result = []
        for x in fetchList:
            if type(x[0]) == type(1L):
                result.append( int(x[0]) )
            else :
                result.append( x[0] ) 
        return result




def writelogs( querytxt ):    
    theLogFile = os.path.join( '/lustre/INHouse/INI' ,  re.search('d\d{5}' , os.getenv('LOGNAME' ) ).group() + '_' +time.strftime('%Y%m%d_%H%M_%S')+'.sql' ) 
    
    f = open(theLogFile , 'w')
    f.write( querytxt )
    f.close()

def createAsset(project , assetType , assetName , workcode ):    
    ASSET = tableInfo( 'ASSET' )    
    assetID = ASSET.search('id' , type = assetType , aname = assetName )
    if assetID == []:
        assetID = ASSET.register( assetType , assetName , '' , project )        
    return assetID
        

def createJob(  project , seq , shot , workcode):
    JOB_INFO = tableInfo( 'JOB_INFO' ) 
    jobInfoID = JOB_INFO.search( 'id' , workcode=workcode ,  showcode=project , seqname=seq , shotname=shot )
    if jobInfoID == []:    
        jobInfoID = JOB_INFO.register( workcode , '' , '' , project , seq , shot , time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) )              
    return jobInfoID
        

def createAssetJob( project , assetType , assetName , workcode ):
    ASSET_JOB = tableInfo( 'ASSET_JOB' )
    assetID = createAsset(project , assetType , assetName , workcode )    
    assetJobID = ASSET_JOB.search( 'id' , workcode = workcode , assetID = assetID[-1] )   
    if assetJobID == []:        
        assetJobID = ASSET_JOB.register( workcode , '' , assetID[-1] , time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) )
    return assetJobID
        
        
def AssetRegister(project , assetType , assetName , workcode ,subjectName, ver , wip , usernum , username , comment ):
    ASSET = tableInfo( 'ASSET' )
    ASSET_JOB = tableInfo( 'ASSET_JOB' )
    ASSET_JOB_VERSION = tableInfo('ASSET_JOB_VERSION')
    
    assetID = createAsset( project , assetType , assetName , workcode )     
    assetJobID = createAssetJob(project , assetType , assetName , workcode)
    assetJobVerID = ASSET_JOB_VERSION.search( 'id' , ver=ver , wip=wip , assetJobID = assetJobID[-1] , usernum = usernum)
    
    if  assetJobVerID == []:        
        assetJobVerID = ASSET_JOB_VERSION.register( ver , wip , assetJobID[-1] , usernum , username , time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) )
        ASSET_JOB.update( assetJobID[-1] , status = 'WIP' ) 
#    else :             
#        assetJobVerID = ASSET_JOB_VERSION.update( assetJobVerID[-1]  , ver=ver , wip=wip , assetJobID = assetJobID[-1] , usernum=usernum , username= username ,uploadDate=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) )
#        ASSET_JOB.update( assetJobID[-1] , status = 'WIP' ) 
      
    ASSET_JOB_CMMT = tableInfo( 'ASSET_JOB_CMMT' )    
    assetJobCmmtID = ASSET_JOB_CMMT.search( 'id' , assetJobVerID = assetJobVerID[-1] )    
   
    if comment != '' and assetJobCmmtID == []:  
        assetJobCmmtID = ASSET_JOB_CMMT.register( comment , assetJobVerID[-1] )
    
    ASSET_SUBJECT = tableInfo( 'ASSET_SUBJECT' )    
    if subjectName != '' :
        assetSubjectID = ASSET_SUBJECT.register( subjectName , assetJobVerID[-1] )
    return True
        
    
    


def JobRegister(project , seq , shot , workcode ,subjectName, ver , wip ,  usernum , username, comment ):
    JOB_INFO = tableInfo( 'JOB_INFO' ) 
    JOB_VERSION = tableInfo( 'JOB_VERSION' )
    JOB_CMMNT = tableInfo( 'JOB_CMMNT' )
    jobInfoID = createJob(  project , seq , shot , workcode )        
    jobVerID = JOB_VERSION.search( 'id' , jobInfoID = jobInfoID[-1] , ver = ver , wip = wip )

    if jobVerID == []:
        jobVerID = JOB_VERSION.register( jobInfoID[-1] , ver ,wip  , usernum , username ,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) )
        JOB_INFO.update( jobInfoID[-1] , status = 'WIP' )
#    else:         
#        jobVerID = JOB_VERSION.update( jobVerID[-1] , ver=ver , wip=wip  ,jobInfoID = jobInfoID[-1] ,  usernum=usernum , username= username , uploadDate=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) )
#        JOB_INFO.update( jobInfoID[-1] , status = 'WIP' )

    if comment != '' and jobVerID != [] :        
        JOB_CMMNT.register( comment , jobVerID[-1] )
        
    JOB_SUBJECT = tableInfo( 'JOB_SUBJECT' )    
    if subjectName != '' :
        jobSubjectID = JOB_SUBJECT.register( subjectName , jobVerID[-1] )
    return True

if __name__ == '__main__':    
#    db = DBhandler()
#    db.dbConn()
##    print db.getFetch("call getcomment('CZ12','R7','R7_012B','ani',2)" )
#    db.cr.execute( "call getcomment('CZ12','R7','R7_012B','ani',2)" )
#    data = db.cr.fetchall()
#    db.dbclose()
#    print data
    
    db = MySQLdb.connect(host = '10.0.201.15' , user = 'idea' , passwd='idea' ,port=3366, db= 'wd' , charset='utf8')
    cr = db.cursor()
    
    cr.execute( "call getcomment('tower','056','056_0350','ani',2)" )
    data = cr.fetchall()
    cr.close()
    db.close()
    print data
    
    
    
#    ASSET_JOB_VERSION = tableInfo('ASSET_JOB_VERSION')
#    db = MySQLdb.connect(host = '10.0.201.15' , user = 'idea' , passwd='idea' , db= 'wd' , charset='utf8')
#    ASSET_JOB = tableInfo('ASSET_JOB')
#    print ASSET_JOB_VERSION.search( 'id' , ver=6 , wip=0 , assetJobID = 2 , usernum = 'd10218')
#    print ASSET_JOB_VERSION.update( 16 , ver=6 , wip=0 , assetJobID = 2 , usernum = 'd10218')
#    assetID = createAsset( project , assetType , assetName , workcode )     
#    assetJobID = createAssetJob(project , assetType , assetName , workcode)
#    AssetRegister('TEMP' , 'char2' , 'krocop' , 'model' , 6 , 1  ,'d10218' , u'오호준' ,'' )
#    JobRegister('TEMP' , 'char2' , 'krocop' , 'anim' , 'simulation', 3 , 4 ,  'd10218' , '오호준', 'good' )
#    assetID = createAsset( 'TEMP' , 'char2' , 'ogre' , 'model' )  
#    ASSET_JOB.register( 'model' , '' , assetID[-1] , time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) )
#    
  
  






    
    
        