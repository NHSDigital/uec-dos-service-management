-- These SQL statements are used to build the JSON response that can be loaded into S3 for
-- the ODS comparison Lambda.

-- Pharmacy
select json_build_object(
  'odscodes', json_agg(
    json_build_object(
      'id', s.id,
      'uid', s.uid,
      'providedBy', s.odscode,
      'type', st.name,
      'publicName', s.publicname,
      'name', s.name,
      'address', s.address,
      'town', s.town,
      'postcode', s.postcode,
      'publicphone', s.publicphone,
      'fax', s.fax,
      'latitude', s.latitude,
      'longitude', s.longitude
      )
    )
  )
from pathwaysdos.services s,
  pathwaysdos.servicetypes st
where s.typeid in (13,132)
and   s.typeid = st.id
and   s.odscode is not null
and   s.statusid = 1
limit 100

--GP

-- GPs Practice
select json_build_object(
  'odscodes', json_agg(
    json_build_object(
      'id', s.id,
      'uid', s.uid,
      'providedBy', s.odscode,
      'type', st.name,
      'publicName', s.publicname,
      'name', s.name,
      'address', s.address,
      'town', s.town,
      'postcode', s.postcode,
      'publicphone', s.publicphone,
      'fax', s.fax,
      'latitude', s.latitude,
      'longitude', s.longitude
      )
    )
  )
from pathwaysdos.services s,
  pathwaysdos.servicetypes st
where s.typeid in (100)
and   s.typeid = st.id
and   s.odscode is not null
and   len(s.odscode)=6
and   s.statusid = 1
limit 100

-- GP branches
select json_build_object(
  'odscodes', json_agg(
    json_build_object(
      'id', s.id,
      'uid', s.uid,
      'providedBy', s.odscode,
      'type', st.name,
      'publicName', s.publicname,
      'name', s.name,
      'address', s.address,
      'town', s.town,
      'postcode', s.postcode,
      'publicphone', s.publicphone,
      'fax', s.fax,
      'latitude', s.latitude,
      'longitude', s.longitude
      )
    )
  )
from pathwaysdos.services s,
  pathwaysdos.servicetypes st
where s.typeid in (100)
and   s.typeid = st.id
and   s.odscode is not null
and   len(s.odscode)>6
and   s.statusid = 1
limit 100
