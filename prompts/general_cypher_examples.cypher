// 0. To find information about a certain substance
MATCH (s:Substance)
WHERE s.name = 'Diuron'
return s.DTXSID as DTXSID, s.name as Name

// 1. To find sites where a certain substance has been measured
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
WHERE s.name='Diuron'
RETURN s.name as ChemicalName, s.DTXSID as DTXSID, r.concentration_value as Concentration,
r.concentration_unit as ConcentrationUnit, r.year as Year, r.quarter as Quarter, l.name as SiteName,
l.country as Country, l.river_basin as RiverBasin, l.water_body as WaterBody

// 2. To find sites where a certain substance has been measured with a mean concentration above a threshold:
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
WHERE s.name='Diuron' AND r.mean_concentration > 0.001
RETURN s.name as ChemicalName, s.DTXSID as DTXSID, r.concentration_value as Concentration,
r.concentration_unit as ConcentrationUnit, r.year as Year, r.quarter as Quarter, l.name as SiteName,
l.country as Country, l.river_basin as RiverBasin, l.water_body as WaterBody

// 3. To find all chemicals measured in a certain river:
MATCH (c:Substance)-[r:MEASURED_AT]->(s:Site)
WHERE s.water_body = 'seine' AND r.mean_concentration > 0.001
RETURN c.DTXSID AS DTXSID, c.name AS Name

// 4. To find all substances measured in France
MATCH (c:Substance)-[r:MEASURED_AT]->(s:Site)
WHERE s.country = 'France'
RETURN DISTINCT c.DTXSID AS DTXSID, c.name AS Name

// 5. To find the 10 most frequent driver chemicals above a driver importance of 0.6
MATCH (s:Substance)-[r:IS_DRIVER]->(l:Site)
WHERE r.driver_importance > 0.6
RETURN s.name AS substance, COUNT(r) AS frequency
ORDER BY frequency DESC
LIMIT 10

// 6. To find the substances with highest driver importance, provide the first 10
MATCH (s:Substance)-[r:IS_DRIVER]->(l:Site)
WHERE r.driver_importance>0.8
RETURN DISTINCT s.name, s.DTXSID, r.driver_importance
ORDER BY r.driver_importance
LIMIT 10
