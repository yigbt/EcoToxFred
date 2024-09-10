// where is Diuron a driver with high driver importance
MATCH (s:Substance)-[r:IS_DRIVER]->(l:Site)
  WHERE s.Name = 'Diuron' AND r.driver_importance > 0.8
RETURN s.DTXSID AS DTXSID, s.Name AS ChemicalName,
       r.driver_importance AS DriverImportance,
       l.name AS SiteName, l.country AS Country, l.water_body AS WaterBody, l.river_basin AS RiverBasin
  ORDER BY r.driver_importance DESC

// find all substances measured above a threshold in a certain river
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE l.water_body = 'danube' AND r.median_concentration > 0.001
RETURN s.DTXSID AS DTXSID, s.Name AS ChemicalName,
       r.median_concentration AS Concentration, r.time_point AS Date,
       l.name AS Site
  ORDER BY r.median_concentration DESC

// find top 10 most frequent drivers
MATCH (s:Substance)-[r:IS_DRIVER]->(l:Site)
  WHERE r.driver_importance > 0.8
RETURN DISTINCT s.Name AS ChemicalName, count(r) AS frequency
  ORDER BY frequency DESC
  LIMIT 10
