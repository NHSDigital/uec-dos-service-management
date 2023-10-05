-- count of active or commissioning pharm services (identified by service by type)
-- with 10 or more profiles
-- grouped by first 5 chrs of odscode
-- used essentially to find ODS codes to use in subsequent scripts
select
left(odscode,5) ,
count(*) from pathwaysdos.services s
left outer join pathwaysdos.servicestatuses t on s.statusid=t.id
left outer join pathwaysdos.servicetypes st on s.typeid=st.id
where odscode<>uid and left(odscode, length(uid))<>uid and odscode<>''
-- and st.name  like 'Pharm%'
and s.typeid in (13,131,132,134,148,149)
--and s.typeid in (134)
and s.statusid in (1,3)
--and s.subregionid = '8'
group by
left(odscode,5)
having count(*)>10
order by count(*) desc
