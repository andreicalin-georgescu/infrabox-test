from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from cli.utils import INFRA_ROOT

TEMPLATES_DIR = INFRA_ROOT / "templates"
env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=True,
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_template(
    template_name: str, context: dict, output_path: Path, dry_run=False
):
    template = env.get_template(template_name)
    rendered_content = template.render(context)

    if dry_run:
        print(f"INFRABOX: 🔍 Dry-run mode: {output_path.name} not written to disk.")
        print(rendered_content)
    else:
        output_path.write_text(rendered_content)
        print(f"INFRABOX: 📝 Generated {output_path.name}")


def generate_main_tf(env_path: Path, context: dict, dry_run=False):
    render_template("main.tf.j2", context, env_path / "main.tf", dry_run)


def generate_variables_tf(env_path: Path, context: dict, dry_run=False):
    render_template("variables.tf.j2", context, env_path / "variables.tf", dry_run)


def generate_outputs_tf(env_path: Path, context: dict, dry_run=False):
    render_template("outputs.tf.j2", context, env_path / "outputs.tf", dry_run)


def generate_provider_tf(env_path: Path, context: dict, dry_run: bool = False):
    render_template("provider.tf.j2", context, env_path / "provider.tf", dry_run)
