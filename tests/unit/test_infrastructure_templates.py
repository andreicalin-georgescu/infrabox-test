from pathlib import Path
from unittest import mock

import jinja2
import pytest

import cli.infrastructure_templates as infra_templates


@pytest.fixture
def fake_env(monkeypatch, tmp_path):
    # Patch INFRA_ROOT and TEMPLATES_DIR to use a temp directory
    fake_templates = tmp_path / "templates"
    fake_templates.mkdir()
    monkeypatch.setattr(infra_templates, "TEMPLATES_DIR", fake_templates)
    # Patch env to use the new TEMPLATES_DIR
    env = infra_templates.Environment(
        loader=infra_templates.FileSystemLoader(fake_templates),
        autoescape=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    monkeypatch.setattr(infra_templates, "env", env)
    return fake_templates


@pytest.fixture
def template_file(fake_env):
    # Create a simple Jinja2 template
    tpl = fake_env / "main.tf.j2"
    tpl.write_text("Hello, {{ name }}!")
    return tpl


@pytest.fixture
def variables_template(fake_env):
    tpl = fake_env / "variables.tf.j2"
    tpl.write_text("var = {{ var }}")
    return tpl


@pytest.fixture
def outputs_template(fake_env):
    tpl = fake_env / "outputs.tf.j2"
    tpl.write_text("output = {{ output }}")
    return tpl


@pytest.fixture
def provider_template(fake_env):
    tpl = fake_env / "provider.tf.j2"
    tpl.write_text("provider = {{ provider }}")
    return tpl


def test_render_template_writes_file(tmp_path, fake_env, template_file):
    output_path = tmp_path / "main.tf"
    context = {"name": "World"}
    infra_templates.render_template("main.tf.j2", context, output_path)
    assert fake_env.exists()
    assert template_file.exists()
    assert output_path.exists()
    assert output_path.read_text() == "Hello, World!"


def test_render_template_dry_run_prints(monkeypatch, fake_env, template_file, capsys):
    output_path = Path("dummy.tf")
    context = {"name": "DryRun"}
    infra_templates.render_template("main.tf.j2", context, output_path, dry_run=True)
    captured = capsys.readouterr()
    assert monkeypatch is not None
    assert fake_env.exists()
    assert template_file.exists()
    assert "Dry-run mode" in captured.out
    assert "Hello, DryRun!" in captured.out


def test_render_template_invalid_template_raises(fake_env):
    output_path = Path("dummy.tf")
    context = {}
    assert fake_env.exists()
    with pytest.raises(jinja2.exceptions.TemplateNotFound):
        infra_templates.render_template("nonexistent.j2", context, output_path)


def test_generate_main_tf(tmp_path, fake_env, template_file):
    context = {"name": "Main"}
    infra_templates.generate_main_tf(tmp_path, context)
    out = tmp_path / "main.tf"
    assert fake_env.exists()
    assert template_file.exists()
    assert out.exists()
    assert out.read_text() == "Hello, Main!"


def test_generate_variables_tf(tmp_path, fake_env, variables_template):
    context = {"var": 123}
    infra_templates.generate_variables_tf(tmp_path, context)
    out = tmp_path / "variables.tf"
    assert fake_env.exists()
    assert variables_template.exists()
    assert out.exists()
    assert out.read_text() == "var = 123"


def test_generate_outputs_tf(tmp_path, fake_env, outputs_template):
    context = {"output": "foo"}
    infra_templates.generate_outputs_tf(tmp_path, context)
    out = tmp_path / "outputs.tf"
    assert fake_env.exists()
    assert outputs_template.exists()
    assert out.exists()
    assert out.read_text() == "output = foo"


def test_generate_provider_tf(tmp_path, fake_env, provider_template):
    context = {"provider": "aws"}
    infra_templates.generate_provider_tf(tmp_path, context)
    out = tmp_path / "provider.tf"
    assert fake_env.exists()
    assert provider_template.exists()
    assert out.exists()
    assert out.read_text() == "provider = aws"


def test_generate_main_tf_dry_run(tmp_path, fake_env, template_file, capsys):
    context = {"name": "Dry"}
    infra_templates.generate_main_tf(tmp_path, context, dry_run=True)
    captured = capsys.readouterr()
    assert fake_env.exists()
    assert template_file.exists()
    assert "Dry-run mode" in captured.out
    assert "Hello, Dry!" in captured.out
    assert not (tmp_path / "main.tf").exists()


def test_generate_variables_tf_dry_run(tmp_path, fake_env, variables_template, capsys):
    context = {"var": "dry"}
    infra_templates.generate_variables_tf(tmp_path, context, dry_run=True)
    captured = capsys.readouterr()
    assert fake_env.exists()
    assert variables_template.exists()
    assert "Dry-run mode" in captured.out
    assert "var = dry" in captured.out
    assert not (tmp_path / "variables.tf").exists()


def test_generate_outputs_tf_dry_run(tmp_path, fake_env, outputs_template, capsys):
    context = {"output": "dry"}
    infra_templates.generate_outputs_tf(tmp_path, context, dry_run=True)
    captured = capsys.readouterr()
    assert fake_env.exists()
    assert outputs_template.exists()
    assert "Dry-run mode" in captured.out
    assert "output = dry" in captured.out
    assert not (tmp_path / "outputs.tf").exists()


def test_generate_provider_tf_dry_run(tmp_path, fake_env, provider_template, capsys):
    context = {"provider": "dry"}
    infra_templates.generate_provider_tf(tmp_path, context, dry_run=True)
    captured = capsys.readouterr()
    assert fake_env.exists()
    assert provider_template.exists()
    assert "Dry-run mode" in captured.out
    assert "provider = dry" in captured.out
    assert not (tmp_path / "provider.tf").exists()


def test_render_template_output_path_is_pathlike(tmp_path, fake_env, template_file):
    # Accepts Path-like objects
    class DummyPath(str):
        def write_text(self, content):
            self.content = content

    dummy = tmp_path / "main.tf"
    context = {"name": "PathLike"}
    infra_templates.render_template("main.tf.j2", context, dummy)
    assert fake_env.exists()
    assert template_file.exists()
    assert dummy.read_text() == "Hello, PathLike!"


def test_render_template_context_edge_cases(tmp_path, fake_env, template_file):
    # Context with missing variable
    output_path = tmp_path / "main.tf"
    context = {}
    # Jinja2 will render as "Hello, !" if 'name' is missing
    infra_templates.render_template("main.tf.j2", context, output_path)
    assert fake_env.exists()
    assert template_file.exists()
    assert output_path.read_text() == "Hello, !"


def test_render_template_non_string_context(tmp_path, fake_env, template_file):
    output_path = tmp_path / "main.tf"
    context = {"name": 123}
    infra_templates.render_template("main.tf.j2", context, output_path)
    assert fake_env.exists()
    assert template_file.exists()
    assert output_path.read_text() == "Hello, 123!"


def test_render_template_output_path_permission_error(
    monkeypatch, fake_env, template_file
):
    output_path = Path("/root/forbidden.tf")
    context = {"name": "fail"}
    # Patch write_text to raise PermissionError
    assert monkeypatch is not None
    assert fake_env.exists()
    assert template_file.exists()
    with mock.patch.object(Path, "write_text", side_effect=PermissionError):
        with pytest.raises(PermissionError):
            infra_templates.render_template("main.tf.j2", context, output_path)
