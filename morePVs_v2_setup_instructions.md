#morePVs v2 model
morePVs v2 Copyright (C) 2018/2019 

Mike B Roberts\
Centre for Energy & Environmental Markets\
UNSW Sydney

*This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.
Contact: m.roberts@unsw.edu.au*

#multi-occupancy residential electricity with PV and storage model


Running the script
---------
Written in Python 3.7\
Script requires the following input parameters.
These can be set using default parameters (allocated after `if __name__ == "__main__": in script`) or using switches as shown in the table.

 | Parameter   | description | default variable | switch |  
 |----|-------|----------| ------------ | 
 | base_path | root directory for all data | `default_base_path` | `-b` |
 | project | subfolder containing data for multiple studies | `default_project` | `-p` |
 | study | Name of study Input parameters for every scenario are in `'study_xxxx.csv'` where `'xxxx'` is the stady name | `default_study` | `-s` |
 | DST region | identifier for DST time difference and dates | `'nsw'` | `-d` |
 | `override_output` | Flag for use when running on UNSW HPC facility to divert output | `False` | `-o` |
 
Sample Directory Structure
----------

```
DATA_EN_6
|
|-  load_profiles
|   |-  siteA
|   |       siteA_load_profiles.csv
|   |
|   |-  siteB
|   |       siteB_load_profiles_v1.csv
|   |       siteB_load_profiles_v1.csv
|   |       siteB_load_profiles_v1.csv
|   |
|   |-  anotherFolderOfLoadFiles
|           LoadFile.csv
|    
|-  pv_profiles
|       pv_profiles_siteA.csv
|       pv_profiles_siteB_v1.csv
|       pv_profiles_siteB_v2.csv
| 
|-  reference
|       battery_control_strategies.csv
|       battery_lookup.csv
|       capex_en_lookup.csv
|       capex_pv_lookup.csv
|       dst_lookup.csv
|       tariff_lookup.csv
|       
|-  studies
|   |-  my_energy_project
|       |-  inputs
|       |      study_demo2.csv  
|       |      study_demo3.csv
|       |
|       |-  outputs
|              |-  study_demo2
|              |   |   demo2_customer_results.csv
|              |   |   demo1_results.csv
|              |   |   demo1_results_std_dev.csv
|              |   |
|              |   |-  saved_tariffs
|              |   |-  scenarios
|              |          demo2_001.csv
|              |          demo2_002.csv
|              |          demo2_003.csv
|              |          demo2_004.csv
|              |     
|              |- study_demo3
```
**Notes:**
 - All the files shown in `reference` folder are required
 - Load profiles, pv profiles and study files are user specified
 - `studies/my_project/` must contain folders for `inputs` and `outputs`


---------
Setup Instructions
---------
All input parameters for each study are contained or referenced in `study_xxxx.csv` file,\
located at `base_path/studies/`'project_name'`/inputs`

File contains one header row and 1 or more additional rows, each specifying a unique scenario, \
with pointers to load profiles, PV profiles, tariffs, battery specs and cost settings.
Column headers and required content are specified below. Columns in [square brackets] are optional.


`scenario` This column contains a unique (integer) Scenario identifier \
All parameters are given *per scenario* i.e. per line of `.csv` file, except \
[`output_types`]
This column lists output formats required, applied to the whole study, not individual scenarios.

-----------
TECHNICAL ARRANGEMENTS
-----------
The column `arrangement` contains a tag indicating the network arrangement for the scenario.

| Arrangement                                                  | Description                                            |
| -------------- | ---------------------------------------------------------- |
| `bau`          | Business as Usual. i.e. all customers on-market with their own retail arrangements. No PV. No BESS |
| `bau_bat`        |  All customers on-market, no PV, individual BESS for some or all customers        |
| `en`  | Embedded Network with no PV |
| `en_pv` | Embedded Network, with central PV and/or individual PV for some or all customers. |
| `cp_only` | All customers on-market. PV (and optional BESS) applied to CP load only  |
| `btm_i_u`  | All customers on-market. Individual PV systems for some or all customers (not CP) |
| `btm_i_c`   | All customers on-market. Individual PV systems for some or all customers AND CP |
| `btm_s_u`  | All customers on-market. Central BTM PV shared between all customers (not CP) |
| `btm_s_u`  | All customers on-market. Central BTM PV shared between all customers (not CP) |
| `btm_s_c`   | All customers on-market. Central BTM PV shared between all customers AND CP) |
| `btm_p_u`  | All customers on-market. Central BTM PV with SOLAR PPA shared between all customers (not CP) |
| `btm_p_c`   | All customers on-market. Central BTM PV with SOLAR PPA shared between all customers AND CP) |
                                                  
 (See also 'BATTERIES' below)
  
