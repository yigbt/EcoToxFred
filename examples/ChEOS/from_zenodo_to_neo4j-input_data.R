# run this script on a machine with more than 20GB RAM, the exposure file is huge!
invisible(
  lapply(
    c(
      "tidyverse",
      "lubridate",
      "magrittr",
      "DBI",
      "RSQLite",
      "dbplyr"
    ),
    base::library, character.only = TRUE)
)

micro_to_mili <- function(data) {
  micro <- "µg/l"
  mili <- "mg/l"
  data %>%
    mutate("concentration_value" = ifelse(concentration_unit == micro,
                                          yes = concentration_value / 1000, no = concentration_value)) %>%
    mutate("concentration_unit" = ifelse(concentration_unit == micro,
                                         yes = mili, no = concentration_unit))
}

get_exposure_data <- function(sql_file) {
  con <- dbConnect(RSQLite::SQLite(), "/data/cheos/zenodo/v2/exposure_data.sqlite")

  query <- "SELECT  from exposure_data e WHERE e.EUROPE like 'TRUE' AND e.AGGREGATED like 'FALSE' AND e.COORDS like 'TRUE' LIMIT 1000"
  data <- dbGetQuery(conn = con, statement = read_file(sql_file)) %>%
    as_tibble()
  data$river_km %<>% as.double()
  data$lat %<>% as.double()
  data$lon %<>% as.double()
  data$concentration_value %<>% as.double()
  dbDisconnect(con)

  return(data %>% micro_to_mili())
}


# Exposure data
# filter for EUROPE, !MARINE, !AGGREGATED
# summarize quarterly with median concentration
# filter for median concentration > 0
# calculate TUs, sumTUs, ratioTUs, and maxTUs
summarize_filter_exposure_data <- function(data) {
  data %>%
    filter(!is.na(time_point))

}

merge_and_rearrange_data <- function(chemical_data, empodat_data) {
  left_join(empodat_data,
            chemical_data %>% select(Norman_SusDat_ID, DTXSID),
            by = join_by("Norman_SusDat_ID" == "Norman_SusDat_ID"), multiple = "first") %>%
    mutate("DTXSID_AVAILABLE" = (!is.na(DTXSID) & DTXSID != "")) %>%
    filter(!is.na(DTXSID)) %>%
    select(starts_with("Norman"), DTXSID, Substance_name, station_name_n, country, national_code,
           river_basin_name_n, water_body_name_n, river_km, lat, lon,
           concentration_value, concentration_unit, time_point)
}

# todo: remove rows where timepoint cannot be generated
# todo: create a united tp column containing the year-quarter combination only
summarize_concentrations <- function(data) {
  df <- data %>%
    filter(time_point != "NA") %>%
    mutate("time_point_original" = ymd(substr(time_point, start = 1, stop = 10))) %>%
    mutate("year" = year(time_point_original),
           "quarter" = paste0("0", quarter(time_point_original)),
           "day" = "01") %>%
    unite(col = "tp", c(year, quarter, day), sep = "-", remove = FALSE) %>%
    mutate("time_point" = ymd(tp)) %>%
    filter(!is.na(time_point)) %>%
    select(-c(tp, time_point_original, year, quarter, day)) %>%
    mutate("tox_label" = "ECOTOX DB + IRFMN QSAR")
  data_sub <- df %>%
    group_by(station_name_n, DTXSID, time_point) %>%
    summarise("median_concentration" = median(concentration_value)) %>%
    ungroup()
  left_join(data_sub,
            df %>% select(-c(concentration_value, Norman_record_ID, Norman_SusDat_ID)) %>% unique(),
            by = join_by(station_name_n, DTXSID, time_point))
}

