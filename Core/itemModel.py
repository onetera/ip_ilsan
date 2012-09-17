# -*- coding: utf-8 -*-

import datetime
import MySQLdb
import sys
import os
import re




class WIPmodel:
    def __init__( self , filename ):
        self.filename = filename
        
        self.created = ''
        self.latest = ''
        self.final = ''
        self.elapsed = ''
        self.fileparse()
        
        
    def fileparse(self):
        self.parsed = self.filename.split( os.sep )
        self.basename = os.path.basename( self.filename )
        
        self.fileinfo = {}
        self.fileinfo['showname']   = self.parsed[2]
        self.fileinfo['prod']       = self.parsed[3]        
        self.fileinfo['level1']     = self.parsed[4]
        self.fileinfo['level2']     = self.parsed[5]
        self.fileinfo['level3']     = self.parsed[6]
        self.fileinfo['type']       = self.parsed[7]
        self.fileinfo['ver']        = re.search( '(?<=_v)\d{2}' , self.basename ).group() if re.search( '(?<=_v)\d{2}' , self.basename ) else ''
        self.fileinfo['wip']        = re.search( '(?<=_w)\d{2}' , self.basename ).group() if re.search( '(?<=_w)\d{2}' , self.basename ) else ''
        
    def dbcon(self):
        self.db = MySQLdb.connect(host = '10.0.201.15' , user = 'idea' , passwd='idea' ,port=3366, db= 'wd' , charset='utf8')
        self.cr = self.db.cursor() 
        
    def getCreatedDate(self):
        self.dbcon()
        if self.fileinfo['prod'] == 'seq':
            query = '''
            select created from JOB_INFO where showcode='%(showname)s' and seqname='%(level1)s' and shotname='%(level2)s' and workcode='%(level3)s'         '''
        else :
              query = '''
                select ASSET_JOB.created from ASSET_JOB,ASSET where ASSET.showcode='%(showname)s' and ASSET.type='%(level1)s' and ASSET.aname='%(level2)s' and ASSET_JOB.workcode='%(level3)s'         '''

        self.cr.execute( query % self.fileinfo )
        result = [x[0] for x in self.cr.fetchall()]
        self.cr.close()
        self.db.close()        
        return result[0] if type( result ) == type( [] ) else None 
        
    
    def getLatestDate(self):
        self.dbcon()
        if self.fileinfo['prod'] == 'seq':
            query = '''
                    select max(JOB_VERSION.uploadDate) as updateDate from JOB_VERSION,JOB_INFO
                    where JOB_INFO.id=JOB_VERSION.jobInfoID and JOB_INFO.showcode='%(showname)s' 
                    and JOB_INFO.seqname='%(level1)s' and JOB_INFO.shotname='%(level2)s' 
                    and JOB_INFO.workcode='%(level3)s' '''
        else :
              query = '''
                    select max(ASSET_JOB_VERSION.uploadDate) as updateDate from ASSET,ASSET_JOB,
                    ASSET_JOB_VERSION where ASSET.id=ASSET_JOB.assetID and
                    ASSET_JOB.id=ASSET_JOB_VERSION.assetJobID and ASSET.showcode='%(showname)s' 
                    and ASSET.type='%(level1)s' and ASSET.aname='%(level2)s' and ASSET_JOB.workcode='%(level3)s'    '''
            
        self.cr.execute( query % self.fileinfo )
        result = [x[0] for x in self.cr.fetchall()]
        self.cr.close()
        self.db.close()        
        return result[0]

    def getFinalDate(self):
        pass
    
    def getElapsedTime(self):        
        return self.getLatestDate() - self.getCreatedDate()
    
    
        
        
        
if __name__ == '__main__':
    thepath = '/show/tower/seq/085/085_1020/ani/dev/scenes/085_1020_ani_v01_w04.mb'
    progress = WIPmodel( thepath )
    print progress.getElapsedTime()