-----
LOADS
-----
`load_folder` contains the name of sub-folder within `base_path\load_profiles` containing the load profile(s) for the scenario.\
The folder can contain a single load file or multiple files.

Load files contain: 
 - `timestamp` (first column) in format `d/mm/yyyy h:mm`
 - `timestamp` has consistent time zone (e.g. `AST`) - load file preparation should include conversion from daylight savings time if required  
 
 - 30 minute timestamps assumed. Up to 1 year (17520) but can be less
 - __NB: timestamp refers to *start* of time period__\
 i.e `1/01/2013 00:00`  timestamp is attached to the period 00:00 - 00:30.
 this is to align with the PV output files produced by NREL SAM.\
  It is likely that interval data will need adjusting to align with this.
 - Customer load columns (in kWh). Headers identify customers (e.g. apartment residents)
 - `'cp'` (optional) common property load (kWh)

If there are multiple loads for each scenario (ie multiple load files within the load folder)\
they must all have the same list of customers within the folder.\
This allows for a stochastic approach, modeling networks with multiple different load profiles and\
assessing average outcomes as well as the variability.

BUT each scenario *can* have different number of residents, etc. i.e. if different load folders are used

---
PV:
---
`pv_filename` points to a file within `base_path\pv_profiles` which contains one or more PV profiles.
- The first column, headed `timestamp` has format `d/mm/yyyy h:mm` and must match the timeseries of the load profile
- For `cp_only` arrangement, pv file has single column, headed 'cp'
- For `btm_i_u` : btm individual for units only:  file has *either*:
  - a column for each unit, or 
  - a single 'total' column that is split equally between units \
  i.e. the single profile is used to determine the output of multiple PV systems 
 - For `btm_i_c` : en has *either*:
    - a column for each unit and cp. Or,
    - a single 'total' column: cp gets share according to cp ratio; units get equal share of remainder\
  i.e. the single profile is used to determine the output of multiple PV systems 
 - For Shared btm inc cp: `btm_s_c` A single `total`  column that is shared according to instantaneous load between all units AND cp
 - For Shared btm Units only:`btm_s_u` single `total` column that is split according to instantaneous load between all units EXCLUDING cp
 - `btm_p_c` and `btm_p_u` are similar to `btm_s_u` and `btm_s_c`,\
  but generation is paid for under a ppa to a solar retailer
  
 - For `en_pv`:
    - a single column indicates (labelled 'central') indicates a single central PV system\
    connected between parent and child meters
    - multiple columns are also possible, for 'cp', 'central' and each unit\
    (with headings the same as the unit identifiers in the load profile) 

For `en` scenario, if the ENO is the strata body, set the tariff for `cp` = `TIDNULL`.\
Otherwise  `cp tariff != TIDNULL` and ENO is an external party

###Scaleable PV:
`pv_scaleable` is an optional flag (default = False) to indicate that the PV Profile in `pv_filename` column is for a 1kWp system,\
and the system is scaled to the value given by `pv_kW_peak` 

**N.B. This is a legacy feature and is not compatible with the following:**
- Embedded network containing individual PV systems
- "Price Point" capex settings (see CAPEX below)

-----
CAPEX
-----
The model only provides calculations for a single year of operation, but capex costs are included by amortizing\ 
costs over a user-selected period.
- amortization `a_term` (years) and `a_rate` (%) are defined in `study_....csv` file and apply to all capex (PV, EN and BESS)
- a_rate is decimal e.g. `0.06` NOT `6%` or `6`

###PV Capex
The `study_...csv` file contains a column for `pv_capex_id` which must be defined for every scenario with PV. 
This references a row in reference file `reference\pv_capex_lookup.csv`

