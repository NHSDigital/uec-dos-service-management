-- servicesgsds from subset of pharm services
select
s.id as service_id,
sg.id as symptom_group_id,
sg.name as symptom_group_name,
sg.zcodeexists as symptom_group_zcode_exists,
sd.id as symptom_discriminator_id,
sd.description as symptom_discriminator_description
from pathwaysdos.services s
join pathwaysdos.servicesgsds sgsds
on s.id = sgsds.serviceid
join pathwaysdos.symptomdiscriminators sd
on sd.id = sgsds.sdid
join pathwaysdos.symptomgroups sg
on sg.id = sgsds.sgid
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
order by s.uid asc, sg.id asc, sd.id asc
