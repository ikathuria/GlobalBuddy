// NYC seed pack — NYU, Columbia, CUNY
// Data is representative/demo only. Verify independently before production use.

CREATE CONSTRAINT community_group_id IF NOT EXISTS FOR (n:CommunityGroup) REQUIRE n.id IS UNIQUE;

MERGE (city_nyc:City {id: 'city_new_york'}) SET city_nyc.name = 'New York';

MERGE (nb_greenwich:Neighborhood {id: 'nb_greenwich_village'}) SET nb_greenwich.name = 'Greenwich Village';
MERGE (nb_morningside:Neighborhood {id: 'nb_morningside'}) SET nb_morningside.name = 'Morningside Heights';
MERGE (nb_flushing:Neighborhood {id: 'nb_flushing'}) SET nb_flushing.name = 'Flushing';
MERGE (nb_jackson:Neighborhood {id: 'nb_jackson_heights'}) SET nb_jackson.name = 'Jackson Heights';
MERGE (nb_astoria:Neighborhood {id: 'nb_astoria'}) SET nb_astoria.name = 'Astoria';

MATCH (nb_greenwich2:Neighborhood {id: 'nb_greenwich_village'}), (nyc:City {id: 'city_new_york'})
MERGE (nb_greenwich2)-[:IN_CITY]->(nyc);
MATCH (nb_morning2:Neighborhood {id: 'nb_morningside'}), (nyc2:City {id: 'city_new_york'})
MERGE (nb_morning2)-[:IN_CITY]->(nyc2);
MATCH (nb_flush2:Neighborhood {id: 'nb_flushing'}), (nyc3:City {id: 'city_new_york'})
MERGE (nb_flush2)-[:IN_CITY]->(nyc3);
MATCH (nb_jack2:Neighborhood {id: 'nb_jackson_heights'}), (nyc4:City {id: 'city_new_york'})
MERGE (nb_jack2)-[:IN_CITY]->(nyc4);
MATCH (nb_ast2:Neighborhood {id: 'nb_astoria'}), (nyc5:City {id: 'city_new_york'})
MERGE (nb_ast2)-[:IN_CITY]->(nyc5);

MERGE (u_nyu:University {id: 'univ_nyu'}) SET u_nyu.name = 'New York University';
MERGE (u_columbia:University {id: 'univ_columbia'}) SET u_columbia.name = 'Columbia University';
MERGE (u_cuny:University {id: 'univ_cuny'}) SET u_cuny.name = 'City University of New York (CUNY)';

MATCH (u_nyu2:University {id: 'univ_nyu'}), (nb_gv:Neighborhood {id: 'nb_greenwich_village'})
MERGE (u_nyu2)-[:LOCATED_IN]->(nb_gv);
MATCH (u_col2:University {id: 'univ_columbia'}), (nb_ms:Neighborhood {id: 'nb_morningside'})
MERGE (u_col2)-[:LOCATED_IN]->(nb_ms);
MATCH (u_cuny2:University {id: 'univ_cuny'}), (nyc6:City {id: 'city_new_york'})
MERGE (u_cuny2)-[:LOCATED_IN]->(nyc6);

// Mentors
MERGE (nm1:Mentor {id: 'mentor_vikram_nyc'})
SET nm1.name = 'Vikram Nair',
    nm1.trust_score = 0.93,
    nm1.response_rate = 0.89,
    nm1.languages = ['English', 'Malayalam', 'Hindi'],
    nm1.country_code = 'IN',
    nm1.email = 'vikram.nair.nyc@globaldost.demo',
    nm1.linkedin_url = '',
    nm1.connect_hint = 'Mention Globalदोस्त and NYU Wasserman in your first message.',
    nm1.city_name = 'New York';

MERGE (nm2:Mentor {id: 'mentor_fatima_nyc'})
SET nm2.name = 'Fatima Al-Rashid',
    nm2.trust_score = 0.90,
    nm2.response_rate = 0.84,
    nm2.languages = ['English', 'Arabic', 'Urdu'],
    nm2.country_code = 'SA',
    nm2.email = 'fatima.alrashid.nyc@globaldost.demo',
    nm2.linkedin_url = '',
    nm2.connect_hint = 'Columbia ISSO can connect you; mention Globalदोस्त.',
    nm2.city_name = 'New York';

MERGE (nm3:Mentor {id: 'mentor_jose_nyc'})
SET nm3.name = 'Jose Martinez',
    nm3.trust_score = 0.86,
    nm3.response_rate = 0.81,
    nm3.languages = ['English', 'Spanish'],
    nm3.country_code = 'MX',
    nm3.email = 'jose.martinez.nyc@globaldost.demo',
    nm3.linkedin_url = '',
    nm3.connect_hint = 'Happy to meet for coffee in Jackson Heights — say you matched on Globalदोस्त.',
    nm3.city_name = 'New York';

