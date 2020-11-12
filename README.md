# Keypirinha Updater

This is a package for the fast keystroke launcher keypirinha (<http://keypirinha.com/>). It checks
at startup if your keypirinha installation is up to date and nags you into updating.

## Prerequisite

One of the following to unpack the new keypirinha version (7z file):

* [7-zip](https://www.7-zip.org/) (normally installed)
* `7z.exe` or `7za.exe` in `%PATH%`
* [WinRAR](https://www.rarlab.com/) (normally installed)
* `winrar.exe` in `%PATH%`

## Usage

The `Update Keypirinha to <version>` item downloads the new version and replaces the running version
with it leaving packages and settings intact.

## Installation

### With [PackageControl](https://github.com/ueffel/Keypirinha-PackageControl)

Install Package "Keypirinha-Updater"

### Manually

* Download the `Updater.keypirinha-package` from the
  [releases](https://github.com/ueffel/Keypirinha-Updater/releases/latest)
* Copy the file into `%APPDATA%\Keypirinha\InstalledPackages` (installed mode) or
  `<Keypirinha_Home>\portable\Profile\InstalledPackages` (portable mode)