get_drivers_per_location <- function(data_l, data_e, limit) {
  tp <- data_l$time_point %>% unique() %>% sort()
  base::return(
    do.call(rbind,
            parallel::mclapply(tp, function(t) {
              # t <- tp[3]
              data_l_t <- data_l %>% dplyr::filter(time_point == t, sumTU > 0)
              data_e_t <- data_e %>% dplyr::filter(time_point == t)
              stations <- data_l_t %>%
                dplyr::pull(station_name_n) %>%
                base::unique()
              do.call(rbind,
                      # base::lapply(stations, function(l) {
                      parallel::mclapply(stations, function(l) {
                        # l <- stations[3]
                        tmp <- dplyr::left_join(data_l_t %>% dplyr::filter(station_name_n == l),
                                                data_e_t %>%
                                                  dplyr::filter(station_name_n == l) %>%
                                                  dplyr::select(station_name_n, DTXSID, TU, tox_stat, species),
                                                by = c("station_name_n", "tox_stat", "species"),
                                                multiple = "all") %>% # this is ok.
                          dplyr::group_by(species, tox_stat, tox_label) %>%
                          dplyr::arrange(desc(TU)) %>%
                          dplyr::select(DTXSID, station_name_n, sumTU, ratioTU, TU, species, tox_stat, tox_label,
                                        time_point)
                        tmp %>%
                          dplyr::slice(base::seq_len(base::which.max(base::cumsum(TU) / sumTU >= limit)))
                      }, mc.cores = 8)
              ) %>%
                dplyr::ungroup() #%>%
              # dplyr::mutate("driver_importance" = TU / sumTU,  # same as ratioTU if compound with highest conc.
              #               "time_point" = t, "year" = year(t), "quarter" = quarter(t))
            }, mc.cores = length(tp))
    )
  )
}


main <- function() {

  # setwd("/home/hertelj/git-hertelj/llm-chatbot-python/examples/ChEOS/")
  empodat_data <- get_exposure_data(
    sql_file = "/home/hertelj/git-hertelj/llm-chatbot-python/examples/ChEOS/exposure_data.sql")

  chemical_data <- read_csv(file = "/data/cheos/zenodo/v2/01_chemical_data.csv")

  data <- merge_and_rearrange_data(chemical_data, empodat_data)  # add DTXSID
  data <- data %>% summarize_concentrations()  # median_concentrations per quarter

  substances <- data$DTXSID %>% unique()
  hazard_data <- read_csv(file = "/data/cheos/zenodo/v2/05_hazard_data.csv") %>%
    filter(tox_stat == "supplemented", DTXSID %in% substances)

  exposure_data <- left_join(data, hazard_data, relationship = "many-to-many", by = join_by(DTXSID)) %>%
    mutate("TU" = ifelse(tox_source_origin == "IRFMN", # this hits qsar and (supplemented from qsar)
                         yes = (median_concentration * neutral_fraction_jchem) / tox_value_mg_L,
                         no = median_concentration / tox_value_mg_L))

  sites_data <- exposure_data %>%
    group_by(station_name_n, country, national_code, river_basin_name_n, water_body_name_n, river_km,
             lat, lon, time_point, species, tox_stat, tox_label) %>%
    summarise("sumTU" = sum(TU), "maxTU" = max(TU), "ratioTU" = ifelse(sumTU > 0, yes = maxTU / sumTU, no = 0)) %>%
    ungroup()

  # filter to sumTU>0 to reduce dataset
  sites_data <- sites_data %>% filter(sumTU > 0)
  exposure_data <- exposure_data %>% filter(station_name_n %in% (sites_data$station_name_n %>% unique()))
  substances <- exposure_data$DTXSID %>% unique()
  chemical_data <- chemical_data %>% filter(DTXSID %in% substances)
  hazard_data <- hazard_data %>% filter(DTXSID %in% substances)

  drivers_data <- get_drivers_per_location(data_l = sites_data,
                                           data_e = exposure_data,
                                           limit = 0.75)

  write_csv(sites_data, file = "/data/cheos/zenodo/v2/neo4j_sites.data")
  write_csv(exposure_data, file = "/data/cheos/zenodo/v2/neo4j_exposure.csv")
  write_csv(chemical_data, file = "/data/cheos/zenodo/v2/neo4j_chemical.csv")
  write_csv(hazard_data, file = "/data/cheos/zenodo/v2/neo4j_hazard.csv")
  write_csv(drivers_data, file = "/data/cheos/zenodo/v2/neo4j_drivers.csv")

  sites_data %>% nrow()
  exposure_data %>% nrow()
  chemical_data %>% nrow()
  hazard_data %>% nrow()
  drivers_data %>% nrow()
}

main()


