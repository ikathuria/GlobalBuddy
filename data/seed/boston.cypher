// Boston seed pack — Northeastern, BU, MIT, Harvard
// Data is representative/demo only. Verify independently before production use.

CREATE CONSTRAINT community_group_id IF NOT EXISTS FOR (n:CommunityGroup) REQUIRE n.id IS UNIQUE;

MERGE (city_bos:City {id: 'city_boston'}) SET city_bos.name = 'Boston';

MERGE (nb_fen:Neighborhood {id: 'nb_fenway'}) SET nb_fen.name = 'Fenway-Kenmore';
MERGE (nb_back:Neighborhood {id: 'nb_back_bay'}) SET nb_back.name = 'Back Bay';
MERGE (nb_cam:Neighborhood {id: 'nb_cambridge'}) SET nb_cam.name = 'Cambridge';
MERGE (nb_all:Neighborhood {id: 'nb_allston'}) SET nb_all.name = 'Allston-Brighton';

MATCH (nb_fen:Neighborhood {id: 'nb_fenway'}), (bos:City {id: 'city_boston'})
MERGE (nb_fen)-[:IN_CITY]->(bos);
MATCH (nb_back:Neighborhood {id: 'nb_back_bay'}), (bos2:City {id: 'city_boston'})
MERGE (nb_back)-[:IN_CITY]->(bos2);
MATCH (nb_cam:Neighborhood {id: 'nb_cambridge'}), (bos3:City {id: 'city_boston'})
MERGE (nb_cam)-[:IN_CITY]->(bos3);
MATCH (nb_all:Neighborhood {id: 'nb_allston'}), (bos4:City {id: 'city_boston'})
MERGE (nb_all)-[:IN_CITY]->(bos4);

MERGE (u_neu:University {id: 'univ_northeastern'}) SET u_neu.name = 'Northeastern University';
MERGE (u_bu:University {id: 'univ_bu'}) SET u_bu.name = 'Boston University';
MERGE (u_mit:University {id: 'univ_mit'}) SET u_mit.name = 'Massachusetts Institute of Technology';
MERGE (u_harv:University {id: 'univ_harvard'}) SET u_harv.name = 'Harvard University';

MATCH (u_neu:University {id: 'univ_northeastern'}), (nb_fen2:Neighborhood {id: 'nb_fenway'})
MERGE (u_neu)-[:LOCATED_IN]->(nb_fen2);
MATCH (u_bu2:University {id: 'univ_bu'}), (nb_fen3:Neighborhood {id: 'nb_fenway'})
MERGE (u_bu2)-[:LOCATED_IN]->(nb_fen3);
MATCH (u_mit2:University {id: 'univ_mit'}), (nb_cam2:Neighborhood {id: 'nb_cambridge'})
MERGE (u_mit2)-[:LOCATED_IN]->(nb_cam2);
MATCH (u_harv2:University {id: 'univ_harvard'}), (nb_cam3:Neighborhood {id: 'nb_cambridge'})
MERGE (u_harv2)-[:LOCATED_IN]->(nb_cam3);

// Mentors
MERGE (bm1:Mentor {id: 'mentor_priya_boston'})
SET bm1.name = 'Priya Venkataraman',
    bm1.trust_score = 0.91,
    bm1.response_rate = 0.86,
    bm1.languages = ['English', 'Tamil', 'Hindi'],
    bm1.country_code = 'IN',
    bm1.email = 'priya.venkataraman.boston@globaldost.demo',
    bm1.linkedin_url = '',
    bm1.connect_hint = 'Mention Globalदोस्त and Northeastern ISS in your message.',
    bm1.city_name = 'Boston';

MERGE (bm2:Mentor {id: 'mentor_ali_boston'})
SET bm2.name = 'Ali Hassan',
    bm2.trust_score = 0.88,
    bm2.response_rate = 0.80,
    bm2.languages = ['English', 'Urdu', 'Arabic'],
    bm2.country_code = 'PK',
    bm2.email = 'ali.hassan.boston@globaldost.demo',
    bm2.linkedin_url = '',
    bm2.connect_hint = 'Available for coffee near BU campus — say you matched on Globalदोस्त.',
    bm2.city_name = 'Boston';

MERGE (bm3:Mentor {id: 'mentor_chen_boston'})
SET bm3.name = 'Wei Chen',
    bm3.trust_score = 0.85,
    bm3.response_rate = 0.78,
    bm3.languages = ['English', 'Mandarin'],
    bm3.country_code = 'CN',
    bm3.email = 'wei.chen.boston@globaldost.demo',
    bm3.linkedin_url = '',
    bm3.connect_hint = 'MIT ISSO can provide an intro; mention Globalदोस्त.',
    bm3.city_name = 'Boston';

