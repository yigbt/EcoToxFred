// Show sites where Diuron has been measured on the European map.
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE s.Name = 'Diuron'
RETURN s.Name AS chemicalname, // plot title
       r.year AS year, r.quarter AS quarter, // add to point hover
       l.name AS sitename, // point hover
       l.water_body AS waterbody, l.river_basin AS riverbasin, // point hover
       l.lat AS lat, l.lon AS lon // x,y coordinates

// Show Diuron's measured concentrations on the European map.
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE s.Name = 'Diuron'
RETURN s.Name AS chemicalname, // plot title
       r.median_concentration AS concentration, // >=0, continuous point color from yellow to red
       r.year AS year, r.quarter AS quarter, // add to point hover
       l.name AS sitename, // point hover
       l.water_body AS waterbody, l.river_basin AS riverbasin, // point hover
       l.lat AS lat, l.lon AS lon // x,y coordinates
  ORDER BY r.median_concentration DESC

// Show Diuron's detected concentrations on the European map.
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE s.Name = 'Diuron' AND r.median_concentration > 0
RETURN s.Name AS chemicalname, // plot title
       r.median_concentration AS concentration, // >=0, continuous point color from yellow to red
       r.year AS year, r.quarter AS quarter, // add to point hover
       l.name AS sitename, // point hover
       l.water_body AS waterbody, l.river_basin AS riverbasin, // point hover
       l.lat AS lat, l.lon AS lon // x,y coordinates
  ORDER BY r.median_concentration DESC

// Show Diuron's measured concentrations between 2010 and 2020 on the European map.
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE s.Name = 'Diuron' AND r.year >= 2010 AND r.year <= 2020
RETURN s.Name AS chemicalname, // plot title
       r.median_concentration AS concentration, // >=0, continuous point color from yellow to red
       r.year AS year, r.quarter AS quarter, // add to point hover
       l.name AS sitename, // point hover
       l.water_body AS waterbody, l.river_basin AS riverbasin, // point hover
       l.lat AS lat, l.lon AS lon // x,y coordinates
  ORDER BY r.median_concentration DESC

// Show Diuron's driver importance distribution in France between January 2010 and December 2012.
MATCH (s:Substance)-[r:IS_DRIVER]->(l:Site)
  WHERE s.Name = 'Diuron' AND l.country = 'France' AND r.year >= 2010 AND r.year <= 2012
RETURN s.Name AS chemicalname, // plot title
       r.driver_importance AS driverimportance, // [0,1], continuous point color from blue to red, with midpoint at 0.5
       r.species AS species, // add to point hover
       r.year AS year, r.quarter AS quarter, // add to point hover
       l.name AS sitename, // point hover
       l.water_body AS waterbody, l.river_basin AS riverbasin, // point hover
       l.lat AS lat, l.lon AS lon // x,y coordinates
  ORDER BY r.driver_importance DESC

// Show Diuron's toxic unit (tu) distribution for algae (unicellular) since 2010.
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE s.Name = 'Diuron' AND r.year >= 2010
RETURN s.Name AS chemicalname, // plot title
       r.TU_algae AS tu, // >=0, continuous point color from yellow to red, with midpoint orange at 1
       r.year AS year, r.quarter AS quarter, // add to point hover
       l.name AS sitename, // point hover
       l.water_body AS waterbody, l.river_basin AS riverbasin, // point hover
       l.lat AS lat, l.lon AS lon // x,y coordinates
  ORDER BY r.TU_algae DESC

// Show the distribution of the summarized toxic unit (sumtu) for algae since 2010.
MATCH (l:Site)-[r:SUMMARIZED_IMPACT_ON]->(s:Species)
  WHERE s.name = 'algae' AND r.year >= 2010
RETURN s.name AS speciesname, // plot title
       r.sumTU AS sumtu, // >=0, continuous point color from yellow to red, with midpoint orange at 0.001
       r.year AS year, r.quarter AS quarter, // add to point hover
       l.name AS sitename, // point hover
       l.water_body AS waterbody, l.river_basin AS riverbasin, // point hover
       l.lat AS lat, l.lon AS lon // x,y coordinates
  ORDER BY r.sumTU DESC

// Show the distribution of the ratio toxic unit (ratiotu) for algae since 2010.
MATCH (l:Site)-[r:SUMMARIZED_IMPACT_ON]->(s:Species)
  WHERE r.year >= 2010 AND s.name = 'algae'
RETURN s.name AS speciesname, // plot title
       r.ratioTU AS ratiotu, // [0,1] - continuous point color from blue to red, with midpoint at 0.5
       r.year AS year, r.quarter AS quarter, r.species, // add to point hover
       l.name AS sitename, // point hover
       l.water_body AS waterbody, l.river_basin AS riverbasin, // point hover
       l.lat AS lat, l.lon AS lon // x,y coordinates
  ORDER BY r.sumTU DESC

// Show the distribution of the maximal toxic unit (maxtu) for algae since 2010.
MATCH (l:Site)-[r:SUMMARIZED_IMPACT_ON]->(s:Species)
  WHERE r.year >= 2010 AND s.name = 'algae'
RETURN s.name AS speciesname, // plot title
       r.maxTU AS maxtu, // >=0, continuous point color from yellow to red
       r.year AS year, r.quarter AS quarter, r.species, // add to point hover
       l.name AS sitename, // point hover
       l.water_body AS waterbody, l.river_basin AS riverbasin, // point hover
       l.lat AS lat, l.lon AS lon // x,y coordinates
  ORDER BY r.sumTU DESC

// Show ratiotu distribution for algae along the Danube (2010–2015).
MATCH (l:Site)-[r:SUMMARIZED_IMPACT_ON]->(s:species)
WHERE r.year >= 2010 AND r.year <= 2015 AND s.name = 'algae' AND l.water_body = 'danube'
RETURN s.name AS speciesname, // plot title
r.ratioTU AS ratiotu, // [0,1] - continuous point color from blue to red, with midpoint at 0.5
r.year AS year, r.quarter AS quarter, // add to point hover
l.name AS sitename, // point hover
l.water_body AS waterbody, l.river_basin AS riverbasin, // point hover
l.lat AS lat, l.lon AS lon // x,y coordinates
ORDER BY r.ratioTU DESC
