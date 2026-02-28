# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.3] - 2026-02-28

### Fixed
- **Twitter API Errors**: Added automatic retry logic with exponential backoff for `503 Service Unavailable` and `429 Too Many Requests` errors from the Twitter API during media upload and tweet creation.


## [0.2.2] - 2026-02-13

### Changed
- **Publishing Schedule**: Updated the GitHub Actions workflow to run 4 times a day (09:00, 14:00, 19:00, 00:00 ART) to cover morning, siesta, afternoon, and night cycles.

## [0.2.1] - 2026-02-06

### Changed
- **Tweet Formatting Logic**: Implemented smart truncation strategies to strictly adhere to Twitter's 280-character limit.
    - If the message exceeds the limit, the deal name is truncated to the first 3 words.
    - If it still exceeds the limit, the deal details are truncated to the first 3 words.
    - As a last resort, the image URL is omitted.

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
- **API Resilience**: Added retry logic with exponential backoff and increased timeouts to 30s to handle Render's "cold start" and transient errors.
- **Twitter Publishing**: integrated image processing pipeline before uploading media.
- **Tweet Formatting**: Improved message readability:
    - Store names displayed in uppercase (e.g., "FRAVEGA" instead of "Fravega").
    - Prices displayed as integers without decimals (e.g., "$19999" instead of "$19999.0").
    - Discount percentages displayed as integers (e.g., "80%" instead of "80.0%").
- **Dependencies**: added `pillow>=10.0.0` to `pyproject.toml`.
- **Tests**: Added formatted tweet output display in test runs for better visibility.

## [0.1.0] - 2026-02-01

### Added
- Initial release of the bot.
- Fetching flash deals from API.
- Filtering duplicates using SQLite.
- Posting logic for Twitter.
- GitHub Actions automation.
