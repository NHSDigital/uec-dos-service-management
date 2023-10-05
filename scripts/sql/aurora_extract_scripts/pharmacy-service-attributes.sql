-- serviceserviceattributes for subset of pharms
select
s.id as service_id,
sa.name as service_attribute_name,
sa.description as service_attribute_description,
sa.status as service_attribute_status,
sav.value
from pathwaysdos.services s
join pathwaysdos.serviceserviceattributes saa
on s.id = saa.serviceid
join pathwaysdos.serviceattributes sa
on sa.id = saa.serviceattributeid
join pathwaysdos.serviceattributetypes sat
on sat.id = sa.serviceattributetypeid
join pathwaysdos.serviceattributevalues sav
on saa.serviceattributevalueid = sav.id
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
