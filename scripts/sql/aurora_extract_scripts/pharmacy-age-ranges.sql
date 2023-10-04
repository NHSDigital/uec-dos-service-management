-- age range data for sub set of pharm services
select
s.id as service_id,
sar.daysfrom as age_range_days_from,
sar.daysto as age_range_days_to
from pathwaysdos.services s
join pathwaysdos.serviceagerange sar
on s.id = sar.serviceid
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
order by s.uid asc, sar.daysfrom asc
