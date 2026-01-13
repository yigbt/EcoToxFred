import pytest

from prompts import CypherExampleCollections
from typing import List
from utils import connect_to_neo4j_for_test


@pytest.fixture(scope="session")
def database_connection():
    try:
        db = connect_to_neo4j_for_test()
        assert db is not None
        yield db
    except:
        assert False, "No database connection could be established"


# For now, simply combining all available Cypher examples and running all of them.
cypher_examples: List[dict] = (CypherExampleCollections.general_cypher_queries.examples +
                               CypherExampleCollections.map_cypher_queries.examples)


@pytest.mark.parametrize("example", cypher_examples, ids=[e["information"][:40] for e in cypher_examples])
def test_cypher_query(database_connection, example):
    try:
        assert "cypher" in example.keys()
        database_connection.query(example["cypher"])
    except ValueError as e:
        assert False, f"Invalid cypher query: {e}"


def test_example_for_vizualization(database_connection):
    cypher_example = """
        MATCH (l:Site)-[r:SUMMARIZED_IMPACT_ON]->(s:Species)
        WHERE s.name = 'algae' AND r.year >= 2010
        RETURN s.name AS SpeciesName, // plot title
        r.sumTU AS sumTU, // >=0, continuous point color from yellow to red, with midpoint orange at 0.001
        r.year AS Year, r.quarter AS Quarter, // add to point hover
        l.name AS SiteName, // point hover
        l.water_body AS WaterBody, l.river_basin AS RiverBasin, // point hover
        l.lat AS Lat, l.lon AS Lon // x,y coordinates
        ORDER BY r.sumTU DESC
    """
    try:
        import pandas as pd
        from tools.plotly_visualization import create_plotly_map
        result = database_connection.query(cypher_example)
        df = pd.DataFrame(result)
        fig = create_plotly_map(df)
        print(fig)
    except ValueError as e:
        assert False, f"Invalid cypher query: {e}"


