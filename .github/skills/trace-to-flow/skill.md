---
name: trace-to-flow
description: Convert Agent execution traces from runs/ into structured Flow Spec YAML for LangChain/LangGraph development planning.
---

# Trace to Flow Skill

## What This Skill Does

This skill converts Agent execution traces (NDJSON format) into structured Flow Spec YAML files. The Flow Spec is a standardized intermediate format that can be used by downstream prompts to generate LangChain/LangGraph development plans.

## When to Use

Use this skill when you need to:
- Convert a completed run's trace into a reusable flow specification
- Prepare trace data for LangChain/LangGraph planning
- Analyze past execution patterns for workflow design
- Generate structured specs from Agent behavior logs

## Usage

### List Available Runs

```bash
python3 .github/skills/trace-to-flow/scripts/trace_to_flow.py list
```

### Convert a Run to Flow Spec

```bash
# Full run name
python3 .github/skills/trace-to-flow/scripts/trace_to_flow.py convert 20260116-203100-take-data-test

# Partial match (will find the most recent matching run)
python3 .github/skills/trace-to-flow/scripts/trace_to_flow.py convert take-data-test

# Output to stdout instead of file
python3 .github/skills/trace-to-flow/scripts/trace_to_flow.py convert take-data-test --stdout

# Custom output path
python3 .github/skills/trace-to-flow/scripts/trace_to_flow.py convert take-data-test -o custom_output.yaml
```

## Output

By default, the Flow Spec is saved to `specs/<run_name>.flow_spec.yaml`.

### Flow Spec Schema

```yaml
run_name: string           # Name of the run
goal: string               # High-level goal from plan
phases:                    # Execution phases
  - name: string           # Phase name (Understand, Fetch, Profile, etc.)
    steps: [string]        # Steps in this phase
    tools: [string]        # Tools used (python, shell, etc.)
    outputs: [string]      # Output files produced
    dependencies: [string] # Required packages
    failure_modes:         # Errors encountered
      - error: string
        context: string
    recovery_playbook:     # How errors were recovered
      - from: string
        to: string
        reason: string
final_summary:             # Task summary
  result: string
  dataset: string
  rows: int
  cols: int
  data_quality: string
  time_range: string
artifacts: [string]        # All output files
```

## Workflow

1. Agent runs a task → generates `runs/<timestamp>-<name>/trace.ndjson`
2. Use this skill to convert → generates `specs/<name>.flow_spec.yaml`
3. Use `trace_to_langchain_plan.prompt.md` → generates `plans/<name>.langchain-plan.md`

## Example

```bash
# List runs
python3 .github/skills/trace-to-flow/scripts/trace_to_flow.py list
# Output:
#   Available runs:
#     - 20260116-203100-take-data-test
#     - 20260116-155902-fetch-data-test

# Convert the take-data-test run
python3 .github/skills/trace-to-flow/scripts/trace_to_flow.py convert take-data-test
# Output:
#   Flow spec saved to: specs/take-data-test.flow_spec.yaml
```

## Dependencies

- Python 3.10+
- PyYAML (`pip install pyyaml`)
