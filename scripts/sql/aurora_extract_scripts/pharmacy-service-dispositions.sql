-- disposition data for sub set of pharmacy services
select
s.id as service_id,
d.id as disposition_id,
d.name as disposition_desc,
d.dxcode as disposition_dx_code,
d.dispositiontime as disposition_time
from pathwaysdos.services s
join pathwaysdos.servicedispositions sd
on s.id = sd.serviceid
join pathwaysdos.dispositions d
on d.id = sd.dispositionid
where (s.odscode like 'FC818%' or
    s.odscode like 'FC972%' or
    s.odscode like 'FWE15%' or
    s.odscode like 'FRR62%' or
    s.odscode like 'FHK43%' or
    s.odscode like 'FFW88%' or
    s.odscode like 'FTM24%' or
    s.odscode like 'FFQ10%' or
    s.odscode like 'FLE70%' or
    s.odscode like 'FMC35%' )
and s.statusid in (1,3)
order by s.uid asc, d.id asc
