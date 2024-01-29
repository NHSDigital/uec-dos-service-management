DROP TABLE IF EXISTS  temp_script_counts;
create TEMP TABLE temp_script_counts(
count int, indicator varchar(50), stage  varchar(50)
);

insert into temp_script_counts
select count(*) as count, 'savedsearches_truncated_table' as indicator, 'before' as stage from pathwaysdos.savedsearches;
insert into temp_script_counts 
select count(*) as count, 'usersavedsearches_truncated_table' , 'before' as stage from pathwaysdos.usersavedsearches ;
insert into temp_script_counts 
select count(*) as count, 'userpermissions_truncated_table' , 'before' as stage from  pathwaysdos.userpermissions up where up.userid not in (31,13608);
insert into temp_script_counts 
select count(*) as count, 'userreferralroles_truncated_table' , 'before' as stage from pathwaysdos.userreferralroles ur where ur.userid not in (31,13608);
insert into temp_script_counts 
select count(*) as count, 'userregions_truncated_table' , 'before' as stage from pathwaysdos.userregions ur where ur.userid not in (31,13608);
insert into temp_script_counts 
select count(*) as count, 'userservices_truncated_table' , 'before' as stage from pathwaysdos.userservices us where us.userid not in (31,13608);
insert into temp_script_counts 
select count(*) as count, 'users_to only_leave_admin' , 'before' as stage from pathwaysdos.users u where u.id not in (31,13608);
insert into temp_script_counts
select count(*) as count, 'capacitygridsheethistories_truncated_table' , 'before' as stage from pathwaysdos.capacitygridsheethistories;
insert into temp_script_counts 
select count(*) as count, 'capacitygridconditionalstyles_truncated_table' , 'before' as stage from pathwaysdos.capacitygridconditionalstyles;
insert into temp_script_counts 
select count(*) as count, 'capacitygridcustomformulas_truncated_table' , 'before' as stage from pathwaysdos.capacitygridcustomformulas;
insert into temp_script_counts 
select count(*) as count, 'capacitygridcustomformulastyles_truncated_table' , 'before' as stage from pathwaysdos.capacitygridcustomformulastyles;
insert into temp_script_counts 
select count(*) as count, 'capacitygriddata_truncated_table' , 'before' as stage from pathwaysdos.capacitygriddata;
insert into temp_script_counts 
select count(*) as count, 'capacitygridheaders_truncated_table' , 'before' as stage from pathwaysdos.capacitygridheaders;
insert into temp_script_counts 
select count(*) as count, 'capacitygridparentsheets_truncated_table' , 'before' as stage from pathwaysdos.capacitygridparentsheets;
insert into temp_script_counts 
select count(*) as count, 'capacitygridservicetypes_truncated_table' , 'before' as stage from pathwaysdos.capacitygridservicetypes;
insert into temp_script_counts 
select count(*) as count, 'servicecapacitygrids_truncated_table' , 'before' as stage from pathwaysdos.servicecapacitygrids;
insert into temp_script_counts 
select count(*) as count, 'news_truncated_table' , 'before' as stage from pathwaysdos.news;
insert into temp_script_counts 
select count(*) as count, 'newsacknowledgedbyusers_truncated_table' , 'before' as stage from pathwaysdos.newsacknowledgedbyusers;
insert into temp_script_counts
select count(*) as count, 'newsforpermissions_truncated_table' , 'before' as stage from pathwaysdos.newsforpermissions;
insert into temp_script_counts
select count(*) as count, 'purgedusers_truncated_table' , 'before' as stage from pathwaysdos.purgedusers;
insert into temp_script_counts
select count(*) as count, 'changes_truncated_table' , 'before' as stage from pathwaysdos.changes;
insert into temp_script_counts
select count(*) as count, 'servicehistories_truncated_table' , 'before' as stage from pathwaysdos.servicehistories;
insert into temp_script_counts
select count(*) as count, 'serviceendpoints_truncated_table' , 'before' as stage from pathwaysdos.serviceendpoints;

insert into temp_script_counts
select count(*) as count, 'publicreferralinstructions_update_field' , 'before' as stage from pathwaysdos.services where publicreferralinstructions is not null;
-- and publicreferralinstructions = concat('STUB Public Referral Instruction Text Field ', id)
insert into temp_script_counts
select count(*) as count, 'telephonetriagereferralinstructions_update_field' , 'before' as stage from pathwaysdos.services where telephonetriagereferralinstructions is not null;
-- and telephonetriagereferralinstructions = concat('STUB Telephone Triage Referral Instructions Text Field ', id)


insert into temp_script_counts
select count(*) as count, 'nonpublicphone_1_update_field' , 'before' as stage from pathwaysdos.services where nonpublicphone is not null AND (id % 2) = 0;
-- and nonpublicphone = '99999 000000'

