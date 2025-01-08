// To retrieve sites where "Atrazine" was measured in the second half of the year 2011:
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE s.Name = 'Atrazine' AND r.year = 2011 AND 3 <= r.quarter <= 4
RETURN s.Name AS ChemicalName,
       l.name AS SiteName,
       l.lat AS Lat, l.lon AS Lon

// To calculate the number of sites exceeding a toxicity threshold for algae in the year 2011:
MATCH (l:Site)-[r:SUMMARIZED_IMPACT_ON]->(s:Species)
  WHERE r.sumTU > 0.001 AND r.year = 2011 AND s.name = 'algae'
RETURN count(l) AS n_sites_at_risk

// To find information about a certain substance by the substance's name
MATCH (s:Substance)
  WHERE s.Name = 'Diuron'
RETURN s.DTXSID AS DTXSID, s.Name AS ChemicalName,
       s.casrn AS CASrn, s.use_groups AS UseGroups,
       s.IN_REACH AS InREACH

// To find sites where a certain substance has been measured. Result is in descending order of the measured concentration.
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE s.Name = 'Diuron'
RETURN s.Name AS ChemicalName, s.DTXSID AS DTXSID,
       r.median_concentration AS Concentration, r.concentration_unit AS ConcentrationUnit, r.year AS Year,
       r.quarter AS Quarter,
       l.name AS SiteName, l.country AS Country, l.river_basin AS RiverBasin, l.water_body AS WaterBody
  ORDER BY r.median_concentration DESC

// To find sites where a certain substance has been measured with a concentration above a threshold. Result is in descending order of the measured concentration.
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE s.Name = 'Diuron' AND r.median_concentration > 0.001
RETURN s.Name AS ChemicalName, s.DTXSID AS DTXSID,
       r.median_concentration AS Concentration, r.concentration_unit AS ConcentrationUnit, r.year AS Year,
       r.quarter AS Quarter,
       l.name AS SiteName, l.country AS Country, l.river_basin AS RiverBasin, l.water_body AS WaterBody
  ORDER BY r.median_concentration DESC

// To find all chemicals measured in a certain river above a threshold:
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE l.water_body = 'seine' //AND r.median_concentration > 0.001
RETURN s.DTXSID AS DTXSID, s.Name AS ChemicalName,
       r.median_concentration AS Concentration, r.time_point AS Date,
       l.name AS Site
  ORDER BY r.median_concentration DESC

// To find all substances measured in France
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE l.country = 'France'
RETURN DISTINCT s.DTXSID AS DTXSID, s.Name  AS ChemicalName
  ORDER BY ChemicalName

// To find the most frequent driver chemicals above a driver importance of 0.6, provide the top 10 records
MATCH (s:Substance)-[r:IS_DRIVER]->(l:Site)
  WHERE r.driver_importance > 0.6
RETURN DISTINCT s.Name AS ChemicalName, count(r) AS frequency
  ORDER BY frequency DESC
  LIMIT 10

// To find the substances with highest driver importance, provide the first 10
MATCH (s:Substance)-[r:IS_DRIVER]->(l:Site)
  WHERE r.driver_importance > 0.8
RETURN DISTINCT s.Name AS ChemicalName, s.DTXSID, r.driver_importance
  ORDER BY r.driver_importance DESC
  LIMIT 10

// To find sites where a certain substance is driver
MATCH (s:Substance)-[r:IS_DRIVER]->(l:Site)
  WHERE s.Name = 'Diuron'
RETURN s.DTXSID AS DTXSID, s.Name AS ChemicalName,
       r.driver_importance AS DriverImportance,
       l.name AS SiteName, l.country AS Country, l.water_body AS WaterBody, l.river_basin AS RiverBasin
  ORDER BY r.driver_importance DESC

// To find the toxic impact of all substances measured in France for the species algae
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE l.country = 'France' AND r.TU_algae IS NOT NULL
RETURN DISTINCT s.DTXSID AS DTXSID, s.Name AS ChemicalName, r.TU_algae AS TU
  ORDER BY ChemicalName

// To find all locations at risk in a certain time span for fish
MATCH (l:Site)-[r:SUMMARIZED_IMPACT_ON]->(s:Species)
  WHERE r.sumTU > 0.001 AND s.name = "fish" AND r.year = 2014
RETURN l.name AS SiteName, l.country AS Country, l.water_body AS WaterBody, l.river_basin AS RiverBasin,
       s.Name AS SpeciesName,
       r.sumTU AS sumTU, r.year AS Year, r.quarter AS Quarter