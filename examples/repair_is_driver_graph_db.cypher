// Delete the old (wrongly created) relations
MATCH ()-[r:IS_DRIVER]->()
DELETE r
MATCH ()-[r:JOINT_DRIVER_WITH]->()
DELETE r

// Add the correct ones:
// ALGAE
// Step 1: Match the relationships and collect the required data
MATCH (site:Site)-[summarized:SUMMARIZED_IMPACT_ON]->(species:Species) 
WHERE species.name = 'algae' AND summarized.sumTU IS NOT NULL
MATCH (substance:Substance)-[measured:MEASURED_AT]->(site) 
WHERE summarized.time_point = measured.time_point AND measured.TU_algae IS NOT NULL
WITH site, summarized, substance, measured.year AS year, measured.quarter AS quarter, measured.TU_algae AS TU, summarized.sumTU AS sumTU, summarized.time_point AS time_point
ORDER BY site, time_point, TU DESC
// Step 2: Calculate cumulative TU and identify driver substances
WITH site, summarized, sumTU, time_point, year, quarter, collect({substance: substance, TU: TU}) AS TU_data
WITH site, summarized, sumTU, time_point, year, quarter, TU_data, [x IN TU_data | x.TU] AS tu_list
UNWIND range(0, size(TU_data) - 1) AS idx
WITH site, summarized, sumTU, time_point, year, quarter, TU_data, idx,
     reduce(s = 0.0, i IN range(0, idx) | s + tu_list[i]) AS cumulativeTU
WHERE cumulativeTU <= 0.75 * sumTU
WITH site, time_point, year, quarter, sumTU, TU_data[idx] AS entry
// Step 3: Create/Update IS_DRIVER2 relationships for driver substances
MATCH (substance:Substance) WHERE substance.DTXSID = entry.substance.DTXSID
MATCH (site_node:Site) WHERE site_node.name = site.name
MERGE (substance)-[driver:IS_DRIVER {time_point: time_point, year: year, quarter: quarter, species: 'algae'}]->(site_node)
SET driver.driver_importance = entry.TU / sumTU

// FISH
// Step 1: Match the relationships and collect the required data
MATCH (site:Site)-[summarized:SUMMARIZED_IMPACT_ON]->(species:Species)
WHERE species.name = 'fish' AND summarized.sumTU IS NOT NULL
MATCH (substance:Substance)-[measured:MEASURED_AT]->(site)
WHERE summarized.time_point = measured.time_point AND measured.TU_fish IS NOT NULL
WITH site, summarized, substance, measured.year AS year, measured.quarter AS quarter, measured.TU_fish AS TU, summarized.sumTU AS sumTU, summarized.time_point AS time_point
ORDER BY site, time_point, TU DESC
// Step 2: Calculate cumulative TU and identify driver substances
WITH site, summarized, sumTU, time_point, year, quarter, collect({substance: substance, TU: TU}) AS TU_data
WITH site, summarized, sumTU, time_point, year, quarter, TU_data, [x IN TU_data | x.TU] AS tu_list
UNWIND range(0, size(TU_data) - 1) AS idx
WITH site, summarized, sumTU, time_point, year, quarter, TU_data, idx,
     reduce(s = 0.0, i IN range(0, idx) | s + tu_list[i]) AS cumulativeTU
WHERE cumulativeTU <= 0.75 * sumTU
WITH site, time_point, year, quarter, sumTU, TU_data[idx] AS entry
// Step 3: Create/Update IS_DRIVER2 relationships for driver substances
MATCH (substance:Substance) WHERE substance.DTXSID = entry.substance.DTXSID
MATCH (site_node:Site) WHERE site_node.name = site.name
MERGE (substance)-[driver:IS_DRIVER {time_point: time_point, year: year, quarter: quarter, species: 'fish'}]->(site_node)
SET driver.driver_importance = entry.TU / sumTU

// CRUSTACEAN
// Step 1: Match the relationships and collect the required data
MATCH (site:Site)-[summarized:SUMMARIZED_IMPACT_ON]->(species:Species)
WHERE species.name = 'crustacean' AND summarized.sumTU IS NOT NULL
MATCH (substance:Substance)-[measured:MEASURED_AT]->(site)
WHERE summarized.time_point = measured.time_point AND measured.TU_crustacean IS NOT NULL
WITH site, summarized, substance, measured.year AS year, measured.quarter AS quarter, measured.TU_crustacean AS TU, summarized.sumTU AS sumTU, summarized.time_point AS time_point
ORDER BY site, time_point, TU DESC
// Step 2: Calculate cumulative TU and identify driver substances
WITH site, summarized, sumTU, time_point, year, quarter, collect({substance: substance, TU: TU}) AS TU_data
WITH site, summarized, sumTU, time_point, year, quarter, TU_data, [x IN TU_data | x.TU] AS tu_list
UNWIND range(0, size(TU_data) - 1) AS idx
WITH site, summarized, sumTU, time_point, year, quarter, TU_data, idx,
     reduce(s = 0.0, i IN range(0, idx) | s + tu_list[i]) AS cumulativeTU
WHERE cumulativeTU <= 0.75 * sumTU
WITH site, time_point, year, quarter, sumTU, TU_data[idx] AS entry
// Step 3: Create/Update IS_DRIVER2 relationships for driver substances
MATCH (substance:Substance) WHERE substance.DTXSID = entry.substance.DTXSID
MATCH (site_node:Site) WHERE site_node.name = site.name
MERGE (substance)-[driver:IS_DRIVER {time_point: time_point, year: year, quarter: quarter, species: 'crustacean'}]->(site_node)
SET driver.driver_importance = entry.TU / sumTU
