// To show the (median) measured concentrations of a certain substance
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE s.name = 'Diuron'
RETURN s.name AS ChemicalName, // plot title
       r.median_concentration AS Concentration, // y-axis
       l.name AS SiteName, // x-axis
       r.time_point AS DateTime, r.year AS Year, r.quarter AS Quarter  // x-asis
  ORDER BY r.median_concentration DESC

// To show the (mean) measured concentrations of a certain substance at a certain range of time
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE s.name = 'Diuron' AND r.year >= 2010 AND r.year <= 2020
RETURN s.name AS ChemicalName, // plot title
       r.mean_concentration AS Concentration, // y-axis
       l.name AS SiteName, // x-axis
       r.time_point AS DateTime, r.year AS Year, r.quarter AS Quarter  // x-asis
  ORDER BY r.median_concentration DESC

// To show the driver_importance distribution of a certain substance
MATCH (s:Substance)-[r:IS_DRIVER]->(l:Site)
  WHERE s.name = 'Diuron'
RETURN s.name AS ChemicalName, // plot title
       r.driver_importance AS DriverImportance, // y-axis
       r.species AS Species, // add to point hover, or as facet variable
       l.name AS SiteName, // x-axis
       r.time_point AS DateTime, r.year AS Year, r.quarter AS Quarter  // x-asis
  ORDER BY r.driver_importance DESC

// To show the driver_importance distribution of a certain substance at a certain time
MATCH (s:Substance)-[r:IS_DRIVER]->(l:Site)
  WHERE s.name = 'Diuron' AND r.year >= 2010
RETURN s.name AS ChemicalName, // plot title
       r.driver_importance AS DriverImportance, // y-axis
       r.species AS Species, // add to point hover, or as facet variable
       l.name AS SiteName, // x-axis
       r.time_point AS DateTime, r.year AS Year, r.quarter AS Quarter  // x-asis
  ORDER BY r.driver_importance DESC

// To show the distribution of the toxic unit (TU) of a certain substance at a certain time for the species algae (unicellular)
MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
  WHERE s.name = 'Diuron' AND r.year >= 2010
RETURN s.name AS ChemicalName, // plot title
       r.TU_algae AS TU, // y-axis
       l.name AS SiteName, // x-axis
       r.time_point AS DateTime, r.year AS Year, r.quarter AS Quarter // x-asis
  ORDER BY r.TU_algae DESC

// To show the distribution of the summarized toxic unit (sumTU) at a certain time for a certain species
MATCH (l:Site)-[r:SUMMARIZED_IMPACT_ON]->(s:Species)
  WHERE s.name = 'algae' AND r.year >= 2010
RETURN s.name AS SpeciesName, // plot title
       r.sumTU AS sumTU, // y-axis
       l.name AS SiteName, // x-axis
       r.time_point AS DateTime, r.year AS Year, r.quarter AS Quarter // x-asis
  ORDER BY r.sumTU DESC

// To show the distribution of the summarized toxic unit (ratioTU) of a certain site at a certain time for the species algae (unicellular)
MATCH (l:Site)-[r:SUMMARIZED_IMPACT_ON]->(s:Species)
  WHERE r.year >= 2010 AND s.name = 'algae'
RETURN s.name AS SpeciesName, // plot title
       r.ratioTU AS ratioTU, // y-axis
       l.name AS SiteName, // x-axis
       r.time_point AS DateTime, r.year AS Year, r.quarter AS Quarter // x-asis
  ORDER BY r.sumTU DESC

// To show the distribution of the summarized toxic unit (maxTU) of a certain site at a certain time for the species algae (unicellular)
MATCH (l:Site)-[r:SUMMARIZED_IMPACT_ON]->(s:Species)
  WHERE r.year >= 2010 AND s.name = 'algae'
RETURN s.name AS SpeciesName, // plot title
       r.maxTU AS maxTU, // y-axis
       l.name AS SiteName, // x-axis
       r.time_point AS DateTime, r.year AS Year, r.quarter AS Quarter // x-asis
  ORDER BY r.sumTU DESC
