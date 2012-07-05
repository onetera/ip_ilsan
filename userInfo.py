# -*- coding: utf-8 -*-


import os
import sys
import subprocess
import re
import socket
import re


from foundations.globals.constants import Constants

if 'linux' in sys.platform:
    try:
        import ldap
    except :    
        sys.path.append( '/lustre/INHouse/Tool/irtool/PyQt4.9.1/python2.7/lib/python2.7/site-packages/python_ldap-2.3.13-py2.7-linux-x86_64.egg' )
        import ldap



class UserInformation:
    def __init__(self):
        self.id = os.getenv('USERNAME')
        self.ip = getCurrentIP()
        
        
        if self.id!=None and re.match('DIGITALIDEA\\\\d\d{5}' , self.id ) and 'linux' in sys.platform :
            self.num = self.id.split('\\')[1]                 
            self.name =  self.getLdapUser()[0]
            self.dept = self.getLdapUser()[1]
            
        else : 
            self.id = 'idea'
            self.num = 'd00000'
            self.name = 'idea'
            self.dept = 'Intern'

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

    def getLdapUser(self ):
        l=ldap.open( Constants.ldapAddress )
        uname="CN=ipipeline,CN=Users,DC=digitalidea,DC=co,DC=kr"
        password="idea"
        
        l.protocol_version=ldap.VERSION3        
        l.simple_bind_s(uname,password)
        
        base_dn = 'CN=Users,DC=digitalidea,DC=co,DC=kr'
        filter = 'sAMAccountNAME=%s' % self.num
        attr = ['info','sAMAccountNAME' , 'mail' ]        
        result = l.search_s(base_dn,ldap.SCOPE_SUBTREE,filter,attr)
        return result[0][1]['info'][0] , result[0][1]['mail'][0]
#        return result[0][1]['info'][0] , re.search( '(?<=CN=).*?(?=,)' , result[0][1]['memberOf'][0] ).group()

def findUserNum( name ):
    l=ldap.open( Constants.ldapAddress )
    uname="CN=ipipeline,CN=Users,DC=digitalidea,DC=co,DC=kr"
    password="idea"
    
    l.protocol_version=ldap.VERSION3        
    l.simple_bind_s(uname,password)
    
    base_dn = 'CN=Users,DC=digitalidea,DC=co,DC=kr'
    filter = 'info=%s' % name
    attr = [ 'sAMAccountName' , 'mail' ]        
    result = l.search_s(base_dn,ldap.SCOPE_SUBTREE,filter,attr)
    return result[0][1]['sAMAccountName'][0] , result[0][1]['mail'][0]

def findUserName( num ):
    l=ldap.open( Constants.ldapAddress )
    uname="CN=ipipeline,CN=Users,DC=digitalidea,DC=co,DC=kr"
    password="idea"
    
    l.protocol_version=ldap.VERSION3        
    l.simple_bind_s(uname,password)
    
    base_dn = 'CN=Users,DC=digitalidea,DC=co,DC=kr'
    filter = 'sAMAccountName=%s' % num
    attr = [ 'info' , 'mail' ]        
    result = l.search_s(base_dn,ldap.SCOPE_SUBTREE,filter,attr)
    return result[0][1]['info'][0] , result[0][1]['mail'][0]

def UserInfo():
    return UserInformation()
            
def getCurrentIP():
    if 'linux' in sys.platform:
        ip_addr=subprocess.Popen("/sbin/ifconfig",stdout=subprocess.PIPE).stdout
    else:
        ip_addr=subprocess.Popen("ipconfig",stdout=subprocess.PIPE).stdout
    data=ip_addr.read().strip().split("\n")
    ip_addr.close()
#  
    pattern=re.compile(r"(10)\.(0)\.(\d{1,2}|1\d{2}|2[0-4]\d|25[0-4])\.(\d{1,3})")
    C_ADDRESS=pattern.findall(str(data))
    return '.'.join( C_ADDRESS[0] )




if __name__ == '__main__':
    print findUserNum('김성훈')
    
#    for x in result[0][1]:   
#        if x == 'memberOf':
#            print result[0][1][x][0]
#            print re.search( '(?<=CN=).*?(?=,)' , result[0][1][x][0] ).group()
            
    
#    print  result[0][1]
#    print  result[0][1]['group'][0]  

    
    