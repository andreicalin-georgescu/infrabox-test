from types import SimpleNamespace

import pytest

import cli.commands.initialize as initialize_mod


@pytest.fixture
def temp_env_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(initialize_mod, "ENVIRONMENTS_DIR", tmp_path)
    yield tmp_path


def mock_prompt_with_default(_prompt, default):
    # Return the default for all prompts
    return default


def mock_validate_cidr(cidr):
    # Return the input as valid
    return cidr


def test_initialize_dry_run(monkeypatch, temp_env_dir, capsys):
    # Arrange
    args = SimpleNamespace(environment="testenv", dry_run=True)
    monkeypatch.setattr(initialize_mod, "prompt_with_default", mock_prompt_with_default)
    monkeypatch.setattr(initialize_mod, "validate_cidr", mock_validate_cidr)
    monkeypatch.setattr(initialize_mod, "check_cidr_overlap", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_variables_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_main_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_outputs_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_provider_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "terraform_init", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "terraform_validate", lambda *_a, **_k: None)

    # Act
    initialize_mod.run(args)
    out = capsys.readouterr().out

    # Assert
    assert "Created environment directory" not in out
    assert not (temp_env_dir / "testenv").exists()


def test_initialize_creates_files(monkeypatch, temp_env_dir):
    args = SimpleNamespace(environment="prod", dry_run=False)
    monkeypatch.setattr(initialize_mod, "prompt_with_default", mock_prompt_with_default)
    monkeypatch.setattr(initialize_mod, "validate_cidr", mock_validate_cidr)
    monkeypatch.setattr(initialize_mod, "check_cidr_overlap", lambda *_a, **_k: None)

    # Track file creation
    created_files = []

    def fake_generate_tf(env_path, context, **_kwargs):
        # Simulate file creation
        for fname in ["variables.tf", "main.tf", "outputs.tf", "provider.tf"]:
            fpath = env_path / fname
            fpath.parent.mkdir(parents=True, exist_ok=True)
            fpath.write_text(f"# {fname} for {context['environment']}")
            created_files.append(fpath)

    monkeypatch.setattr(initialize_mod, "generate_variables_tf", fake_generate_tf)
    monkeypatch.setattr(initialize_mod, "generate_main_tf", fake_generate_tf)
    monkeypatch.setattr(initialize_mod, "generate_outputs_tf", fake_generate_tf)
    monkeypatch.setattr(initialize_mod, "generate_provider_tf", fake_generate_tf)
    monkeypatch.setattr(initialize_mod, "terraform_init", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "terraform_validate", lambda *_a, **_k: None)

    # Act
    initialize_mod.run(args)

    # Assert
    env_path = temp_env_dir / "prod"
    assert env_path.exists()
    for fname in ["variables.tf", "main.tf", "outputs.tf", "provider.tf"]:
        assert (env_path / fname).exists()
        assert (env_path / fname).read_text().startswith("#")


def test_initialize_aborts_if_env_exists(monkeypatch, temp_env_dir, capsys):
    # Arrange
    env_name = "existing"
    env_path = temp_env_dir / env_name
    env_path.mkdir(parents=True)
    args = SimpleNamespace(environment=env_name, dry_run=False)
    monkeypatch.setattr(initialize_mod, "ENVIRONMENTS_DIR", temp_env_dir)
    monkeypatch.setattr(initialize_mod, "prompt_with_default", mock_prompt_with_default)
    monkeypatch.setattr(initialize_mod, "validate_cidr", mock_validate_cidr)
    monkeypatch.setattr(initialize_mod, "check_cidr_overlap", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_variables_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_main_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_outputs_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_provider_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "terraform_init", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "terraform_validate", lambda *_a, **_k: None)

    # Act
    initialize_mod.run(args)
    out = capsys.readouterr().out

    # Assert
    assert "already exist" in out


