# -*- coding: utf-8 -*-

import MySQLdb
import time
import os
import re

if 'd10218' in os.getenv('LOGNAME'):
    mysqlhost = 'localhost'
else :
    mysqlhost = '10.0.201.15'
theLogFile = '/lustre/INHouse/INI/'

class tableInfo:
    def __init__(self , table ): 
        self.table = table
        self.logs = ''
        self.querytext = ''
        
    def dbConn(self):
        if 'd10218' in os.getenv('LOGNAME'):     
            self.db = MySQLdb.connect(host = mysqlhost , user = 'root' , passwd='studio77' , db= 'wd' , charset='utf8')
        else :
            self.db = MySQLdb.connect(host = mysqlhost , user = 'idea' , passwd='idea' ,port=3366, db= 'wd' , charset='utf8')
        self.cr = self.db.cursor()
        return True
       
    
    def getlastid(self):
        self.dbConn()
        lastid =  self.cr.lastrowid if self.cr.lastrowid != None else ''
        self.dbclose()
        return str( lastid )
    
    def dbclose(self):
        if self.db.open:
            self.db.close()
        
    def query(self , query ):
        '''여러 아이템을 리턴하는 값들과 통일하기 위해 lastid를 리스트로 리턴 시킴.
        '''
        self.dbConn()
        success = 0
        try : 
            self.querytext = query
            self.cr.execute(query )
            self.db.commit()
            lastid =  self.cr.lastrowid if self.cr.lastrowid != None else ''
            self.dbclose()
            lasetid = int(lastid) if type(lastid) == type(1L) else lastid 
            success = 1            
        except :            
            success = 0
        if success == 1 :            
            return [ lastid ]
        else :   
            writelogs( self.querytext )
            return False
        
    def getFetch(self , query ): 
        self.dbConn()                         
        self.cr.execute(query )
        data = self.cr.fetchall()
        self.dbclose()               
        return list( data )
        

    def getAttr(self ):
        self.dbConn()
        temp = []
        for x in self.getFetch('desc %s' % self.table ):
            if not 'auto_increment' in x and not 'timestamp' in  x  and not 'status' in x :                
                temp.append( x[0] )        
        return temp  

    def register(self , *arg ):
        self.dbConn()
        attr = self.getAttr()
                    
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
        query = "UPDATE %(table)s SET %(values)s , uploadDate=NOW() WHERE id = %(id)s " % {'table':self.table , 'id':id , 'values':values[:-1] }
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
    print 'querytxt = ', querytxt
    theLogFile = os.path.join( '/lustre/INHouse/INI' ,  re.search('d\d{5}' , os.getenv('LOGNAME' ) ).group() + '_' +time.strftime('%Y%m%d_%H%M_%S')+'.sql' ) 
    
    f = open(theLogFile , 'w')
    f.write( querytxt )
    f.close()


def createAsset(project , assetType , assetName , workcode ):
    
    ASSET = tableInfo( 'ASSET' )    
    assetID = ASSET.search('id' , type = assetType , name = assetName )
    
    writelogs( ASSET.querytext )
    if assetID == []:
        assetID = ASSET.register( assetType , assetName , '' , 'TEMP' )        
    return assetID
        

def createJob(  project , seq , shot , workcode):
    JOB_INFO = tableInfo( 'JOB_INFO' ) 
    jobInfoID = JOB_INFO.search( 'id' , workcode=workcode ,  showcode=project , seqname=seq , shotname=shot )
    if jobInfoID == []:    
        jobInfoID = JOB_INFO.register( workcode , '' , '' , project , seq , shot)              
    return jobInfoID
        

def createAssetJob( project , assetType , assetName , workcode ):
    ASSET_JOB = tableInfo( 'ASSET_JOB' )
    assetID = createAsset(project , assetType , assetName , workcode )    
    assetJobID = ASSET_JOB.search( 'id' , workcode = workcode , assetID = assetID[-1] )   
    if assetJobID == []:        
        assetJobID = ASSET_JOB.register( workcode , '' , assetID[-1] )            
    return assetJobID
        
        
def AssetRegister(project , assetType , assetName , workcode , ver , wip , usernum , comment ):
    ASSET = tableInfo( 'ASSET' )
    ASSET_JOB = tableInfo( 'ASSET_JOB' )
    ASSET_JOB_VERSION = tableInfo('ASSET_JOB_VERSION')
    
    assetID = createAsset( project , assetType , assetName , workcode )     
    assetJobID = createAssetJob(project , assetType , assetName , workcode)
    assetJobVerID = ASSET_JOB_VERSION.search( 'id' , ver=ver , wip=wip , assetJobID = assetJobID[-1] , usernum = usernum)
    
    if  assetJobVerID == []:        
        assetJobVerID = ASSET_JOB_VERSION.register( ver , wip , assetJobID[-1] , usernum ) 
    else :        
        assetJobVerID = ASSET_JOB_VERSION.update( assetJobVerID[-1]  , ver=ver , wip=wip , assetJobID = assetJobID[-1] , usernum=usernum )
      
    ASSET_JOB_CMMT = tableInfo( 'ASSET_JOB_CMMT' )    
    assetJobCmmtID = ASSET_JOB_CMMT.search( 'id' , assetJobVerID = assetJobVerID[-1] )
    
   
    if comment != '' and assetJobCmmtID == []:  
        assetJobCmmtID = ASSET_JOB_CMMT.register( comment , assetJobVerID[-1] )


