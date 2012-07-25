import MySQLdb
import sys
import os
import pprint


if os.path.isdir('/home/d10218'):
    sys.path.append( '/home/d10218/work/ipipeline' )
    from conndb import *
    
from userInfo import findUserName

mysqlhost = '10.0.201.15'    

db = MySQLdb.connect(host = mysqlhost , user = 'idea' , port = 3366 , passwd='idea' , db= 'wd' , charset='utf8')
cr = db.cursor()
def deldb():
    db = MySQLdb.connect(host = mysqlhost , user = 'idea' , port = 3366 , passwd='idea' , db= 'wd' , charset='utf8')
    cr = db.cursor()
    cr.execute( 'delete from ASSET' )
    db.commit()    
    cr.execute( 'alter table ASSET auto_increment = 1')
    cr.execute( 'alter table ASSET_JOB auto_increment = 1' )
    cr.execute( 'alter table ASSET_JOB_VERSION auto_increment = 1' )
    db.commit()
    db.close()
    
    
def insertdb():
    cr.execute( "select JOB_INFO.seqname , JOB_INFO.shotname , JOB_INFO.description , JOB_INFO.showcode , JOB_INFO.workcode , JOB_INFO.status , JOB_INFO.deadline , JOB_INFO.created ,JOB_INFO.id from JOB_INFO where workcode='model' or workcode='rig' " )
    result = cr.fetchall() 
    #pprint.pprint( result ) 
    
    for x in result:
        cr.execute( "select ASSET.id from ASSET where type='%s' and name='%s' and showcode='%s'" % (x[0] , x[1] ,x[3] ) )
        check = cr.fetchall()    
        if check ==() :
            query = 'insert into ASSET(type,name,description,showcode) values("%s","%s","%s","%s")' % (x[0],x[1],x[2],x[3])
            cr.execute( query )
            
        cr.execute( "select ASSET.id from ASSET where type='%s' and name='%s' and showcode='%s'" % (x[0] , x[1] ,x[3] ) )
        assetID = str(int(cr.fetchall()[0][0]))
        query = 'insert into ASSET_JOB( workcode ,status,deadline,assetID,created) values("%s","%s","%s","%s","%s")' % ( x[4],x[5],x[6],assetID,x[7] )
        cr.execute( query )  
        
        cr.execute( "select ver , wip , usernum , uploadDate from JOB_VERSION  where jobInfoID=%s " % x[8] )
        versions =  [ x for x in cr.fetchall() ]
        
        cr.execute( "select ASSET_JOB.id from ASSET_JOB where assetID = %s " % assetID )
        assetJobID = [ x[0] for x in cr.fetchall() ]
        
        for m in assetJobID:
            for n in versions:
                print (int(n[0]) , int(n[1]) , int(m) , n[2] , n[3])                          
                cr.execute( 'insert into ASSET_JOB_VERSION(ver,wip,assetJobID,usernum,uploadDate) values("%s","%s","%s","%s","%s")' % (int(n[0]) , int(n[1]) , int(m) , n[2] , n[3]) )
    db.commit()
    db.close()

#deldb()
#insertdb()

def changeName():
    cr.execute( "select usernum from ASSET_JOB_VERSION" )
    theList = cr.fetchall()
    for x in theList:
        theName = findUserName(x[0])
#        print theName[0]
        cr.execute( "UPDATE ASSET_JOB_VERSION SET username='%s' WHERE usernum='%s'" % (theName[0] , x[0]) )
    db.commit()
    db.close()

changeName()  

 