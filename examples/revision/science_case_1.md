# Science case 1

Every claim in Section 2.1 is now tied to one or two explicit, rerunnable prompts.
You can cite these prompts (or their logic) in Supplementary Methods without exposing system internals.

This shows how exactly these summaries were obtained.

## prompt 1

For European rivers and lakes, summarize the distribution of summed toxic units (sumTU)
by year and species group (algae, crustaceans, fish).

For each year × species group, report:
- number of site–time records,
- mean sumTU,
- median sumTU,
- 99th percentile (p99),
- maximum sumTU.

Aggregate site–time records by year.

> Interpret the huge difference between the median, p99, and max values that are observed for each species group.

### Expected output

- [x] Table with strong skew: median ≪ p99 ≪ max.
- [x] Requested interpretation confirms that median is pulled by extremes.

## prompt 2

 
### Expected output

- Chronic exceedance proportions often substantial.
- Acute exceedance proportions lower but non-zero.

## prompt 3

Identify substances that act as mixture toxicity drivers at site–time records
with elevated summed toxic units (sumTU).

For each species group (algae, crustaceans, fish) and risk class (chronic, acute):
- list the top driver substances by frequency,
- report how often each substance appears as a driver,
- report the summed driver importance across all relevant site–time records.

Limit results to the top 10 substances per species group and risk class.

### Expected output

- Metals (e.g. Copper) recurring with high frequency and importance.
- Herbicides prominent for algae.
- Hydrophobic organics appearing for fish in impacted systems.

## prompt 4

Compare the composition of mixture toxicity drivers between species groups
(algae, crustaceans, fish).

For each species group:
- summarize the dominant chemical classes contributing to mixture toxicity,
- indicate whether contributions are driven by frequent low-level presence
  or by episodic high-impact events.

Base the comparison on site–time records with sumTU ≥ 0.001.

### Expected output

- Algae: herbicides + metals.
- Crustaceans: insecticides + metals, spiky behavior.
- Fish: metals + hydrophobic organics.

## prompt 5

Assess temporal trends in summed toxic units (sumTU) for European rivers and lakes.

For each species group:
- describe how median, 99th percentile, and maximum sumTU values change over time,
- indicate whether changes are driven primarily by central tendencies or by extreme values.

Summarize results qualitatively and quantitatively where possible.

### Expected output

- Stable medians.
- Strongly fluctuating p99/max.
- No monotonic trend.
