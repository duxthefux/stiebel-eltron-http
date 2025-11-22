# Stiebel Eltron heat pump integration as Home Assistant sensors
## What it does
Stiebel Eltron HTTP is a Home Assistant integration that connects and scrapes your local Stiebel Eltron ISG webserver to retrieve data from your heat pump system, as HA sensors. See below the provided sensors.

It is not meant to be a climate entity and thus cannot set the temperatures, change the modes, etc. See the official HA integration for that (but know that you'll need to find a way to activate Modbus on your ISG, which might or might not be possible).

This integration is designed to work out-of-the-box and auto-discover your Stiebel Eltron ISG device.


## Prerequisites
- A [Stiebel Eltron heat pump](https://www.stiebel-eltron.com/en/home/products-solutions/renewables/heat_pump.html)
- A [Stiebel Eltron Internet Service Gateway (ISG)](https://www.stiebel-eltron.com/en/home/products-solutions/renewables/controller_energymanagement/isg-web/isg-web.html), connected to your heat pump and your network


## Installation
<details><summary><b>Using HACS</b></summary>

1. Go to the [HACS](https://hacs.xyz/) section
2. Search and install **Stiebel Eltron** from the HACS store
3. After a few moments, your Stiebel Eltron ISG should be auto-detected, and you can set it up in **Settings / Devices & Services**
4. Otherwise, set it up manually from the same menu, using your ISG IP address

</details>
<details><summary><b>Manually</b></summary>

1. Download this repository;
2. Copy the directory **custom_components/stiebel_eltron_http** to your Home Assistant **config/custom_components/stiebel_eltron_http**
3. Restart HomeAssistant
4. After a few moments, your Stiebel Eltron ISG should be auto-detected, and you can set it up in **Settings / Devices & Services**
5. Otherwise, set it up manually from the same menu, using your ISG IP address

</details>

## Provided sensors

### Core Sensors
- Room temperature
- Room relative humidity
- Outside temperature
- DHW (hot water) temperature
- Total heating produced
- Heating produced today
- Total DHW produced
- DHW produced today
- Total energy consumption (heating)
- Heating consumed today
- Total energy consumption (DHW)
- DHW consumed today

### Process Data & Performance Sensors
- Return temperature
- Supply temperature
- Frost protection temperature
- Compressor inlet temperature
- Hot gas temperature
- Condenser temperature
- Oil sump temperature
- Evaporator inlet/outlet temperature
- Low/High pressure
- Water flow
- Inverter current/voltage
- Compressor speed (actual/target)
- Fan power (relative)
- Inverter power input

### Efficiency Metrics (COP)
- Heating efficiency today
- Heating efficiency 1-12 months
- Heating efficiency 13-24 months
- DHW efficiency today
- DHW efficiency 1-12 months
- DHW efficiency 13-24 months

### External Heat Source Sensors (Hybrid Systems)
For systems with external/auxiliary heat sources:
- External actual temperature
- External set temperature
- Dual mode temperature (heating)
- Dual mode temperature (DHW)
- Lower operating limit (heating)
- Lower operating limit (DHW)

### Runtime & Diagnostics
- Runtime VD heating
- Runtime VD DHW
- Runtime VD defrost
- Defrost time
- Defrost starts
- Compressor starts

### System Status
- Operation mode (from START page)
- MAC address

With the **Total energy consumption** sensors, you can add this precious data to your Energy dashboard.

### Runtime options

- The integration exposes a runtime option `fetch_energy` (available in the integration Options) which controls whether the optional Energy page (`/?s=1,8`) is fetched. This option is stored in the integration Options (not in setup data). Existing installations will be migrated automatically.

- The integration also exposes an `update_interval_minutes` option (available in the integration Options) that controls how often the integration scrapes the ISG pages. The value is an integer number of minutes (default: 1). Valid range is 1–1440 minutes.

	- Change it from the integration Options in Home Assistant to increase or decrease scrape frequency. The coordinator will use this value to set the DataUpdateCoordinator `update_interval`.


## Screenshots
![Sensors](./screenshots/device.png)

## Language detection and tests

- Language detection: the scraper determines the ISG UI language by reading the visible
	language-switch element on the ISG pages (the small link in the header). The code
	interprets the link text directly to auto-detect the UI language. Supported languages:
	English (en), German (de), French (fr), Dutch (nl), Italian (it), Swedish (sv),
	Spanish (es), Polish (pl), Czech (cs), Hungarian (hu), Finnish (fi), and Danish (da).
	Meta tags or your local machine's locale are ignored because they can be misleading
	(for example, a locally German system may set page metadata to `de` even when the
	ISG UI is displayed in English).

- Tests: the repository includes a small pytest suite under `tests/` that exercises
	the parsing logic against saved ISG pages in `scripts/testdata/`. To make tests
	lightweight, the test-runner uses minimal shims for Home Assistant and network
	libraries so you don't need a full HA environment to run them. To run tests locally:

```powershell
py -3 -m pip install -U pytest beautifulsoup4
# Or install the development requirements in one go:
py -3 -m pip install -r requirements-dev.txt
py -3 -m pytest -q
```

- **Fetching testdata**: The `scripts/fetch_testdata.py` script can download ISG pages
	for testing purposes. With `--all-languages`, it automatically switches the ISG
	through all available languages and downloads each page variant. By default, it
	harmonizes numeric values across all languages so that testdata files differ only
	in language labels (not in sensor values), making cross-language tests more
	reliable and easier to maintain:

```powershell
# Fetch all languages with harmonized values (recommended for testing)
py -3 .\scripts\fetch_testdata.py --base http://192.168.1.50 --all-languages

# Fetch without harmonization (keep original values)
py -3 .\scripts\fetch_testdata.py --base http://192.168.1.50 --all-languages --no-harmonize

# Fetch specific endpoints only
py -3 .\scripts\fetch_testdata.py --base http://192.168.1.50 --all-languages --endpoints "/?s=1,1" "/?s=1,8"
```

	Value harmonization replaces actual sensor readings with fixed reference values
	(e.g., temperatures → 23.3°C, pressures → 5.22bar, energies → 12345.6kWh) while
	preserving all language-specific labels and structure. This ensures that tests
	comparing sensor extraction across languages verify alias correctness rather than
	failing due to timing differences in when pages were downloaded.

## CanonicalKey enum and alias helpers

This project uses a typed enum `CanonicalKey` (see `custom_components/stiebel_eltron_http/mapping.py`) to represent canonical
header/label identifiers used by the parser. Use the following helpers when
working with parsing or scraping helpers:

- `CanonicalKey` — typed string enum for canonical keys (e.g. `CanonicalKey.VD_HEATING_TOTAL`)
- `get_aliases(value)` — return a list of localized alias strings for a given
	canonical key or a literal string. This centralizes parsing of localized
	labels.
- `to_canonical_key(value)` — convert a string to a `CanonicalKey` when it
	matches an enum member, otherwise returns `None`.

Parsing helpers in `custom_components/stiebel_eltron_http/parsing.py` accept
either a `CanonicalKey` member or a plain string for compatibility, but the
preferred style is to use `CanonicalKey` where possible.

