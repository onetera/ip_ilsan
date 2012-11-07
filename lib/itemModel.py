# -*- coding: utf-8 -*-

import os
import datetime
import re
import sys

try :
    import conndb
except :
    import sys
    if 'd10218' in os.getenv('USERNAME'):
        sys.path.append( '/home/d10218/work/ipipeline' )
    else:
        sys.path.append( '/lustre/INHouse/Tool/ipipeline/pub' )
    import conndb




def fileParser( thefile ):    
    basename = os.path.basename( thefile )
    basepath = os.path.dirname( thefile )
    basenamesplit = basename.split('_')
    if 'linux' in sys.platform:
        basepathsplit = basepath.split( os.path.sep )
        tab           = 1 if basepathsplit[3] == 'assets' else 2
        mode          = basepathsplit[7]
        prj           = basepathsplit[2]
        level1        = basepathsplit[4]
        level2        = basepathsplit[5]
        level3        = basepathsplit[6]
    else :
        basepath      = basepath.replace('/','\\')
        basepathsplit = [ x for x in basepath.split( '\\' ) if x!='']                       
        tab           = 1 if basepathsplit[2] == 'assets' else 2
        mode          = basepathsplit[6]
        prj           = basepathsplit[1]
        level1        = basepathsplit[3]
        level2        = basepathsplit[4]
        level3        = basepathsplit[5]

    ver  =  re.search( '(?<=v)\d{2}' , basename ).group()
    wip = re.search( '(?<=w)\d{2}' , basename ).group() if re.search( '(?<=w)\d{2}' , basename ) != None else '0'
    
    if mode == 'dev':
        ex = "(?<=w[0-9]{2}_).+?(?=.mb)"
    else:
        ex = "(?<=v[0-9]{2}_).+?(?=.mb)"
    subject = re.search( ex , basename ).group() if re.search( ex , basename ) != None else ''
    return {'tab':tab,'mode':mode,'prj':prj,'level1':level1,'level2':level2,'level3':level3,'ver':ver,'wip':wip,'subject':subject}

def findOwner( thefile  ): 
    theDic = fileParser( thefile )
    if theDic['tab'] == 1:
        query = """          
        select distinct c.username from 
        (select v.id , v.username,j.workcode,a.aname,v.ver,v.wip
        from ASSET_JOB_VERSION v,ASSET_JOB j ,ASSET a , ASSET_SUBJECT s
        where a.id=j.assetID and j.id=v.assetJobID and a.showcode='%(prj)s' and j.workcode='%(level3)s' 
        and a.type='%(level1)s' and a.aname='%(level2)s'  and v.ver = %(ver)s and v.wip=%(wip)s  ) as c
        left join ASSET_SUBJECT s on c.id=s.assetJobVerID order by c.ver desc
                    """
                    
    elif theDic['tab'] == 2:
        query = """
        select distinct c.username from
        (select v.id,v.username,a.workcode,a.shotname,v.ver,v.wip
        from JOB_INFO as a,JOB_VERSION as  v
        where a.id=v.jobInfoID and a.showcode='%(prj)s' and a.seqname='%(level1)s' and a.shotname='%(level2)s' and 
        a.workcode='%(level3)s' and v.ver = %(ver)s and v.wip=%(wip)s  ) as c
        left join JOB_SUBJECT as  d on c.id=d.jobVerID order by c.ver desc
                    """
#    theDic = {'prj':prj , 'level1':level1 , 'level2':level2 , 'level3':level3 ,'ver':ver , 'wip':wip  }        
            
    db = conndb.DBhandler()
    db.dbConn()
    result = db.getFetch(query % theDic )

    result = result[0][0] if result != [] else ''
    
#    currSelected = self.getCurrentlySelectedItem(1, 3)
#    historyObj = self.getEventNotes(1, currSelected[0], currSelected[1], currSelected[2])      
#   
#        for row, note in enumerate(historyObj):
#            author = QTableWidgetItem(note.author)
            
    return result           



                    
                    
