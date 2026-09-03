# Contributing

Thank you for your interest in contributing to yt-downloader! This document provides guidelines and information for contributors.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/edududs/yt_downloader.git
   cd yt_downloader
   ```

2. **Install dependencies** (uv installs the `dev` group by default)
   ```bash
   uv sync
   ```

3. **Run the quality gate**
   ```bash
   uv run ruff format . && uv run ruff check . && uv run pyright && uv run pytest
   ```

## Code Style

- **Python version**: 3.12+
- **ruff**: `select = ["ALL"]`; every ignore in `pyproject.toml` carries a one-line reason. Do not add `# noqa` without one.
- **pyright**: strict on `src/`, standard on `tests/`. No `Any`; `# pyright: ignore[rule]` only with a justification on the same line.
- **Type hints**: required everywhere.

## Architecture rules

- `domain/` imports nothing from the package. `application/` imports only `domain/` and its own ports.
- Use cases receive ports through the constructor and raise/catch only `DomainError`.
- Adapters implement ports structurally (`typing.Protocol`) and translate every vendor exception into a `DomainError` subclass at the boundary.
- A new outbound adapter goes in `src/yt_downloader/adapters/outbound/<kind>/` and is wired in `bootstrap/container.py`. A new YouTube provider also gets a case in `adapters/outbound/youtube/registry.py` and a member in `YouTubeSettings.provider`.
- `Settings` is read only by `bootstrap/`, the CLI adapter and the provider registry.
- Vendor SDKs (`pytubefix`) are imported only inside their adapter package; `subprocess` only inside the ffmpeg adapter.

## Testing

- Tests live in `tests/` and use the fakes in `tests/fakes.py` for the ports — no network, no ffmpeg.
- Tests that need the real network or a real `ffmpeg` are marked `@pytest.mark.integration` and skipped by default (`uv run pytest -m integration` runs them).
- Coverage gate: 90% (`--cov-fail-under` in `pyproject.toml`).
- Run the full gate before opening a PR.

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Commit Messages

[Conventional Commits](https://www.conventionalcommits.org/): `feat`, `fix`, `docs`, `refactor`, `test`, `build`, `chore`. Breaking changes use `!` and a `BREAKING CHANGE:` footer.

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.
