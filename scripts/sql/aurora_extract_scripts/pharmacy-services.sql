

--  basic service data for services linked by odscode
select s.*, st.name as type_desc,t.name as status_name
from services s
left outer join pathwaysdos.servicestatuses t on s.statusid=t.id
left outer join pathwaysdos.servicetypes st on s.typeid = st.id
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
order by s.odscode asc, s.typeid asc