@pytest.mark.parametrize("env_name", ["dev", "stage", "prod"])
def test_initialize_supported_environments(monkeypatch, temp_env_dir, env_name):
    args = SimpleNamespace(environment=env_name, dry_run=False)
    monkeypatch.setattr(initialize_mod, "prompt_with_default", mock_prompt_with_default)
    monkeypatch.setattr(initialize_mod, "validate_cidr", mock_validate_cidr)
    monkeypatch.setattr(initialize_mod, "check_cidr_overlap", lambda *_a, **_k: None)

    def fake_generate_tf(env_path, context, **_kwargs):
        for fname in ["variables.tf", "main.tf", "outputs.tf", "provider.tf"]:
            fpath = env_path / fname
            fpath.parent.mkdir(parents=True, exist_ok=True)
            fpath.write_text(f"# {fname} for {context['environment']}")

    monkeypatch.setattr(initialize_mod, "generate_variables_tf", fake_generate_tf)
    monkeypatch.setattr(initialize_mod, "generate_main_tf", fake_generate_tf)
    monkeypatch.setattr(initialize_mod, "generate_outputs_tf", fake_generate_tf)
    monkeypatch.setattr(initialize_mod, "generate_provider_tf", fake_generate_tf)
    monkeypatch.setattr(initialize_mod, "terraform_init", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "terraform_validate", lambda *_a, **_k: None)

    initialize_mod.run(args)
    env_path = temp_env_dir / env_name
    assert env_path.exists()
    for fname in ["variables.tf", "main.tf", "outputs.tf", "provider.tf"]:
        assert (env_path / fname).exists()


