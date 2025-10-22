# Data Documentation

This document describes the data sources and variables used in the third Anthropic Economic Index (AEI) report.

## Claude.ai Usage Data

### Overview
The core dataset contains Claude AI usage metrics aggregated by geography and analysis dimensions (facets).

**Source files**:
- `aei_raw_claude_ai_2025-08-04_to_2025-08-11.csv` (pre-enrichment data in data/intermediate/)
- `aei_enriched_claude_ai_2025-08-04_to_2025-08-11.csv` (enriched data in data/output/)

**Note on data sources**: The AEI raw file contains raw counts and percentages. Derived metrics (indices, tiers, per capita calculations, automation/augmentation percentages) are calculated during the enrichment process in `aei_report_v3_preprocessing_claude_ai.ipynb`.

### Data Schema
Each row represents one metric value for a specific geography and facet combination:

| Column | Type | Description |
|--------|------|-------------|
| `geo_id` | string | Geographic identifier (ISO-2 country code for countries, US state code, or "GLOBAL", ISO-3 country codes in enriched data) |
| `geography` | string | Geographic level: "country", "state_us", or "global" |
| `date_start` | date | Start of data collection period |
| `date_end` | date | End of data collection period |
| `platform_and_product` | string | "Claude AI (Free and Pro)" |
| `facet` | string | Analysis dimension (see Facets below) |
| `level` | integer | Sub-level within facet (0-2) |
| `variable` | string | Metric name (see Variables below) |
| `cluster_name` | string | Specific entity within facet (task, pattern, etc.). For intersections, format is "base::category" |
| `value` | float | Numeric metric value |

### Facets
- **country**: Country-level aggregations
- **state_us**: US state-level aggregations
- **onet_task**: O*NET occupational tasks
- **collaboration**: Human-AI collaboration patterns
- **request**: Request complexity levels (0=highest granularity, 1=middle granularity, 2=lowest granularity)
- **onet_task::collaboration**: Intersection of tasks and collaboration patterns
- **request::collaboration**: Intersection of request categories and collaboration patterns

### Core Variables

Variables follow the pattern `{prefix}_{suffix}` with specific meanings:

**From AEI processing**: `*_count`, `*_pct`
**From enrichment**: `*_per_capita`, `*_per_capita_index`, `*_pct_index`, `*_tier`, `automation_pct`, `augmentation_pct`, `soc_pct`

#### Usage Metrics
- **usage_count**: Total number of conversations/interactions in a geography
- **usage_pct**: Percentage of total usage (relative to parent geography - gobal for countries, US for states)
- **usage_per_capita**: Usage count divided by working age population
- **usage_per_capita_index**: Concentration index showing if a geography has more/less usage than expected based on population share (1.0 = proportional, >1.0 = over-representation, <1.0 = under-representation)
- **usage_tier**: Usage adoption tier (0 = no/little adoption, 1-4 = quartiles of adoption among geographies with sufficient usage)

#### Content Facet Metrics
**O*NET Task Metrics**:
- **onet_task_count**: Number of conversations using this specific O*NET task
- **onet_task_pct**: Percentage of geographic total using this task
- **onet_task_pct_index**: Specialization index comparing task usage to baseline (global for countries, US for states)
- **onet_task_collaboration_count**: Number of conversations with both this task and collaboration pattern (intersection)
- **onet_task_collaboration_pct**: Percentage of the base task's total that has this collaboration pattern (sums to 100% within each task)

#### Occupation Metrics
- **soc_pct**: Percentage of classified O*NET tasks associated with this SOC major occupation group (e.g., Management, Computer and Mathematical)

**Request Metrics**:
- **request_count**: Number of conversations in this request category level
- **request_pct**: Percentage of geographic total in this category
- **request_pct_index**: Specialization index comparing request usage to baseline
- **request_collaboration_count**: Number of conversations with both this request category and collaboration pattern (intersection)
- **request_collaboration_pct**: Percentage of the base request's total that has this collaboration pattern (sums to 100% within each request)

**Collaboration Pattern Metrics**:
- **collaboration_count**: Number of conversations with this collaboration pattern
- **collaboration_pct**: Percentage of geographic total with this pattern
- **collaboration_pct_index**: Specialization index comparing pattern to baseline
- **automation_pct**: Percentage of classifiable collaboration that is automation-focused (directive, feedback loop patterns)
- **augmentation_pct**: Percentage of classifiable collaboration that is augmentation-focused (validation, task iteration, learning patterns)

