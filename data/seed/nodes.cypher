// Constraints (idempotent)
CREATE CONSTRAINT student_id IF NOT EXISTS FOR (n:Student) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT mentor_id IF NOT EXISTS FOR (n:Mentor) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT peer_id IF NOT EXISTS FOR (n:Peer) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT university_id IF NOT EXISTS FOR (n:University) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT country_id IF NOT EXISTS FOR (n:Country) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT city_id IF NOT EXISTS FOR (n:City) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT need_id IF NOT EXISTS FOR (n:Need) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT task_id IF NOT EXISTS FOR (n:Task) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT restaurant_id IF NOT EXISTS FOR (n:Restaurant) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT event_id IF NOT EXISTS FOR (n:Event) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT resource_id IF NOT EXISTS FOR (n:Resource) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT neighborhood_id IF NOT EXISTS FOR (n:Neighborhood) REQUIRE n.id IS UNIQUE;

// Geography and institutions — MERGE on `id` only, then SET (so re-seed updates Austin→Chicago safely)
MERGE (c_in:Country {id: 'country_in'}) SET c_in.name = 'India', c_in.code = 'IN';
MERGE (c_us:Country {id: 'country_us'}) SET c_us.name = 'United States', c_us.code = 'US';
MERGE (city:City {id: 'city_chicago'}) SET city.name = 'Chicago';
MERGE (u:University {id: 'univ_iit'}) SET u.name = 'Illinois Institute of Technology';
MERGE (nb:Neighborhood {id: 'nb_south_loop'}) SET nb.name = 'South Loop';

// Needs
MERGE (n_bank:Need {id: 'need_banking'}) SET n_bank.name = 'banking', n_bank.label = 'Banking setup';
MERGE (n_house:Need {id: 'need_housing'}) SET n_house.name = 'housing', n_house.label = 'Housing search';
MERGE (n_orient:Need {id: 'need_orientation'}) SET n_orient.name = 'orientation', n_orient.label = 'University orientation';
MERGE (n_comm:Need {id: 'need_community'}) SET n_comm.name = 'community', n_comm.label = 'Community & events';

// Mentors (demo-critical names)
MERGE (m1:Mentor {id: 'mentor_ananya_sharma'})
SET m1.name = 'Ananya Sharma',
    m1.trust_score = 0.92,
    m1.response_rate = 0.88,
    m1.languages = ['English', 'Hindi', 'Kannada'],
    m1.country_code = 'IN',
    m1.email = 'ananya.sharma.mentor@globalbuddy.demo',
    m1.linkedin_url = 'https://www.linkedin.com/in/example-ananya-sharma',
    m1.connect_hint = 'Mention GlobalBuddy + IIT OIA ambassador intro in your subject line.';
MERGE (m2:Mentor {id: 'mentor_rajesh_kumar'})
SET m2.name = 'Rajesh Kumar',
    m2.trust_score = 0.87,
    m2.response_rate = 0.82,
    m2.languages = ['English', 'Hindi', 'Tamil'],
    m2.country_code = 'IN',
    m2.email = 'rajesh.kumar.mentor@globalbuddy.demo',
    m2.linkedin_url = '',
    m2.connect_hint = 'Available for 20-min Zoom — book via IIT international student Slack (demo).';

// Peer — same id as older seeds; must not MERGE on full property set or duplicate-id errors occur
MERGE (peer:Peer {id: 'peer_alex_kim'})
SET peer.name = 'Alex Kim',
    peer.university = 'Illinois Institute of Technology',
    peer.neighborhood = 'South Loop',
    peer.email = 'akim3@hawk.iit.edu',
    peer.connect_hint = 'Say you matched on GlobalBuddy; happy to grab coffee near campus.';

// Restaurants — Chicago / Devon Ave corridor (South Asian food)
MERGE (r1:Restaurant {id: 'rest_devon_kitchen'})
SET r1.name = 'Devon Kitchen', r1.price_level = 2, r1.distance_km = 2.4;
MERGE (r2:Restaurant {id: 'rest_tiffin_express_chi'})
SET r2.name = 'Tiffin Express (Devon Ave)', r2.price_level = 1, r2.distance_km = 3.1;

// Events — HackWithChicago + IIT
MERGE (e1:Event {id: 'event_hackwithchicago_3'})
SET e1.name = 'HackWithChicago 3.0',
    e1.start_time = '2026-04-12T09:00:00Z',
    e1.location = 'Chicago Loop · venue on Luma',
    e1.category = 'hackathon';
MERGE (e2:Event {id: 'event_iit_intl_orientation'})
SET e2.name = 'IIT International Student Orientation',
    e2.start_time = '2026-08-18T10:00:00Z',
    e2.location = 'McCormick Tribune Campus Center, IIT',
    e2.category = 'orientation';

// Resources — banking, IIT OIA, Luma for events
MERGE (res1:Resource {id: 'resource_chase_south_loop'})
SET res1.name = 'Chase Bank - South Loop / Grant Park', res1.resource_type = 'banking';
MERGE (res2:Resource {id: 'resource_iit_oia'})
SET res2.name = 'IIT Office of International Affairs', res2.resource_type = 'support';
MERGE (res3:Resource {id: 'resource_luma_chicago'})
SET res3.name = 'Luma (lu.ma) — Chicago tech & student events', res3.resource_type = 'community';

// Tasks — dependency chain uses PRECEDES in relationships file
MERGE (t1:Task {id: 'task_identity_docs'})
SET t1.name = 'Complete identity and immigration documentation checklist',
    t1.priority = 1,
    t1.estimated_day_window = 'Day 1-3';
MERGE (t2:Task {id: 'task_open_bank_account'})
SET t2.name = 'Open a US bank account with required documents',
    t2.priority = 2,
    t2.estimated_day_window = 'Day 3-7';
MERGE (t3:Task {id: 'task_housing_commitment'})
SET t3.name = 'Secure housing commitment and understand lease terms',
    t3.priority = 3,
    t3.estimated_day_window = 'Day 7-14';
