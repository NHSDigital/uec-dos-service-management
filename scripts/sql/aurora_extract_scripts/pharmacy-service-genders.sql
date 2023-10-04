-- genders served by sub set of pharm services
select
s.id as service_id,
sg.genderid as gender_id,
g.name as gender_desc
from pathwaysdos.services s
join pathwaysdos.servicegenders sg
on s.id = sg.serviceid
join pathwaysdos.genders g
on g.id = sg.genderid
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
order by s.uid asc, sg.genderid asc
