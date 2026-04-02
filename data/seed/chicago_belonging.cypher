// Chicago Belonging + Navigation Intelligence — curated demo data (verify dates and locations independently for production)
CREATE CONSTRAINT place_of_worship_id IF NOT EXISTS FOR (n:PlaceOfWorship) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT grocery_store_id IF NOT EXISTS FOR (n:GroceryStore) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT housing_area_id IF NOT EXISTS FOR (n:HousingArea) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT exploration_spot_id IF NOT EXISTS FOR (n:ExplorationSpot) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT transit_tip_id IF NOT EXISTS FOR (n:TransitTip) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT diet_tag_id IF NOT EXISTS FOR (n:DietTag) REQUIRE n.id IS UNIQUE;

MERGE (diet_veg:DietTag {id: 'diet_vegetarian'}) SET diet_veg.name = 'vegetarian';
MERGE (diet_halal:DietTag {id: 'diet_halal'}) SET diet_halal.name = 'halal';

MERGE (nb_devon:Neighborhood {id: 'nb_devon_ave'}) SET nb_devon.name = 'Devon Ave';

// MATCH City first — MERGE (n)-[:R]->(:City {id}) can otherwise CREATE a duplicate City when the edge is missing.
MATCH (nb_devon:Neighborhood {id: 'nb_devon_ave'}), (cchi:City {id: 'city_chicago'})
MERGE (nb_devon)-[:IN_CITY]->(cchi);

MATCH (nb:Neighborhood {id: 'nb_south_loop'}), (cchi2:City {id: 'city_chicago'})
MERGE (nb)-[:IN_CITY]->(cchi2);

MERGE (pow1:PlaceOfWorship {id: 'pow_devon_temple_demo'})
SET pow1.name = 'Ganesh Temple of Chicago (Devon corridor)',
    pow1.subtype = 'hindu_temple',
    pow1.address = '5959 N California Ave, Chicago, IL',
    pow1.neighborhood = 'West Ridge / Devon Ave',
    pow1.latitude = 41.991,
    pow1.longitude = -87.703,
    pow1.maps_query = 'Ganesh Temple of Chicago 5959 N California Ave',
    pow1.maps_link = 'https://www.google.com/maps/search/?api=1&query=Ganesh%20Temple%20of%20Chicago',
    pow1.audience_tags = ['hindu', 'south_asian', 'indian'],
    pow1.city_name = 'Chicago';

MERGE (pow2:PlaceOfWorship {id: 'pow_ifo_north_demo'})
SET pow2.name = 'Islamic Foundation North (suburban Chicago)',
    pow2.subtype = 'mosque',
    pow2.address = '1751 O-Plaine Rd, Libertyville, IL',
    pow2.neighborhood = 'North suburbs',
    pow2.latitude = 42.283,
    pow2.longitude = -87.958,
    pow2.maps_query = 'Islamic Foundation North Libertyville IL',
    pow2.maps_link = 'https://www.google.com/maps/search/?api=1&query=Islamic%20Foundation%20North%20Libertyville',
    pow2.audience_tags = ['muslim', 'south_asian'],
    pow2.city_name = 'Chicago';

MERGE (pow3:PlaceOfWorship {id: 'pow_sikh_palatine_demo'})
SET pow3.name = 'Sikh Religious Society Palatine',
    pow3.subtype = 'gurdwara',
    pow3.address = '1280 Winnetka St, Palatine, IL',
    pow3.neighborhood = 'Northwest suburbs',
    pow3.latitude = 42.095,
    pow3.longitude = -88.034,
    pow3.maps_query = 'Sikh Religious Society Palatine IL',
    pow3.maps_link = 'https://www.google.com/maps/search/?api=1&query=Sikh%20Religious%20Society%20Palatine',
    pow3.audience_tags = ['sikh', 'punjabi', 'south_asian'],
    pow3.city_name = 'Chicago';

MERGE (gs1:GroceryStore {id: 'grocery_patel_devon'})
SET gs1.name = 'Patel Brothers (Devon Ave)',
    gs1.address = '2610 W Devon Ave, Chicago, IL',
    gs1.neighborhood = 'Devon Ave',
    gs1.latitude = 42.000,
    gs1.longitude = -87.698,
    gs1.maps_query = 'Patel Brothers 2610 W Devon Ave Chicago',
    gs1.maps_link = 'https://www.google.com/maps/search/?api=1&query=Patel%20Brothers%20Devon%20Ave%20Chicago',
    gs1.diet_tags = ['vegetarian', 'south_asian'],
    gs1.city_name = 'Chicago';

