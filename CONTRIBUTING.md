# Contributing Guidelines 🤝

Thank you for considering contributing to **Sticker Cases**!
We welcome contributions of all kinds — bug reports, feature requests, documentation improvements, and code.

---

## 📑 Table of Contents

1. [Code of Conduct](#1-code-of-conduct)
2. [How to Contribute](#2-how-to-contribute)
3. [Development Workflow](#3-development-workflow)
4. [Coding Standards](#4-coding-standards)
5. [Pull Request Process](#5-pull-request-process)
6. [Reporting Issues](#6-reporting-issues)

---

## 1. Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).
By participating, you agree to uphold those standards.

⬆️ [Back to top](#contributing-guidelines-)

---

## 2. How to Contribute

* **Bug reports**: Open a [GitHub Issue](../../issues) with clear steps to reproduce.
* **Feature requests**: Describe the problem your feature solves.
* **Pull requests**: Fork the repo, create a branch, and submit a PR.
* **Docs**: Improvements to docs are always appreciated.

⬆️ [Back to top](#contributing-guidelines-)

---

## 3. Development Workflow

We use **Docker Compose** for local dev.

* Start the stack:

  * Linux/macOS: `make up`
  * Windows: `.\dev.ps1 up`
* Stop:

  * Linux/macOS: `make down`
  * Windows: `.\dev.ps1 down`

See [PROJECT Docs](README.md) for full setup.

⬆️ [Back to top](#contributing-guidelines-)

---

## 4. Coding Standards

* **Python (Django)**:

  * Follow [PEP 8](https://peps.python.org/pep-0008/).
  * Use type hints where possible.
  * Keep functions small and focused.

* **JavaScript/TypeScript (Next.js)**:

  * Follow ESLint rules (already configured).
  * Use Prettier for formatting.
  * Use functional components and hooks.

* **Git**:

  * Write clear commit messages (`feat:`, `fix:`, `docs:`, `chore:`).
  * Keep PRs small and focused.

⬆️ [Back to top](#contributing-guidelines-)

---

## 5. Pull Request Process

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/my-feature`).
3. Make your changes.
4. Ensure your code passes linting/tests.
5. Update docs if needed.
6. Submit a PR with a clear description of your changes.

Maintainers will review, provide feedback, and merge once approved.

⬆️ [Back to top](#contributing-guidelines-)

---

## 6. Reporting Issues

If you find a bug, security issue, or documentation gap:

* For **security issues**, see [SECURITY.md](SECURITY.md).
* For everything else, open a GitHub Issue.

⬆️ [Back to top](#contributing-guidelines-)