with serviceProfiles as (select
    serviceid,
    'To be defined by the DoS lead' as name
    ,json_agg(
        json_build_array(rr.name)) eligibleFor
        from pathwaysdos.servicereferralroles sr
        inner join pathwaysdos.referralroles rr
        on sr.referralroleid=rr.id
        group by serviceid
)


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
                when s.typeid=134 then 'Distance Selling Pharmacy Service'
                when length(s.odscode) = 5 then 'General Pharmacy Service'
                when s.name like '%CPCS%' then 'Community Pharmacy Consultation Service'
                when s.publicname like '%CPCS%' then 'Community Pharmacy Consultation Service'
                when lower(s.name) like '%pharm+%' then 'Community Pharmacy Consultation Service'
                when s.name like '%UTI%' then 'UTI Care Service'
                when s.typeid=148 then 'Blood Pressure Service'
                when s.typeid=149 then 'Contraception Service'
                when s.name like '%inor%ilments%' then 'Minor Ailments Service'
                when s.name like '%ervice%' and position (':' in lower(s.name))>0 then split_part(s.name,':',1)
                when s.name like '%ervice%' and position ('-' in lower(s.name))>0 then split_part(s.name,'-',1)
                when position (':' in lower(s.name))>0 then split_part(s.name,':',1)||' Service'
                when position ('-' in lower(s.name))>0 then split_part(s.name,'-',1)||' Service'
                else s.name end) ,
              'telecom',
              json_build_array(
                json_build_object('system','phone','value',s.publicphone, 'use', 'public'),
                json_build_object('system','fax','value',s.fax, 'use', 'non-public'),
                json_build_object('system','email','value',s.email, 'use', 'non-public')
              ),
              'serviceProfiles',
              json_build_object(
                'name',serviceProfiles.name,
                'eligibleFor',serviceProfiles.eligiblefor,
                'genders', genders.gender,
                'ageranges', ageranges.ageranges,
                'gpReferral', gpReferral.gpReferral
              )
            )
        )
    ) services
from pathwaysdos.services s
left join serviceProfiles
on s.id = serviceProfiles.serviceid
left join
(select
    serviceid, 'gender',
    json_agg(
        json_build_object('gendername',g.name,'genderletter', g.letter)) gender
        from pathwaysdos.servicegenders sg
        inner join pathwaysdos.genders g
        on sg.genderid=g.id
        group by serviceid
) genders
on s.id = genders.serviceid
left join
(select
    serviceid, 'ageranges',
    json_agg(
        json_build_object('agefrom',sa.daysfrom,'ageto', sa.daysto)) ageranges
        from pathwaysdos.serviceagerange sa
        group by serviceid
) ageranges
on s.id = ageranges.serviceid
left join
(select
    s.id as serviceid,
    json_build_array(
      json_build_object('restricted',s.restricttoreferrals),
      'referredFrom', json_agg(
            json_build_object('resourceType','Organization','identifier',sr.referredserviceid)) ) gpReferral
            from pathwaysdos.services s inner join
            pathwaysdos.servicereferrals sr on s.id=sr.referralserviceid
            group by s.id,uid) gpReferral
on s.id = gpReferral.serviceid
inner join  (select distinct serviceid from pathwaysdos.servicesgsds) sgsd on s.id=sgsd.serviceid
where s.typeid in ( 13, 131,134,132,148,149) and s.statusid=1
