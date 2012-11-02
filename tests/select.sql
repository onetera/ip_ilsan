


#select s.assetJobVerID , aa.id , aa.username , aa.aname , aa.ver , aa.wip , s.subject  from
#(select v.id ,v.username ,a.aname,v.ver,v.wip from ASSET a , ASSET_JOB j, ASSET_JOB_VERSION v
#where j.id=v.assetJobID and j.workcode='model' and a.aname='elevatorBController' and a.id=j.assetID ) aa 
#left join
#ASSET_SUBJECT s on aa.id=s.assetJobVerID 
#left join
#ASSET_JOB_CMMT c on aa.id=c.assetJobVerID
#order by aa.id desc


#, c.comment

select aa.id , aa.username , aa.shotname ,aa.ver,aa.wip , s.subject , c.comment from
(select v.id ,v.username ,i.shotname,v.ver,v.wip from JOB_INFO i , JOB_VERSION v
where i.id=v.jobInfoID and i.workcode='ani' and i.shotname='085_1020') aa 
left join
JOB_SUBJECT s on s.jobVerID=aa.id 
left join
JOB_CMMNT c on c.jobVerID=aa.id 
order by aa.id desc



