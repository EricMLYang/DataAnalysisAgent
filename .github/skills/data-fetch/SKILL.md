---
name: data-fetch
description: Load mock CSV datasets from mock_data/ based on task text and output a JSON profile for downstream analysis.
---

# Data Fetch Skill

## What This Skill Does

This skill loads mock CSV datasets from the `mock_data/` directory based on task text input and outputs a comprehensive JSON profile of the loaded data. The profile includes metadata, data types, null counts, sample data, and optional timestamp range information.

## When to Use

Use this skill when you need to:
- Load mock sales or inventory data for analysis
- Generate a data profile for quality checks
- Extract dataset metadata for downstream anomaly detection
- Prepare data context for further processing

## Dataset Registry

The skill supports the following datasets:
- `sales` → `mock_data/sales.csv`
- `inventory` → `mock_data/inventory.csv`
- `default` → `mock_data/sales.csv` (fallback)

## How It Works

### Steps

1. **Parse Task Text**: Analyzes the input task text to determine which dataset to load
   - If text contains "inventory" → loads inventory dataset
   - If text contains "sales" → loads sales dataset
   - Otherwise → loads default (sales) dataset

2. **Load Dataset**: Reads the CSV file using pandas from the `mock_data/` directory

3. **Profile Data**: Generates comprehensive profile including:
   - Row and column counts
   - Data types for each column
   - Null value counts
   - Sample of first 5 rows
   - Timestamp range (if `ts` column exists and is parseable)

4. **Output JSON**: Prints the profile to stdout in JSON format

## Usage

### Command

```bash
python .github/skills/data-fetch/scripts/fetch.py --task "<task text>"
```

### Arguments

- `--task` (required): Task description text used to determine which dataset to load
- `--save` (optional): Path to save the JSON profile. Default is `data_fetch_profile.json`. Use empty string to skip saving.

### Examples

```bash
# Load sales data
python .github/skills/data-fetch/scripts/fetch.py --task "撈 sales 資料"

# Load inventory data
python .github/skills/data-fetch/scripts/fetch.py --task "讀 inventory 看看"

# Load default data (sales)
python .github/skills/data-fetch/scripts/fetch.py --task "先把資料抓出來"

# Load without saving to file
python .github/skills/data-fetch/scripts/fetch.py --task "撈 sales 資料" --save ""
```

## Output JSON Schema

The skill outputs JSON with the following structure:

```json
{
  "dataset_key": "sales|inventory|default",
  "path": "string - actual file path loaded",
  "rows": "integer - number of rows",
  "cols": "integer - number of columns",
  "dtypes": {
    "column_name": "dtype_string"
  },
  "null_counts": {
    "column_name": "integer - count of nulls"
  },
  "sample_head": [
    {
      "column_name": "value",
      "...": "..."
    }
  ],
  "min_ts": "string - earliest timestamp (if ts column exists)",
  "max_ts": "string - latest timestamp (if ts column exists)"
}
```

### Field Descriptions

- **dataset_key**: Identifier of the dataset loaded (`sales`, `inventory`, or `default`)
- **path**: Full path to the CSV file that was loaded
- **rows**: Total number of data rows (excluding header)
- **cols**: Total number of columns
- **dtypes**: Mapping of column names to their pandas data types
- **null_counts**: Mapping of column names to count of null/missing values
- **sample_head**: Array of the first 5 rows as JSON objects
- **min_ts** (optional): Earliest timestamp found if `ts` column exists and is parseable
- **max_ts** (optional): Latest timestamp found if `ts` column exists and is parseable

## Error Handling

The skill will raise clear errors if:
- The requested dataset file does not exist
- The CSV file cannot be read
- Required arguments are missing

## Limitations

- Only supports CSV format
- Only reads from `mock_data/` directory within the repository
- Does not support downloading external data sources
- Timestamp parsing is best-effort (uses `errors='coerce'`)
