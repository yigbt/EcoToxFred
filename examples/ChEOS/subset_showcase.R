library("tidyverse")
library("dplyr")

load_data <- function(files) {
  data <- lapply(files, read_csv)
  names(data) <- gsub(pattern = ".csv", replacement = "", basename(files))
  return(data)
}

filter_exposure_data <- function(data, limit = NULL) {
  if (is.null(limit)) { limit <- data %>% nrow() }
  data %>%
    filter( #species == "algae",
      tox_stat == "supplemented",
      median_concentration > 0) %>% # keep detected substances measurements only
    arrange(desc(TU)) %>%
    head(limit)
}

filter_locations_data <- function(data) {
  data %>%
    filter( #species == "algae",
      tox_stat == "supplemented") %>%
    select(station_name_n:time_point, species, sumTU, maxTU, ratioTU) %>%
    arrange(desc(sumTU))

}

filter_hazard_data <- function(data) {
  data %>%
    filter( #species == "algae",
      tox_stat == "supplemented") %>%
    select(DTXSID, species, tox_value_mg_L, neutral_fraction_jchem) %>%
    arrange(desc(tox_value_mg_L))
}

filter_drivers_data <- function(data) {
  data %>%
    filter( #species == "algae",
      tox_stat == "supplemented") %>%
    select(DTXSID, station_name_n, species, time_point, year, quarter, driver_importance) %>%
    arrange(desc(driver_importance))
}

