# -*- coding: utf-8 -*-


import os
import sys
import subprocess
import re
import ldap
import socket

class UserInformation:
    def __init__(self):
        self.id = os.getenv('USERNAME')
        self.ip = getCurrentIP()        
        if self.id != 'idea':
            self.num = self.id.split('\\')[1]      
            self.name = self.getUsername()
            
        else : 
            self.num = 'd00000'
            self.name = ''

    def __repr__(self):
        return  self.name 

    def checkAccount( self ):
        errnum = 0
        if not 'linux' in sys.platform:
            return        
        if not 'DIGITALIDEA' in  self.id:
            errnum += 1
        if self.num[0] != 'd':
            errnum += 1
        if len( self.num )  != 6:
            errnum += 1
        if errnum != 0:
            return False
        else:
            return True

    def getUsername(self ):
        l=ldap.open('10.0.99.10')
        uname="CN=ipipeline,CN=Users,DC=digitalidea,DC=co,DC=kr"
        password="idea"
        
        l.protocol_version=ldap.VERSION3        
        l.simple_bind_s(uname,password)
        
        base_dn = 'CN=Users,DC=digitalidea,DC=co,DC=kr'
        filter = 'sAMAccountNAME=%s' % self.num
        attr = ['info','sAMAccountNAME']        
        result = l.search_s(base_dn,ldap.SCOPE_SUBTREE,filter,attr)
        return result[0][1]['info'][0]

def UserInfo():
    return UserInformation()
            
def getCurrentIP():
    ip_addr=subprocess.Popen("/sbin/ifconfig",stdout=subprocess.PIPE).stdout
    data=ip_addr.read().strip().split("\n")
    ip_addr.close()
#  
    pattern=re.compile(r"(10)\.(0)\.(\d{1,2}|1\d{2}|2[0-4]\d|25[0-4])\.(\d{1,3})")
    C_ADDRESS=pattern.findall(str(data))
    return '.'.join( C_ADDRESS[0] )

if __name__ == '__main__':
    id = UserInfo()
    print id.ip
    print id.name
    print id.num
    
    for x in sys.path:
        print x
#    print id.checkAccount()
#    print id
#    print os.getenv('USERNAME')    
    
#    ip_addr=subprocess.Popen("/sbin/ifconfig",stdout=subprocess.PIPE).stdout
#    data=ip_addr.read().strip().split("\n")
#    ip_addr.close()
##  
#    pattern=re.compile(r"(10)\.(0)\.(\d{1,2}|1\d{2}|2[0-4]\d|25[0-4])\.(\d{1,3})")
#    C_ADDRESS=pattern.findall(str(data))
#    print C_ADDRESS
    
    