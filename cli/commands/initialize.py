import shutil

from cli.infrastructure_templates import (
    generate_main_tf,
    generate_outputs_tf,
    generate_provider_tf,
    generate_variables_tf,
)
from cli.terraform_utils import terraform_init, terraform_validate
from cli.utils import (
    ENVIRONMENTS_DIR,
    check_cidr_overlap,
    prompt_with_default,
    sanitize_input,
    validate_cidr,
)


def run(args):
    environment = sanitize_input(args.environment.lower())
    env_path = ENVIRONMENTS_DIR / environment

    if env_path.exists():
        print(
            f"INFRABOX: ⚠️ Environment files for environment '{environment}' already exist. Aborting."
        )
        return

    try:
        # Prompt user for core environment values
        name_prefix = prompt_with_default("Enter name prefix", "Infrabox")
        location = prompt_with_default("Enter Azure location", "westeurope")
        dns_zone_name = prompt_with_default(
            "Enter DNS zone name", f"{name_prefix}-{environment}.com"
        )
        admin_username = prompt_with_default("Enter admin username", "azureuser")
        ssh_public_key_path = prompt_with_default(
            "Enter path to SSH public key", "~/.ssh/id_rsa_infrabox.pub"
        )

        vnet_cidr = validate_cidr(prompt_with_default("Enter VNet CIDR", "10.0.0.0/16"))
        subnet_cidr = validate_cidr(
            prompt_with_default("Enter Subnet CIDR", "10.0.1.0/24")
        )

        # CIDR overlap checks
        try:
            check_cidr_overlap(vnet_cidr, environment, ENVIRONMENTS_DIR)
            check_cidr_overlap(subnet_cidr, environment, ENVIRONMENTS_DIR)
        except ValueError as e:
            print(f"INFRABOX: ❌ {e}")
            return

        if not args.dry_run:
            env_path.mkdir(parents=True)
            print(f"INFRABOX: 📁 Created environment directory at {env_path}")

        # Prepare context for rendering templates
        context = {
            "name_prefix": name_prefix,
            "environment": environment,
            "location": location,
            "dns_zone_name": dns_zone_name,
            "admin_username": admin_username,
            "ssh_public_key_path": ssh_public_key_path,
            "vnet_address_space": vnet_cidr,
            "subnet_address_space": subnet_cidr,
        }

        # Render all Terraform files using jinja2 templates
        generate_variables_tf(env_path, context, dry_run=args.dry_run)
        generate_main_tf(env_path, context, dry_run=args.dry_run)
        generate_outputs_tf(env_path, context, dry_run=args.dry_run)
        generate_provider_tf(env_path, context, dry_run=args.dry_run)

        # Run Terraform initialization & validation
        terraform_init(env_path, dry_run=args.dry_run)
        terraform_validate(env_path, dry_run=args.dry_run)

        if not args.dry_run:
            print(
                f"INFRABOX: ✅ Initialization and validation complete for environment: {environment}"
                f"\nINFRABOX: 📂 Environment files created at {env_path}."
            )
    except KeyboardInterrupt:
        print("\nINFRABOX: ⚠️ Initialization interrupted by user.")
        if not args.dry_run and env_path.exists():
            shutil.rmtree(env_path)
            print(
                f"INFRABOX: 🧹 Removed environment directory {env_path} due to error."
            )
    except Exception as e:
        print(f"INFRABOX: ❌ Unexpected error: {e}")
        if not args.dry_run and env_path.exists():
            shutil.rmtree(env_path)
            print(
                f"INFRABOX: 🧹 Removed environment directory {env_path} due to error."
            )
        raise
