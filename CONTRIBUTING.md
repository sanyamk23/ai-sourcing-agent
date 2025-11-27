# Contributing to AI Candidate Sourcing System

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/ai-candidate-sourcing.git
   cd ai-candidate-sourcing
   ```
3. **Set up development environment**
   ```bash
   make dev
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

- Write clean, readable code
- Follow existing code style
- Add comments for complex logic
- Update documentation if needed

### 3. Test Your Changes

```bash
# Run tests
make test

# Run specific test
pytest tests/test_your_feature.py -v

# Check code quality
make lint
make format
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
# or
git commit -m "fix: resolve bug in scraper"
```

**Commit Message Format:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Maximum line length: 120 characters
- Use meaningful variable names
- Add docstrings to functions/classes

Example:
```python
def scrape_candidates(job_description: JobDescription) -> List[Candidate]:
    """
    Scrape candidates from job portals.
    
    Args:
        job_description: Job requirements and details
        
    Returns:
        List of candidate objects
    """
    # Implementation
    pass
```

### Formatting

Run before committing:
```bash
make format
make lint
```

## Testing

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use descriptive test names
- Test both success and failure cases

Example:
```python
def test_candidate_matching_success(sample_job_description, sample_candidate):
    """Test successful candidate matching"""
    matcher = CandidateMatcher()
    score = matcher.match(sample_candidate, sample_job_description)
    assert 0 <= score <= 1
```

### Running Tests

```bash
# All tests
make test

# Specific test file
pytest tests/test_matcher.py -v

# With coverage
pytest --cov=src tests/
```

## Documentation

### Code Documentation

- Add docstrings to all public functions/classes
- Include parameter types and return types
- Provide usage examples for complex functions

### User Documentation

- Update README.md for user-facing changes
- Update API.md for API changes
- Update DEPLOYMENT.md for deployment changes
- Add entries to CHANGELOG.md

## Pull Request Guidelines

### Before Submitting

- [ ] Tests pass (`make test`)
- [ ] Code is formatted (`make format`)
- [ ] Linting passes (`make lint`)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Commit messages are clear

### PR Description

Include:
1. **What**: What changes were made
2. **Why**: Why these changes were needed
3. **How**: How the changes work
4. **Testing**: How you tested the changes

Example:
```markdown
## What
Added support for GitHub Jobs scraping

## Why
To increase candidate pool from developer-focused platform

## How
- Implemented GitHubJobsScraper class
- Added API integration
- Included rate limiting

## Testing
- Added unit tests for scraper
- Tested with real API calls
- Verified candidate data extraction
```

## Adding New Features

### New Scraper

1. Create scraper class in `src/scrapers.py`
2. Inherit from `BasePortalScraper`
3. Implement `scrape()` method
4. Add configuration to `config.yaml`
5. Add tests
6. Update documentation

### New API Endpoint

1. Add endpoint to `src/api_server.py`
2. Define request/response models in `src/models.py`
3. Add tests
4. Update `docs/API.md`

### New Ranking Factor

1. Add factor to `src/ranker.py`
2. Update `calculate_rank_score()` method
3. Add tests
4. Document in README.md

## Bug Reports

### Before Reporting

- Check existing issues
- Verify it's reproducible
- Test with latest version

### Report Format

```markdown
**Description**
Clear description of the bug

**Steps to Reproduce**
1. Step one
2. Step two
3. ...

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: macOS 14.0
- Python: 3.12.0
- Version: 1.0.0

**Logs**
```
Relevant log output
```
```

## Feature Requests

### Request Format

```markdown
**Feature Description**
Clear description of the feature

**Use Case**
Why this feature is needed

**Proposed Solution**
How it could be implemented

**Alternatives**
Other approaches considered
```

## Code Review Process

1. Maintainer reviews PR
2. Feedback provided if needed
3. Changes requested or approved
4. PR merged after approval

## Questions?

- Open an issue for questions
- Check existing documentation
- Review closed issues/PRs

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
