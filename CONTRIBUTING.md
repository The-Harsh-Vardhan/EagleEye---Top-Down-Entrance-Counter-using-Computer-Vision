# Contributing to EagleEye

First off, thank you for considering contributing to EagleEye! It's people like you that make EagleEye such a great tool.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Code Contributions](#code-contributions)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project and everyone participating in it is governed by common sense and mutual respect. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

**Bug Report Template:**

```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. Set configuration '...'
3. See error

**Expected behavior**
A clear description of what you expected to happen.

**Screenshots/Logs**
If applicable, add screenshots or error logs.

**Environment:**
- OS: [e.g., Windows 11, Ubuntu 22.04]
- Python version: [e.g., 3.10.5]
- EagleEye version/commit: [e.g., main branch, commit abc123]
- GPU: [e.g., NVIDIA RTX 3060, CPU only]

**Additional context**
Any other relevant information.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Create an issue and provide:

- **Clear title** describing the enhancement
- **Detailed description** of the proposed functionality
- **Use case** explaining why this would be useful
- **Possible implementation** (if you have ideas)

### Code Contributions

We welcome code contributions! Here are some areas where help is especially appreciated:

- **Bug fixes**
- **Performance improvements**
- **Documentation improvements**
- **New features** (discuss in an issue first for large features)
- **Test coverage**
- **Edge device support** (Raspberry Pi, Jetson)
- **Web dashboard**
- **Multi-camera support**

## Development Setup

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/The-Harsh-Vardhan/EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision.git
   cd EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/macOS
   source .venv/bin/activate
   ```

3. **Install development dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   
   # Optional: Install development tools
   pip install pytest black flake8 mypy
   ```

4. **Create a feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some flexibility:

- **Line length**: 100 characters (not strict 79)
- **Indentation**: 4 spaces
- **Imports**: Group and sort (standard library, third-party, local)
- **Docstrings**: Use Google-style docstrings

### Code Formatting

Use `black` for automatic formatting:

```bash
black src/ main.py
```

### Type Hints

We encourage type hints for function signatures:

```python
def process_frame(frame: np.ndarray, confidence: float = 0.5) -> List[Detection]:
    """Process a video frame and return detections."""
    pass
```

### Docstrings

Use comprehensive docstrings for modules, classes, and functions:

```python
def line_crossing_detection(track: TrackedPerson, line_y: int) -> Optional[CrossingDirection]:
    """
    Detect if a tracked person crossed the counting line.
    
    Args:
        track: TrackedPerson object with current and previous positions
        line_y: Y-coordinate of the counting line in pixels
        
    Returns:
        CrossingDirection.IN if crossed upward, CrossingDirection.OUT if 
        crossed downward, None if no crossing detected.
        
    Example:
        >>> track = TrackedPerson(id=1, bbox=(100, 200, 150, 300))
        >>> direction = line_crossing_detection(track, line_y=240)
    """
    pass
```

## Commit Guidelines

### Commit Message Format

We use conventional commits for clear history:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Examples:**

```bash
feat(detector): add support for yolov9 models

- Integrate yolov9 detection
- Update config for model selection
- Add documentation for new models

Closes #123
```

```bash
fix(tracker): prevent duplicate counting on track ID reuse

The tracker was reusing IDs too quickly, causing duplicate counts.
Now implements a cooldown period for recycled IDs.

Fixes #456
```

### Good Commit Practices

- Write clear, descriptive commit messages
- Keep commits atomic (one logical change per commit)
- Reference issues/PRs in commit messages
- Avoid committing debug code or commented-out blocks

## Pull Request Process

1. **Update documentation** if you're changing functionality
2. **Add tests** for new features (if applicable)
3. **Ensure all tests pass** (if we have a test suite)
4. **Update README.md** if adding user-facing features
5. **Follow the PR template** (will be provided when you open PR)

### PR Checklist

- [ ] Code follows the project's style guidelines
- [ ] Documentation has been updated (README.md, docs/ folder)
- [ ] No new warnings or errors introduced
- [ ] Tested on at least one platform (Windows/Linux/macOS)
- [ ] Commit messages follow conventional commits
- [ ] PR description clearly explains the changes

### PR Review Process

1. Submit your PR with a clear description
2. Maintainers will review within a few days
3. Address any requested changes
4. Once approved, a maintainer will merge
## Documentation

When updating documentation:

- **User guides**: Update [README.md](README.md) and files in [docs/](docs/)
- **API changes**: Update [docs/API_REFERENCE.md](docs/API_REFERENCE.md)
- **New features**: Add examples to [docs/EXAMPLES.md](docs/EXAMPLES.md)
- **Installation changes**: Update [docs/INSTALLATION.md](docs/INSTALLATION.md)
## Development Tips

### Testing Your Changes

```bash
# Test with webcam
python main.py --source 0

# Test with video file
python main.py --source test_video.mp4

# Test headless mode
python main.py --source 0 --no-display
```

### Debugging

Enable verbose logging (if we add it):

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Profiling

Use cProfile for performance analysis:

```bash
python -m cProfile -o profile.stats main.py --source video.mp4
python -m pstats profile.stats
```

## Questions?

- Open a [GitHub Discussion](https://github.com/The-Harsh-Vardhan/EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision/discussions)
- Comment on relevant issues
- Reach out to maintainers

---

Thank you for contributing to EagleEye! 🦅
