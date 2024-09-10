// Find all sites where Diuron is a driver substance after 2010 and show the distribution of driver importance on a map
MATCH (s:Substance)-[r:IS_DRIVER]->(l:Site)
  WHERE s.Name = 'Diuron' AND r.year > 2010
RETURN s.Name AS ChemicalName,
       r.driver_importance AS DriverImportance,
       l.name AS SiteName, l.lat AS Lat, l.lon AS Lon, l.country AS Country
  ORDER BY r.driver_importance DESC

// Plot sites at risk for fish in 2014 on a map
MATCH (l:Site)-[r:SUMMARIZED_IMPACT_ON]->(s:Species)
  WHERE s.name = 'fish' AND r.year = 2014
RETURN s.name AS SpeciesName,
       r.sumTU AS sumTU,
       r.year AS Year, r.quarter AS Quarter, // add to point hover
       l.name AS SiteName,
       l.name AS SiteName, l.lat AS Lat, l.lon AS Lon, l.country AS Country
ORDER BY r.sumTU DESC

