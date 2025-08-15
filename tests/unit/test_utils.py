import os
import re
import types

import pytest

from cli import utils


def test_sanitize_input_normal():
    assert utils.sanitize_input("hello-world_123") == "hello-world_123"


def test_sanitize_input_removes_special_chars():
    assert utils.sanitize_input("hello; rm -rf /") == "hellorm-rf"


def test_sanitize_input_edge_empty():
    assert utils.sanitize_input("   ") == ""


def test_sanitize_env_name_normal():
    assert utils.sanitize_env_name("Dev-Env_1") == "dev-env_1"


def test_sanitize_env_name_removes_invalid():
    assert utils.sanitize_env_name("env!@#name") == "envname"


def test_sanitize_env_name_edge_empty():
    assert utils.sanitize_env_name("") == ""


def test_validate_environment_valid():
    utils.validate_environment("dev")


def test_validate_environment_invalid():
    with pytest.raises(ValueError):
        utils.validate_environment("invalid")


def test_validate_environment_allow_new():
    # Should not raise
    utils.validate_environment("UserAcceptance", allow_new=True)


def test_get_env_path_exists(tmp_path, monkeypatch):
    env = "dev"
    env_dir = tmp_path / env
    env_dir.mkdir()
    monkeypatch.setattr(utils, "ENVIRONMENTS_DIR", tmp_path)
    monkeypatch.setattr(utils, "validate_environment", lambda _e: None)
    monkeypatch.setattr(os.path, "exists", lambda _p: True)
    assert utils.get_env_path(env) == str(tmp_path / env)


def test_get_env_path_not_exists(monkeypatch, capsys, tmp_path):
    env = "dev"
    fake_env_dir = tmp_path / "fake"
    monkeypatch.setattr(utils, "ENVIRONMENTS_DIR", fake_env_dir)
    monkeypatch.setattr(utils, "validate_environment", lambda _e: None)
    monkeypatch.setattr(os.path, "exists", lambda _p: False)
    with pytest.raises(SystemExit):
        utils.get_env_path(env)
    out = capsys.readouterr().out
    assert "does not exist" in out


def test_validate_cidr_valid():
    assert utils.validate_cidr("10.0.0.0/24") == "10.0.0.0/24"


def test_validate_cidr_invalid():
    with pytest.raises(ValueError):
        utils.validate_cidr("not-a-cidr")


def test_validate_cidr_edge_hostmask():
    assert utils.validate_cidr("192.168.1.1/32") == "192.168.1.1/32"


def make_env_dir_with_cidr(tmp_path, env_name, cidr):
    env_dir = tmp_path / env_name
    env_dir.mkdir()
    (env_dir / "variables.tf").write_text(f'vnet_cidr = "{cidr}"\n')
    return env_dir


def test_check_cidr_overlap_no_overlap(tmp_path):
    make_env_dir_with_cidr(tmp_path, "env1", "10.1.0.0/16")
    utils.check_cidr_overlap("10.2.0.0/16", "env2", tmp_path)


def test_check_cidr_overlap_skips_current_env_and_non_dirs(tmp_path):
    make_env_dir_with_cidr(tmp_path, "env2", "10.0.0.0/24")
    (tmp_path / "not_a_dir").write_text("not a dir")
    (tmp_path / "empty_env").mkdir()

    utils.check_cidr_overlap("10.0.1.0/24", "env2", tmp_path)


def test_check_cidr_overlap_with_overlap(tmp_path):
    # Overlapping CIDRs: both /24
    make_env_dir_with_cidr(tmp_path, "env1", "10.0.0.0/24")
    content = (tmp_path / "env1" / "variables.tf").read_text()
    matches = re.findall(r'vnet_cidr\s*=\s*["\']([^"\']+)["\']', content)
    assert matches == ["10.0.0.0/24"], f"Regex did not match: {content}"
    with pytest.raises(ValueError) as e:
        utils.check_cidr_overlap("10.0.0.0/24", "env2", tmp_path)
    assert "overlaps" in str(e.value)


def test_run_cmd_normal(monkeypatch, tmp_path):
    fake_result = types.SimpleNamespace(stdout="output", returncode=0)
    monkeypatch.setattr("subprocess.run", lambda *_a, **_k: fake_result)
    result = utils.run_cmd(
        ["echo", "hi"], str(tmp_path), dry_run=False, capture_output=True
    )
    assert result.stdout == "output"


def test_run_cmd_dry_run(capsys, tmp_path):
    result = utils.run_cmd(["echo", "hi"], str(tmp_path), dry_run=True)
    out = capsys.readouterr().out
    assert "Dry-run mode" in out
    assert result is None


def test_run_cmd_capture_output_false(monkeypatch, tmp_path):
    fake_result = types.SimpleNamespace(stdout="output", returncode=0)
    monkeypatch.setattr("subprocess.run", lambda *_a, **_k: fake_result)
    result = utils.run_cmd(
        ["echo", "hi"], str(tmp_path), dry_run=False, capture_output=False
    )
    assert result.stdout == "output"


def test_prompt_input_normal(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _prompt: "foo")
    assert utils.prompt_input("Prompt", default="bar") == "foo"


def test_prompt_input_default(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _prompt: "")
    assert utils.prompt_input("Prompt", default="bar") == "bar"


def test_prompt_with_default_user(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _prompt: "foo!@#")
    assert utils.prompt_with_default("Prompt", "bar") == "foo"


def test_prompt_with_default_default(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _prompt: "")
    assert utils.prompt_with_default("Prompt", "bar") == "bar"


@pytest.mark.parametrize(
    "user_input,default,expected",
    [
        ("y", False, True),
        ("yes", False, True),
        ("", False, False),
        ("n", True, False),
        ("", True, True),
    ],
)
def test_prompt_user_confirmation(monkeypatch, user_input, default, expected):
    monkeypatch.setattr("builtins.input", lambda _prompt: user_input)
    assert utils.prompt_user_confirmation("Proceed?", default=default) == expected
