-- servicedayopening times for subset of pharm
-- 1 = Mon 2 = Tues
select
s.id as service_id,
sdo.dayid,
sdot.starttime,
sdot.endtime
from pathwaysdos.services s
join pathwaysdos.servicedayopenings sdo
on s.id = sdo.serviceid
join pathwaysdos.servicedayopeningtimes sdot
on sdo.dayid = sdot.servicedayopeningid
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
order by s.uid asc, sdo.dayid asc, sdot.starttime asc
