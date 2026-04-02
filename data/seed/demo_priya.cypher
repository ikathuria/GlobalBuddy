// Hero student: Priya — India -> Illinois Institute of Technology (Chicago), needs banking + housing + community
MERGE (s:Student {id: 'student_priya'})
SET s.name = 'Priya', s.home_city = 'Bengaluru';

MATCH (s:Student {id: 'student_priya'})-[r:STUDIES_AT]->(u:University)
WHERE u.id <> 'univ_iit'
DELETE r;

MATCH (s:Student {id: 'student_priya'}), (c:Country {id: 'country_in'})
MERGE (s)-[:FROM_COUNTRY]->(c);

MATCH (s:Student {id: 'student_priya'}), (u:University {id: 'univ_iit'})
MERGE (s)-[:STUDIES_AT]->(u);

MATCH (s:Student {id: 'student_priya'}), (n:Need {id: 'need_banking'})
MERGE (s)-[:NEEDS_HELP_WITH]->(n);

MATCH (s:Student {id: 'student_priya'}), (n:Need {id: 'need_housing'})
MERGE (s)-[:NEEDS_HELP_WITH]->(n);

MATCH (s:Student {id: 'student_priya'}), (n:Need {id: 'need_community'})
MERGE (s)-[:NEEDS_HELP_WITH]->(n);
