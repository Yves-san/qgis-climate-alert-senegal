# Contributing Guide

## Development Setup
```bash
git clone https://github.com/YvesKingsman/qgis-climate-alert-senegal.git
cd qgis-climate-alert-senegal
pip install -r requirements-dev.txt
pre-commit install
```

## Code Standards
- PEP 8 for Python
- Type hints required
- Docstrings on all public functions
- Tests for new features

## Pull Request Process
1. Create feature branch: `git checkout -b feature/my-feature`
2. Write tests first (TDD)
3. Run tests: `pytest tests/ -v`
4. Submit PR with description
