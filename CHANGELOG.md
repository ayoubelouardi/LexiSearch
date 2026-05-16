# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Right-Click Copy**: You can now right-click anywhere in the app to instantly copy the currently displayed plain-text definition to your system clipboard.

### Removed
- **Command Palette Disabled**: The default `Ctrl+p` command palette has been disabled to streamline the interface and prevent accidental activations.

## [0.2.0-beta] - 2026-05-14

### Added
- **Cross-Platform Binaries**: Added automated PyInstaller builds for Linux, macOS, and Windows.
- **Community Standards**: Added Code of Conduct, Contributing guidelines, and Issue/PR templates.
- **CI/CD Pipeline**: Added GitHub Action workflows for continuous integration (linting with Pyright/Pylint/Black) and releasing.
- **Dependabot**: Enabled automated dependency updates.

## [0.1.1] - 2026-05-14

### Added
- **Vim Navigation**: Added support for Vim-style shortcuts (`j`, `k`, `h`, `l`, `gg`, `G`) in a new "Normal Mode".
- **Insert/Normal Mode Paradigm**: Pressing `Escape` enters Normal Mode for navigation. Pressing `/` enters Insert Mode to type in the search bar.
- **Help Modal**: Added an interactive help screen triggered by `?` in Normal Mode to display all active shortcuts.
- **Search Shortcuts**: Added `Ctrl+Backspace` (Ctrl+H) to instantly clear the search bar, and `Enter` to instantly highlight the first word result.
- **Changelog**: Added `CHANGELOG.md` to track project evolution.

### Removed
- **Legacy Formats**: Removed the `legacy_data/` directory (CSV and MySQL dumps) to strictly focus the repository on the Python TUI application and its highly optimized SQLite backend.
