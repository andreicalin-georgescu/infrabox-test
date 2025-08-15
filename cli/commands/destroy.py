from cli.terraform_utils import (
    terraform_apply,
    terraform_init,
    terraform_state_has_changes,
    terraform_validate,
)
from cli.utils import get_env_path, prompt_user_confirmation


def run(args):
    env_path = get_env_path(args.environment)

    terraform_init(env_path, dry_run=args.dry_run)
    terraform_validate(env_path, dry_run=args.dry_run)

    if (
        terraform_state_has_changes(env_path, destroy=True, dry_run=args.dry_run)
        and prompt_user_confirmation()
    ):
        terraform_apply(env_path, destroy=True, dry_run=args.dry_run)