// Peers
MERGE (bp1:Peer {id: 'peer_boston_1'})
SET bp1.name = 'Sofia Reyes',
    bp1.university = 'Northeastern University',
    bp1.neighborhood = 'Fenway-Kenmore',
    bp1.email = 's.reyes@northeastern.edu',
    bp1.connect_hint = 'Matched on Globalदोस्त; happy to share Northeastern co-op tips.';

// Restaurants
MERGE (br1:Restaurant {id: 'rest_punjabi_dhaba_boston'})
SET br1.name = 'Punjab Palace (Mass Ave)', br1.price_level = 1, br1.distance_km = 1.8;
MERGE (br2:Restaurant {id: 'rest_india_quality_boston'})
SET br2.name = 'India Quality Restaurant', br2.price_level = 2, br2.distance_km = 2.2;
MERGE (br3:Restaurant {id: 'rest_halal_cart_boston'})
SET br3.name = 'Moody Street Halal Market', br3.price_level = 1, br3.distance_km = 3.5;

// Events
MERGE (be1:Event {id: 'event_boston_neu_orientation'})
SET be1.name = 'Northeastern International Student Orientation',
    be1.start_time = '2026-08-25T09:00:00Z',
    be1.location = 'Northeastern Curry Student Center, Boston',
    be1.category = 'orientation',
    be1.notes = 'Official orientation week. Check Northeastern OneStop for confirmed date.',
    be1.maps_query = 'Northeastern Curry Student Center Boston',
    be1.maps_link = 'https://www.google.com/maps/search/?api=1&query=Northeastern+Curry+Student+Center+Boston';

MERGE (be2:Event {id: 'event_boston_diwali_demo'})
SET be2.name = 'Diwali celebrations (Boston-area universities)',
    be2.start_time = 'TBD_FALL_ANNUAL',
    be2.location = 'Multiple venues — Northeastern, BU, MIT, Harvard',
    be2.category = 'religious_cultural',
    be2.notes = 'Each university South Asian Students Association hosts their own event; check SA club calendars in October.',
    be2.maps_query = 'South Asian Students Association Boston',
    be2.maps_link = 'https://www.google.com/maps/search/?api=1&query=Northeastern+Boston';

MERGE (be3:Event {id: 'event_boston_hackathon_demo'})
SET be3.name = 'HackBeanpot (annual MIT + Boston universities)',
    be3.start_time = 'TBD_FEBRUARY_ANNUAL',
    be3.location = 'MIT or Northeastern campus — see hackbeanpot.com',
    be3.category = 'hackathon',
    be3.notes = 'Popular multi-school hackathon. Check hackbeanpot.com for registration and venue.',
    be3.maps_query = 'HackBeanpot MIT Cambridge',
    be3.maps_link = 'https://www.google.com/maps/search/?api=1&query=MIT+Cambridge+MA';

// Resources
MERGE (bres1:Resource {id: 'resource_tdbank_fenway'})
SET bres1.name = 'TD Bank - Fenway area', bres1.resource_type = 'banking';
MERGE (bres2:Resource {id: 'resource_neu_isso'})
SET bres2.name = 'Northeastern International Student and Scholar Services', bres2.resource_type = 'support';
MERGE (bres3:Resource {id: 'resource_bu_isso'})
SET bres3.name = 'Boston University International Students & Scholars Office', bres3.resource_type = 'support';

// Places of Worship
MERGE (bpow1:PlaceOfWorship {id: 'pow_boston_hindu_temple'})
SET bpow1.name = 'Hindu Temple of New England (Sharon, MA)',
    bpow1.subtype = 'hindu_temple',
    bpow1.address = '158 N Main St, Sharon, MA 02067',
    bpow1.neighborhood = 'South suburbs (30 min from Boston)',
    bpow1.latitude = 42.122,
    bpow1.longitude = -71.178,
    bpow1.maps_query = 'Hindu Temple of New England Sharon MA',
    bpow1.maps_link = 'https://www.google.com/maps/search/?api=1&query=Hindu+Temple+New+England+Sharon+MA',
    bpow1.audience_tags = ['hindu', 'south_asian', 'indian'],
    bpow1.city_name = 'Boston';

MERGE (bpow2:PlaceOfWorship {id: 'pow_boston_masjid_demo'})
SET bpow2.name = 'Islamic Society of Boston (Cambridge)',
    bpow2.subtype = 'mosque',
    bpow2.address = '204 Prospect St, Cambridge, MA 02139',
    bpow2.neighborhood = 'Cambridge',
    bpow2.latitude = 42.365,
    bpow2.longitude = -71.099,
    bpow2.maps_query = 'Islamic Society of Boston Cambridge MA',
    bpow2.maps_link = 'https://www.google.com/maps/search/?api=1&query=Islamic+Society+Boston+Cambridge',
    bpow2.audience_tags = ['muslim', 'south_asian', 'international'],
    bpow2.city_name = 'Boston';