#### Demographic & Economic Metrics
- **working_age_pop**: Population aged 15-64 (working age definition used by World Bank)
- **gdp_per_working_age_capita**: Total GDP divided by working age population (in USD)

#### Special Values
- **not_classified**: Indicates data that was filtered for privacy protection or could not be classified
- **none**: Indicates the absence of the attribute (e.g., no collaboration, no task selected)

### Data Processing Notes
- **Minimum Observations**: 200 conversations per country, 100 per US state (applied in enrichment step, not raw preprocessing)
- **Population Base**: Working-age population (ages 15-64)
- **not_classified**:
  - For regular facets: Captures filtered/unclassified conversations
  - For intersection facets: Each base cluster has its own not_classified (e.g., "task1::not_classified")
- **Intersection Percentages**: Calculated relative to base cluster totals, ensuring each base cluster's percentages sum to 100%
- **Percentage Index Calculations**:
  - Exclude `not_classified` and `none` categories from index calculations as they are not meaningful
- **Country Codes**: ISO-2 format (e.g., "US" in raw data), ISO-3 (e.g., "USA", "GBR", "FRA") for countries after enrichment
- **Variable Definitions**: See Core Variables section above

## 1P API Usage Data

### Overview
Dataset containing first-party API usage metrics along various dimensions based on a sample of 1P API traffic and analyzed using privacy-preserving methods.

**Source file**: `aei_raw_1p_api_2025-08-04_to_2025-08-11.csv` (in data/intermediate/)

### Data Schema
Each row represents one metric value for a specific facet combination at global level:

| Column | Type | Description |
|--------|------|-------------|
| `geo_id` | string | Geographic identifier (always "GLOBAL" for API data) |
| `geography` | string | Geographic level (always "global" for API data) |
| `date_start` | date | Start of data collection period |
| `date_end` | date | End of data collection period |
| `platform_and_product` | string | "1P API" |
| `facet` | string | Analysis dimension (see Facets below) |
| `level` | integer | Sub-level within facet (0-2) |
| `variable` | string | Metric name (see Variables below) |
| `cluster_name` | string | Specific entity within facet. For intersections, format is "base::category" or "base::index"/"base::count" for mean value metrics |
| `value` | float | Numeric metric value |

### Facets
- **onet_task**: O*NET occupational tasks
- **collaboration**: Human-AI collaboration patterns
- **request**: Request categories (hierarchical levels 0-2 from bottom-up taxonomy)
- **onet_task::collaboration**: Intersection of tasks and collaboration patterns
- **onet_task::prompt_tokens**: Mean prompt tokens per task (normalized, average = 1.0)
- **onet_task::completion_tokens**: Mean completion tokens per task (normalized, average = 1.0)
- **onet_task::cost**: Mean cost per task (normalized, average = 1.0)
- **request::collaboration**: Intersection of request categories and collaboration patterns

### Core Variables

#### Usage Metrics
- **collaboration_count**: Number of 1P API records with this collaboration pattern
- **collaboration_pct**: Percentage of total with this pattern

#### Content Facet Metrics
**O*NET Task Metrics**:
- **onet_task_count**: Number of 1P API records using this specific O*NET task
- **onet_task_pct**: Percentage of total using this task
- **onet_task_collaboration_count**: Records with both this task and collaboration pattern
- **onet_task_collaboration_pct**: Percentage of the task's total with this collaboration pattern

**Mean Value Intersection Metrics** (unique to API data):
- **prompt_tokens_index**: Re-indexed mean prompt tokens (1.0 = average across all tasks)
- **prompt_tokens_count**: Number of records for this metric
- **completion_tokens_index**: Re-indexed mean completion tokens (1.0 = average across all tasks)
- **completion_tokens_count**: Number of records for this metric
- **cost_index**: Re-indexed mean cost (1.0 = average across all tasks)
- **cost_count**: Number of records for this metric

**Request Metrics**:
- **request_count**: Number of 1P API records in this request category
- **request_pct**: Percentage of total in this category
- **request_collaboration_count**: Records with both this request category and collaboration pattern
- **request_collaboration_pct**: Percentage of the request's total with this collaboration pattern

## External Data Sources

We use external data to enrich Claude usage data with external economic and demographic sources.

### ISO Country Codes

