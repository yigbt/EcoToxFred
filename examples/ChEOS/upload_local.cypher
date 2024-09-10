// NODES

// Substance
LOAD CSV WITH HEADERS FROM 'file:///ETF_auradb_substance_nodes.csv'
AS nodeRecord
WITH nodeRecord
  WHERE nodeRecord.DTXSID IS NOT NULL
MERGE (n:Substance {DTXSID: nodeRecord.DTXSID})
SET n.casrn = toString(nodeRecord.casrn)
SET n.Name = toString(nodeRecord.Name)
SET n.inchi = toString(nodeRecord.inchi)
SET n.inchiKey = toString(nodeRecord.inchiKey)
SET n.IN_REACH = toBoolean(nodeRecord.IN_REACH)
SET n.use_groups = toString(nodeRecord.use_groups)
SET n.use_groups_N = toInteger(nodeRecord.use_groups_N);

// Site
LOAD CSV WITH HEADERS FROM 'file:///ETF_auradb_site_nodes.csv'
AS nodeRecord
WITH nodeRecord
  WHERE nodeRecord.station_name_n IS NOT NULL
MERGE (n:Site {name: nodeRecord.station_name_n})
SET n.lon = toFloat(nodeRecord.lon)
SET n.lat = toFloat(nodeRecord.lat)
SET n.country = toString(nodeRecord.country)
SET n.water_body = toString(nodeRecord.water_body_name_n)
SET n.river_basin = toString(nodeRecord.river_basin_name_n);


// Species
LOAD CSV WITH HEADERS FROM "file:///ETF_auradb_species_nodes.csv"
AS nodeRecord
WITH nodeRecord
  WHERE nodeRecord.species IS NOT NULL
MERGE (n:Species {name: nodeRecord.species})
SET n.classification = toString(nodeRecord.classification);


// RELATIONS
// IS_DRIVER relation
LOAD CSV WITH HEADERS FROM "file:///ETF_auradb_is_driver_relation.csv" AS relRecord
MATCH (source:Substance {DTXSID: relRecord.DTXSID})
MATCH (target:Site {name: relRecord.station_name_n})
CREATE (source)-[r:IS_DRIVER]->(target)
SET r.key = toInteger(relRecord.key)
SET r.species = toString(relRecord.species)
SET r.time_point = datetime(relRecord.time_point)
SET r.year = toInteger(relRecord.year)
SET r.quarter = toInteger(relRecord.quarter)
SET r.driver_importance = toFloat(relRecord.driver_importance)
RETURN *

// MEASURED_AT relation
LOAD CSV WITH HEADERS FROM 'file:///ETF_auradb_measured_at_relation.csv' AS relRecord
MATCH (source:Substance {DTXSID: relRecord.DTXSID})
MATCH (target:Site {name: relRecord.station_name_n})
CREATE (source)-[r:MEASURED_AT]->(target)
SET r.key = toInteger(relRecord.key)
SET r.median_concentration = toFloat(relRecord.median_concentration)
SET r.mean_concentration = toFloat(relRecord.mean_concentration)
SET r.concentration_unit = toString(relRecord.concentration_unit)
SET r.time_point = datetime(relRecord.time_point)
SET r.year = toInteger(relRecord.year)
SET r.quarter = toInteger(relRecord.quarter)
SET r.TU_crustacean = toFloat(relRecord.TU_crustacean)
SET r.TU_fish = toFloat(relRecord.TU_fish)
SET r.TU_algae = toFloat(relRecord.TU_algae)
RETURN *


// TESTED_FOR_TOXICITY relation
LOAD CSV WITH HEADERS FROM 'file:///ETF_auradb_tested_for_toxicity_relation.csv' AS relRecord
MATCH (source:Substance {DTXSID: relRecord.DTXSID})
MATCH (target:Species {name: relRecord.species})
CREATE (source)-[r:TESTED_FOR_TOXICITY]->(target)
SET r.key = toInteger(relRecord.key)
SET r.tox_value_mg_L = toFloat(relRecord.tox_value_mg_L)
SET r.neutral_fraction_jchem = toFloat(relRecord.neutral_fraction_jchem)
RETURN *

// SUMMARIZED_IMPACT_ON relation
LOAD CSV WITH HEADERS FROM 'file:///ETF_auradb_summarized_impact_on_relation.csv' AS relRecord
MATCH (source:Site {name: relRecord.station_name_n})
MATCH (target:Species {name: relRecord.species})
CREATE (source)-[r:SUMMARIZED_IMPACT_ON]->(target)
SET r.key = toInteger(relRecord.key)
SET r.time_point = datetime(relRecord.time_point)
SET r.year = toInteger(relRecord.year)
SET r.quarter = toInteger(relRecord.quarter)
SET r.sumTU = toFloat(relRecord.sumTU)
SET r.maxTU = toFloat(relRecord.maxTU)
SET r.ratioTU = toFloat(relRecord.ratioTU)
RETURN *


