# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2026-10-19

### Added
- 2 new Fossil MCP tools: `fossil_clone` and `fossil_close` (with `--force` parameter support), expanding the server to 31 tools.
- JSON schemas for all 31 MCP tools generated in `doc/schemas/`.
- Automated regression test suite (`scripts/test_regression_v101.py`).
- Bilingual documentation synchronization (English and Romanian).

### Changed
- `fossil_open`: automatic creation of destination directories and enhanced checkout state reporting.
- Improved Windows path normalization and command argument escaping.

### Fixed
- Handled whitespace in repository paths and working directories reliably.

## [1.0.0] - 2026-10-12

### Added
- Initial public release of FossilSoloMCP with 29 dedicated MCP tools for Fossil SCM repositories.
- Stdio transport for AI clients (Google Antigravity, Claude Desktop, Cursor).
- Headless anti-hang architecture with 30-second execution timeouts and automatic prompts handling.
- Comprehensive bilingual documentation and standalone interactive `MANUAL.html`.