def test_integrity(database_connection):
    """
    Test database integrity by fetching comprehensive statistics about nodes, relationships, and data properties.
    This function prints detailed information that can later be used for assertions.
    """

    integrity_queries = {
        # Node counts
        "total_substances": """
            MATCH (s:Substance)
            RETURN count(s) as count
        """,
        "total_sites": """
            MATCH (l:Site)
            RETURN count(l) as count
        """,
        "total_species": """
            MATCH (sp:Species)
            RETURN count(sp) as count, collect(DISTINCT sp.name) as species_names
        """,
        # Relationship counts
        "total_measurements": """
            MATCH ()-[r:MEASURED_AT]->()
            RETURN count(r) as count
        """,
        "total_toxicity_tests": """
            MATCH ()-[r:TESTED_FOR_TOXICITY]->()
            RETURN count(r) as count
        """,
        "total_drivers": """
            MATCH ()-[r:IS_DRIVER]->()
            WHERE r.is_driver = true
            RETURN count(r) as count
        """,
        "total_summarized_impacts": """
            MATCH ()-[r:SUMMARIZED_IMPACT_ON]->()
            RETURN count(r) as count
        """,
        # Data quality checks
        "substances_with_reach": """
            MATCH (s:Substance)
            WHERE s.IN_REACH = true
            RETURN count(s) as count
        """,
        "substances_with_use_groups": """
            MATCH (s:Substance)
            WHERE s.use_groups IS NOT NULL
            RETURN count(s) as count, avg(s.use_groups_N) as avg_use_groups
        """,
        "measurement_year_range": """
            MATCH ()-[r:MEASURED_AT]->()
            RETURN min(r.year) as min_year, max(r.year) as max_year, 
                   count(DISTINCT r.year) as distinct_years
        """,
        "countries_covered": """
            MATCH (l:Site)
            WHERE l.country IS NOT NULL
            RETURN count(DISTINCT l.country) as count_countries,
                   collect(DISTINCT l.country)[0..10] as sample_countries
        """,
        "detected_substances": """
            MATCH (s:Substance)-[r:MEASURED_AT]->()
            WHERE r.median_concentration > 0
            RETURN count(DISTINCT s) as substances_with_detections
        """,
        "toxic_sites_per_species": """
            MATCH (l:Site)-[r:SUMMARIZED_IMPACT_ON]->(sp:Species)
            WHERE r.sumTU > 0.001
            RETURN sp.name as species, count(DISTINCT l) as toxic_sites
            ORDER BY species
        """,
        "max_concentrations": """
            MATCH ()-[r:MEASURED_AT]->()
            WHERE r.median_concentration IS NOT NULL
            RETURN max(r.median_concentration) as max_concentration,
                   avg(r.median_concentration) as avg_concentration,
                   count(CASE WHEN r.median_concentration > 0 THEN 1 END) as detections
        """,
        "driver_importance_stats": """
            MATCH ()-[r:IS_DRIVER]->()
            WHERE r.is_driver = true
            RETURN min(r.driver_importance) as min_importance,
                   max(r.driver_importance) as max_importance,
                   avg(r.driver_importance) as avg_importance
        """,
        "sites_with_coordinates": """
            MATCH (l:Site)
            WHERE l.lat IS NOT NULL AND l.lon IS NOT NULL
            RETURN count(l) as sites_with_coords,
                   min(l.lat) as min_lat, max(l.lat) as max_lat,
                   min(l.lon) as min_lon, max(l.lon) as max_lon
        """,
        "water_body_types": """
            MATCH (l:Site)
            WHERE l.water_body IS NOT NULL
            RETURN count(DISTINCT l.water_body) as distinct_water_bodies,
                   count(DISTINCT l.river_basin) as distinct_river_basins
        """,
        "toxicity_unit_ranges": """
            MATCH ()-[r:MEASURED_AT]->()
            WHERE r.TU_algae IS NOT NULL OR r.TU_crustacean IS NOT NULL OR r.TU_fish IS NOT NULL
            RETURN 
                count(CASE WHEN r.TU_algae > 1 THEN 1 END) as toxic_algae,
                count(CASE WHEN r.TU_crustacean > 1 THEN 1 END) as toxic_crustacean,
                count(CASE WHEN r.TU_fish > 1 THEN 1 END) as toxic_fish,
                count(CASE WHEN r.TU_algae > 0.001 THEN 1 END) as chronic_algae,
                count(CASE WHEN r.TU_crustacean > 0.001 THEN 1 END) as chronic_crustacean,
                count(CASE WHEN r.TU_fish > 0.001 THEN 1 END) as chronic_fish
        """,
        "quarterly_data_distribution": """
            MATCH ()-[r:MEASURED_AT]->()
            WHERE r.quarter IS NOT NULL
            RETURN r.quarter as quarter, count(r) as measurements
            ORDER BY quarter
        """,
        "top_measured_substances": """
            MATCH (s:Substance)-[r:MEASURED_AT]->()
            WHERE r.median_concentration > 0
            RETURN s.name as substance, count(r) as measurement_count
            ORDER BY measurement_count DESC
            LIMIT 5
        """,
    }

    print("\n" + "=" * 80)
    print("DATABASE INTEGRITY CHECK RESULTS")
    print("=" * 80)

    for query_name, cypher_query in integrity_queries.items():
        try:
            result = database_connection.query(cypher_query)
            print(f"\n{query_name.upper().replace('_', ' ')}:")
            print("-" * 40)

            if result:
                # Pretty print the results
                if len(result) == 1:
                    # Single row result
                    for key, value in result[0].items():
                        if isinstance(value, list) and len(value) > 10:
                            # Truncate long lists
                            print(
                                f"  {key}: {value[:10]} ... (and {len(value) - 10} more)"
                            )
                        else:
                            print(f"  {key}: {value}")
                else:
                    # Multiple row result
                    import pandas as pd

                    df = pd.DataFrame(result)
                    print(df.to_string(index=False))
            else:
                print("  No results")

        except Exception as e:
            print(f"\n{query_name.upper().replace('_', ' ')}:")
            print(f"  ERROR: {str(e)}")

    print("\n" + "=" * 80)
    print("END OF INTEGRITY CHECK")
    print("=" * 80 + "\n")

    # Return True for now - later we'll add assertions
    return True