MERGE (nm4:Mentor {id: 'mentor_ankit_nyc'})
SET nm4.name = 'Ankit Gupta',
    nm4.trust_score = 0.87,
    nm4.response_rate = 0.82,
    nm4.languages = ['English', 'Hindi', 'Bengali'],
    nm4.country_code = 'IN',
    nm4.email = 'ankit.gupta.nyc@globaldost.demo',
    nm4.linkedin_url = '',
    nm4.connect_hint = 'CUNY DSI alumnus; mention Globalदोस्त for intro.',
    nm4.city_name = 'New York';

MERGE (nm5:Mentor {id: 'mentor_liu_nyc'})
SET nm5.name = 'Mei Liu',
    nm5.trust_score = 0.84,
    nm5.response_rate = 0.79,
    nm5.languages = ['English', 'Mandarin', 'Cantonese'],
    nm5.country_code = 'CN',
    nm5.email = 'mei.liu.nyc@globaldost.demo',
    nm5.linkedin_url = '',
    nm5.connect_hint = 'Flushing community leader; reach out via Globalदोस्त intro.',
    nm5.city_name = 'New York';

// Peers
MERGE (np1:Peer {id: 'peer_nyc_1'})
SET np1.name = 'Arjun Bose',
    np1.university = 'New York University',
    np1.neighborhood = 'Greenwich Village',
    np1.email = 'abose@nyu.edu',
    np1.connect_hint = 'NYU GSU Desi club — say you matched on Globalदोस्त.';

// Restaurants
MERGE (nr1:Restaurant {id: 'rest_jackson_heights_nyc'})
SET nr1.name = 'Jackson Diner (Indian, Jackson Heights)', nr1.price_level = 1, nr1.distance_km = 8.0;
MERGE (nr2:Restaurant {id: 'rest_curry_hill_nyc'})
SET nr2.name = 'Curry Hill (Lexington Ave — Indian restaurant row)', nr2.price_level = 2, nr2.distance_km = 4.5;
MERGE (nr3:Restaurant {id: 'rest_halal_guys_nyc'})
SET nr3.name = 'The Halal Guys (original 53rd St cart)', nr3.price_level = 1, nr3.distance_km = 5.2;

// Events
MERGE (ne1:Event {id: 'event_nyu_orientation_nyc'})
SET ne1.name = 'NYU International Student Orientation',
    ne1.start_time = '2026-08-22T09:00:00Z',
    ne1.location = 'NYU Kimmel Center, Washington Square, NYC',
    ne1.category = 'orientation',
    ne1.notes = 'Check NYU Global Welcome for confirmed schedule and mandatory SEVIS check-in dates.',
    ne1.maps_query = 'NYU Kimmel Center Washington Square Park NYC',
    ne1.maps_link = 'https://www.google.com/maps/search/?api=1&query=NYU+Kimmel+Center+NYC';

MERGE (ne2:Event {id: 'event_nyc_diwali_demo'})
SET ne2.name = 'Diwali on Times Square (annual)',
    ne2.start_time = 'TBD_FALL_ANNUAL',
    ne2.location = 'Times Square, NYC',
    ne2.category = 'religious_cultural',
    ne2.notes = 'Free public Diwali celebration; confirm exact date with Times Square Alliance each year.',
    ne2.maps_query = 'Diwali on Times Square NYC',
    ne2.maps_link = 'https://www.google.com/maps/search/?api=1&query=Times+Square+NYC';

MERGE (ne3:Event {id: 'event_nyc_hackathon_demo'})
SET ne3.name = 'MHacks / Major League Hacking NYC events',
    ne3.start_time = 'TBD_VARIES',
    ne3.location = 'Varies — check MLH.io for NYC-area hackathons',
    ne3.category = 'hackathon',
    ne3.notes = 'MLH runs multiple hackathons in the NYC metro. Check mlh.io for confirmed events.',
    ne3.maps_query = 'hackathon NYC',
    ne3.maps_link = 'https://www.google.com/maps/search/?api=1&query=hackathon+New+York+City';

// Resources
MERGE (nres1:Resource {id: 'resource_chase_nyc_midtown'})
SET nres1.name = 'Chase Bank - Midtown Manhattan', nres1.resource_type = 'banking';
MERGE (nres2:Resource {id: 'resource_nyu_ois'})
SET nres2.name = 'NYU Office of Global Services', nres2.resource_type = 'support';
MERGE (nres3:Resource {id: 'resource_columbia_isso'})
SET nres3.name = 'Columbia University International Students and Scholars Office', nres3.resource_type = 'support';