MERGE (gs2:GroceryStore {id: 'grocery_mariano_south_loop'})
SET gs2.name = "Mariano's South Loop",
    gs2.address = '1615 S Clark St, Chicago, IL',
    gs2.neighborhood = 'South Loop',
    gs2.latitude = 41.860,
    gs2.longitude = -87.631,
    gs2.maps_query = "Marianos 1615 S Clark St Chicago",
    gs2.maps_link = 'https://www.google.com/maps/search/?api=1&query=Marianos%20South%20Loop%20Chicago',
    gs2.diet_tags = ['vegetarian', 'halal_section_typical'],
    gs2.city_name = 'Chicago';

MERGE (ha1:HousingArea {id: 'housing_lake_meadows'})
SET ha1.name = 'Lake Meadows (apartment cluster)',
    ha1.address = 'Near 29th St and Martin Luther King Dr, Chicago, IL',
    ha1.neighborhood = 'Bronzeville',
    ha1.latitude = 41.842,
    ha1.longitude = -87.618,
    ha1.maps_query = 'Lake Meadows apartments Chicago IL',
    ha1.maps_link = 'https://www.google.com/maps/search/?api=1&query=Lake%20Meadows%20Chicago',
    ha1.audience_tags = ['student_friendly', 'near_green_line'],
    ha1.city_name = 'Chicago';

MERGE (ha2:HousingArea {id: 'housing_prairie_shores'})
SET ha2.name = 'Prairie Shores (near IIT)',
    ha2.address = '2937 S King Dr, Chicago, IL',
    ha2.neighborhood = 'Bronzeville',
    ha2.latitude = 41.838,
    ha2.longitude = -87.618,
    ha2.maps_query = 'Prairie Shores Chicago IL',
    ha2.maps_link = 'https://www.google.com/maps/search/?api=1&query=Prairie%20Shores%20Chicago',
    ha2.audience_tags = ['near_iit', 'student_friendly'],
    ha2.city_name = 'Chicago';

MERGE (ha3:HousingArea {id: 'housing_bridgeport_demo'})
SET ha3.name = 'Bridgeport (neighborhood near Orange Line)',
    ha3.address = 'Bridgeport, Chicago, IL',
    ha3.neighborhood = 'Bridgeport',
    ha3.latitude = 41.838,
    ha3.longitude = -87.645,
    ha3.maps_query = 'Bridgeport Chicago IL',
    ha3.maps_link = 'https://www.google.com/maps/search/?api=1&query=Bridgeport%20Chicago',
    ha3.audience_tags = ['budget_friendly', 'cta_orange_line'],
    ha3.city_name = 'Chicago';

MERGE (ex1:ExplorationSpot {id: 'explore_art_institute'})
SET ex1.name = 'Art Institute of Chicago',
    ex1.subtype = 'museum',
    ex1.address = '111 S Michigan Ave, Chicago, IL',
    ex1.neighborhood = 'Downtown Loop',
    ex1.latitude = 41.879,
    ex1.longitude = -87.624,
    ex1.maps_query = 'Art Institute of Chicago',
    ex1.maps_link = 'https://www.google.com/maps/search/?api=1&query=Art%20Institute%20of%20Chicago',
    ex1.audience_tags = ['downtown', 'weekend'],
    ex1.city_name = 'Chicago';

MERGE (ex2:ExplorationSpot {id: 'explore_millennium'})
SET ex2.name = 'Millennium Park and Cloud Gate',
    ex2.subtype = 'park',
    ex2.address = '201 E Randolph St, Chicago, IL',
    ex2.neighborhood = 'Loop',
    ex2.latitude = 41.882,
    ex2.longitude = -87.622,
    ex2.maps_query = 'Millennium Park Chicago',
    ex2.maps_link = 'https://www.google.com/maps/search/?api=1&query=Millennium%20Park%20Chicago',
    ex2.audience_tags = ['downtown', 'weekend', 'free_outdoor'],
    ex2.city_name = 'Chicago';

