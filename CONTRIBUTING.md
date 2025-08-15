# Contributing to InfraBox

Thank you for considering contributing to InfraBox!

## Ways to Contribute

- 💻 Code contributions (features, bug fixes)
- 📝 Documentation improvements
- 🐞 Reporting issues
- ✅ Writing tests or improving automation

## Development Setup

1. Clone the repo:  
   `git clone https://github.com/your-org/infrabox.git`

2. Install Python dependencies:  
   `make setup`

3. Run CLI commands:  
   `python InfraBox.py --help`

4. Lint, format, and scan for security:  
   `make check`

## Git Branch Strategy

- All development happens on feature branches.
- Open pull requests against `main`.

## Commit Messages

Use clear, descriptive commit messages.

Example:

`feat(cli): add create command for new environment`
`fix(parser): harden input validation logic`


## Before Submitting

- Run all tests and checks: `make check`
- Ensure pre-commit hooks pass: `make pre-commit-all`

---

If you're new to open source, please check out [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/).