// Grocery stores
MERGE (bgs1:GroceryStore {id: 'grocery_india_market_cambridge'})
SET bgs1.name = 'India Market (Cambridge)',
    bgs1.address = '689 Cambridge St, Cambridge, MA',
    bgs1.neighborhood = 'Cambridge',
    bgs1.latitude = 42.366,
    bgs1.longitude = -71.129,
    bgs1.maps_query = 'India Market Cambridge MA',
    bgs1.maps_link = 'https://www.google.com/maps/search/?api=1&query=India+Market+Cambridge+MA',
    bgs1.diet_tags = ['vegetarian', 'south_asian', 'halal'],
    bgs1.city_name = 'Boston';

MERGE (bgs2:GroceryStore {id: 'grocery_whole_foods_fenway'})
SET bgs2.name = 'Whole Foods - Fenway',
    bgs2.address = '15 Westland Ave, Boston, MA 02115',
    bgs2.neighborhood = 'Fenway-Kenmore',
    bgs2.latitude = 42.340,
    bgs2.longitude = -71.096,
    bgs2.maps_query = 'Whole Foods Fenway Boston MA',
    bgs2.maps_link = 'https://www.google.com/maps/search/?api=1&query=Whole+Foods+Fenway+Boston',
    bgs2.diet_tags = ['vegetarian', 'organic', 'halal_section_typical'],
    bgs2.city_name = 'Boston';

// Housing areas
MERGE (bha1:HousingArea {id: 'housing_allston_boston'})
SET bha1.name = 'Allston-Brighton (student area)',
    bha1.address = 'Allston, Boston, MA',
    bha1.neighborhood = 'Allston-Brighton',
    bha1.latitude = 42.353,
    bha1.longitude = -71.133,
    bha1.maps_query = 'Allston Brighton apartments Boston MA',
    bha1.maps_link = 'https://www.google.com/maps/search/?api=1&query=Allston+Brighton+Boston+apartments',
    bha1.audience_tags = ['budget_friendly', 'student_friendly', 'near_bu'],
    bha1.city_name = 'Boston';

MERGE (bha2:HousingArea {id: 'housing_cambridgeport'})
SET bha2.name = 'Cambridgeport (near MIT)',
    bha2.address = 'Cambridgeport, Cambridge, MA',
    bha2.neighborhood = 'Cambridge',
    bha2.latitude = 42.359,
    bha2.longitude = -71.115,
    bha2.maps_query = 'Cambridgeport Cambridge MA apartments',
    bha2.maps_link = 'https://www.google.com/maps/search/?api=1&query=Cambridgeport+Cambridge+MA',
    bha2.audience_tags = ['near_mit', 'student_friendly'],
    bha2.city_name = 'Boston';

// Exploration spots
MERGE (bex1:ExplorationSpot {id: 'explore_boston_common'})
SET bex1.name = 'Boston Common and Public Garden',
    bex1.subtype = 'park',
    bex1.address = '139 Tremont St, Boston, MA',
    bex1.neighborhood = 'Downtown',
    bex1.latitude = 42.355,
    bex1.longitude = -71.065,
    bex1.maps_query = 'Boston Common Boston MA',
    bex1.maps_link = 'https://www.google.com/maps/search/?api=1&query=Boston+Common',
    bex1.audience_tags = ['downtown', 'weekend', 'free_outdoor'],
    bex1.city_name = 'Boston';

MERGE (bex2:ExplorationSpot {id: 'explore_mfa_boston'})
SET bex2.name = 'Museum of Fine Arts Boston',
    bex2.subtype = 'museum',
    bex2.address = '465 Huntington Ave, Boston, MA',
    bex2.neighborhood = 'Fenway-Kenmore',
    bex2.latitude = 42.339,
    bex2.longitude = -71.094,
    bex2.maps_query = 'Museum of Fine Arts Boston',
    bex2.maps_link = 'https://www.google.com/maps/search/?api=1&query=Museum+Fine+Arts+Boston',
    bex2.audience_tags = ['museum', 'weekend', 'student_discount'],
    bex2.city_name = 'Boston';

// Transit tips
MERGE (btt1:TransitTip {id: 'transit_mbta_green_line'})
SET btt1.name = 'MBTA Green Line (E branch) — Northeastern corridor',
    btt1.summary = 'Green Line E branch stops at Northeastern and Museum of Fine Arts. Free with CharlieCard loaded via MBTA app.',
    btt1.route_hint = 'Board at Copley or Prudential heading outbound; exit at Northeastern stop. Verify on mbta.com.',
    btt1.neighborhood = 'Fenway-Kenmore',
    btt1.maps_link = 'https://www.google.com/maps/search/?api=1&query=Northeastern+MBTA+Green+Line',
    btt1.city_name = 'Boston';

