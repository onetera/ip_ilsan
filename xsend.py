# -*- coding: utf-8 -*-
import re
import sys,os,xmpp,time



def Message( tojid  , message ):
    if type( tojid ) == type(''):
        tojid = [ tojid ]
    elif type(tojid) == type(1) or message == '':
        return
     
    tojid = [ x+'@10.0.99.25' for x in tojid ]
    
      
    if re.search( 'd\d{5}' , os.getenv('USERNAME') ) != None:
        myid = re.search( 'd\d{5}' , os.getenv('USERNAME') ).group()  
    else :
        myid = 'd20001'
        
    myid += '@10.0.99.25'    
    jid=xmpp.protocol.JID( myid )    
    cl=xmpp.Client(jid.getDomain(),debug=[])    
    con=cl.connect()
    
    if not con:
        print 'could not connect!'
        cl.disconnect()
        return
    
    auth=cl.auth(jid.getNode(),'idea',resource=jid.getResource())
    if not auth:
        print 'could not authenticate!'
        cl.disconnect()
        return
            
    #cl.SendInitPresence(requestRoster=0)   # you may need to uncomment this for old server
    for x in tojid:
        id=cl.send( xmpp.protocol.Message( x ,message) )
        print 'sent message with id',id
    
#    time.sleep(1)   # some older servers will not send the message if you disconnect immediately after sending
    
    cl.disconnect()
    return True
    

if __name__ == '__main__':    
    Message('d10218','마야에서 보네는 메시지 입니다.')
    
    