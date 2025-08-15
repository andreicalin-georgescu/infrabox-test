from unittest import mock

import pytest

import cli.commands.create as create_cmd


class DummyArgs:
    def __init__(self, environment="dev", dry_run=False):
        self.environment = environment
        self.dry_run = dry_run


@pytest.fixture
def patch_all(monkeypatch):
    patches = {}
    for name in [
        "get_env_path",
        "terraform_init",
        "terraform_validate",
        "terraform_state_has_changes",
        "prompt_user_confirmation",
        "terraform_apply",
    ]:
        patch = mock.Mock()
        monkeypatch.setattr(f"cli.commands.create.{name}", patch)
        patches[name] = patch
    return patches


def test_run_happy_path_apply(monkeypatch, patch_all):
    args = DummyArgs()
    patch_all["get_env_path"].return_value = "env_path"
    patch_all["terraform_state_has_changes"].return_value = True
    patch_all["prompt_user_confirmation"].return_value = True

    create_cmd.run(args)

    patch_all["get_env_path"].assert_called_once_with("dev")
    patch_all["terraform_init"].assert_called_once_with("env_path", dry_run=False)
    patch_all["terraform_validate"].assert_called_once_with("env_path", dry_run=False)
    patch_all["terraform_state_has_changes"].assert_called_once_with(
        "env_path", dry_run=False
    )
    patch_all["prompt_user_confirmation"].assert_called_once_with()
    patch_all["terraform_apply"].assert_called_once_with("env_path", dry_run=False)
    assert monkeypatch is not None


def test_run_no_changes_no_apply(monkeypatch, patch_all):
    args = DummyArgs()
    patch_all["get_env_path"].return_value = "env_path"
    patch_all["terraform_state_has_changes"].return_value = False

    create_cmd.run(args)

    patch_all["terraform_apply"].assert_not_called()
    patch_all["prompt_user_confirmation"].assert_not_called()

    assert monkeypatch is not None


def test_run_changes_but_user_declines(monkeypatch, patch_all):
    args = DummyArgs()
    patch_all["get_env_path"].return_value = "env_path"
    patch_all["terraform_state_has_changes"].return_value = True
    patch_all["prompt_user_confirmation"].return_value = False

    create_cmd.run(args)

    patch_all["terraform_apply"].assert_not_called()
    patch_all["prompt_user_confirmation"].assert_called_once_with()

    assert monkeypatch is not None


def test_run_dry_run(monkeypatch, patch_all):
    args = DummyArgs(dry_run=True)
    patch_all["get_env_path"].return_value = "env_path"
    patch_all["terraform_state_has_changes"].return_value = True
    patch_all["prompt_user_confirmation"].return_value = True

    create_cmd.run(args)

    patch_all["terraform_init"].assert_called_once_with("env_path", dry_run=True)
    patch_all["terraform_validate"].assert_called_once_with("env_path", dry_run=True)
    patch_all["terraform_state_has_changes"].assert_called_once_with(
        "env_path", dry_run=True
    )
    patch_all["terraform_apply"].assert_called_once_with("env_path", dry_run=True)

    assert monkeypatch is not None


def test_run_get_env_path_raises(monkeypatch, patch_all):
    args = DummyArgs()
    patch_all["get_env_path"].side_effect = Exception("fail")
    with pytest.raises(Exception, match="fail"):
        create_cmd.run(args)
    patch_all["terraform_init"].assert_not_called()
    assert monkeypatch is not None


def test_run_terraform_init_raises(monkeypatch, patch_all):
    args = DummyArgs()
    patch_all["get_env_path"].return_value = "env_path"
    patch_all["terraform_init"].side_effect = RuntimeError("init fail")
    with pytest.raises(RuntimeError, match="init fail"):
        create_cmd.run(args)
    patch_all["terraform_validate"].assert_not_called()
    assert monkeypatch is not None


def test_run_terraform_validate_raises(monkeypatch, patch_all):
    args = DummyArgs()
    patch_all["get_env_path"].return_value = "env_path"
    patch_all["terraform_validate"].side_effect = RuntimeError("validate fail")
    with pytest.raises(RuntimeError, match="validate fail"):
        create_cmd.run(args)
    patch_all["terraform_state_has_changes"].assert_not_called()
    assert monkeypatch is not None


def test_run_terraform_state_has_changes_raises(monkeypatch, patch_all):
    args = DummyArgs()
    patch_all["get_env_path"].return_value = "env_path"
    patch_all["terraform_state_has_changes"].side_effect = RuntimeError("plan fail")
    with pytest.raises(RuntimeError, match="plan fail"):
        create_cmd.run(args)
    patch_all["prompt_user_confirmation"].assert_not_called()
    assert monkeypatch is not None


def test_run_terraform_apply_raises(monkeypatch, patch_all):
    args = DummyArgs()
    patch_all["get_env_path"].return_value = "env_path"
    patch_all["terraform_state_has_changes"].return_value = True
    patch_all["prompt_user_confirmation"].return_value = True
    patch_all["terraform_apply"].side_effect = RuntimeError("apply fail")
    assert monkeypatch is not None
    with pytest.raises(RuntimeError, match="apply fail"):
        create_cmd.run(args)