MERGE (btt2:TransitTip {id: 'transit_mbta_red_line'})
SET btt2.name = 'MBTA Red Line — MIT and Harvard corridor',
    btt2.summary = 'Red Line Kendall/MIT and Harvard Square stations. Main link between Cambridge universities.',
    btt2.route_hint = 'Southbound from Alewife toward Ashmont/Braintree. Exit Kendall/MIT for MIT, Harvard Sq for Harvard.',
    btt2.neighborhood = 'Cambridge',
    btt2.maps_link = 'https://www.google.com/maps/search/?api=1&query=Kendall+MIT+Red+Line+MBTA',
    btt2.city_name = 'Boston';

// Community groups
MERGE (bcg1:CommunityGroup {id: 'cg_boston_isa'})
SET bcg1.name = 'Indian Students Association — Boston universities coalition',
    bcg1.city_name = 'Boston',
    bcg1.platform = 'WhatsApp + Facebook',
    bcg1.join_hint = 'Search your university ISA on Facebook; WhatsApp groups shared at orientation.';

// Relationships
MATCH (bm1:Mentor {id: 'mentor_priya_boston'}), (u_neu2:University {id: 'univ_northeastern'})
MERGE (bm1)-[:AFFILIATED_WITH]->(u_neu2);
MATCH (bm2b:Mentor {id: 'mentor_ali_boston'}), (u_bu3:University {id: 'univ_bu'})
MERGE (bm2b)-[:AFFILIATED_WITH]->(u_bu3);
MATCH (bm3b:Mentor {id: 'mentor_chen_boston'}), (u_mit3:University {id: 'univ_mit'})
MERGE (bm3b)-[:AFFILIATED_WITH]->(u_mit3);
MATCH (bm1b:Mentor {id: 'mentor_priya_boston'}), (bos5:City {id: 'city_boston'})
MERGE (bm1b)-[:LIVES_IN]->(bos5);
MATCH (bm2c:Mentor {id: 'mentor_ali_boston'}), (bos6:City {id: 'city_boston'})
MERGE (bm2c)-[:LIVES_IN]->(bos6);
MATCH (bm3c:Mentor {id: 'mentor_chen_boston'}), (bos7:City {id: 'city_boston'})
MERGE (bm3c)-[:LIVES_IN]->(bos7);
MATCH (bha1b:HousingArea {id: 'housing_allston_boston'}), (u_bu4:University {id: 'univ_bu'})
MERGE (bha1b)-[:NEAR_UNIVERSITY]->(u_bu4);
MATCH (bha2b:HousingArea {id: 'housing_cambridgeport'}), (u_mit4:University {id: 'univ_mit'})
MERGE (bha2b)-[:NEAR_UNIVERSITY]->(u_mit4);
MATCH (bpow1b:PlaceOfWorship {id: 'pow_boston_hindu_temple'}), (bos8:City {id: 'city_boston'})
MERGE (bpow1b)-[:LOCATED_IN]->(bos8);
MATCH (bpow2b:PlaceOfWorship {id: 'pow_boston_masjid_demo'}), (nb_cam4:Neighborhood {id: 'nb_cambridge'})
MERGE (bpow2b)-[:LOCATED_IN]->(nb_cam4);
MATCH (bgs1b:GroceryStore {id: 'grocery_india_market_cambridge'}), (nb_cam5:Neighborhood {id: 'nb_cambridge'})
MERGE (bgs1b)-[:LOCATED_IN]->(nb_cam5);
MATCH (bgs2b:GroceryStore {id: 'grocery_whole_foods_fenway'}), (nb_fen4:Neighborhood {id: 'nb_fenway'})
MERGE (bgs2b)-[:LOCATED_IN]->(nb_fen4);
MATCH (bex1b:ExplorationSpot {id: 'explore_boston_common'}), (bos9:City {id: 'city_boston'})
MERGE (bex1b)-[:LOCATED_IN]->(bos9);
MATCH (bex2b:ExplorationSpot {id: 'explore_mfa_boston'}), (nb_fen5:Neighborhood {id: 'nb_fenway'})
MERGE (bex2b)-[:LOCATED_IN]->(nb_fen5);
MATCH (btt1b:TransitTip {id: 'transit_mbta_green_line'}), (bos10:City {id: 'city_boston'})
MERGE (btt1b)-[:SERVES]->(bos10);
MATCH (btt2b:TransitTip {id: 'transit_mbta_red_line'}), (bos11:City {id: 'city_boston'})
MERGE (btt2b)-[:SERVES]->(bos11);