In `pv_capex_lookup.csv`, PV capex can be defined in two ways:
1. (preferable method) As a series of $/W values which are applied to each PV system in the scenario
2. (legacy method) as a single total system cost which includes all the PV in the scenario.

For both methods, values are given for the system cost (*including array, inverter, installation cost *), 
after rebates and including GST, and for replacement of the inverter after a period specified by `inverter_life`
The replacement inverter cost is only required if `inverter_life` > `a_term`

###PV Capex Preferable Method (1)
This method is preferable because it allows different $/W capex values for differently sized systems 
and **must** be used where there are multiple PV systems within an EN.
- `pv_capex_id` must contain the text `pricepoint` or `price_point`
- `study_...csv` must contain columns headed `xxx_kWp` containing numerical values of peak system size for every system 
defined in the scenario, where `xxx` corresponds to a column in the `pv_profile`, and `xxx` can be a customer / resident 
identifier (= column header in load profile) or `cp` or `central`
- columns must be provided (in `pv_capex_lookup.csv`) for the total ($/W) system and inverter replacement costs 
for ranges of system size. e.g. `sys_10_20` and `inv_10_20` contain $/W costs for system sizes >10kWp and <= 20kWp
- Ranges are exclusive, except for bound (e.g. `sys_0_10` and `sys_10_20` do not overlap) and must include
 all systems in the scenario as there is currently no validation to deal with overlapping or missing ranges.

###PV Capex Legacy Method (2)
Here, `pv_capex_lookup.csv` contains `pv_capex` (*including inverter cost *, after rebates and including GST) 
and `inverter_cost` (only required if `inverter_life` > amortization period). Both refer to the total amount of PV in the scenario.
 - For `en_pv` or `btm_s` this is capex of central, shared PV system (and *no individual PV systems are allowed*) 
 - For `btm_i_`, this is total capex of all PV systems, which is allocated to individual customers 
 in the same proportion as the allocation of PV generation

- if `pv_scaleable == True` and `pv_capex_scaleable` is `True` or absent (ie default setting = `True`): 
    the $ values are taken as $/kW and scaled by `pv_kW_peak` 
    (NB - use of this method should be restricted to system sizes with equal $/kWp capex).
   if `pv_scaleable == True` and `pv_capex_scaleable` is `False` then `pv_cap_id` has absolute capex values

 - N.B. Different `pv_capex_id` ids required for individual systems (`btm_i_u` and `btm_i_c`)
to allow for higher $/W costs for smaller systems:

###EN Capex
- The `study_...csv` file contains a column for `en_capex_id` which must be defined for every scenario with PV.
This references a row in reference file `reference\en_capex_lookup.csv`
- NB if `capex_en_lookup` has duplicate `en_capex_id`s, it all goes to cock. (read_csv returns a series instead of single value).

###BESS Capex

- TBC....

-------
TARIFFS
-------
- All tariffs are defined in `reference/tariff_lookup.csv` with tariff id's defined in `study_....csv` 
- Each customer, including `cp` can have their (bundled retail and network) tariff defined in a column headed by the same \
identifier as is used in the load_profile file. 
    - For `en` and `en_pv`, this is the internal EN tariff; 
    - for `bau`, `btm_i`, `btm_s`, `cp_only`, etc., this is the on-market retail tariff.
    - for `btm_p` it includes an element for the solar PPA
- If `all_residents` has a tariff id defined, it applies to all households (not cp); this overrides individual tariffs 
- All tariffs can include a flat-rate Feed-in rate `fit_flat_rate`

Tariffs are treated according to their `tariff_type`:
- 'Static tariffs' include `Flat_Rate`, `Zero_Rate`, `TOU`\
 and are calculated independent of energy flows;\
- 'Dynamic' tariffs (identified by having `Block` or `Dynamic` in the the `tariff_type`) are calculated iteratively\
for each timestep dependent on network status (e.g. on cumulative load, pv generation, battery state). 

