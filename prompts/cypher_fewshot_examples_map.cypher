// To show the (median) measured concentrations of a certain substance
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE s.Name = 'Diuron'
RETURN s.Name AS ChemicalName, // plot title
       r.median_concentration AS Concentration, // >=0, continuous point color from yellow to red
       l.name AS SiteName, // point hover
       l.lat AS Lat, l.lon AS Lon // x,y coordinates
  ORDER BY r.median_concentration DESC

// To show the (median) measured concentrations of a certain substance at a certain range of time
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE s.Name = 'Diuron' AND r.year >= 2010 AND r.year <= 2020
RETURN s.Name AS ChemicalName, // plot title
       r.median_concentration AS Concentration, // >=0, continuous point color from yellow to red
       r.year AS Year, r.quarter AS Quarter, // add to point hover
       l.name AS SiteName, // point hover
       l.lat AS Lat, l.lon AS Lon // x,y coordinates
  ORDER BY r.median_concentration DESC

// To show the driver_importance distribution of a certain substance
MATCH (s:Substance)-[r:IS_DRIVER]->(l:Site)
  WHERE s.Name = 'Diuron'
RETURN s.Name AS ChemicalName, // plot title
       r.driver_importance AS DriverImportance, // [0,1], continuous point color from blue to red, with midpoint at 0.5
       r.species AS Species, // add to point hover
       l.name AS SiteName, // point hover
       l.lat AS Lat, l.lon AS Lon // x,y coordinates
  ORDER BY r.driver_importance DESC

// To show the driver_importance distribution of a certain substance at a certain time
MATCH (s:Substance)-[r:IS_DRIVER]->(l:Site)
  WHERE s.Name = 'Diuron' AND r.year >= 2010
RETURN s.Name AS ChemicalName, // plot title
       r.driver_importance AS DriverImportance, // [0,1], continuous point color from blue to red, with midpoint at 0.5
       r.year AS Year, r.quarter AS Quarter, r.species AS Species, // add to point hover
       l.name AS SiteName, l.country AS Country, // point hover
       l.lat AS Lat, l.lon AS Lon // x,y coordinates
  ORDER BY r.driver_importance DESC

// To show the distribution of the toxic unit (TU) of a certain substance at a certain time for the species algae (unicellular)
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE s.Name = 'Diuron' AND r.year >= 2010
RETURN s.Name AS ChemicalName, // plot title
       r.TU_algae AS TU, // >=0, continuous point color from yellow to red, with midpoint orange at 1
       r.year AS Year, r.quarter AS Quarter, // add to point hover
       l.name AS SiteName, // point hover
       l.lat AS Lat, l.lon AS Lon // x,y coordinates
  ORDER BY r.TU_algae DESC

// To show the distribution of the summarized toxic unit (sumTU) at a certain time for a certain species
MATCH (l:Site)-[r:SUMMARIZED_IMPACT_ON]->(s:Species)
  WHERE s.name = 'algae' AND r.year >= 2010
RETURN s.name AS SpeciesName, // plot title
       r.sumTU AS sumTU, // >=0, continuous point color from yellow to red, with midpoint orange at 0.001
       r.year AS Year, r.quarter AS Quarter, // add to point hover
       l.name AS SiteName, // point hover
       l.lat AS Lat, l.lon AS Lon // x,y coordinates
  ORDER BY r.sumTU DESC

// To show the distribution of the summarized toxic unit (ratioTU) of a certain site at a certain time for the species algae (unicellular)
MATCH (l:Site)-[r:SUMMARIZED_IMPACT_ON]->(s:Species)
  WHERE r.year >= 2010 AND s.name = 'algae'
RETURN s.name AS SpeciesName, // plot title
       r.ratioTU AS ratioTU, // [0,1] - continuous point color from blue to red, with midpoint at 0.5
       r.year AS Year, r.quarter AS Quarter, r.species, // add to point hover
       l.name AS SiteName, // point hover
       l.lat AS Lat, l.lon AS Lon // x,y coordinates
  ORDER BY r.sumTU DESC

// To show the distribution of the summarized toxic unit (maxTU) of a certain site at a certain time for the species algae (unicellular)
MATCH (l:Site)-[r:SUMMARIZED_IMPACT_ON]->(s:Species)
  WHERE r.year >= 2010 AND s.name = 'algae'
RETURN s.name AS SpeciesName, // plot title
       r.maxTU AS maxTU, // >=0, continuous point color from yellow to red
       r.year AS Year, r.quarter AS Quarter, r.species, // add to point hover
       l.name AS SiteName, // point hover
       l.lat AS Lat, l.lon AS Lon // x,y coordinates
  ORDER BY r.sumTU DESC
