# 🚀 InfraBox - DevOps Infrastructure Bootstrapper

![GitHub Workflow Status](https://github.com/andreicalin-georgescu/InfraBox/actions/workflows/python-cli-checks.yml/badge.svg)
![Terraform Validate](https://github.com/andreicalin-georgescu/InfraBox/actions/workflows/terraform-checks.yml/badge.svg)
![License](https://img.shields.io/github/license/andreicalin-georgescu/InfraBox)

# test change

**InfraBox** is a secure, modular, and reusable infrastructure-as-code boilerplate using **Terraform on Azure**. It is designed to make provisioning cloud infrastructure fast, predictable, and accessible — especially for teams and developers who want to spin up fully working environments with minimal friction.

## 📦 Project Goals

- 🛠️ Modular, scalable, and DRY Terraform code
- 🔐 Strong DevSecOps and input validation principles
- ⚙️ CLI wrapper for simplified provisioning and teardown
- 🧪 Integrated with GitHub Actions for linting, validation and security scanning
- 🧰 Support for multiple environments (e.g., `dev`, `stage`, `prod`)

## 📁 Project Structure

```bash
InfraBox/
│
├── environments/
│   └── dev/                  # Example environment
│       ├── main.tf
│       ├── variables.tf
│       ├── terraform.tfvars
│       └── backend.tf
│
├── modules/
│   ├── networking/
│   ├── virtual_machine/
│   ├── storage_account/
│   └── resource_group/
│
├── cli/                      # Python CLI wrapper logic
│   ├── __init__.py
│   ├── parser.py             # Argument parser
│   ├── utils.py              # Secure command runner, path validation
│   ├── infrstructure_templates.py # Wrapper for generating the required tf files for an environment
│   ├── terraform_utils.py    # Terraform-specific wrappers
│   └── commands/
│       ├── __init__.py
│       ├── create.py         # Implements 'create' command
│       ├── destroy.py        # Implements 'destroy' command
│       └── initialize.py     # Implements 'initialize' command
│
├── InfraBox.py               # Entry point for the CLI
├── .github/
│   └── workflows/            # GitHub Actions for linting, security, smoke tests
│
├── .gitignore
├── .pre-commit-config.yaml   # Pre-commit hook definitions
├── README.md
├── Makefile                  # Common development tasks
├── pyproject.toml            # Configuration for formatters/lint tools
└── requirements.txt          # Python project dependencies
```

## 🧱 Provisioned Resources

Currently, InfraBox provisions the following in Azure:

- Resource Group: `InfraBox-dev-RG`
- Virtual Network and Subnet
- Network Interface
- Static Public IP
- Linux Virtual Machine (Ubuntu 20.04 LTS)
- DNS A Record for VM using Azure DNS

## 🌐 Resource Naming Convention

InfraBox-\<Environment\>-\<ResourceType\>

Example: `InfraBox-dev-VM`, `InfraBox-dev-PublicIP`, etc.  
This allows for easy scaling across environments like *Test*, *Stage*, and *Prod*.

## ⚙️ Getting Started

### 🔧 Prerequisites

- [Terraform CLI](https://developer.hashicorp.com/terraform/downloads)
- Python 3.9+
- Azure CLI (logged in and configured)
- RSA SSH key (required for VM access)
- A registered domain in Azure DNS (optional for DNS record)
- virtualenv (recommended for encapsulation of future project dependencies)

### 📂 Setup Instructions

#### 🗂️ Clone Repository Structure

```bash
git clone https://github.com/<your-username>/infrabox.git && cd infrabox
```

#### 🔑 Create RSA SSH key (if needed)
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/infrabox_key
```
#### 🐍 Install Python dependencies
```bash
pip3 install -r requirements.txt
```

#### 🔧 Install pre-commit hooks
``` bash
pre-commit install
```

#### 🧰 View available CLI options
```bash
python3 InfraBox.py --help
```

#### 📄 Create a terraform.tfvars file
Add the following to a file called `terraform.tfvars` (*already added to .gitignore*):

```hcl
ssh_public_key_path = "~/.ssh/infrabox_key.pub"
dns_zone_name       = "example.com"
resource_group_name = "InfraBox-dev-RG"
```
Infrabox can be used with native terraform from each of the `environments/` sub-directory, or by using the InfraBox CLI wrapper.

### 🧰 Makefile Commands

Use the Makefile to streamline common dev workflows:
```bash
make help            # Show all available commands
make setup           # Setup pre-commit and install dependencies
make lint            # Run ruff for linting
make format          # Auto-format Python files with black
make security        # Run security analysis (bandit)
make test            # Run unit and integration
make coverage        # Run test code coverage
```

### 🧑‍💻 Using the CLI

InfraBox comes with a secure, extensible Python CLI that abstracts Terraform commands.

#### 🧳 Initialize an environment
``` bash
python3 InfraBox.py initialize dev
```

- This will create `main.tf`, `variables.tf`, `outputs.tf` and `provider.tf` for the selected environment, under the `environments/dev` folder
- It will ask for user input for every step of the setup process
- For CIDR subnets, it will automatically check for overlap against other CIDRs in the environments folder

#### 🔨 Create an environment
``` bash
python3 InfraBox.py create dev
```

- This will validate the target environment by running `terraform validate`
- Run `terraform plan`
- Ask for confirmation before applying changes
- Skips `terraform apply` if no changes are detected
- Output environment details once provisioned

#### 🧨 Destroy an environment
``` bash
python3 InfraBox.py destroy dev
```
- Validates the environment
- Runs `terraform plan -destroy`
- Asks for confirmation before applying
- Skips `terraform apply -destroy` if no changes are required

#### 🧪 Dry-run mode
To preview what InfraBox would do without making changes:

```bash
python3 InfraBox.py create dev --dry-run
```

### 🛡️ Security Considerations

- All CLI commands are validated for path traversal and injection
- Sensitive output (Terraform secrets, tokens) is never printed
- All subprocesses use safe execution patterns

### 🤖 Standardization through Pre-commits and GitHub Actions

InfraBox includes CI workflows for:

- ✅ Terraform linting, formatting, and validation (.tf, .tfvars)
- ✅ Static analysis using tflint and tfsec
- ✅ Required checks enforced before merging to main
- ✅ Uses `black` auto-formatting for consistent standards in pre-commit and CI
- ✅ Uses `ruff` linting for optimized code quality checks in pre-commit and CI
- ✅ Uses `bandit` static analysis for security analysis in pre-commit and CI
- ✅ Uses `pytest` testing framework for unit and integration testing in CI
- ✅ Uses `pytest-cov` coverage analysis for generating test coverage reports locally in HTML format

### 📌 DevSecOps Best Practices Followed

- ✅ Shift-left security with early validation
- ✅ Separation of config, code, and secrets
- ✅ Secure CLI with strict input handling
- ✅ Continuous security scanning via GitHub Actions
- ✅ Explicit terraform.required_version and provider constraints

### 👨‍💻 Pre-Commit Hooks

To maintain a clean and secure codebase, InfraBox uses *pre-commit* to enforce standards before code is committed:

#### 🔌 Included Hooks
- black: Formats Python files
- ruff: Linting and formatting consistency
- bandit: Checks for Python security risks

### 📝 Notes on Coding Best Practices Reflected:

- Modules are **resource-type scoped**, keeping them reusable and scalable.
- environments/ uses a clear separation per environment (dev, test, etc.).
- DRY and clarity are balanced - each folder does one thing well.

### 🔄 Roadmap

 - Add environment-specific SSH key pair generation and management
 - Extend CLI to support selective module provisioning
 - Add support for multiple cloud providers (future)
 - Add wrapper output renderer for non-technical users
 - Auto-generate documentation from modules

### 🤝 Contributions

If interested in contributing, please make sure to:
- Use *make setup* before your first commit
- Commit only code that passes all pre-commit hooks
- Create PRs against main with clear descriptions

**Open to issues and pull requests!** Future goals include:

- Modular environment support
- Integration with CI/CD pipelines
- Kubernetes (CKA) and Terraform examples

### 🪪 License

MIT License. See LICENSE.txt file.

### 📌 Author
Created by Andrei-Călin Georgescu, with the goal of making infrastructure provisioning more accessible to others in the software development community.