def JobRegister(project , seq , shot , workcode , ver , wip ,  usernum ,  comment ):
    JOB_VERSION = tableInfo( 'JOB_VERSION' )
    JOB_CMMNT = tableInfo( 'JOB_CMMNT' )
    jobInfoID = createJob(  project , seq , shot , workcode )        
    jobVerID = JOB_VERSION.search( 'id' , jobInfoID = jobInfoID[-1] , ver = ver , wip = wip )

    if jobVerID == []:
        jobVerID = JOB_VERSION.register( jobInfoID[-1] , ver ,wip  , usernum )
    else:         
        jobVerID = JOB_VERSION.update( jobVerID[-1] , ver=ver , wip=wip  ,jobInfoID = jobInfoID[-1] ,  usernum=usernum )

    if comment != '' and jobVerID != [] :        
        JOB_CMMNT.register( comment , jobVerID[-1] )
        



if __name__ == '__main__':
#    ASSET_JOB_VERSION = tableInfo('ASSET_JOB_VERSION')
#    print ASSET_JOB_VERSION.search( 'id' , ver=6 , wip=0 , assetJobID = 2 , usernum = 'd10218')
#    print ASSET_JOB_VERSION.update( 16 , ver=6 , wip=0 , assetJobID = 2 , usernum = 'd10218')
#    AssetRegister('TEMP' , 'char2' , 'krocop' , 'model' , 6 , 1  ,'d10218' , '' )
#    JOB_INFO = tableInfo( 'JOB_INFO' )
#    print JOB_INFO.search( 'id' , workcode='comp' ,  showcode='TEMP' , seqname='lego' , shotname='002' )
    writelogs( 'ohho' )
    # 어셋 등록 
#    tb = tableInfo( 'ASSET' )
#    theLastID = tb.register( 'vehicle' , 'bus' , '', 'TEMP' )
#    print theLastID


    # 워크코드 등록 
#    tjob = tableInfo( 'ASSET_JOB' )    
#    jobID = tjob.register( 'rig' , '' , 2  )

    # 버전 컨트
#    jobVer = tableInfo( 'ASSET_JOB_VERSION' )
#    jobVerID = jobVer.register('2','1' , '1' , 'd10218'  )

    # 커멘
#    jobCommt = tableInfo('ASSET_JOB_CMMT')
#    jobCommt.register('수고하셨습니다' , jobVerID )

#    project = 'TEMP'
#    assetType = 'char'
#    assetName = 'karasC'
#    workcode = 'rig'
#    ver = 1
#    wip = 1
#    comment = '테스트중입니다 '
#
#    ASSET = tableInfo( 'ASSET' )
#    ASSET_JOB = tableInfo( 'ASSET_JOB' )
#    ASSET_JOB_VERSION = tableInfo('ASSET_JOB_VERSION')
    
    
    #asset job version을 코멘트와 같이 등록할때 
#    assetID = ASSET.search('id' , type = assetType , name = assetName )
#    if assetID == []:
#        print 'There was no such asset'
#        assetID = ASSET.register( assetType , assetName , '' , 'TEMP' )
#    elif assetID == False:        
#        print ASSET.logs
#        
#    assetJobID = ASSET_JOB.search( 'id' , workcode = workcode , assetID = assetID[0] )
#    if assetJobID == []:
#        print 'There was no such asset job'
#        print 'assetID = ' , assetID
#        assetJobID = ASSET_JOB.register( workcode , '' , assetID[0] )
#
#    assetJobVerID = ASSET_JOB_VERSION.search( 'id' , ver=ver , wip=wip , assetJobID = assetJobID[0] , usernum = 'd10218')
#    if  assetJobVerID == []:       
#        assetJobVerID = ASSET_JOB_VERSION.register( ver , wip , assetJobID[0] , 'd10218' )
#    print assetJobVerID
#   
#    ASSET_JOB_CMMT = tableInfo( 'ASSET_JOB_CMMT' )
#    assetJobCmmtID = ASSET_JOB_CMMT.search( 'id' , assetJobVerID = assetJobVerID[0] )
#    if comment != '' and assetJobCmmtID == []:
#        assetJobCmmtID = ASSET_JOB_CMMT.register( comment , assetJobVerID[0] )
#    print assetJobCmmtID
        
        
    
#    ASSET_JOB_VERSION.register(  )
    
#    assetID = ASSET.search('id' , type = assetType , name = assetName )
#    if assetID == []:
#        ASSET.register( assetType , assetName , '' , 'TEMP' )

    
    # Task 등록할때 
#    project = 'TEMP'
#    seq = 'R7'
#    shot = '0034'
#    workcode = 'ani'
#    
#
#    ver = 1
#    wip = 1
#    comment = '에니메이션 테스트중입니다 '
#
#    JOB_INFO = tableInfo( 'JOB_INFO' )
#    JOB_VERSION = tableInfo( 'JOB_VERSION' )
#    JOB_CMMNT = tableInfo( 'JOB_CMMNT' )
#    
#    jobInfoID = JOB_INFO.register( workcode , '' , '' , project , seq , shot)
#
#    if jobInfoID == []:
#        jobInfoID = JOB_INFO.register( workcode , '' , '' , project , seq , shot)
#    
#    jobVerID = JOB_VERSION.search( 'id' , jobInfoID = jobInfoID[0] , ver = ver , wip = wip )
#    if jobVerID == []:
#        jobVerID = JOB_VERSION.register( jobInfoID[0] , ver , wip  , 'd10218' )
#    
#    if comment != '' and jobVerID != [] :
#        JOB_CMMNT.register( comment , jobVerID[0] ) 
        
  






    
    
        