// Places of Worship
MERGE (npow1:PlaceOfWorship {id: 'pow_ganesh_temple_flushing'})
SET npow1.name = 'Ganesh Temple (Flushing, Queens)',
    npow1.subtype = 'hindu_temple',
    npow1.address = '45-57 Bowne St, Flushing, NY 11355',
    npow1.neighborhood = 'Flushing',
    npow1.latitude = 40.769,
    npow1.longitude = -73.824,
    npow1.maps_query = 'Ganesh Temple Flushing Queens NY',
    npow1.maps_link = 'https://www.google.com/maps/search/?api=1&query=Ganesh+Temple+Flushing+Queens',
    npow1.audience_tags = ['hindu', 'south_asian', 'indian'],
    npow1.city_name = 'New York';

MERGE (npow2:PlaceOfWorship {id: 'pow_nyc_isb_masjid'})
SET npow2.name = 'Islamic Cultural Center of New York',
    npow2.subtype = 'mosque',
    npow2.address = '1711 3rd Ave, New York, NY 10029',
    npow2.neighborhood = 'Upper East Side',
    npow2.latitude = 40.785,
    npow2.longitude = -73.951,
    npow2.maps_query = 'Islamic Cultural Center New York 3rd Ave',
    npow2.maps_link = 'https://www.google.com/maps/search/?api=1&query=Islamic+Cultural+Center+New+York',
    npow2.audience_tags = ['muslim', 'south_asian', 'international'],
    npow2.city_name = 'New York';

MERGE (npow3:PlaceOfWorship {id: 'pow_sikh_gurdwara_nyc'})
SET npow3.name = 'Sikh Cultural Society (Richmond Hill, Queens)',
    npow3.subtype = 'gurdwara',
    npow3.address = '95-30 118th St, Richmond Hill, NY 11419',
    npow3.neighborhood = 'Richmond Hill',
    npow3.latitude = 40.697,
    npow3.longitude = -73.828,
    npow3.maps_query = 'Sikh Cultural Society Richmond Hill Queens NY',
    npow3.maps_link = 'https://www.google.com/maps/search/?api=1&query=Sikh+Cultural+Society+Richmond+Hill+Queens',
    npow3.audience_tags = ['sikh', 'punjabi', 'south_asian'],
    npow3.city_name = 'New York';

// Grocery stores
MERGE (ngs1:GroceryStore {id: 'grocery_patel_brothers_nyc'})
SET ngs1.name = 'Patel Brothers (Jackson Heights)',
    ngs1.address = '37-27 74th St, Jackson Heights, NY 11372',
    ngs1.neighborhood = 'Jackson Heights',
    ngs1.latitude = 40.746,
    ngs1.longitude = -73.893,
    ngs1.maps_query = 'Patel Brothers 74th St Jackson Heights NYC',
    ngs1.maps_link = 'https://www.google.com/maps/search/?api=1&query=Patel+Brothers+Jackson+Heights+NYC',
    ngs1.diet_tags = ['vegetarian', 'south_asian', 'halal'],
    ngs1.city_name = 'New York';

MERGE (ngs2:GroceryStore {id: 'grocery_h_mart_nyc'})
SET ngs2.name = 'H Mart Manhattan (Asian grocery)',
    ngs2.address = '39 Third Ave, New York, NY 10003',
    ngs2.neighborhood = 'East Village',
    ngs2.latitude = 40.729,
    ngs2.longitude = -73.989,
    ngs2.maps_query = 'H Mart Third Ave Manhattan NYC',
    ngs2.maps_link = 'https://www.google.com/maps/search/?api=1&query=H+Mart+Third+Ave+Manhattan',
    ngs2.diet_tags = ['asian', 'vegetarian', 'halal_section_typical'],
    ngs2.city_name = 'New York';

// Housing areas
MERGE (nha1:HousingArea {id: 'housing_astoria_nyc'})
SET nha1.name = 'Astoria, Queens (affordable)',
    nha1.address = 'Astoria, Queens, NY',
    nha1.neighborhood = 'Astoria',
    nha1.latitude = 40.772,
    nha1.longitude = -73.930,
    nha1.maps_query = 'Astoria Queens apartments NYC',
    nha1.maps_link = 'https://www.google.com/maps/search/?api=1&query=Astoria+Queens+apartments',
    nha1.audience_tags = ['budget_friendly', 'student_friendly', 'n_q_subway'],
    nha1.city_name = 'New York';

