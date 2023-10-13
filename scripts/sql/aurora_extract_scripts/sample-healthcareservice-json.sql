select
    json_build_object(
        'services', json_agg(
            json_build_object(
                'resourceType','HealthcareService',
                'identifier',
                json_build_array(
                json_build_object('use','official','type','NEWID','value',md5(s.id::text)),
                json_build_object('use','old','type','DOSID','value',s.id),
                json_build_object('use','old','type','UID','value', s.uid)
                ),
              'active','true',
              'providedBy',
                json_build_object(
                  'resourceType', 'Organization',
                  'identifier', 'TBC'
                ),
              'type', 'Pharmacy',
              'location',
              json_build_object(
                  'resourceType', 'Location',
                  'identifier', 'TBC'
              ),
              'service_name',
              (case
              when length(s.odscode) = 5 then 'General Pharmacy Service'
              when s.name like 'DSP%' then 'Distance Selling Service'
              when s.name like 'CPCS%' then 'Community Pharmacy Service'
              when s.name like 'Pharm+%' then 'Community Pharmacy Service'
              when s.name = s.publicname then split_part(s.name,'-',1)
              else s.name end) ,
              'telecom',
              json_build_array(
                json_build_object('system','phone','value',s.publicphone, 'use', 'public'),
                json_build_object('system','fax','value',s.fax, 'use', 'non-public'),
                json_build_object('system','email','value',s.email, 'use', 'non-public')
              ),
              'serviceProfiles',json_build_object('name',serviceProfiles.name, 'eligibleFor',serviceProfiles.eligiblefor)
            )
        )
    ) services
from pathwaysdos.services s
left join
(select
    serviceid,
    'To be defined by the DoS lead' as name
    ,json_agg(
        json_build_array(rr.name)) eligibleFor
        from pathwaysdos.servicereferralroles sr
        inner join pathwaysdos.referralroles rr
        on sr.referralroleid=rr.id
        group by serviceid
) serviceProfiles
on s.id = serviceProfiles.serviceid

where s.id in (169621,
143973,
127423,
107275,
107273)
;
