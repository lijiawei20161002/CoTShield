# Contributing to CoTShield

Thank you for your interest in contributing to CoTShield! This project aims to make AI reasoning more transparent and auditable.

## 🎯 Vision

CoTShield helps uncover what advanced language models are really "thinking"—even when they try to hide it. We're building tools to detect deceptive reasoning patterns and make AI systems more accountable.

## 🚀 Getting Started

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/lijiawei20161002/CoTShield.git
   cd CoTShield
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**
   ```bash
   pip install -e .
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

### Running Tests

```bash
# Run all examples to verify functionality
python examples/basic_detection.py
python examples/intent_reconstruction.py
python examples/run_evals.py

# Start the web viewer
python examples/run_viewer.py
```

## 🛠️ Development Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions focused and modular

### Project Structure

```
CoTShield/
├── monitor/          # Core detection and analysis tools
│   ├── detector.py        # CoT divergence detection
│   ├── reconstructor.py   # Intent reconstruction
│   └── cli.py            # Command-line interface
├── evals/           # Evaluation tasks and metrics
│   └── tasks.py          # Adversarial task suite
├── ui/              # Web-based viewer interface
│   └── viewer.py         # FastAPI web app
├── examples/        # Example scripts
└── tests/           # Unit and integration tests (coming soon)
```

### Adding New Features

#### 1. New Detection Patterns

To add a new divergence detection pattern:

1. Add a new `DivergenceType` in `monitor/detector.py`
2. Implement detection logic in `CoTDivergenceDetector`
3. Add test cases in examples or tests
4. Update documentation

Example:
```python
class DivergenceType(Enum):
    # ... existing types
    YOUR_NEW_TYPE = "your_new_type"

def _detect_your_pattern(self, reasoning: str, output: str) -> List[DivergenceFlag]:
    """Detect your specific pattern."""
    flags = []
    # Your detection logic here
    return flags
```

#### 2. New Evaluation Tasks

To add new adversarial evaluation tasks:

1. Add tasks to `_initialize_tasks()` in `evals/tasks.py`
2. Specify category, prompt, expected behavior, and red flags
3. Test with example model responses

Example:
```python
EvalTask(
    id="your_task_id",
    category=TaskCategory.FACTUAL_ACCURACY,
    prompt="Your task prompt here",
    expected_behavior="What the model should do",
    red_flags=["warning sign 1", "warning sign 2"],
    description="Brief description",
    difficulty="medium"
)
```

#### 3. New Reconstructor Providers

To add support for new LLM providers:

1. Add provider handling in `ShadowIntentReconstructor.__init__`
2. Implement the query method for the provider
3. Test with example traces
4. Update documentation

### Documentation

- Update README.md for user-facing changes
- Add docstrings for all new functions/classes
- Include examples in docstrings when helpful
- Update this CONTRIBUTING.md for dev-facing changes

## 🧪 Adding Tests

We welcome test contributions! Focus areas:

- Unit tests for detector patterns
- Integration tests for full analysis pipeline
- Edge cases and error handling
- Performance benchmarks

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Description**: Clear description of the issue
2. **Reproduction**: Minimal code to reproduce
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Environment**: Python version, OS, dependencies

## 💡 Suggesting Features

We're especially interested in:

- New detection patterns for deceptive reasoning
- Improved evaluation tasks
- Better visualization tools
- Integration with other AI safety tools
- Performance optimizations

Please open an issue to discuss major features before implementing.

## 📝 Pull Request Process

1. **Fork** the repository
2. **Create a branch** for your feature (`git checkout -b feature/amazing-feature`)
3. **Make your changes** with clear, focused commits
4. **Test thoroughly** - run examples and verify functionality
5. **Update documentation** as needed
6. **Submit PR** with clear description of changes

### PR Guidelines

- Keep PRs focused on a single feature/fix
- Write clear commit messages
- Reference related issues
- Ensure all examples still work
- Update README/docs if needed

## 🤝 Code of Conduct

### Our Standards

- Be respectful and inclusive
- Focus on constructive feedback
- Welcome diverse perspectives
- Prioritize project goals and user safety

### Scope

This project deals with AI safety and deception detection. We expect contributors to:

- Maintain high ethical standards
- Consider potential misuse of features
- Prioritize transparency and accountability
- Respect user privacy and data

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙋 Getting Help

- Open an issue for bugs or feature requests
- Join discussions in existing issues
- Reach out to maintainers for guidance

## 🌟 Recognition

Contributors will be acknowledged in:
- README.md contributors section
- Release notes for their contributions
- Project documentation

Thank you for helping make AI systems more transparent and accountable!