MERGE (tt1:TransitTip {id: 'transit_cta_3_king_drive'})
SET tt1.name = 'CTA #3 King Drive (example north-south)',
    tt1.summary = 'Use CTA trip planner for real-time schedules; this is a common north-south option in the grid.',
    tt1.route_hint = 'Bus 3 runs along King Drive; connect to Green Line for IIT area. Verify stops on transitchicago.com.',
    tt1.neighborhood = 'Citywide',
    tt1.maps_link = 'https://www.google.com/maps/search/?api=1&query=CTA%20King%20Drive%20bus%203%20Chicago',
    tt1.city_name = 'Chicago';

MERGE (tt2:TransitTip {id: 'transit_green_line_iit'})
SET tt2.name = 'Green Line to 35th-Bronzeville-IIT',
    tt2.summary = 'Nearest rapid transit reference for Illinois Tech area.',
    tt2.route_hint = 'CTA Green Line 35th-Bronzeville-IIT station. Confirm exits and walking route to campus.',
    tt2.neighborhood = 'Bronzeville',
    tt2.maps_link = 'https://www.google.com/maps/search/?api=1&query=35th%20Bronzeville%20IIT%20CTA',
    tt2.city_name = 'Chicago';

MERGE (ev_st:Event {id: 'event_st_patricks_seasonal_demo'})
SET ev_st.name = "Chicago St. Patrick's Day parade (seasonal)",
    ev_st.start_time = 'TBD_MARCH_ANNUAL',
    ev_st.location = 'Downtown Chicago river area',
    ev_st.category = 'seasonal_cultural',
    ev_st.notes = 'Recurring cultural event; year-specific date and route must be confirmed with City of Chicago or parade organizers.',
    ev_st.maps_query = 'Chicago St Patrick parade downtown',
    ev_st.maps_link = 'https://www.google.com/maps/search/?api=1&query=Downtown%20Chicago%20Riverwalk';

MERGE (ev_rn:Event {id: 'event_ram_navami_community_demo'})
SET ev_rn.name = 'Ram Navami community celebrations (Chicago area)',
    ev_rn.start_time = 'TBD_SPRING_ANNUAL',
    ev_rn.location = 'Various temples and cultural halls. Check local mandir calendars.',
    ev_rn.category = 'religious_cultural',
    ev_rn.notes = 'Representative community pattern; confirm schedules with individual temples and cultural associations.',
    ev_rn.maps_query = 'Hindu temple Chicago Ram Navami',
    ev_rn.maps_link = 'https://www.google.com/maps/search/?api=1&query=Devon%20Ave%20temples%20Chicago';

MERGE (ev_eid:Event {id: 'event_eid_community_demo'})
SET ev_eid.name = 'Eid al-Fitr community gatherings (Chicago area)',
    ev_eid.start_time = 'TBD_LUNAR_CALENDAR',
    ev_eid.location = 'Mosques and community centers. Varies.',
    ev_eid.category = 'religious_cultural',
    ev_eid.notes = 'Islamic calendar determines dates; confirm with local mosques and student associations.',
    ev_eid.maps_query = 'Islamic Foundation North Libertyville',
    ev_eid.maps_link = 'https://www.google.com/maps/search/?api=1&query=mosque%20Chicago%20Eid';

