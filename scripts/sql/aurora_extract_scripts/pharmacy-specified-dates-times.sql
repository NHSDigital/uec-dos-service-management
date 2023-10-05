--servicespecifiedopeningdates and times for subset of pharms
select
s.id as service_id,
ssod.date,
ssot.starttime,
ssot.endtime,
ssot.isclosed
from pathwaysdos.services s
join pathwaysdos.servicespecifiedopeningdates ssod
on s.id = ssod.serviceid
join pathwaysdos.servicespecifiedopeningtimes ssot
on ssod.id = ssot.servicespecifiedopeningdateid
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
order by s.uid asc, ssod.date asc, ssot.starttime asc
