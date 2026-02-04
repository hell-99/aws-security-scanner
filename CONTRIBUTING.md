# Contributing to AWS Security Scanner

Thank you for your interest in contributing to this project!

## How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Add tests** for new functionality
5. **Run tests**: `python -m pytest tests/`
6. **Commit your changes**: `git commit -m "Add feature: description"`
7. **Push to your fork**: `git push origin feature/your-feature-name`
8. **Open a Pull Request**

## Development Setup

```bash
# Clone your fork
git clone https://github.com/hell-99/aws-security-scanner.git
cd aws-security-scanner

# Install dependencies
pip install -r requirements.txt

# Run in mock mode
python scanner.py --mock
```

## Adding New Scanners

To add a new service scanner (e.g., EC2, IAM):

1. Create a new file in `scanners/` directory (e.g., `ec2_scanner.py`)
2. Implement the scanner class following the pattern in `s3_scanner.py`
3. Add mock data to `mock_data/` directory
4. Update `scanner.py` to include the new scanner
5. Add tests in `tests/`

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to all functions and classes
- Keep functions focused and modular

## Security Best Practices

- Never commit AWS credentials
- Always validate and sanitize user inputs
- Follow the principle of least privilege
- Document security assumptions

## Questions?

Open an issue or reach out to the maintainer.
