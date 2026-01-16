#!/usr/bin/env python3
"""
Trace to Flow Spec Converter

Converts Agent trace NDJSON files into structured Flow Spec YAML format.
This structured format is suitable for downstream LangChain/LangGraph planning.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

try:
    import yaml
except ImportError:
    print("Error: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def parse_trace(trace_path: Path) -> list[dict]:
    """Parse NDJSON trace file into list of events."""
    events = []
    with open(trace_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def extract_run_name(events: list[dict]) -> str:
    """Extract run name from init event."""
    for event in events:
        if event.get('type') == 'init':
            return event.get('data', {}).get('run_name', 'unknown')
    return 'unknown'


def extract_goal(events: list[dict]) -> str:
    """Extract goal from plan event."""
    for event in events:
        if event.get('type') == 'plan':
            return event.get('message', '')
    return ''


def build_phases(events: list[dict]) -> list[dict]:
    """Build phases from trace events."""
    phases = []
    current_phase = None

    for event in events:
        event_type = event.get('type')
        data = event.get('data', {})
        message = event.get('message', '')

        if event_type == 'plan':
            # Create phases from plan steps
            steps = data.get('steps', [])
            phase_map = {
                0: 'Understand',
                1: 'Fetch',
                2: 'Profile',
                3: 'QualityCheck',
                4: 'Summarize'
            }
            for i, step in enumerate(steps):
                phase_name = phase_map.get(i, f'Phase{i+1}')
                phases.append({
                    'name': phase_name,
                    'steps': [step],
                    'tools': [],
                    'outputs': [],
                    'dependencies': [],
                    'failure_modes': [],
                    'recovery_playbook': []
                })

        elif event_type == 'error':
            # Add error info to current/relevant phase
            if phases:
                error_msg = data.get('error', message)
                context = data.get('context', '')
                # Find the Fetch phase or last phase
                for phase in phases:
                    if phase['name'] == 'Fetch':
                        phase['failure_modes'].append({
                            'error': error_msg,
                            'context': context
                        })
                        break

        elif event_type == 'strategy_shift':
            # Add recovery info
            if phases:
                for phase in phases:
                    if phase['name'] == 'Fetch':
                        phase['recovery_playbook'].append({
                            'from': data.get('from', ''),
                            'to': data.get('to', ''),
                            'reason': data.get('reason', '')
                        })
                        break

        elif event_type == 'tool_result':
            if phases and data.get('success'):
                output_file = data.get('output_file')
                package = data.get('package')
                for phase in phases:
                    if phase['name'] == 'Fetch':
                        if output_file:
                            phase['outputs'].append(output_file)
                            phase['tools'].append('python')
                        if package:
                            phase['dependencies'].append(package)
                        break

    return phases


def extract_summary(events: list[dict]) -> dict:
    """Extract final summary from trace."""
    for event in reversed(events):
        if event.get('type') == 'summary':
            data = event.get('data', {})
            return {
                'result': data.get('result', ''),
                'dataset': data.get('dataset', ''),
                'rows': data.get('rows', 0),
                'cols': data.get('cols', 0),
                'data_quality': data.get('data_quality', ''),
                'time_range': data.get('time_range', ''),
            }
    return {}


def extract_artifacts(events: list[dict]) -> list[str]:
    """Extract output artifacts from trace."""
    artifacts = []
    for event in events:
        if event.get('type') == 'tool_result':
            output_file = event.get('data', {}).get('output_file')
            if output_file and output_file not in artifacts:
                artifacts.append(output_file)
        if event.get('type') == 'summary':
            output_file = event.get('data', {}).get('output_file')
            if output_file and output_file not in artifacts:
                artifacts.append(output_file)
    return artifacts


def convert_trace_to_flow_spec(trace_path: Path) -> dict:
    """Convert trace NDJSON to Flow Spec dict."""
    events = parse_trace(trace_path)

    flow_spec = {
        'run_name': extract_run_name(events),
        'goal': extract_goal(events),
        'phases': build_phases(events),
        'final_summary': extract_summary(events),
        'artifacts': extract_artifacts(events)
    }

    return flow_spec


def find_run_dir(run_identifier: str, runs_base: Path) -> Path | None:
    """Find run directory by name or partial match."""
    # Direct path
    if (runs_base / run_identifier).exists():
        return runs_base / run_identifier

    # Search for matching directories
    for run_dir in sorted(runs_base.iterdir(), reverse=True):
        if run_dir.is_dir() and run_identifier in run_dir.name:
            return run_dir

    return None


def list_runs(runs_base: Path) -> list[str]:
    """List all available runs."""
    runs = []
    for run_dir in sorted(runs_base.iterdir(), reverse=True):
        if run_dir.is_dir() and not run_dir.name.startswith('.'):
            trace_file = run_dir / 'trace.ndjson'
            if trace_file.exists():
                runs.append(run_dir.name)
    return runs


def main():
    parser = argparse.ArgumentParser(
        description='Convert Agent trace to Flow Spec YAML'
    )
    parser.add_argument(
        'command',
        choices=['convert', 'list'],
        help='Command to execute'
    )
    parser.add_argument(
        'run',
        nargs='?',
        help='Run directory name or partial match (for convert command)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output path for flow spec YAML (default: specs/<run_name>.flow_spec.yaml)'
    )
    parser.add_argument(
        '--stdout',
        action='store_true',
        help='Print to stdout instead of saving to file'
    )

    args = parser.parse_args()

    # Determine project root (3 levels up from this script)
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent.parent.parent
    runs_base = project_root / 'runs'
    specs_base = project_root / 'specs'

    if args.command == 'list':
        runs = list_runs(runs_base)
        if runs:
            print("Available runs:")
            for run in runs:
                print(f"  - {run}")
        else:
            print("No runs found in runs/")
        return

    # Convert command
    if not args.run:
        print("Error: run identifier required for convert command", file=sys.stderr)
        print("Usage: trace_to_flow.py convert <run_name>", file=sys.stderr)
        sys.exit(1)

    run_dir = find_run_dir(args.run, runs_base)
    if not run_dir:
        print(f"Error: Run '{args.run}' not found in runs/", file=sys.stderr)
        print("Available runs:", file=sys.stderr)
        for run in list_runs(runs_base):
            print(f"  - {run}", file=sys.stderr)
        sys.exit(1)

    trace_path = run_dir / 'trace.ndjson'
    if not trace_path.exists():
        print(f"Error: No trace.ndjson found in {run_dir}", file=sys.stderr)
        sys.exit(1)

    # Convert
    flow_spec = convert_trace_to_flow_spec(trace_path)
    yaml_output = yaml.dump(flow_spec, allow_unicode=True, default_flow_style=False, sort_keys=False)

    if args.stdout:
        print(yaml_output)
    else:
        # Determine output path
        if args.output:
            output_path = Path(args.output)
        else:
            specs_base.mkdir(exist_ok=True)
            output_path = specs_base / f"{flow_spec['run_name']}.flow_spec.yaml"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(yaml_output)

        print(f"Flow spec saved to: {output_path}")


if __name__ == '__main__':
    main()
