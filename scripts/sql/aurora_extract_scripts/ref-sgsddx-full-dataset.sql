select
sgsd.symptomgroupid,
sg.name sg_name,
sgsd.symptomdiscriminatorid,
sd.description sd_description,
ddg.disposgrpid,
ddg.dxname disposition_name,
ddg.dxdxcode dispositioncode,
ddg.dxtime disposition_time
from pathwaysdos.symptomgroupsymptomdiscriminators sgsd
join pathwaysdos.symptomgroups sg
on sg.id = sgsd.symptomgroupid
join pathwaysdos.symptomdiscriminators sd
on sd.id = sgsd.symptomdiscriminatorid
cross join
(select dis.id dxid, dis.name dxname, dis.dxcode dxdxcode, dis.dispositiontime dxtime, dg.uid disposgrpid
from pathwaysdos.dispositions dis
join pathwaysdos.dispositiongroupdispositions dgd
on dis.id= dgd.dispositionid
join pathwaysdos.dispositiongroups dg
on dg.id=dgd.dispositiongroupid
where dg.uid > 24 and dg.uid not in (9000,9001,9002,9003,9004,9005,9100,9101,9102,9103,9200,9300,9400)) ddg
where sg.zcodeexists is null or sg.zcodeexists<>'true'
