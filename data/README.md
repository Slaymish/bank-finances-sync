# Data Directory

This directory contains runtime data files generated and used by the sync service.

## Files

- **`sync_state.json`** - Automatically generated. Stores the timestamp of the last successful sync to enable incremental syncing.
- **`CategoryMap.csv`** - Optional. Category rules you can upload to your Google Sheet using `python run.py --upload-categories data/CategoryMap.csv`
- **`*.csv`** - Any other CSV files you want to use for importing category rules

## Note

All files in this directory are gitignored by default to avoid committing sensitive or generated data.
