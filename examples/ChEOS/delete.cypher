// delete everything
MATCH (n)
DETACH DELETE n;

// delete all relations
MATCH p = ()-[r]->()
DETACH DELETE r;

// delete all relations, and the participating nodes!
MATCH p = ()-[r]->()
DETACH DELETE p;

// execute in browser neo4j interface
DROP CONSTRAINT DTXSID_Substance_uniq;
DROP CONSTRAINT name_Species_uniq;
DROP CONSTRAINT name_Site_uniq;
DROP CONSTRAINT key_measured_at_uniq;
DROP CONSTRAINT key_tested_for_toxicity_uniq;
DROP CONSTRAINT key_summarized_impact_on_uniq;
DROP CONSTRAINT key_is_driver_uniq;
