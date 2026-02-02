# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-02-02

### Added
- **Image Processing**:
    - Automatic discount badge overlay (rounded rectangle with fire gradient).
    - Watermark overlay ("lagangaofertas.com") for copyright protection.
    - Branded footer with "La Ganga Ofertas" logo.
    - Intelligent text color selection for visibility.
    - Dependency on `Pillow` library for image manipulation.
- **Database Maintenance**:
    - New `--clear-db` command-line argument to reset the publication history.
    - Automated GitHub Action workflow (`cleanup_db.yml`) to clear the database every 15 days (1st and 15th of each month), allowing old deals to be reposted.
- **Developer Tools**:
    - `visual_test.py` script to preview image processing results locally.
    - `state/inspect_db.py` interactive script to inspect and clear the database.

### Changed
- **Twitter Publishing**: integrated image processing pipeline before uploading media.
- **Dependencies**: added `pillow>=10.0.0` to `pyproject.toml`.

## [0.1.0] - 2026-02-01

### Added
- Initial release of the bot.
- Fetching flash deals from API.
- Filtering duplicates using SQLite.
- Posting logic for Twitter.
- GitHub Actions automation.