insert into temp_script_counts
select count(*) as count, 'nonpublicphone_2_update_field' , 'before' as stage from pathwaysdos.services where nonpublicphone is not null AND (id % 2) = 1;
-- and nonpublicphone = '00000 888888'

insert into temp_script_counts
select count(*) as count, 'nonpublicphone_total' , 'before' as stage from pathwaysdos.services where nonpublicphone is not null ;

insert into temp_script_counts
select count(*) as count, 'fax_1_update_field' , 'before' as stage from pathwaysdos.services where fax is not null AND (id % 2) = 0;
-- and fax = '77777 000000'

insert into temp_script_counts
select count(*) as count, 'fax_2_update_field' , 'before' as stage from pathwaysdos.services where fax is not null AND (id % 2) = 1;
-- and fax = '00000 666666'

insert into temp_script_counts
select count(*) as count, 'fax_total' , 'before' as stage from pathwaysdos.services where fax is not null ;

insert into temp_script_counts
select count(*) as count, 'email_update_field' , 'before' as stage from pathwaysdos.services where email is not null;
-- and email = concat(id, '-fake@nhs.gov.uk') 

insert into temp_script_counts
select count(*) as count, 'createdby_update_field' , 'before' as stage from pathwaysdos.services where createdby != 'ROBOT';
--and createdby = 'HUMAN'

insert into temp_script_counts
select count(*) as count, 'createdby_ROBOT' , 'before' as stage from pathwaysdos.services where createdby = 'ROBOT';
 

insert into temp_script_counts
select count(*) as count, 'modifiedby_update_field' , 'before' as stage from pathwaysdos.services where modifiedby != 'ROBOT';
--and modifiedby = 'HUMAN' 

insert into temp_script_counts
select count(*) as count, 'modifiedby_ROBOT' , 'before' as stage from pathwaysdos.services where modifiedby = 'ROBOT';


insert into temp_script_counts
select count(*) as count, 'notes_update_field' , 'before' as stage from pathwaysdos.servicecapacities where notes is not null; 
--notes is null

insert into temp_script_counts
select count(*) as count, 'modifiedbyid_update_field' , 'before' as stage from pathwaysdos.servicecapacities where modifiedbyid is not null; 
--modifiedbyid is null

insert into temp_script_counts
select count(*) as count, 'modifiedby_update_field' , 'before' as stage from pathwaysdos.servicecapacities where modifiedby is not null; 
--modifiedby is null

insert into temp_script_counts
select count(*) as count, 'modifieddate_update_field' , 'before' as stage from pathwaysdos.servicecapacities where modifieddate is not null; 
--modifieddate is null

insert into temp_script_counts
select count(*) as count, 'capacitystatusid_total' , 'before' as stage from pathwaysdos.servicecapacities ;

insert into temp_script_counts
select count(*) as count, 'capacitystatusid_not_1_update_field' , 'before' as stage from pathwaysdos.servicecapacities where capacitystatusid <> 1 ;
--where capacitystatusid = 1 

insert into temp_script_counts
select count(*) as count, 'servicephonenumbers_nonpublic_1_update_field' , 'before' as stage from pathwaysdos.servicephonenumbers where ispublic=false AND (id % 2) = 0;
--where phonenumber = '99999 000000' and phonedescription = concat('STUB Phonedescription NonPublic 1  Text Field ' , id) 

insert into temp_script_counts
select count(*) as count, 'servicephonenumbers_nonpublic_2_update_field' , 'before' as stage from pathwaysdos.servicephonenumbers where ispublic=false AND (id % 2) = 1;
--where phonenumber = '00000 888888', phonedescription = concat('STUB Phonedescription NonPublic 2 Text Field ' , id

insert into temp_script_counts
select count(*) as count, 'servicephonenumbers_public_1_update_field' , 'before' as stage from pathwaysdos.servicephonenumbers where ispublic=true AND (id % 2) = 0;
--where phonenumber = '888888 000000', phonedescription = concat('STUB Phonedescription Public 1 Text Field ' , id) 

insert into temp_script_counts
select count(*) as count, 'servicephonenumbers_public_1_update_field' , 'before' as stage from pathwaysdos.servicephonenumbers where ispublic=true AND (id % 2) = 1;
--where phonenumber = '00000 999999', phonedescription = concat('STUB Phonedescription Public 2 Text Field ' , id) 

insert into temp_script_counts
select count(*) as count, 'professionalreferralinfo_update_field' , 'before' as stage from pathwaysdos.services where professionalreferralinfo is not null;
-- and 
/*professionalreferralinfo = '# **Service Information**

The flu vaccine is a safe and effective vaccine. 
It''s offered every year on the NHS to help protect people at risk of getting seriously ill 'before' as stage from flu.

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

' */

select stage, indicator, count  from temp_script_counts;