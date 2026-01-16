#!/usr/bin/env python3
"""
Data Fetch Skill - Load mock CSV datasets and output JSON profiles
"""
import argparse
import json
import os
import sys
from pathlib import Path
import pandas as pd


# Dataset registry mapping
DATASET_REGISTRY = {
    'sales': 'mock_data/sales.csv',
    'inventory': 'mock_data/inventory.csv',
    'default': 'mock_data/sales.csv'
}


def parse_dataset_key(task_text: str) -> str:
    """
    Parse task text to determine which dataset to load.
    
    Args:
        task_text: User task description text
        
    Returns:
        Dataset key (sales, inventory, or default)
    """
    task_lower = task_text.lower()
    
    if 'inventory' in task_lower:
        return 'inventory'
    elif 'sales' in task_lower:
        return 'sales'
    else:
        return 'default'


def get_dataset_path(dataset_key: str) -> Path:
    """
    Get the full path to dataset file.
    
    Args:
        dataset_key: Dataset identifier
        
    Returns:
        Path object to the dataset file
        
    Raises:
        ValueError: If dataset_key is not in registry
        FileNotFoundError: If dataset file does not exist
    """
    if dataset_key not in DATASET_REGISTRY:
        raise ValueError(f"Unknown dataset key: {dataset_key}. Valid keys: {list(DATASET_REGISTRY.keys())}")
    
    # Get repo root (4 levels up from this script: scripts -> data-fetch -> skills -> .github -> repo_root)
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent.parent.parent
    
    # Build dataset path
    relative_path = DATASET_REGISTRY[dataset_key]
    dataset_path = repo_root / relative_path
    
    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset file not found: {dataset_path}\n"
            f"Expected dataset '{dataset_key}' at: {relative_path}"
        )
    
    return dataset_path


def profile_df(df: pd.DataFrame, dataset_path: Path) -> dict:
    """
    Generate comprehensive profile of DataFrame.
    
    Args:
        df: DataFrame to profile
        dataset_path: Path to the dataset file
        
    Returns:
        Dictionary with profile information
    """
    profile = {
        'rows': len(df),
        'cols': len(df.columns),
        'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
        'null_counts': {col: int(df[col].isnull().sum()) for col in df.columns},
        'sample_head': df.head(5).to_dict('records')
    }
    
    # Convert non-serializable types in sample_head
    for row in profile['sample_head']:
        for key, value in row.items():
            if pd.isna(value):
                row[key] = None
            elif isinstance(value, pd.Timestamp):
                row[key] = str(value)
            elif not isinstance(value, (str, int, float, bool, type(None))):
                row[key] = str(value)
    
    # Try to parse timestamp column if exists
    if 'ts' in df.columns:
        try:
            ts_series = pd.to_datetime(df['ts'], errors='coerce')
            valid_ts = ts_series.dropna()
            
            if len(valid_ts) > 0:
                profile['min_ts'] = str(valid_ts.min())
                profile['max_ts'] = str(valid_ts.max())
        except Exception:
            # Silently skip if timestamp parsing fails
            pass
    
    return profile


def load_and_profile(task_text: str) -> dict:
    """
    Main function to load dataset and generate profile.
    
    Args:
        task_text: User task description
        
    Returns:
        Complete profile dictionary including dataset metadata
    """
    # Parse dataset key from task
    dataset_key = parse_dataset_key(task_text)
    
    # Get dataset path
    dataset_path = get_dataset_path(dataset_key)
    
    # Load CSV
    try:
        df = pd.read_csv(dataset_path)
    except Exception as e:
        raise RuntimeError(f"Failed to read CSV from {dataset_path}: {e}")
    
    # Generate profile
    profile = profile_df(df, dataset_path)
    
    # Add metadata
    profile['dataset_key'] = dataset_key
    profile['path'] = str(dataset_path)
    
    # Reorder keys for better readability
    ordered_profile = {
        'dataset_key': profile['dataset_key'],
        'path': profile['path'],
        'rows': profile['rows'],
        'cols': profile['cols'],
        'dtypes': profile['dtypes'],
        'null_counts': profile['null_counts'],
        'sample_head': profile['sample_head']
    }
    
    # Add optional timestamp fields if present
    if 'min_ts' in profile:
        ordered_profile['min_ts'] = profile['min_ts']
    if 'max_ts' in profile:
        ordered_profile['max_ts'] = profile['max_ts']
    
    return ordered_profile


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Load mock CSV datasets and output JSON profiles'
    )
    parser.add_argument(
        '--task',
        required=True,
        help='Task description text to determine dataset'
    )
    parser.add_argument(
        '--save',
        default='data_fetch_profile.json',
        help='Path to save JSON profile (use empty string to skip saving)'
    )
    
    args = parser.parse_args()
    
    try:
        # Load and profile data
        profile = load_and_profile(args.task)
        
        # Output JSON to stdout
        json_output = json.dumps(profile, ensure_ascii=False, indent=2)
        print(json_output)
        
        # Optionally save to file
        if args.save:
            output_path = Path(args.save)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_output)
            
            # Print save confirmation to stderr (not stdout)
            print(f"\n[Profile saved to: {output_path}]", file=sys.stderr)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