MATCH (pow1:PlaceOfWorship {id: 'pow_devon_temple_demo'}), (nbd:Neighborhood {id: 'nb_devon_ave'})
MERGE (pow1)-[:LOCATED_IN]->(nbd);
MATCH (gs1:GroceryStore {id: 'grocery_patel_devon'}), (nbd2:Neighborhood {id: 'nb_devon_ave'})
MERGE (gs1)-[:LOCATED_IN]->(nbd2);
MATCH (gs2:GroceryStore {id: 'grocery_mariano_south_loop'}), (nbs:Neighborhood {id: 'nb_south_loop'})
MERGE (gs2)-[:LOCATED_IN]->(nbs);
MATCH (pow2:PlaceOfWorship {id: 'pow_ifo_north_demo'}), (chi:City {id: 'city_chicago'})
MERGE (pow2)-[:LOCATED_IN]->(chi);
MATCH (pow3:PlaceOfWorship {id: 'pow_sikh_palatine_demo'}), (chi2:City {id: 'city_chicago'})
MERGE (pow3)-[:LOCATED_IN]->(chi2);
MATCH (ha1:HousingArea {id: 'housing_lake_meadows'}), (u:University {id: 'univ_iit'})
MERGE (ha1)-[:NEAR_UNIVERSITY]->(u);
MATCH (ha2:HousingArea {id: 'housing_prairie_shores'}), (u2:University {id: 'univ_iit'})
MERGE (ha2)-[:NEAR_UNIVERSITY]->(u2);
MATCH (ha3:HousingArea {id: 'housing_bridgeport_demo'}), (u3:University {id: 'univ_iit'})
MERGE (ha3)-[:NEAR_UNIVERSITY]->(u3);
MATCH (ex1:ExplorationSpot {id: 'explore_art_institute'}), (c3:City {id: 'city_chicago'})
MERGE (ex1)-[:LOCATED_IN]->(c3);
MATCH (ex2:ExplorationSpot {id: 'explore_millennium'}), (c4:City {id: 'city_chicago'})
MERGE (ex2)-[:LOCATED_IN]->(c4);
MATCH (tt1:TransitTip {id: 'transit_cta_3_king_drive'}), (c5:City {id: 'city_chicago'})
MERGE (tt1)-[:GOOD_FOR]->(c5);
MATCH (tt2:TransitTip {id: 'transit_green_line_iit'}), (c6:City {id: 'city_chicago'})
MERGE (tt2)-[:GOOD_FOR]->(c6);
MATCH (pow1b:PlaceOfWorship {id: 'pow_devon_temple_demo'}), (cin:Country {id: 'country_in'})
MERGE (pow1b)-[:RELEVANT_TO]->(cin);
MATCH (pow2b:PlaceOfWorship {id: 'pow_ifo_north_demo'}), (cin2:Country {id: 'country_in'})
MERGE (pow2b)-[:RELEVANT_TO]->(cin2);
MATCH (pow3b:PlaceOfWorship {id: 'pow_sikh_palatine_demo'}), (cin3:Country {id: 'country_in'})
MERGE (pow3b)-[:RELEVANT_TO]->(cin3);
MATCH (gs1b:GroceryStore {id: 'grocery_patel_devon'}), (dv:DietTag {id: 'diet_vegetarian'})
MERGE (gs1b)-[:MATCHES_DIET]->(dv);
MATCH (gs1c:GroceryStore {id: 'grocery_patel_devon'}), (cin4:Country {id: 'country_in'})
MERGE (gs1c)-[:RELEVANT_TO]->(cin4);
MATCH (gs2b:GroceryStore {id: 'grocery_mariano_south_loop'}), (cin5:Country {id: 'country_in'})
MERGE (gs2b)-[:RELEVANT_TO]->(cin5);
MATCH (ev_st:Event {id: 'event_st_patricks_seasonal_demo'}), (cus:Country {id: 'country_us'})
MERGE (ev_st)-[:RELEVANT_TO]->(cus);
MATCH (ev_st2:Event {id: 'event_st_patricks_seasonal_demo'}), (cin6:Country {id: 'country_in'})
MERGE (ev_st2)-[:RELEVANT_TO]->(cin6);
MATCH (ev_st3:Event {id: 'event_st_patricks_seasonal_demo'}), (c7:City {id: 'city_chicago'})
MERGE (ev_st3)-[:OCCURS_IN]->(c7);
MATCH (ev_rn:Event {id: 'event_ram_navami_community_demo'}), (cin7:Country {id: 'country_in'})
MERGE (ev_rn)-[:RELEVANT_TO]->(cin7);
MATCH (ev_rn2:Event {id: 'event_ram_navami_community_demo'}), (c8:City {id: 'city_chicago'})
MERGE (ev_rn2)-[:OCCURS_IN]->(c8);
MATCH (ev_eid:Event {id: 'event_eid_community_demo'}), (cin8:Country {id: 'country_in'})
MERGE (ev_eid)-[:RELEVANT_TO]->(cin8);
MATCH (ev_eid2:Event {id: 'event_eid_community_demo'}), (c9:City {id: 'city_chicago'})
MERGE (ev_eid2)-[:OCCURS_IN]->(c9);
