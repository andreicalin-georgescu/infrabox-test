import ipaddress
import os
import re
import subprocess  # nosec B404
import sys
from pathlib import Path

VALID_ENVIRONMENTS = {"dev", "stage", "prod"}
INFRA_ROOT = Path(__file__).resolve().parent.parent
ENVIRONMENTS_DIR = INFRA_ROOT / "environments"
DEFAULT_VNET = "10.0.0.0/16"
DEFAULT_SUBNET = "10.0.1.0/24"


def sanitize_input(value: str) -> str:
    """Sanitize CLI input to avoid injection or path traversal."""
    return re.sub(r"[^\w\-]", "", value.strip())


def sanitize_env_name(name):
    """Return a safe environment name (alphanumeric, dashes, underscores)."""
    return "".join(c for c in name if c.isalnum() or c in ("-", "_")).lower()


def validate_environment(env, allow_new=False):
    if not allow_new and env not in VALID_ENVIRONMENTS:
        raise ValueError(f"Invalid environment: {env}")


def get_env_path(env):
    """Get the path to the specified environment directory. Abort if it doesn't exist."""
    validate_environment(env)
    env_path = os.path.join(ENVIRONMENTS_DIR, env)

    if not os.path.exists(env_path):
        print(f"INFRABOX: ❌ Environment directory '{env}' does not exist.")
        print(
            f"INFRABOX: 💡 You may need to run: `infrabox.py initialize {env}` first."
        )
        sys.exit(1)

    return env_path


def validate_cidr(cidr: str) -> str:
    """Ensure the given CIDR is valid."""
    try:
        return str(ipaddress.IPv4Network(cidr, strict=True))
    except Exception as e:
        raise ValueError(f"Invalid CIDR '{cidr}': {e}") from e


def check_cidr_overlap(new_cidr: str, current_env: str, environments_dir: Path) -> None:
    print(
        f"INFRABOX: Checking overlap for new_cidr={new_cidr}, current_env={current_env}, environments_dir={environments_dir}"
    )
    new_network = ipaddress.IPv4Network(new_cidr, strict=True)

    for env_dir in environments_dir.iterdir():
        if not env_dir.is_dir() or env_dir.name == current_env:
            continue

        variables_file = env_dir / "variables.tf"
        if not variables_file.exists():
            continue

        content = variables_file.read_text()
        matches = re.findall(r'vnet_cidr\s*=\s*["\']([^"\']+)["\']', content)

        for match in matches:
            existing_net = ipaddress.IPv4Network(match, strict=True)
            if new_network.overlaps(existing_net):
                print(
                    f"INFRABOX: Overlap found: {new_network} overlaps {existing_net} in {env_dir.name}"
                )
                raise ValueError(
                    f"CIDR {new_network} overlaps with {existing_net} in environment '{env_dir.name}'"
                )


def run_cmd(cmd, cwd, dry_run=False, capture_output=True):
    """Run a command in a specified directory."""
    print(f"\nINFRABOX: 📦 Running command: {' '.join(cmd)} in {cwd}")
    if dry_run:
        print("INFRABOX: 🔍 Dry-run mode: command not executed.")
        return

    # subprocess call is safe — shell=False and cmd is a validated list

    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=capture_output,
        text=True,
        shell=False,
        check=False,
    )  # nosec: B603
    if capture_output:
        print(result.stdout)
    return result


def prompt_input(prompt, default=""):
    """Ask user for input with a default fallback."""
    response = input(f"{prompt} [{default}]: ").strip()
    return response or default


def prompt_with_default(prompt_text: str, default: str) -> str:
    """Prompt user for input, return sanitized string or default."""
    user_input = input(f"{prompt_text} [default: {default}]: ").strip()
    return sanitize_input(user_input) if user_input else default


def prompt_user_confirmation(message="INFRABOX: Proceed?", default=False):
    """Prompt the user for confirmation with a default option."""
    suffix = "[Y/n]" if default else "[y/N]"
    answer = input(f"{message} {suffix}: ").strip().lower()
    if not answer:
        return default
    return answer in ("y", "yes")