main <- function() {
  log_file <- file("examples/ChEOS/subset_showcase_big.log", open = "a")

  files <- list.files(path = "/data/cheos/cheos_mix/Quarters/CleanGeoStreamR/rdata", pattern = ".rda", full.names = TRUE)
  # files <- files[grep(pattern = 'neo4j_', files)]

  for (file_name in (files)) { load(file_name) }

  sink(log_file)
  print("01 Loaded files:")
  sink()

  sink(log_file)
  files
  sink()

  sink(log_file)
  print("02 # of entries:")
  print(paste("Chemicals #:", chemical_data %>% nrow()))
  print(paste("Hazard #:", hazard_data %>% nrow()))
  print(paste("Exposure #:", exposure_TU_data %>% nrow()))
  print(paste("Locations #:", location_tox_data %>% nrow()))
  print(paste("Drivers #:", drivers_per_location %>% nrow()))
  sink()

  exposure <- exposure_TU_data %>% filter_exposure_data()
  exposure_sites <- exposure$station_name_n %>% unique()
  exposure_substances <- exposure$DTXSID %>% unique()

  sites <- location_tox_data %>%
    filter_locations_data() %>%
    filter(station_name_n %in% exposure_sites) %>%
    select(station_name_n, lon, lat, country, water_body_name_n, river_basin_name_n) %>%
    unique()

  substances <- chemical_data %>%
    filter(DTXSID %in% exposure_substances)

  hazard <- hazard_data %>%
    filter_hazard_data() %>%
    filter(DTXSID %in% exposure_substances)

  drivers <- drivers_per_location %>%
    filter_drivers_data() %>%
    filter(DTXSID %in% exposure_substances, station_name_n %in% exposure_sites)

  sink(log_file)
  print("03 # of filtered entries:")
  print(paste("Chemicals #:", substances %>% nrow()))
  print(paste("Hazard #:", hazard %>% nrow()))
  print(paste("Exposure #:", exposure %>% nrow()))
  print(paste("Locations #:", sites %>% nrow()))
  print(paste("Drivers #:", drivers %>% nrow()))
  sink()


  sink(log_file)
  print("04 # of nodes:")
  print(paste("Site #:", site_nodes %>% nrow()))
  print(paste("Substance #:", substance_nodes %>% nrow()))
  print(paste("Species #:", species_nodes %>% nrow()))
  print(paste("Total #:", (site_nodes %>% nrow()) +
    (substance_nodes %>% nrow()) +
    (species_nodes %>% nrow())))
  sink()

  # relations
  # MEASURED_AT : substance-site
  measured_at_limit <- 70000
  measured_at <- exposure %>%
    # head(10000) %>%
    select(DTXSID, station_name_n, median_concentration, mean_concentration, concentration_unit,
           time_point, year, quarter, species, TU) %>%
    pivot_wider(names_from = species, values_from = TU, values_fill = NA) %>%
    rename("TU_algae" = "algae", "TU_fish" = "fish", "TU_crustacean" = "crustacean") %>%
    unique() %>%
    mutate("TU_aggregated" = TU_crustacean + TU_fish + TU_algae) %>%
    arrange(desc(TU_aggregated))
  measured_at <- measured_at %>%
    head(measured_at_limit) %>%
    select(-TU_aggregated) %>%
    rowid_to_column("key")
  relevant_sites <- measured_at$station_name_n %>% unique()
  relevant_substances <- measured_at$DTXSID %>% unique()
  measured_at_n <- measured_at %>% nrow()

  # TESTED_FOR_TOXICITY : substance-species
  tested_for_toxicity <- hazard %>%
    filter(DTXSID %in% relevant_substances) %>%
    unique() %>%
    rowid_to_column("key")
  tested_for_toxicity_n <- tested_for_toxicity %>% nrow()

  # SUMMARIZED_IMPACT_ON
  summarized_impact_on <- location_tox_data %>%
    filter_locations_data() %>%
    filter(station_name_n %in% relevant_sites) %>%
    select(station_name_n, species, time_point, year, quarter, sumTU, ratioTU, maxTU) %>%
    unique() %>%
    rowid_to_column("key")
  summarized_impact_on_n <- summarized_impact_on %>% nrow()

  # IS_DRIVER
  driver_dtxsids <- drivers %>%
    filter(DTXSID %in% relevant_substances) %>%
    pull(DTXSID) %>%
    unique()
  is_driver <- do.call(rbind,
                       lapply(driver_dtxsids, function(d) {
                         # d <- driver_dtxsids[100]
                         drivers %>%
                           filter(DTXSID == d) %>%
                           filter(station_name_n %in% relevant_sites) #%>% nrow()
                       })) %>%
    filter(driver_importance > 0.5) %>%
    rowid_to_column("key")
  is_driver_n <- is_driver %>% nrow()

  relations_n <- sum(is_driver_n, measured_at_n, summarized_impact_on_n, tested_for_toxicity_n)

  # nodes
  species_nodes <- exposure %>%
    select(species) %>%
    unique() %>%
    mutate("classification" = ifelse(species == "algae", yes = "unicellular",
                                     no = ifelse(species == "crustacean", yes = "invertebrate",
                                                 no = ifelse(species == "fish", yes = "vertebrate", no = "unknown"))))
  site_nodes <- sites %>%
    select(station_name_n, lon, lat, country, water_body_name_n, river_basin_name_n) %>%
    unique() %>%
    filter(station_name_n %in% relevant_sites)
  substance_nodes <- substances %>%
    select(DTXSID, casrn, Name, inchi, inchiKey, IN_REACH, use_groups, use_groups_N) %>%
    unique() %>%
    filter(DTXSID %in% relevant_substances)

  nodes_n <- sum(nrow(species_nodes), nrow(substance_nodes), nrow(site_nodes))

  # save nodes to .csv
  write_csv(site_nodes, file = "/data/cheos/cheos_mix/Quarters/NORMAN_2024/output/ETF_auradb_site_nodes.csv")
  write_csv(substance_nodes, file = "/data/cheos/cheos_mix/Quarters/NORMAN_2024/output/ETF_auradb_substance_nodes.csv")
  write_csv(species_nodes, file = "/data/cheos/cheos_mix/Quarters/NORMAN_2024/output/ETF_auradb_species_nodes.csv")
  # save relations to .csv
  write_csv(measured_at, file = "/data/cheos/cheos_mix/Quarters/NORMAN_2024/output/ETF_auradb_measured_at_relation.csv")
  write_csv(tested_for_toxicity, file = "/data/cheos/cheos_mix/Quarters/NORMAN_2024/output/ETF_auradb_tested_for_toxicity_relation.csv")
  write_csv(is_driver, file = "/data/cheos/cheos_mix/Quarters/NORMAN_2024/output/ETF_auradb_is_driver_relation.csv")
  write_csv(summarized_impact_on, file = "/data/cheos/cheos_mix/Quarters/NORMAN_2024/output/ETF_auradb_summarized_impact_on_relation.csv")

}

main()

