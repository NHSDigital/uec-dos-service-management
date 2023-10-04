-- servicealignment data for subset of pharm services
select
s.id as service_id,
sa.commissioningorganisationid as commissioning_org_id,
commissioners.name as commissioning_org_name,
sa.islimited as is_limited
from pathwaysdos.services s
join pathwaysdos.servicealignments sa
on s.id = sa.serviceid
join pathwaysdos.services commissioners
on commissioners.id = sa.commissioningorganisationid
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
order by s.uid asc
