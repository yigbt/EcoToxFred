SELECT Norman_record_ID,
       Norman_SusDat_ID,
       Substance_name,
       national_code,
       river_km,
       station_name_n,
       lat,
       lon,
       country,
       water_body_name_n,
       river_basin_name_n,
       concentration_value,
       concentration_unit,
       time_point
from exposure_data e
WHERE e.EUROPE like 'TRUE'
  AND e.AGGREGATED like 'FALSE'
  AND e.COORDS like 'TRUE'
  AND e.MARINE like 'FALSE'
-- LIMIT 1000000