MERGE (nha2:HousingArea {id: 'housing_morningside_nyc'})
SET nha2.name = 'Morningside Heights (near Columbia)',
    nha2.address = 'Morningside Heights, Manhattan, NY',
    nha2.neighborhood = 'Morningside Heights',
    nha2.latitude = 40.810,
    nha2.longitude = -73.960,
    nha2.maps_query = 'Morningside Heights Manhattan apartments',
    nha2.maps_link = 'https://www.google.com/maps/search/?api=1&query=Morningside+Heights+Manhattan+apartments',
    nha2.audience_tags = ['near_columbia', 'student_friendly'],
    nha2.city_name = 'New York';

MERGE (nha3:HousingArea {id: 'housing_jackson_heights_nyc'})
SET nha3.name = 'Jackson Heights, Queens (diverse, South Asian hub)',
    nha3.address = 'Jackson Heights, Queens, NY',
    nha3.neighborhood = 'Jackson Heights',
    nha3.latitude = 40.748,
    nha3.longitude = -73.891,
    nha3.maps_query = 'Jackson Heights Queens apartments NYC',
    nha3.maps_link = 'https://www.google.com/maps/search/?api=1&query=Jackson+Heights+Queens+apartments',
    nha3.audience_tags = ['budget_friendly', 'south_asian', '7_train_subway'],
    nha3.city_name = 'New York';

// Exploration spots
MERGE (nex1:ExplorationSpot {id: 'explore_central_park_nyc'})
SET nex1.name = 'Central Park',
    nex1.subtype = 'park',
    nex1.address = 'Central Park, New York, NY',
    nex1.neighborhood = 'Upper West Side',
    nex1.latitude = 40.785,
    nex1.longitude = -73.968,
    nex1.maps_query = 'Central Park New York City',
    nex1.maps_link = 'https://www.google.com/maps/search/?api=1&query=Central+Park+NYC',
    nex1.audience_tags = ['weekend', 'free_outdoor', 'iconic'],
    nex1.city_name = 'New York';

MERGE (nex2:ExplorationSpot {id: 'explore_the_met_nyc'})
SET nex2.name = 'The Metropolitan Museum of Art',
    nex2.subtype = 'museum',
    nex2.address = '1000 5th Ave, New York, NY 10028',
    nex2.neighborhood = 'Upper East Side',
    nex2.latitude = 40.779,
    nex2.longitude = -73.963,
    nex2.maps_query = 'Metropolitan Museum of Art New York',
    nex2.maps_link = 'https://www.google.com/maps/search/?api=1&query=Metropolitan+Museum+of+Art+NYC',
    nex2.audience_tags = ['museum', 'weekend', 'student_discount'],
    nex2.city_name = 'New York';

// Transit tips
MERGE (ntt1:TransitTip {id: 'transit_mta_7_train'})
SET ntt1.name = 'MTA 7 Train — International Express to Jackson Heights and Flushing',
    ntt1.summary = 'The 7 train connects Midtown Manhattan to Jackson Heights (South Asian), Flushing (Chinese, Korean). Essential for cultural groceries and worship.',
    ntt1.route_hint = 'Board at Times Square-42nd St; Jackson Heights-Roosevelt Ave (82nd stop); Main St-Flushing terminal. Verify on new.mta.info.',
    ntt1.neighborhood = 'Citywide',
    ntt1.maps_link = 'https://www.google.com/maps/search/?api=1&query=Jackson+Heights+Roosevelt+Ave+7+train+NYC',
    ntt1.city_name = 'New York';

MERGE (ntt2:TransitTip {id: 'transit_mta_a_train'})
SET ntt2.name = 'MTA A/C/E Lines — Midtown to downtown and Brooklyn',
    ntt2.summary = 'A train is the fastest downtown route. C and E serve West Side. Student MetroCard monthly unlimited available at reduced fare — check MTA Fair Fares.',
    ntt2.route_hint = 'Board at Penn Station (34th St) or Times Square. Check new.mta.info for real-time service alerts.',
    ntt2.neighborhood = 'Citywide',
    ntt2.maps_link = 'https://www.google.com/maps/search/?api=1&query=Penn+Station+MTA+NYC',
    ntt2.city_name = 'New York';

// Community groups
MERGE (ncg1:CommunityGroup {id: 'cg_nyc_isa'})
SET ncg1.name = 'Indian Students Association — NYC metro coalition',
    ncg1.city_name = 'New York',
    ncg1.platform = 'WhatsApp + GroupMe',
    ncg1.join_hint = 'Search ISA at NYU, Columbia, or CUNY on Facebook/Instagram; links shared at orientation.';