###Demand tariff
Any tariff with `Demand` in the `tariff_type` has an additional `demand_tariff` component based on the peak demand\
(`kW` or `kVA` according to `demand_type`) in the `demand_period` of the 12-month period (or whole timeseries, whichever is longer).\
`demand_period` runs from `demand_start` to `demand_end` for `demand_week` = `end`, `day` or `both`
Demand tariffs also have an optional `demand_network_peak` boolean parameter. If `True', peak demand is taken at time of network peak (within demand charge period); if `False`, it is taken at customer's peak

###'cp' tariff:
In `en` scenarios, If ENO  is the  strata body, `cp tariff = TIDNULL`,\
If ENO is not the strata  `cp` tariff is what strata pays ENO for CP load

###Discount
% discount is applied to fixed and volumetric charges

###Block Tariffs
Tariff type: `block_daily`has upto three rates for daily usage. Parameters are:\
- `block_rate_1`,`high_1`,
- `block_rate_2`,`high_2`,
- `block_rate_3`\
`high_1` and `high_2` are daily thresholds in kWh. If `high_1` is provided, `block_rate_2` is required.

Tariff type: `block_quarterly`:
 - as above but quarterly thresholds, also in kWh. 
 - 1st Quarter starts at start of time period. 

### Solar TOU Tariffs
Any solar TOU tariff can be added, e.g. 
`STS_xx`  Solar TOU Tariff based on peak, shoulder and off-peak solar periods with rates at xx% discount from EASO TOU rates
`STC_xx`  Solar TOU Combined tariff based on EASO TOU periods, with additional off-peak solar period and xx% off EASO TOU rates

###Solar PPA Tariffs 
For `btm_p_u` and `btm_p_c` arrangements:
`SIT_xx` Solar Instantaneous TOU tariff : 
 - `tariff_type` = `Solar_Instantaneous`
 - Based on underlying (`Flat_Rate` or `TOU`) tariff which is paid to primary retailer.
 - Additional solar instantaneous rate and period
 - customers allocated % of instantaneous generation at that timestamp after cp load has been satisfied
 - If `name_x` is `solar_sc`:
     - solar used by customer charged at `solar_rate` (paid to solar retailler)
     - solar exported charged at FiT (paid to solar retailer)
  - else: `name_x` is `solar`: 
    - All solar charged at `solar_rate`
    
- Solar rate must have details for solar period (even if it is `00:00` to `23:59`)     
- This is **not** a block tariff. 
- `local_import` is calculated statically, 
- So  doesn't allow for individual batteries.

###Legacy `btm_s`
for `btm_s` (eg `upfront`). btm capex and opex are treated as en capex and opex
and shared between customers. PV is treated as if owned individually,
with instantaneous generation allocated equally

###EN Parent tariff
`parent` is Tariff paid at the parent meter for `en` arrangement.(Bundled network and retail tariff) 
For Non EN scenarios (bau, btm, cp_only, etc.), parent tariff must be `TIDNULL`

##Daylight Savings
All load and generation profiles are given in local standard time (no DST)\
Most tariffs have adjustment for DST\
(i.e. periods are fixed but applied to DST-shifted times)\
 In`study_.....csv` file :
 - Set `dst = NSW`  (e.g.)  
 - __NB__ Default is `nsw`
 - __NB__ `dst` must be the same for the whole study

Then `reference/dst_lookup.csv` has start and end timestamps (`nsw_start` and `nsw_end` ) for  each year.
NB Timestamps are given as local standard time (e.g 2am for start and end)

-------
BATTERIES
-------
**N.B. (all `_id`s require `_strategy` too.)**

###For central Battery
 - In `study_xxxxxxx.csv` file, battery is identified by `central_battery_id` and battery control strategy by `central_battery_strategy` 
 - If `central_battery_id` and `central_battery_strategy` are in the headers, then both must be supplied; 
 - If `central_battery_id` and `central_battery_strategy` are NOT BOTH in the headers, then battery is not included.

###For Individual Batteries
- Batteries are identified by `x_battery_id` and battery control strategy by `x_battery_strategy`\
where `x = customer id` from load file
- *OR* `all_battery_id` and `all_battery_strategy` for all *households* having the same battery arrangement,\
plus `cp_battery_id` and `cp_battery_stratagey` **(this overrides individual settings).**

| Arrangement                                                  | Battery Set-up                                             |
| ------------------------------------------------------------ | ---------------------------------------------------------- |
| `bau`                                                        | No battery, by definition                                  |
| `bau_bat` -  no pv, individual bats                          | `all_battery_id`  (or multiple `x_bat....`)`cp_battery_id` |
| `en` or `en_pv`  - with central battery                      | `central_battery_id`                                       |
| *This isn't allowed currently:*<br />`en` or `en_pv` with individual batteries | `all_battery_id`  (or multiple `x_bat....`)`cp_battery_id` |
|                                                              |                                                            |
| `en...` with central *and* individual ??                     | `central_` and `all_` and `cp_` ??                         |
| `cp_only` - cp bat only                                 | `cp_battery_id`                                       |
| `btm_i_c`  `btm_i_u`- only ind batteries                     | `all_battery_id`  (or multiple `x_bat....`)`cp_battery_id` |
| `btm_s_c`  `btm_s_u` - only ind batteries                    | `all_battery_id`  (or multiple `x_bat....`)`cp_battery_id` |
|                                                              |                                                            |

### Battery Characteristics
All battery technical data is kept in `reference\battery_lookup.csv`
- `battery_id`  - identifier unique to battery characteristics 
- `capacity_kWh`      - Single capacity figure: Useful discharge energy
- `efficiency_cycle`  - for charge and discharge (MAX = 1.0)  (default `0.95`)
- `charge_kW` - for charge and discharge. Max charge rate constrained by inverter power and/or max ~0.8C for charging. Defaults to `0.5C`
- `maxDOD` (default `0.8`
- `maxSOC` (default `0.9`)
- `max_cycles`(default `2000`)
- `battery_cost`: Installed battery cost __*excluding*__ inverter (if inverter cost is given) , including GST
- `battery_inv_cost` : Installed cost of battery inverter, inc GST (If = zero, inverter and battery treated as single unit).

N.B. If `battery_capex_per_kWh` is given in the `study_` parameter file, it overrides capital costs given in `battery_lookup.csv`

`life_bat_inv` : lifetime of battery inverter (years)) (Defaults to capital amortization period `a_term` )

###Scalable Battery
If `battery_id` includes `scale` and `x.....battery_capacity_kWh` is in the `study....csv` file\
(for x = `central` or `cp` or `all` or `customer_id`)\
then this capacity is used to scale the capacity and `max_charge_kW` in the `battery_lookup.csv` file

### Battery Control Strategies
kept in `reference/battery_control_strategies`\

**Discharge periods:**
- Discharge *only* allowed between - `discharge_start1` and `discharge_end1` (optional) or\
 between `discharge_start2` and `discharge_end2`.\
 - `discharge_day1` , `discharge_day2`	= `week`, `end` or `both` specify days to discharge 
 - If there is no period, specified, battery is discharged whenever load > generation.

**Charge Periods**
- Battery is charged whenever generation > load, 
- *plus* Optional additional grid-charging periods\
(`charge_start1` to `charge_end1`) and (`charge_start2` to`charge_end2 `)\
 `charge_day1` and `charge_day2` 	= `week`, `end` or `both` : days to charge from grid 
- If there is no charge period specified, battery is never charged from grid.

**Seasonal Strategy**
- If `seasonal_strategy = True` then the model shifts all charge and discharge periods an hour EARLIER in summer.\
- If `False` then winter and summer periods are the same.

**Charge / Discharge Rate_**
- `charge_c_rate` and `discharge_c_rate` given in `battery_control_strategies.csv`\
 as C-rate fraction of capacity to charge / discharge in 1 hour.\
 e.g 0.5C takes 2 hours to charge / discharge
 - i.e. charging power = `battery.charge_c_rate` * `battery.capacity_kWh`
 - If omitted, charge and discharge rate default to `max_charge_kW` in `battery_lookup.csv`

**Priority Charging**
- If `prioritise_battery` is `True`: PV generation is applied to charge battery *before* applying to net load.

**Peak demand Strategy**
- If `peak_demand_percentage` is present (0 <= x <=100), it is applied as a percentage\
to the maximum 30-minute demand in the timeseries to calculate a `peak_demand_threshold`.
- Battery is discharged *only* if net import is above this threshold *and* timestep is within `discharge_period`.\
- Default is `0` - i.e. discharge is regardless of load value.\
i.e. to discharge battery to meet peak demand, regardless of time, `discharge_period` should be set to 24 hours.

------------
OUTPUT TYPES
------------
Column `output_types` in `'study_...csv` 

