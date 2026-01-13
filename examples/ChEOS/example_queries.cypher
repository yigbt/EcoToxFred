// delete all relations MEASURED_AT in chunks to avoid mem overflow
MATCH (s:Substance)-[r:MEASURED_AT]->()
CALL {
WITH r
DETACH DELETE r
} IN TRANSACTIONS OF 10000 ROWS

// delete all substance nodes
MATCH (n:Substance)
DETACH DELETE n

// where is Diuron a driver with high driver importance
MATCH (s:Substance {name: 'Diuron'})-[r:IS_DRIVER]->(l:Site)
  WHERE r.driver_importance > 0.8
RETURN s, r, l

// find all substances measured above a threshold in a certain river
MATCH (c:Substance)-[r:MEASURED_AT]->(s:Site {water_body: 'seine'})
  WHERE r.mean_concentration > 0
RETURN c.DTXSID AS DTXSID, c.preferredName AS Name

MATCH (c:Substance)-[r:MEASURED_AT]->(s:Site {country: 'France'})
RETURN DISTINCT c.DTXSID AS DTXSID, c.preferredName AS Name

// find most frequent drivers
MATCH (s:Substance)-[r:IS_DRIVER]->(l:Site)
  WHERE r.driver_importance > 0.8
RETURN DISTINCT s.name, s.DTXSID, r.driver_importance
  ORDER BY r.driver_importance

// TU computation in GDB
// median_concentration = median(concentration_value)
// TU = ifelse (toxsource=qsar); (median_concentration * neutral_fraction) / tox_value; median_concentration / tox_value

LOAD CSV WITH HEADERS FROM 'file:///companies.csv' AS row
WITH row WHERE row.Id IS NOT NULL
WITH row,
(CASE row.BusinessType
 WHEN 'P' THEN 'Public'
 WHEN 'R' THEN 'Private'
 WHEN 'G' THEN 'Government'
 ELSE 'Other' END) AS type
MERGE (c:Company {companyId: row.Id, hqLocation: coalesce(row.Location, "Unknown")})
SET c.emailAddress = CASE trim(row.Email) WHEN "" THEN null ELSE row.Email END
SET c.businessType = type
RETURN *

LOAD CSV WITH HEADERS FROM "file:///Relationships.csv" AS row
//look up the two nodes we want to connect up
MATCH (p1:Person {id:row.id_from}), (p2:Person {id:row.id_to})
//now create a relationship between them
CREATE (p1)-[:KNOWS]->(p2);


MATCH (s1:Substance)-[r1:MEASURED_AT]->(l:Site)<-[r2:MEASURED_AT]-(s2:Substance)
WHERE s1 <> s2 AND s1.Name < s2.Name AND r1.median_concentration > 0 AND r2.median_concentration > 0
RETURN s1.Name AS Compound1, s2.Name AS Compound2, count(l) AS Frequency
ORDER BY Frequency DESC