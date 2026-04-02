// Re-seed: drop edges tied to old geography (e.g. Austin) when node ids stayed the same
MATCH (p:Peer {id: 'peer_alex_kim'})-[r:STUDIES_AT]->(u:University)
WHERE u.id <> 'univ_iit'
DELETE r;
MATCH (m:Mentor)-[r:ALUM_OF]->(u:University)
WHERE m.id IN ['mentor_ananya_sharma', 'mentor_rajesh_kumar'] AND u.id <> 'univ_iit'
DELETE r;
MATCH (p:Peer {id: 'peer_alex_kim'})-[r:LIVES_NEAR]->(nb:Neighborhood)
WHERE nb.id <> 'nb_south_loop'
DELETE r;

// University / peers
MATCH (peer:Peer {id: 'peer_alex_kim'}), (u:University {id: 'univ_iit'})
MERGE (peer)-[:STUDIES_AT]->(u);

MATCH (peer:Peer {id: 'peer_alex_kim'}), (nb:Neighborhood {id: 'nb_south_loop'})
MERGE (peer)-[:LIVES_NEAR]->(nb);

// Mentors — alumni + country + help
MATCH (m1:Mentor {id: 'mentor_ananya_sharma'}), (u:University {id: 'univ_iit'})
MERGE (m1)-[:ALUM_OF]->(u);

MATCH (m1:Mentor {id: 'mentor_ananya_sharma'}), (c:Country {id: 'country_in'})
MERGE (m1)-[:FROM_COUNTRY]->(c);

MATCH (m1:Mentor {id: 'mentor_ananya_sharma'}), (n:Need {id: 'need_banking'})
MERGE (m1)-[:CAN_HELP_WITH]->(n);

MATCH (m1:Mentor {id: 'mentor_ananya_sharma'}), (n:Need {id: 'need_housing'})
MERGE (m1)-[:CAN_HELP_WITH]->(n);

MATCH (m2:Mentor {id: 'mentor_rajesh_kumar'}), (u:University {id: 'univ_iit'})
MERGE (m2)-[:ALUM_OF]->(u);

MATCH (m2:Mentor {id: 'mentor_rajesh_kumar'}), (c:Country {id: 'country_in'})
MERGE (m2)-[:FROM_COUNTRY]->(c);

MATCH (m2:Mentor {id: 'mentor_rajesh_kumar'}), (n:Need {id: 'need_banking'})
MERGE (m2)-[:CAN_HELP_WITH]->(n);

MATCH (m2:Mentor {id: 'mentor_rajesh_kumar'}), (n:Need {id: 'need_orientation'})
MERGE (m2)-[:CAN_HELP_WITH]->(n);

// Restaurants & events — cultural / location
MATCH (r1:Restaurant {id: 'rest_devon_kitchen'}), (c:Country {id: 'country_in'})
MERGE (r1)-[:SERVES_CUISINE]->(c);

MATCH (r2:Restaurant {id: 'rest_tiffin_express_chi'}), (c:Country {id: 'country_in'})
MERGE (r2)-[:SERVES_CUISINE]->(c);

MATCH (e1:Event {id: 'event_hackwithchicago_3'}), (c:Country {id: 'country_in'})
MERGE (e1)-[:RELEVANT_TO]->(c);

MATCH (e1:Event {id: 'event_hackwithchicago_3'}), (city:City {id: 'city_chicago'})
MERGE (e1)-[:OCCURS_IN]->(city);

MATCH (e2:Event {id: 'event_iit_intl_orientation'}), (c:Country {id: 'country_in'})
MERGE (e2)-[:RELEVANT_TO]->(c);

MATCH (e2:Event {id: 'event_iit_intl_orientation'}), (city:City {id: 'city_chicago'})
MERGE (e2)-[:OCCURS_IN]->(city);

// Resources — needs
MATCH (res1:Resource {id: 'resource_chase_south_loop'}), (n:Need {id: 'need_banking'})
MERGE (res1)-[:HELPS_WITH]->(n);

MATCH (res2:Resource {id: 'resource_iit_oia'}), (n:Need {id: 'need_orientation'})
MERGE (res2)-[:HELPS_WITH]->(n);

MATCH (res2:Resource {id: 'resource_iit_oia'}), (n:Need {id: 'need_housing'})
MERGE (res2)-[:HELPS_WITH]->(n);

MATCH (res3:Resource {id: 'resource_luma_chicago'}), (n:Need {id: 'need_community'})
MERGE (res3)-[:HELPS_WITH]->(n);

MATCH (res3:Resource {id: 'resource_luma_chicago'}), (n:Need {id: 'need_orientation'})
MERGE (res3)-[:HELPS_WITH]->(n);

// Task dependency chain: identity -> banking -> housing
MATCH (t1:Task {id: 'task_identity_docs'}), (t2:Task {id: 'task_open_bank_account'})
MERGE (t1)-[:PRECEDES]->(t2);

MATCH (t2:Task {id: 'task_open_bank_account'}), (t3:Task {id: 'task_housing_commitment'})
MERGE (t2)-[:PRECEDES]->(t3);