| `output_types`       |                                                      | Fields                                                       |
| -------------------- | ---------------------------------------------------- | ------------------------------------------------------------ |
| `log_timeseries_brief` | timeseries `.csv` for each scenario and load profile | ` total load  `,` total building import`, `sum_of_customer_imports` |
| `log_timeseries_detailed` | timeseries `.csv` for each scenario and load profile | ` total load  `,` total building import`, `total building export`,`total generation`,`battery saved charge`, etc. |


the following are no longer functional:

| -------------------- | ---------------------------------------------------- | 
| `csv_total_vs_type`  | Summary `.csv`                                       | `scenario_label`,`load_folder`, `arrangement`, `number_of_households`,`total$_building_costs_mean`,`cp_ratio_mean`,`pv_ratio_mean` |
| `csv_total_vs_bat`   | summary `.csv`                                       | `scenario_label`,`load_folder`, `arrangement`, `number_of_households`,`total$_building_costs_mean`,`self-consumption_mean`,`pv_ratio_mean`, `battery_id` `battery_strategy` |
|                      |                                                      |                                                              |
|                      |                                                      |                                                              |

--------------
OUTPUT RESULTS
--------------
Fields output in `/outouts/xxxx/xxxx_results.csv`

TBC......

| Name | Description |
| ----| -------|
| `scenario` |  |
| `scenario_label` |  |
| `arrangement` |  |
| `number_of_households` |  |
| `load_folder` |  |
| `en_opex` |  |
| `en_capex_repayment` |  |
| `pv_capex_repayment` |  |
| `average_hh_bill$` |  |
| `average_hh_solar_bill$` |  |
| `average_hh_total$` |  |
| `central_battery_SOH_mean` |  |
| `central_battery_capacity_kWh_mean` |  |
| `central_battery_cycles_mean` |  |
| `checksum_total_payments$_mean` |  |
| `cp_ratio_mean` |  |
| `cust_bill_cp_mean` |  |
| `cust_solar_bill_cp_mean` |  |
| `cust_total$_cp_mean` |  |
| `eno$_bat_capex_repay_mean` |  |
| `eno$_demand_charge_mean` |  |
| `eno$_energy_bill_mean` |  |
| `eno$_npv_building_mean` |  |
| `eno$_receipts_from_residents_mean` |  |
| `eno$_total_payment_mean` |  |
| `eno_net$_mean` |  |
| `export_kWh_mean` |  |
| `import_kWh_mean` |  |
| `pv_ratio_mean` |  |
| `retailer_bill$_mean` |  |
| `retailer_receipt$_mean` |  |
| `self-consumption_mean` |  |
| `self-consumption_OLD_mean` |  |
| `self-sufficiency_mean` |  |
| `self-sufficiency_OLD_mean` |  |
| `solar_retailer_profit_mean` |  |
| `total$_building_costs_mean` |  |
| `total_battery_losses_mean` |  |
| `total_building_load_mean` |  |


----------
REFERENCES
----------
The following publications are based on research conducted using this model and may be useful in\
explaining terms used and contextualising the settings described above:

    Roberts, M.B., A. Bruce and I. MacGill, Impact of shared battery energy storage systems on photovoltaic\
     self-consumption and electricity bills in apartment buildings. Applied Energy, 2019. 245: p. 78-95.
    Roberts, M.B., A. Bruce, I. MacGill, J. Copper and N. Haghdadi. Photovoltaics on Apartment Buildings \
    - Project Report. 2019; Available from: http://ceem.unsw.edu.au/sites/default/files/documents/Solar_Apartments_Final_Report_2019_4_3.pdf.
    Roberts, M.B., A. Bruce and I. MacGill, A comparison of arrangements for increasing self-consumption and\ 
    maximising the value of distributed photovoltaics on apartment buildings. Solar Energy, under review.