**ISO 3166 Country Codes**

International standard codes for representing countries and territories, used for mapping IP-based geolocation data to standardized country identifiers.

- **Standard**: ISO 3166-1
- **Source**: GeoNames geographical database
- **URL**: https://download.geonames.org/export/dump/countryInfo.txt
- **License**: Creative Commons Attribution 4.0 License (https://creativecommons.org/licenses/by/4.0/)
- **Download date**: September 2, 2025
- **Output files**:
  - `geonames_countryInfo.txt` (raw GeoNames data in data/input/)
  - `iso_country_codes.csv` (processed country codes with some changes in data/intermediate/)
- **Key fields**:
  - `iso_alpha_2`: Two-letter country code (e.g., "US", "GB", "FR")
  - `iso_alpha_3`: Three-letter country code (e.g., "USA", "GBR", "FRA")
  - `country_name`: Country name from GeoNames
- **Usage**: Maps IP-based country identification to standardized ISO codes for consistent geographic aggregation

### US State Codes

**State FIPS Codes and USPS Abbreviations**

Official state and territory codes including FIPS codes and two-letter USPS abbreviations for all U.S. states, territories, and the District of Columbia.

- **Series**: State FIPS Codes
- **Source**: U.S. Census Bureau, Geography Division
- **URL**: https://www2.census.gov/geo/docs/reference/state.txt
- **License**: Public Domain (U.S. Government Work)
- **Download date**: September 2, 2025
- **Output files**:
  - `census_state_codes.txt` (raw pipe-delimited text file in data/input/)
- **Usage**: Maps state names to two-letter abbreviations (e.g., "California" → "CA")

### Population Data

### US State Population

**State Characteristics Estimates - Age and Sex - Civilian Population**

Annual estimates of the civilian population by single year of age, sex, race, and Hispanic origin for states and the District of Columbia.

- **Series**: SC-EST2024-AGESEX-CIV
- **Source**: U.S. Census Bureau, Population Division
- **URL**: https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/state/asrh/sc-est2024-agesex-civ.csv
- **License**: Public Domain (U.S. Government Work)
- **Download date**: September 2, 2025
- **Output files**:
  - `sc-est2024-agesex-civ.csv` (raw Census data in data/input/)
  - `working_age_pop_2024_us_state.csv` (processed data summed for ages 15-64 by state in data/intermediate/)
- **Documentation**: https://www2.census.gov/programs-surveys/popest/technical-documentation/file-layouts/2020-2024/SC-EST2024-AGESEX-CIV.pdf

### Country Population

**Population ages 15-64, total**

Total population between the ages 15 to 64. Population is based on the de facto definition of population, which counts all residents regardless of legal status or citizenship.

- **Series**: SP.POP.1564.TO
- **Source**: World Population Prospects, United Nations (UN), publisher: UN Population Division; Staff estimates, World Bank (WB)
- **URL**: https://api.worldbank.org/v2/country/all/indicator/SP.POP.1564.TO?format=json&date=2024&per_page=1000
- **License**: Creative Commons Attribution 4.0 License (https://creativecommons.org/licenses/by/4.0/)
- **Download date**: September 2, 2025
- **Output files**:
  - `working_age_pop_2024_country_raw.csv` (raw World Bank data in data/input/)
  - `working_age_pop_2024_country.csv` (processed country-level data including Taiwan in data/intermediate/)

### Taiwan Population

**Population by single age**

Population projections by single year of age for Taiwan (Republic of China). This data supplements the World Bank country data which excludes Taiwan.

- **Series**: Population by single age (Medium variant, Total gender)
- **Source**: National Development Council, Population Projections for the R.O.C (Taiwan)
- **URL**: https://pop-proj.ndc.gov.tw/main_en/Custom_Detail_Statistics_Search.aspx?n=175&_Query=258170a1-1394-49fe-8d21-dc80562b72fb&page=1&PageSize=10&ToggleType=
- **License**: Open Government Data License (Taiwan)
- **Update date**: 2025.06.17
- **Download date**: September 2, 2025
- **Reference year**: 2024
- **Variable name in script**: `df_taiwan` (raw data), added to `df_working_age_pop_country`
- **Output files**:
  - `Population by single age _20250802235608.csv` (raw data in data/input/, pre-filtered to ages 15-64)
  - Merged into `working_age_pop_2024_country.csv` (processed country-level data in data/intermediate/)

## GDP Data

### Country GDP

**Gross Domestic Product, Current Prices (Billions of U.S. Dollars)**

Total gross domestic product at current market prices for all countries and territories.

- **Series**: NGDPD
- **Source**: International Monetary Fund (IMF), World Economic Outlook Database
- **URL**: https://www.imf.org/external/datamapper/api/v1/NGDPD
- **License**: IMF Data Terms and Conditions
- **Reference year**: 2024
- **Download date**: September 2, 2025
- **Output files**:
  - `imf_gdp_raw_2024.json` (raw API response in data/input/)
  - `gdp_2024_country.csv` (processed country GDP data in data/intermediate/)

### US State GDP

**SASUMMARY State Annual Summary Statistics: Personal Income, GDP, Consumer Spending, Price Indexes, and Employment**

Gross domestic product by state in millions of current U.S. dollars.

- **Series**: SASUMMARY (Gross Domestic Product by State)
- **Source**: U.S. Bureau of Economic Analysis (BEA)
- **URL**: https://apps.bea.gov/itable/?ReqID=70&step=1
- **License**: Public Domain (U.S. Government Work)
- **Download date**: September 2, 2025
- **Reference year**: 2024
- **Output files**:
  - `bea_us_state_gdp_2024.csv` (raw data in data/input/, manually downloaded from BEA)
  - `gdp_2024_us_state.csv` (processed state GDP data in data/intermediate/)
- **Citation**: U.S. Bureau of Economic Analysis, "SASUMMARY State annual summary statistics: personal income, GDP, consumer spending, price indexes, and employment" (accessed September 2, 2025)

## SOC and O*NET Data

### O*NET Task Statements

**O*NET Task Statements Dataset**

Comprehensive database of task statements associated with occupations in the O*NET-SOC taxonomy, providing detailed work activities for each occupation.

- **Database Version**: O*NET Database 20.1
- **Source**: O*NET Resource Center, U.S. Department of Labor
- **URL**: https://www.onetcenter.org/dl_files/database/db_20_1_excel/Task%20Statements.xlsx
- **License**: Public Domain (U.S. Government Work)
- **Download date**: September 2, 2025
- **Output files**:
  - `onet_task_statements_raw.xlsx` (raw Excel file in data/input/)
  - `onet_task_statements.csv` (processed data with soc_major_group in data/intermediate/)
- **Key fields**:
  - `O*NET-SOC Code`: Full occupation code (e.g., "11-1011.00")
  - `Title`: Occupation title
  - `Task ID`: Unique task identifier
  - `Task`: Description of work task
  - `Task Type`: Core or Supplemental
  - `soc_major_group`: First 2 digits of SOC code (e.g., "11" for Management)
- **Notes**:
  - SOC major group codes extracted from O*NET-SOC codes for aggregation
  - Used to map Claude usage patterns to occupational categories

### SOC Structure

**Standard Occupational Classification (SOC) Structure**

Hierarchical classification system for occupations, providing standardized occupation titles and codes.

- **SOC Version**: 2019
- **Source**: O*NET Resource Center (SOC taxonomy)
- **URL**: https://www.onetcenter.org/taxonomy/2019/structure/?fmt=csv
- **License**: Public Domain (U.S. Government Work)
- **Download date**: September 2, 2025
- **Variable name in script**: `df_soc` (SOC structure dataframe)
- **Output files**:
  - `soc_structure_raw.csv` (raw data in data/input/)
  - `soc_structure.csv` (processed SOC structure in data/intermediate/)
- **Key fields**:
  - `Major Group`: SOC major group code (e.g., "11-0000")
  - `Minor Group`: SOC minor group code
  - `Broad Occupation`: Broad occupation code
  - `Detailed Occupation`: Detailed occupation code
  - `soc_major_group`: 2-digit major group code (e.g., "11")
  - `SOC or O*NET-SOC 2019 Title`: Occupation group title
- **Notes**:
  - Provides hierarchical structure for occupational classification

### Business Trends and Outlook Survey

Core questions, National.

- **Source**: U.S. Census Bureau
- **URL**: https://www.census.gov/hfp/btos/downloads/National.xlsx
- **License**: Public Domain (U.S. Government Work)
- **Download date**: September 5, 2025
- **Reference periods**: Ending in September 2023 and August 2025
- **Input file**: `BTOS_National.xlsx`