def test_initialize_custom_user_input(monkeypatch, temp_env_dir):
    args = SimpleNamespace(environment="dev", dry_run=False)

    # Custom user input for name_prefix
    def custom_prompt(prompt, default):
        if "prefix" in prompt:
            return "customprefix"
        return default

    monkeypatch.setattr(initialize_mod, "prompt_with_default", custom_prompt)
    monkeypatch.setattr(initialize_mod, "validate_cidr", mock_validate_cidr)
    monkeypatch.setattr(initialize_mod, "check_cidr_overlap", lambda *_a, **_k: None)

    def fake_generate_variables_tf(env_path, context, **_kwargs):
        fpath = env_path / "variables.tf"
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(f'name_prefix = "{context.get("name_prefix", "")}"')

    monkeypatch.setattr(
        initialize_mod, "generate_variables_tf", fake_generate_variables_tf
    )
    monkeypatch.setattr(initialize_mod, "generate_main_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_outputs_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_provider_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "terraform_init", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "terraform_validate", lambda *_a, **_k: None)

    initialize_mod.run(args)
    env_path = temp_env_dir / "dev"
    content = (env_path / "variables.tf").read_text()
    assert 'name_prefix = "customprefix"' in content


def test_initialize_template_content(monkeypatch, temp_env_dir):
    args = SimpleNamespace(environment="dev", dry_run=False)

    # Patch prompt_with_default to return specific values for each prompt
    def prompt_with_default_side_effect(prompt, default):
        if "prefix" in prompt.lower():
            return "customprefix"
        if "cidr" in prompt.lower():
            return "10.0.0.0/16"
        if "location" in prompt.lower():
            return "westeurope"
        if "dns" in prompt.lower():
            return "customdns"
        return default

    monkeypatch.setattr(
        initialize_mod, "prompt_with_default", prompt_with_default_side_effect
    )
    monkeypatch.setattr(initialize_mod, "validate_cidr", lambda cidr: cidr)
    monkeypatch.setattr(initialize_mod, "check_cidr_overlap", lambda *_a, **_k: None)

    # Patch terraform functions to no-ops
    monkeypatch.setattr(initialize_mod, "terraform_init", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "terraform_validate", lambda *_a, **_k: None)

    # Act
    initialize_mod.run(args)
    env_path = temp_env_dir / "dev"
    content = (env_path / "variables.tf").read_text()

    # Assert: Check that user inputted values are present in the generated file
    assert "customprefix" in content
    assert "10.0.0.0/16" in content
    assert "westeurope" in content
    assert "customdns" in content


def test_initialize_cidr_overlap(monkeypatch, temp_env_dir, capsys):
    args = SimpleNamespace(environment="dev", dry_run=False)
    monkeypatch.setattr(initialize_mod, "prompt_with_default", mock_prompt_with_default)
    monkeypatch.setattr(initialize_mod, "validate_cidr", mock_validate_cidr)

    def raise_overlap(*_a, **_k):
        raise ValueError("CIDR overlap detected")

    monkeypatch.setattr(initialize_mod, "check_cidr_overlap", raise_overlap)
    monkeypatch.setattr(initialize_mod, "generate_variables_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_main_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_outputs_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_provider_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "terraform_init", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "terraform_validate", lambda *_a, **_k: None)

    initialize_mod.run(args)
    out = capsys.readouterr().out
    assert temp_env_dir is not None
    assert "CIDR overlap detected" in out or "overlap" in out.lower()


def test_initialize_keyboard_interrupt(monkeypatch, temp_env_dir, capsys):
    args = SimpleNamespace(environment="dev", dry_run=False)
    monkeypatch.setattr(initialize_mod, "prompt_with_default", mock_prompt_with_default)
    monkeypatch.setattr(initialize_mod, "validate_cidr", mock_validate_cidr)
    monkeypatch.setattr(initialize_mod, "check_cidr_overlap", lambda *_a, **_k: None)

    def raise_keyboard_interrupt(*_a, **_k):
        raise KeyboardInterrupt()

    monkeypatch.setattr(
        initialize_mod, "generate_variables_tf", raise_keyboard_interrupt
    )
    monkeypatch.setattr(initialize_mod, "generate_main_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_outputs_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_provider_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "terraform_init", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "terraform_validate", lambda *_a, **_k: None)

    initialize_mod.run(args)
    out = capsys.readouterr().out
    env_path = temp_env_dir / "dev"

    assert temp_env_dir is not None
    assert "aborted" in out.lower() or "interrupt" in out.lower()
    assert "removed environment directory" in out.lower()
    assert not env_path.exists()


def test_initialize_terraform_calls(monkeypatch, temp_env_dir):
    args = SimpleNamespace(environment="dev", dry_run=False)
    monkeypatch.setattr(initialize_mod, "prompt_with_default", mock_prompt_with_default)
    monkeypatch.setattr(initialize_mod, "validate_cidr", mock_validate_cidr)
    monkeypatch.setattr(initialize_mod, "check_cidr_overlap", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_variables_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_main_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_outputs_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_provider_tf", lambda *_a, **_k: None)

    called = {"init": False, "validate": False}

    def fake_terraform_init(*_a, **_k):
        called["init"] = True

    def fake_terraform_validate(*_a, **_k):
        called["validate"] = True

    monkeypatch.setattr(initialize_mod, "terraform_init", fake_terraform_init)
    monkeypatch.setattr(initialize_mod, "terraform_validate", fake_terraform_validate)

    initialize_mod.run(args)
    assert temp_env_dir is not None
    assert called["init"]
    assert called["validate"]


def test_initialize_dry_run_skips_terraform(monkeypatch, temp_env_dir, capsys):
    args = SimpleNamespace(environment="dev", dry_run=True)
    monkeypatch.setattr(initialize_mod, "prompt_with_default", mock_prompt_with_default)
    monkeypatch.setattr(initialize_mod, "validate_cidr", mock_validate_cidr)
    monkeypatch.setattr(initialize_mod, "check_cidr_overlap", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_variables_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_main_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_outputs_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_provider_tf", lambda *_a, **_k: None)

    # Act
    initialize_mod.run(args)
    out = capsys.readouterr().out

    # Assert
    assert temp_env_dir is not None
    assert "dry-run mode: command not executed" in out.lower()


def test_initialize_unexpected_error_removes_env_dir(monkeypatch, temp_env_dir, capsys):
    args = SimpleNamespace(environment="dev", dry_run=False)
    monkeypatch.setattr(initialize_mod, "prompt_with_default", mock_prompt_with_default)
    monkeypatch.setattr(initialize_mod, "validate_cidr", mock_validate_cidr)
    monkeypatch.setattr(initialize_mod, "check_cidr_overlap", lambda *_a, **_k: None)

    # Patch generate_main_tf to raise an unexpected error
    def raise_unexpected_error(*_a, **_k):
        raise RuntimeError("Unexpected error during template generation")

    monkeypatch.setattr(initialize_mod, "generate_variables_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_main_tf", raise_unexpected_error)
    monkeypatch.setattr(initialize_mod, "generate_outputs_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "generate_provider_tf", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "terraform_init", lambda *_a, **_k: None)
    monkeypatch.setattr(initialize_mod, "terraform_validate", lambda *_a, **_k: None)

    # Act
    with pytest.raises(
        RuntimeError, match="Unexpected error during template generation"
    ):
        initialize_mod.run(args)
    out = capsys.readouterr().out
    env_path = temp_env_dir / "dev"

    # Assert
    assert "removed environment directory" in out.lower()
    assert not env_path.exists()
