-- Script to clean production data for use in non-prod environments


-- 1.0 Truncate User related Tables

truncate pathwaysdos.savedsearches, pathwaysdos.usersavedsearches ;
truncate pathwaysdos.serviceattributes cascade;

-- 1.1 Clear down accounts 
delete from pathwaysdos.userpermissions up where up.userid not in (31);
delete from pathwaysdos.userreferralroles ur where ur.userid not in (31);
delete from pathwaysdos.userregions ur where ur.userid not in (31);
delete from pathwaysdos.userservices us where us.userid not in (31);
delete from pathwaysdos.users u where u.id not in (31);

--- run separate script to update user 31

-- 2.0 Stub Sensitive Fields In The Services Table
update pathwaysdos.services
set publicreferralinstructions = concat('STUB Public Referral Instruction Text Field ', id)
where publicreferralinstructions is not null;

update pathwaysdos.services
set telephonetriagereferralinstructions = concat('STUB Telephone Triage Referral Instructions Text Field ', id)
where telephonetriagereferralinstructions is not null;

update pathwaysdos.services set nonpublicphone = '99999 000000' where nonpublicphone is not null AND (id % 2) = 0;

update pathwaysdos.services set nonpublicphone = '00000 888888' where nonpublicphone is not null AND (id % 2) = 1;

update pathwaysdos.services set fax = '77777 000000' where fax is not null AND (id % 2) = 0;

update pathwaysdos.services set fax = '00000 666666' where fax is not null AND (id % 2) = 1;

update pathwaysdos.services set email = concat(id, '-fake@nhs.gov.uk') where email is not null;

update pathwaysdos.services set createdby = 'HUMAN' where createdby != 'ROBOT';

update pathwaysdos.services set modifiedby = 'HUMAN' where modifiedby != 'ROBOT';

-- 3.0 Stub Possibly Sensitive Fields In The Service Capacities Table
update pathwaysdos.servicecapacities set notes = null, modifiedbyid = null, modifiedby = null,
modifieddate = null, capacitystatusid = 1;

-- 4.1 Truncate grid tables
truncate pathwaysdos.capacitygridsheethistories;
truncate pathwaysdos.capacitygridconditionalstyles, pathwaysdos.capacitygridcustomformulas, pathwaysdos.capacitygridcustomformulastyles,
pathwaysdos.capacitygriddata, pathwaysdos.capacitygridheaders, pathwaysdos.capacitygridparentsheets, pathwaysdos.capacitygridservicetypes;
truncate pathwaysdos.servicecapacitygrids;

-- 4.2 Truncate news and news related data
truncate pathwaysdos.news, pathwaysdos.newsacknowledgedbyusers, pathwaysdos.newsforpermissions;

-- 4.3 Truncate purgedusers
truncate pathwaysdos.purgedusers;

-- 4.4 Truncate Service Change History Tables and The Service Endpoints Table
truncate pathwaysdos.changes, pathwaysdos.servicehistories;
truncate pathwaysdos.serviceendpoints cascade;

-- 5.0 Stub Sensitive Fields in the Service Phone Numbers table

update pathwaysdos.servicephonenumbers set phonenumber = '99999 000000', phonedescription = concat('STUB Phonedescription NonPublic 1  Text Field ' , id) where ispublic=false AND (id % 2) = 0;

update pathwaysdos.servicephonenumbers set phonenumber = '00000 888888', phonedescription = concat('STUB Phonedescription NonPublic 2  Text Field ' , id)  where ispublic=false AND (id % 2) = 1;

update pathwaysdos.servicephonenumbers set phonenumber = '888888 000000', phonedescription = concat('STUB Phonedescription Public 1  Text Field ' , id)   where ispublic=true AND (id % 2) = 0;

update pathwaysdos.servicephonenumbers set phonenumber = '00000 999999', phonedescription = concat('STUB Phonedescription Public 2  Text Field ' , id)   where ispublic=true AND (id % 2) = 1;


 -- 6.0 Stub out Sensitive Professionalreferralinfo in Services table to contain realistic characters and length
update pathwaysdos.services  set professionalreferralinfo = '# **Service Information**

The flu vaccine is a safe and effective vaccine. 
It''s offered every year on the NHS to help protect people at risk of getting seriously ill from flu.

**Information Links:**

Adult''s flu vaccine - https://www.nhs.uk/conditions/vaccinations/flu-influenza-vaccine/

Children''s flu vaccine - https://www.nhs.uk/conditions/vaccinations/child-flu-vaccine/

Made Up Links  - https://www.nhs.uk/service-search/pharmacy/find-a-pharmacy/download.cfm?doc=docm93jijm4n19386.docx&ver=51796

The best time to have the flu vaccine is in the autumn or early winter before flu starts spreading. But you can get the vaccine later.
# **Where to get the flu vaccine?**
You can have the NHS flu vaccine at:
* Your GP surgery
* A pharmacy offering the service
* Your midwifery service if you''re pregnant
* A hospital appointment
If you do not have your flu vaccine at your GP surgery, you do not have to tell the surgery. This will be done for you.

# **Who can have the flu vaccine?**
The flu vaccine is given free on the NHS to people who:
* Are 50 and over (including those who''ll be 50 by 31 March 2022)
* Have certain health conditions
* Are pregnant
* Are in long-stay residential care
* Receive a carer''s allowance, or are the main carer for an older or disabled person who may be at risk if you get sick
* Live with someone who is more likely to get infections (such as someone who has HIV, has had a transplant or is having certain treatments for cancer, lupus or rheumatoid arthritis)
* Frontline health or social care workers

# Who should not have the flu vaccine?
Most adults can have the flu vaccine, but you should avoid it if you have had a serious allergic reaction to a flu vaccine in the past.

You may be at risk of an allergic reaction to the flu vaccine injection if you have an egg allergy. This is because some flu vaccines are made using eggs.

Ask a GP or pharmacist for a low-egg or egg-free vaccine.

If you''re ill with a high temperature, it''s best to wait until you''re better before having the flu vaccine.

' where professionalreferralinfo is not null