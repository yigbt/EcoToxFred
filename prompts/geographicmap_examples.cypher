// Show sites where Diuron has been measured on the European map.
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE s.name = 'Diuron'
RETURN s.name AS ChemicalName, // plot title
       r.year AS Year, r.quarter AS Quarter, // add to point hover
       l.name AS SiteName, // point hover
       l.water_body AS WaterBody, l.river_basin AS RiverBasin, // point hover
       l.lat AS Lat, l.lon AS Lon // x,y coordinates

// Show Diuron's measured concentrations on the European map.
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE s.name = 'Diuron'
RETURN s.name AS ChemicalName, // plot title
       r.median_concentration AS Concentration, // >=0, continuous point color from yellow to red
       r.year AS Year, r.quarter AS Quarter, // add to point hover
       l.name AS SiteName, // point hover
       l.water_body AS WaterBody, l.river_basin AS RiverBasin, // point hover
       l.lat AS Lat, l.lon AS Lon // x,y coordinates
  ORDER BY r.median_concentration DESC

// Show Diuron's measured concentrations between 2010 and 2020 on the European map.
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE s.name = 'Diuron' AND r.year >= 2010 AND r.year <= 2020
RETURN s.name AS ChemicalName, // plot title
       r.median_concentration AS Concentration, // >=0, continuous point color from yellow to red
       r.year AS Year, r.quarter AS Quarter, // add to point hover
       l.name AS SiteName, // point hover
       l.water_body AS WaterBody, l.river_basin AS RiverBasin, // point hover
       l.lat AS Lat, l.lon AS Lon // x,y coordinates
  ORDER BY r.median_concentration DESC

// Show Diuron's driver importance distribution in France between January 2010 and December 2012.
MATCH (s:Substance)-[r:IS_DRIVER]->(l:Site)
  WHERE s.name = 'Diuron' AND l.country = 'France' AND r.year >= 2010 AND r.year <=2012
RETURN s.name AS ChemicalName, // plot title
       r.driver_importance AS DriverImportance, // [0,1], continuous point color from blue to red, with midpoint at 0.5
       r.species AS Species, // add to point hover
       r.year AS Year, r.quarter AS Quarter, // add to point hover
       l.name AS SiteName, // point hover
       l.water_body AS WaterBody, l.river_basin AS RiverBasin, // point hover
       l.lat AS Lat, l.lon AS Lon // x,y coordinates
  ORDER BY r.driver_importance DESC

// Show Diuron's toxic unit (TU) distribution for algae (unicellular) since 2010.
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE s.name = 'Diuron' AND r.year >= 2010
RETURN s.name AS ChemicalName, // plot title
       r.TU_algae AS TU, // >=0, continuous point color from yellow to red, with midpoint orange at 1
       r.year AS Year, r.quarter AS Quarter, // add to point hover
       l.name AS SiteName, // point hover
       l.water_body AS WaterBody, l.river_basin AS RiverBasin, // point hover
       l.lat AS Lat, l.lon AS Lon // x,y coordinates
  ORDER BY r.TU_algae DESC

// Show the distribution of the summarized toxic unit (sumTU) for algae since 2010.
MATCH (l:Site)-[r:SUMMARIZED_IMPACT_ON]->(s:Species)
  WHERE s.name = 'algae' AND r.year >= 2010
RETURN s.name AS SpeciesName, // plot title
       r.sumTU AS sumTU, // >=0, continuous point color from yellow to red, with midpoint orange at 0.001
       r.year AS Year, r.quarter AS Quarter, // add to point hover
       l.name AS SiteName, // point hover
       l.water_body AS WaterBody, l.river_basin AS RiverBasin, // point hover
       l.lat AS Lat, l.lon AS Lon // x,y coordinates
  ORDER BY r.sumTU DESC

// Show the distribution of the ratio toxic unit (ratioTU) for algae since 2010.
MATCH (l:Site)-[r:SUMMARIZED_IMPACT_ON]->(s:Species)
  WHERE r.year >= 2010 AND s.name = 'algae'
RETURN s.name AS SpeciesName, // plot title
       r.ratioTU AS ratioTU, // [0,1] - continuous point color from blue to red, with midpoint at 0.5
       r.year AS Year, r.quarter AS Quarter, r.species, // add to point hover
       l.name AS SiteName, // point hover
       l.water_body AS WaterBody, l.river_basin AS RiverBasin, // point hover
       l.lat AS Lat, l.lon AS Lon // x,y coordinates
  ORDER BY r.sumTU DESC

// Show the distribution of the maximal toxic unit (maxTU) for algae since 2010.
MATCH (l:Site)-[r:SUMMARIZED_IMPACT_ON]->(s:Species)
  WHERE r.year >= 2010 AND s.name = 'algae'
RETURN s.name AS SpeciesName, // plot title
       r.maxTU AS maxTU, // >=0, continuous point color from yellow to red
       r.year AS Year, r.quarter AS Quarter, r.species, // add to point hover
       l.name AS SiteName, // point hover
       l.water_body AS WaterBody, l.river_basin AS RiverBasin, // point hover
       l.lat AS Lat, l.lon AS Lon // x,y coordinates
  ORDER BY r.sumTU DESC
