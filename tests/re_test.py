import re

a='chute_rig_v01_w02_beltOnly.mb'
b ='chute_rig_v01_beltOnly.mb'
c='chute_rig_v01_w02.mb'
d ='chute_rig_v01.mb'



#ex = "v[0-9]{2}_w[0-9]{2}_[\w]+.mb"
#print re.search('(?<=w\d{2}_?).+(?=\.)' , a).group()
#ex = '(?(w)w|v).+(?=\.)'
#ex = "v[0-9]{2}(_w[0-9]{2}_)?.*(?=.mb)"

exdev = "(?<=w[0-9]{2}_).+?(?=.mb)"
expub = "(?<=v[0-9]{2}_).+?(?=.mb)"

print 'dev a : ' , re.search( exdev,a).group() if re.search( exdev,a) else ''
print 'dev c : ' , re.search( exdev,c).group() if re.search( exdev,c) else ''

print 'pub b : ' , re.search( expub,b).group() if re.search( expub,b) else ''
print 'pub d : ' , re.search( expub,d).group() if re.search( expub,d) else ''
