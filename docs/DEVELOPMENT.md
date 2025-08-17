# TRACE_OFFBEATS Development Guide

## Setup

1. Clone the repository
2. Install in development mode: `pip install -e .`
3. Install dependencies: `pip install -r requirements.txt`

## Architecture

- `src/trace_offbeats/cli.py` - Command line interface
- `src/trace_offbeats/policy_compiler.py` - Core policy compilation logic
- `src/trace_offbeats/harmony_client.py` - gpt-oss integration via Harmony format
- `src/trace_offbeats/test_runner.py` - Automated test execution
- `src/trace_offbeats/audit_generator.py` - Reasoning audit trail generation

## Development Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes
3. Test: `pytest tests/`
4. Commit: `git commit -m "descriptive message"`
5. Push: `git push origin feature/your-feature`
6. Create Pull Request on GitHub
