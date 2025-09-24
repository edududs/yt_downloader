# Contributing

Thank you for your interest in contributing to yt-downloader! This document provides guidelines and information for contributors.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/eduardojesus12/yt-downloader.git
   cd yt-downloader
   ```

2. **Install dependencies**
   ```bash
   pip install uv
   uv sync --dev
   ```

3. **Run tests**
   ```bash
   uv run pytest
   ```

## Code Style

This project follows these coding standards:

- **Python version**: 3.12+
- **Type hints**: Required throughout the codebase
- **PEP 8**: Code style compliance
- **Pydantic V2**: Modern patterns and best practices
- **Async/Await**: Preferred over threading where applicable

## Testing

- Write tests for new features
- Maintain test coverage above 10%
- Run the full test suite before submitting PRs
- Use `pytest` for testing framework

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Commit Messages

Use clear, descriptive commit messages following this format:
- `feat: add new feature`
- `fix: resolve bug`
- `docs: update documentation`
- `refactor: improve code structure`
- `test: add or update tests`

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.
