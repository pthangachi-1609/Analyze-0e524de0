# Analyze-0e524de0

A lightweight Flask application that demonstrates data preview, attachment handling, dynamic script execution, and static-site export for offline viewing. Also includes a CI workflow to lint, execute a script, and publish results.

Live Demo: https://pthangachi-1609.github.io/Analyze-0e524de0/

Note: This README and the repository contents (including the code and assets) were generated with AI assistance for transparency.

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Setup & Installation](#setup--installation)
- [Usage & How to Run](#usage--how-to-run)
  - [Development (Dynamic)](#development-dynamic)
  - [Static Export Mode](#static-export-mode)
  - [Export Flag Details](#export-flag-details)
- [Data & Attachments](#data--attachments)
- [Code Structure & How It Works](#code-structure--how-it-works)
- [Data Conversion & Commit Notes](#data-conversion--commit-notes)
- [CI & GitHub Actions](#ci--github-actions)
- [License](#license)
- [AI Generation Notice](#ai-generation-notice)
- [Appendix: Quick References & Examples](#appendix-quick-references--examples)

---

## Overview

The app exposes a few core capabilities:

- Data Preview: Reads data from data.csv (or converts from data.xlsx) and renders an HTML table.
- Attachments: Reads attachment metadata from data.json and renders downloadable or inline data URIs.
- Execute Script: Dynamically loads and runs a run() function from execute.py, displaying the result.
- Static Export: Generates a small static site (index.html, data.html, attachments.html, execute.html, and a styles.css) suitable for offline viewing, and places it under an output/ directory.

The project is designed to work with Python 3.11+ and Pandas 2.3+. It uses inline CSS for consistent rendering across runtime and export.

---

## Prerequisites

- Python 3.11 or newer
- Pandas 2.3 (for data loading and rendering)
- Flask (web framework)
- Optional for CI: ruff (linting)
- Git & GitHub Pages (for publishing results)

Files of interest in the repository:
- app.py: The main Flask application with routes for index, data, attachments, execute, and export.
- data.xlsx: Provided in the project (convertible to data.csv).
- data.json: Used for attachments metadata (described below).
- execute.py: Script loaded and executed via /execute.
- output/: Directory created when exporting static site (created by the app when running with --export).

Important note: The project’s CI workflow will run:
- ruff for linting
- python execute.py > result.json
- Publish result.json via GitHub Pages (result.json is generated in CI, not committed)

---

## Setup & Installation

1. Create and activate a Python virtual environment
   - Linux/macOS:
     - python3 -m venv venv
     - source venv/bin/activate
   - Windows:
     - python -m venv venv
     - venv\Scripts\activate

2. Install runtime dependencies
   - pip install flask pandas

3. Optional: Install development/CI dependencies
   - pip install ruff

4. Data preparation (as required by the code)
   - Data conversion:
     - The app can convert data.xlsx to data.csv automatically if data.csv is missing (via ensure_csv_from_excel). If you want to pre-seed data.csv, you can create it directly.
     - If you’d like to rely on the automatic conversion, keep data.xlsx in the repo and ensure data.csv is absent before starting the server.
   - Attachments data:
     - Create data.json with an attachments array, e.g.:
       {
         "attachments": [
           {
             "name": "Sample Image",
             "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgA... (base64 data)"
           },
           {
             "name": "Downloadable File",
             "url": "https://example.com/sample.txt"
           }
         ]
       }
     - The app will read data.json and render attachments. If a URL is a data URI (starting with data:), it will render inline; otherwise it will render a download link.

5. Commit notes (as per project goals)
   - data.xlsx is converted to data.csv and committed in the repository as part of the data assets.
   - execute.py has been fixed to address a non-trivial error and is committed with a robust run() function (see CI section for run expectations).

---

## Usage — How to Run

Start the development server (dynamic, live changes)
- Command:
  - python app.py
- Access:
  - http://0.0.0.0:5000 or http://localhost:5000

Key endpoints:
- /         -> Application Overview
- /data     -> Data Preview (renders HTML table from data.csv or converted data.xlsx)
- /attachments -> List and render attachments from data.json
- /execute  -> Executes execute.py via its run() function and shows the result
- /export   -> Triggers a static-site export and serves a notice page

Exported static site (offline-ready)
- Run with export flag:
  - python app.py --export
- What happens:
  - Creates an output/ directory (if not present)
  - Writes assets: styles.css, index.html, data.html, attachments.html, execute.html
  - Returns an on-page notice indicating export completion
- The exported pages are suitable for hosting without the Python runtime and can be served with any static server.

Notes:
- If you want to re-export later, simply rerun the command above; the output/ directory will be updated accordingly.
- The static export mirrors the dynamic pages so you can compare behavior between the live app and its static version.

---

## Data & Attachments

- Data source:
  - data.csv is the primary table source. If missing and data.xlsx exists, the app can convert data.xlsx to data.csv on the fly (via ensure_csv_from_excel).
  - If neither is present or readable, the data page shows a friendly message indicating no data is available.
- Attachments:
  - data.json is the source for attachments. Each attachment has:
    - name: Display name
    - url: Could be a data URI (data:...) for inline content (e.g., images) or a normal URL for downloads
  - The UI renders:
    - Inline images when data_uri starts with data:image
    - Download links for other URLs
  - If data.json cannot be parsed, a placeholder entry is added noting a parse error

File references recap:
- data.xlsx → optionally converted to data.csv (and committed)
- data.csv → primary table data for /data
- data.json → attachments metadata for /attachments
- execute.py → dynamically loaded and executed via /execute

---

## Code Structure & How It Works

Key components in app.py:

- Global assets
  - CSS: Inline CSS string to ensure consistent rendering between runtime and export
  - TEMPLATES: Lightweight in-file HTML templates for index, data, attachments, execute, and export notice pages

- Helper functions
  - load_attachments():
    - Reads data.json (if present) and builds a list of attachments with name and data_uri (if the URL is a data URI)
  - load_data_html():
    - Attempts to load data from data.csv
    - If data.csv is missing, attempts to convert data.xlsx to a DataFrame
    - If neither is available, or if Pandas is unavailable, returns a user-friendly message
    - Returns an HTML table representation of the data (via DataFrame.to_html)
  - ensure_csv_from_excel():
    - If data.csv is absent but data.xlsx exists, converts it to CSV using Pandas
    - Used at startup to ensure data.csv presence when possible

- Routes
  - / (index): Renders application overview
  - /data: Renders data preview via load_data_html()
  - /attachments: Renders attachments list via load_attachments()
  - /execute: Attempts to load and execute execute.py's run() function; returns its repr
  - /export: Creates a static export (index.html, data.html, attachments.html, execute.html, styles.css) into output/

- Export flow
  - When /export is requested, the app builds the static site by rendering templates with CSS and content
  - Writes respective HTML files into output/
  - Returns a minimal export notice page pointing to the export location

- Non-obvious routines
  - The execute route gracefully handles missing execute.py or missing run() with informative messages
  - The data route gracefully handles missing Pandas or data sources, returning friendly HTML
  - The export flow creates a CSS asset (styles.css) for consistency between runtime and exported pages

- Error handling
  - The code wraps potentially failing IO and parsing operations in try/except blocks to avoid crashing and to provide helpful messages

- Data lifecycle
  - CSV conversion is done on-demand if needed and persistent (i.e., data.csv is created from data.xlsx and can be committed)
  - Attachments metadata is read from data.json at runtime

---

## Data Conversion & Commit Notes

- Data conversion
  - data.xlsx is provided and can be converted to data.csv (either on startup via ensure_csv_from_excel or manually)
  - For stability and offline rendering, commit data.csv to the repository after conversion (as per project summary)
- Data attachments
  - data.json should be prepared with an attachments array as described above
  - Attachments may embed images as data URIs or provide external URLs for downloads

Note: The project’s CI (GitHub Actions) workflow is designed to:
- Run ruff for linting
- Execute python execute.py > result.json
- Publish result.json to GitHub Pages (result.json is generated in CI, not committed)

---

## CI & GitHub Actions

- A dedicated CI workflow (.github/workflows/ci.yml) handles:
  - Setting up Python 3.11+
  - Installing dependencies (Flask, Pandas, and ruff for linting)
  - Linting with ruff (log visible in CI)
  - Running the execute script: python execute.py > result.json
  - Publishing result.json to GitHub Pages
- Important: result.json is generated during CI and is not committed to the repository

---

## License

MIT License

- Permissions: Commercial use, modification, distribution, and private use
- Limitations: Liability and warranty disclaimers, must include original license text
- This project is provided under the MIT license; see the LICENSE file for full terms.

---

## Appendix: Quick References & Examples

- Start development server:
  - python app.py
  - Visit http://localhost:5000

- Start with static export:
  - python app.py --export
  - Look in the output/ directory for:
    - index.html
    - data.html
    - attachments.html
    - execute.html
    - styles.css
  - These pages are self-contained and can be served by any static web server.

- Data and attachments example:
  - data.xlsx (provided as a source)
  - data.csv (preferred if committed)
  - data.json with attachments:
    {
      "attachments": [
        {"name": "Sample Image", "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgA..."},
        {"name": "Sample File", "url": "https://example.com/file.txt"}
      ]
    }

- execute.py
  - The app attempts to load and run a run() function from execute.py
  - If execute.py is missing or run() is not defined, the /execute route will display a meaningful message

- Live demonstration link
  - https://pthangachi-1609.github.io/Analyze-0e524de0/

---

## AI Generation Notice

This README and much of the content were generated with an AI tool to provide a thorough, user-friendly guide. It is crafted to reflect the actual code and intended usage described in app.py and the project summary.

---

If you’d like, I can tailor this README to align precisely with any updates you make (e.g., exact execute.py behavior, sample data.json content, or additional endpoints).