-- service referral data for subset of pharm services
select
s.id as service_id,
referred_from.id as referred_from_service_id,
referred_from.name as referred_from_service_name
from pathwaysdos.services s
join pathwaysdos.servicereferrals sr
on s.id = sr.referralserviceid
join pathwaysdos.services referred_from
on referred_from.id = sr.referredserviceid
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
