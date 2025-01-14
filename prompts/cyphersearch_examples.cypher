// Retrieve the sampling sites and time points where Fentanyl was measured:
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE s.Name = 'Fentanyl'
RETURN s.Name AS ChemicalName,
       l.name AS SiteName,
       l.country AS Country,
       l.water_body AS WaterBody,
       l.river_basin AS RiverBasin,
       date(r.time_point) AS MeasurementTime

// Retrieve sites where "Atrazine" was measured in the second half of the year 2011:
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE s.Name = 'Atrazine' AND r.year = 2011 AND 3 <= r.quarter <= 4
RETURN s.Name AS ChemicalName,
       l.name AS SiteName,
       l.lat AS Lat, l.lon AS Lon

// Calculate the number of sites exceeding a toxicity threshold for algae in the year 2011:
MATCH (l:Site)-[r:SUMMARIZED_IMPACT_ON]->(s:Species)
  WHERE r.sumTU > 0.001 AND r.year = 2011 AND s.name = 'algae'
RETURN count(l) AS n_sites_at_risk

// Find information about a certain substance by the substance's name
MATCH (s:Substance)
  WHERE s.Name = 'Diuron'
RETURN s.DTXSID AS DTXSID, s.Name AS ChemicalName,
       s.casrn AS CASrn, s.use_groups AS UseGroups,
       s.IN_REACH AS InREACH

// Find sites where a certain substance has been detected. Result is in descending order of the measured concentration.
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE s.Name = 'Diuron' AND r.median_concentration > 0
RETURN s.Name AS ChemicalName, s.DTXSID AS DTXSID,
       r.median_concentration AS Concentration, r.concentration_unit AS ConcentrationUnit, r.year AS Year,
       r.quarter AS Quarter,
       l.name AS SiteName, l.country AS Country, l.river_basin AS RiverBasin, l.water_body AS WaterBody
  ORDER BY r.median_concentration DESC

// Find sites where a certain substance has been detected with a concentration above a threshold. Result is in descending order of the measured concentration.
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE s.Name = 'Diuron' AND r.median_concentration > 0.001
RETURN s.Name AS ChemicalName, s.DTXSID AS DTXSID,
       r.median_concentration AS Concentration, r.concentration_unit AS ConcentrationUnit, r.year AS Year,
       r.quarter AS Quarter,
       l.name AS SiteName, l.country AS Country, l.river_basin AS RiverBasin, l.water_body AS WaterBody
  ORDER BY r.median_concentration DESC

// Find all chemicals detected in a certain river above a threshold:
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE l.water_body = 'seine' AND r.median_concentration > 0
RETURN s.DTXSID AS DTXSID, s.Name AS ChemicalName,
       r.median_concentration AS Concentration, r.time_point AS Date,
       l.name AS Site
  ORDER BY r.median_concentration DESC

// Find all substances measured in France
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE l.country = 'France'
RETURN DISTINCT s.DTXSID AS DTXSID, s.Name  AS ChemicalName
  ORDER BY ChemicalName

// Find the most frequent multiple risk drivers
MATCH (s:Substance)-[r:IS_DRIVER]->(l:Site)
  WHERE r.is_driver = true AND r.driver_importance < 1
RETURN DISTINCT s.Name AS ChemicalName, count(r) AS frequency
  ORDER BY frequency DESC

// Find the substances with highest driver importance, provide the first 10
MATCH (s:Substance)-[r:IS_DRIVER]->(l:Site)
  WHERE r.driver_importance > 0.8
RETURN DISTINCT s.Name AS ChemicalName, s.DTXSID, r.driver_importance
  ORDER BY r.driver_importance DESC

// Find sites where a certain substance is driver
MATCH (s:Substance)-[r:IS_DRIVER]->(l:Site)
  WHERE s.Name = 'Diuron'
RETURN s.DTXSID AS DTXSID, s.Name AS ChemicalName,
       r.driver_importance AS DriverImportance,
       l.name AS SiteName, l.country AS Country, l.water_body AS WaterBody, l.river_basin AS RiverBasin
  ORDER BY r.driver_importance DESC

// Find the toxic impact of all substances detected in France for the species algae
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE l.country = 'France' AND r.median_concentration > 0 AND r.TU_algae IS NOT NULL
RETURN DISTINCT s.DTXSID AS DTXSID, s.Name AS ChemicalName, r.TU_algae AS TU
  ORDER BY ChemicalName

// Find all locations at risk in a certain time span for fish
MATCH (l:Site)-[r:SUMMARIZED_IMPACT_ON]->(s:Species)
  WHERE r.sumTU > 0.001 AND s.name = 'fish' AND r.year = 2014
RETURN l.name AS SiteName, l.country AS Country, l.water_body AS WaterBody, l.river_basin AS RiverBasin,
       s.Name AS SpeciesName,
       r.sumTU AS sumTU, r.year AS Year, r.quarter AS Quarter

// Find pairs of substances that were detected together most often
MATCH (s1:Substance)-[r1:MEASURED_AT]->(l:Site)<-[r2:MEASURED_AT]-(s2:Substance)
  WHERE s1 <> s2 AND s1.Name < s2.Name AND r1.median_concentration > 0 AND r2.median_concentration > 0
RETURN s1.Name AS Compound1, s2.Name AS Compound2, count(l) AS Frequency
  ORDER BY Frequency DESC

// Find pairs of drivers that were detected together most often at same site and same time point
MATCH p = (s1:Substance)-[r:JOINT_DRIVER_WITH]->(s2:Substance)
RETURN s1.Name AS Substance1, s2.Name AS Substance2, r.frequency AS Frequency
  ORDER BY Frequency DESC