def tableitem( tab , prj , level1 , level2 , level3 , mode ):
    if tab == 1:
        query = """
        select distinct c.username,c.workcode,c.aname,
        c.ver,%(c_wip)s s.subject,c.uploadDate from 
        (select v.id , v.username,j.workcode,a.aname,
        v.ver,v.wip,v.uploadDate ,j.created
        from ASSET_JOB_VERSION v,ASSET_JOB j ,ASSET a
        where a.id=j.assetID and j.id=v.assetJobID and a.showcode='%(prj)s' and j.workcode='%(level3)s' 
        and a.type='%(level1)s' and a.aname='%(level2)s' %(v_wip)s ) as c
        left join ASSET_SUBJECT s on c.id=s.assetJobVerID order by %(order)s desc
                    """
    elif tab == 2:
        query = """
        select distinct c.username,c.workcode,c.shotname,c.ver,%(c_wip)s d.subject,c.uploadDate from
        (select v.id,v.username,a.workcode,a.shotname,v.ver,v.wip,a.created,v.uploadDate
        from JOB_INFO as a,JOB_VERSION as  v
        where a.id=v.jobInfoID and a.showcode='%(prj)s' and a.seqname='%(level1)s' and a.shotname='%(level2)s' and 
        a.workcode='%(level3)s' %(v_wip)s ) as c
        left join JOB_SUBJECT as  d on c.id=d.jobVerID order by %(order)s desc
                    """
    theDic = {'prj':prj , 'level1':level1 , 'level2':level2 , 'level3':level3 } 
    if mode == 'dev':
        theDic['c_wip'] = 'c.wip,'
        theDic['v_wip'] = 'and v.wip <> 0'
        theDic['order'] = 'c.wip'
    else :
        theDic['c_wip'] = ''
        theDic['v_wip'] = ''
        theDic['order'] = 'c.ver'
        
    atype = 'assets' if tab ==1 else 'seq'     
    originPath = os.path.join( str(prj) , atype , level1 , level2 , level3 , mode , 'scenes' )
        
    db = conndb.DBhandler()
    db.dbConn()
    result = db.getFetch(query % theDic )         
    for i,x in enumerate(result): 
        result[i] = list( result[i] )
        if mode == 'dev':       
            result[i][3] = str(x[3]).zfill(2)
            result[i][4] = str(x[4]).zfill(2)
            result[i][5] = '' if x[5] == None else x[5] 
            n = getitemfilename( mode , x[2] , x[1] , result[i][3] , result[i][4]  )
             
        else : 
            result[i][3] = str(x[3]).zfill(2)
            result[i][4] = '' if x[4] == None else x[4]
            n = getitemfilename( mode , x[2] , x[1] , result[i][3] , None  )
            
        
        result[i][-1] = unicode( x[-1].strftime('%Y/%m/%d %I:%M:%S %p') )            
#        result[i].append(n)
#        result[i].append( os.path.join( originPath , n+'.mb' ) )
      
    return result


def getComments( tab , prj , level1 , level2 , level3 ):
    if tab == 1:
        query = """
        select distinct c.username,c.workcode,c.aname,
        c.ver,%(c_wip)s s.subject,c.uploadDate from 
        (select v.id , v.username,j.workcode,a.aname,
        v.ver,v.wip,v.uploadDate ,j.created
        from ASSET_JOB_VERSION v,ASSET_JOB j ,ASSET a
        where a.id=j.assetID and j.id=v.assetJobID and a.showcode='%(prj)s' and j.workcode='%(level3)s' 
        and a.type='%(level1)s' and a.aname='%(level2)s' %(v_wip)s ) as c
        left join ASSET_SUBJECT s on c.id=s.assetJobVerID order by %(order)s desc
                    """

            
def getitemfilename( mode , level2 , level3 , ver , wip ):
        filename = '_'.join( [ level2 , level3 , ver ]  )
        if mode != 'pub':
            filename = '_'.join([filename , wip ])
        return filename    
    

        



if __name__ == '__main__':
    print fileParser('/show/show/tower/seq/059A/059A_0020/matchmove/dev/scenes/059A_0020_matchmove_v01_w01.mb')
#    print findOwner('/show/CZ12/seq/R7/R7_115/ani/dev/scenes/R7_115_ani_v02_w03.mb' ,
#                     1 , 'dev' , 'CZ12' , 'R7' , 'R7_115' , 'ani' , '02' , '03' , subject='' )


#    for x in  tableitem( 1 , 'CZ12' , 'prop' , 'chute' , 'rig' , 'dev' ):
#        print x  
#    for x in  tableitem( 2 , 'CZ12' , 'R7' , 'R7_115' , 'ani' , 'dev' ):
#        print x
        
        
                  