select
json_build_object(
  'services',
  json_agg(
    json_build_object(
      'resourceType','HealthcareService',
      'identifier', identifier.identifier,
      'active','true',
      'providedBy',
      json_build_object(
        'resourceType', 'Organization',
        'identifier', 'TBC' ),
      'type',
      st.name,
      'location',
      json_build_object(
        'resourceType', 'Location',
        'identifier', 'TBC' ),
      'service_name',
      (case
        when length(s.odscode) = 5 then 'General Pharmacy Service'
        when s.name like 'DSP%' then 'Distance Selling Service'
        when s.name like 'CPCS%' then 'Community Pharmacy Service'
        when s.name like 'Pharm+%' then 'Community Pharmacy Service'
        when s.name = s.publicname then split_part(s.name,'-',1)
        else s.name end) ,
      'telecom', telecom.telecoms,
      'serviceProfiles',
      serviceProfiles
    )
  )
) services
from pathwaysdos.services s inner join pathwaysdos.servicetypes st on s.typeid=st.id
left join (
  select
  id,
    json_agg(
      json_build_object(
        'use', 'old',
        substr(c.identifier,1,position('-' IN c.identifier)-1) ,
        split_part(c.identifier,'-',2)
      )
    ) identifier
from pathwaysdos.services  s
cross join lateral (values ('uid-'||uid),('serviceid-'||id)) as c(identifier)
group by id
) identifier
on s.id = identifier.id
left join (
  select
  id,
    json_agg(
      json_build_object(
        substr(c.telecom,1,position('-' IN c.telecom)-1),
        split_part(c.telecom,'-',2)
      )
    ) telecoms
  from pathwaysdos.services  s
  cross join lateral (values ('publicphone-'||publicphone),('nonpublicphone-'||nonpublicphone),('fax-'||fax)) as c(telecom)
  where  c.telecom is not null
  group by id
) telecom
on s.id = telecom.id
left join
(select
serviceid,
'To be defined by the DoS lead' as name
,json_agg(
json_build_array(rr.name)) eligibleFor
from pathwaysdos.servicereferralroles sr
inner join pathwaysdos.referralroles rr on sr.referralroleid=rr.id group by serviceid
) serviceProfiles
on s.id = serviceProfiles.serviceid
where s.id in (169621,
143973,
127423,
107275,
107273)
;