MERGE (ncg2:CommunityGroup {id: 'cg_nyc_south_asian_network'})
SET ncg2.name = 'NYC South Asian Graduate Student Network',
    ncg2.city_name = 'New York',
    ncg2.platform = 'LinkedIn + Slack',
    ncg2.join_hint = 'Search South Asian Graduate Network NYC on LinkedIn; open membership.';

// Relationships
MATCH (nm1b:Mentor {id: 'mentor_vikram_nyc'}), (u_nyu3:University {id: 'univ_nyu'})
MERGE (nm1b)-[:AFFILIATED_WITH]->(u_nyu3);
MATCH (nm2b:Mentor {id: 'mentor_fatima_nyc'}), (u_col3:University {id: 'univ_columbia'})
MERGE (nm2b)-[:AFFILIATED_WITH]->(u_col3);
MATCH (nm4b:Mentor {id: 'mentor_ankit_nyc'}), (u_cuny3:University {id: 'univ_cuny'})
MERGE (nm4b)-[:AFFILIATED_WITH]->(u_cuny3);
MATCH (nm1c:Mentor {id: 'mentor_vikram_nyc'}), (nyc7:City {id: 'city_new_york'})
MERGE (nm1c)-[:LIVES_IN]->(nyc7);
MATCH (nm2c:Mentor {id: 'mentor_fatima_nyc'}), (nyc8:City {id: 'city_new_york'})
MERGE (nm2c)-[:LIVES_IN]->(nyc8);
MATCH (nm3c:Mentor {id: 'mentor_jose_nyc'}), (nyc9:City {id: 'city_new_york'})
MERGE (nm3c)-[:LIVES_IN]->(nyc9);
MATCH (nm4c:Mentor {id: 'mentor_ankit_nyc'}), (nyc10:City {id: 'city_new_york'})
MERGE (nm4c)-[:LIVES_IN]->(nyc10);
MATCH (nm5c:Mentor {id: 'mentor_liu_nyc'}), (nyc11:City {id: 'city_new_york'})
MERGE (nm5c)-[:LIVES_IN]->(nyc11);
MATCH (nha1b:HousingArea {id: 'housing_morningside_nyc'}), (u_col4:University {id: 'univ_columbia'})
MERGE (nha1b)-[:NEAR_UNIVERSITY]->(u_col4);
MATCH (nha2b:HousingArea {id: 'housing_jackson_heights_nyc'}), (nyc12:City {id: 'city_new_york'})
MERGE (nha2b)-[:LOCATED_IN]->(nyc12);
MATCH (npow1b:PlaceOfWorship {id: 'pow_ganesh_temple_flushing'}), (nb_flush3:Neighborhood {id: 'nb_flushing'})
MERGE (npow1b)-[:LOCATED_IN]->(nb_flush3);
MATCH (npow2b:PlaceOfWorship {id: 'pow_nyc_isb_masjid'}), (nyc13:City {id: 'city_new_york'})
MERGE (npow2b)-[:LOCATED_IN]->(nyc13);
MATCH (npow3b:PlaceOfWorship {id: 'pow_sikh_gurdwara_nyc'}), (nyc14:City {id: 'city_new_york'})
MERGE (npow3b)-[:LOCATED_IN]->(nyc14);
MATCH (ngs1b:GroceryStore {id: 'grocery_patel_brothers_nyc'}), (nb_jack3:Neighborhood {id: 'nb_jackson_heights'})
MERGE (ngs1b)-[:LOCATED_IN]->(nb_jack3);
MATCH (ngs2b:GroceryStore {id: 'grocery_h_mart_nyc'}), (nyc15:City {id: 'city_new_york'})
MERGE (ngs2b)-[:LOCATED_IN]->(nyc15);
MATCH (nex1b:ExplorationSpot {id: 'explore_central_park_nyc'}), (nyc16:City {id: 'city_new_york'})
MERGE (nex1b)-[:LOCATED_IN]->(nyc16);
MATCH (nex2b:ExplorationSpot {id: 'explore_the_met_nyc'}), (nyc17:City {id: 'city_new_york'})
MERGE (nex2b)-[:LOCATED_IN]->(nyc17);
MATCH (ntt1b:TransitTip {id: 'transit_mta_7_train'}), (nyc18:City {id: 'city_new_york'})
MERGE (ntt1b)-[:SERVES]->(nyc18);
MATCH (ntt2b:TransitTip {id: 'transit_mta_a_train'}), (nyc19:City {id: 'city_new_york'})
MERGE (ntt2b)-[:SERVES]->(nyc19);
