CREATE CONSTRAINT `DTXSID_Substance_uniq` IF NOT EXISTS
FOR (n: `Substance`)
REQUIRE (n.`DTXSID`) IS UNIQUE;

CREATE CONSTRAINT `name_Species_uniq` IF NOT EXISTS
FOR (n: `Species`)
REQUIRE (n.`name`) IS UNIQUE;

CREATE CONSTRAINT `name_Site_uniq` IF NOT EXISTS
FOR (n: `Site`)
REQUIRE (n.`name`) IS UNIQUE;

CREATE CONSTRAINT `key_measured_at` IF NOT EXISTS
FOR ()-[r: MEASURED_AT]->()
REQUIRE (r.key) IS KEY;

CREATE CONSTRAINT `key_tested_for_toxicity_uniq` IF NOT EXISTS
FOR ()-[r: TESTED_FOR_TOXICITY]->()
REQUIRE (r.`key`) IS UNIQUE;

CREATE CONSTRAINT `key_summarized_impact_on_uniq` IF NOT EXISTS
FOR ()-[r: SUMMARIZED_IMPACT_ON]->()
REQUIRE (r.`key`) IS UNIQUE;

CREATE CONSTRAINT `key_is_driver_uniq` IF NOT EXISTS
FOR ()-[r: IS_DRIVER]->()
REQUIRE (r.`key`) IS UNIQUE;
