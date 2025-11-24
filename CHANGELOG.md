# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-11-24

### Added
- **55 sensors** across 10 languages with structure-based translation extraction
- Energy page sensors (s=1,8): heat amount, power consumption, efficiency metrics
- All process values sensors (s=1,1): temperatures, pressures, flow rates, power metrics
- Dual-mode temperature sensors for bivalent systems
- Runtime and defrost statistics sensors
- Heating circuit 2 (HK2) temperature sensors
- External heat source temperature sensors
- Configurable update interval (1-1440 minutes) via integration options UI
- Comprehensive documentation in `ADDING_NEW_SENSORS.md` with complete workflow
- Sample scripts for adding new ISG pages (`scripts/samples/`)
- Utility scripts for translation extraction and verification
- GitHub Actions workflow for automated testing
- This CHANGELOG file

### Changed
- Reorganized repository structure: moved analysis scripts to `scripts/`, test shims to `tests/`
- Updated to structure-based translation mapping for better maintainability
- Improved language detection for 12 languages (cs, da, de, en, es, fi, fr, hu, it, nl, pl, sv)
- Version bumped to 0.2.0 reflecting significant feature additions

### Fixed
- Options flow configuration UI (Configure button) now works correctly
- `async_get_options_flow` moved to ConfigFlow class as static method
- Unicode encoding issues on Windows for translation extraction scripts
- HTML pattern compatibility for different ISG firmware versions

### Removed
- Temporary analysis files from repository root
- Non-functional `test_options_flow.py` that always skipped
- Duplicate and obsolete utility scripts

## [0.1.1] - Previous version

### Initial Release
- Basic sensor integration for Stiebel Eltron ISG
- SSDP auto-discovery
- Core sensors: temperatures, energy consumption, hot water
- Multi-language support
