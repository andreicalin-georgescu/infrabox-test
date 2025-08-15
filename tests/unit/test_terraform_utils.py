from unittest import mock

import pytest

import cli.terraform_utils as tf_utils


@pytest.fixture
def fake_env_path(tmp_path):
    return tmp_path / "env"


def test_terraform_init_calls_run_cmd(fake_env_path):
    with mock.patch("cli.terraform_utils.run_cmd") as run_cmd:
        tf_utils.terraform_init(fake_env_path, dry_run=True)
        run_cmd.assert_called_once_with(
            ["terraform", "init", "-input=false"],
            cwd=fake_env_path,
            dry_run=True,
            capture_output=True,
        )


def test_terraform_validate_calls_run_cmd(fake_env_path):
    with mock.patch("cli.terraform_utils.run_cmd") as run_cmd:
        tf_utils.terraform_validate(fake_env_path, dry_run=False)
        run_cmd.assert_called_once_with(
            ["terraform", "validate"],
            cwd=fake_env_path,
            dry_run=False,
            capture_output=True,
        )


@pytest.mark.parametrize(
    "destroy,expected_cmd",
    [
        (False, ["terraform", "plan", "-detailed-exitcode"]),
        (True, ["terraform", "plan", "-detailed-exitcode", "-destroy"]),
    ],
)
def test_terraform_plan_calls_run_cmd(fake_env_path, destroy, expected_cmd):
    with mock.patch("cli.terraform_utils.run_cmd") as run_cmd:
        tf_utils.terraform_plan(fake_env_path, destroy=destroy, dry_run=True)
        run_cmd.assert_called_once_with(
            expected_cmd,
            cwd=fake_env_path,
            dry_run=True,
            capture_output=False,
        )


@pytest.mark.parametrize(
    "destroy,expected_cmd",
    [
        (False, ["terraform", "apply", "-auto-approve"]),
        (True, ["terraform", "apply", "-auto-approve", "-destroy"]),
    ],
)
def test_terraform_apply_calls_run_cmd(fake_env_path, destroy, expected_cmd):
    with mock.patch("cli.terraform_utils.run_cmd") as run_cmd:
        tf_utils.terraform_apply(fake_env_path, destroy=destroy, dry_run=False)
        run_cmd.assert_called_once_with(
            expected_cmd,
            cwd=fake_env_path,
            dry_run=False,
            capture_output=False,
        )


def test_terraform_state_has_changes_no_changes(capsys, fake_env_path):
    result = mock.Mock()
    result.returncode = tf_utils.TERRAFORM_NO_CHANGES_DETECTED_CODE
    with mock.patch("cli.terraform_utils.terraform_plan", return_value=result):
        changed = tf_utils.terraform_state_has_changes(fake_env_path)
        assert changed is False
        out = capsys.readouterr().out
        assert "No changes detected" in out


def test_terraform_state_has_changes_changes_detected(capsys, fake_env_path):
    result = mock.Mock()
    result.returncode = tf_utils.TERRAFORM_CHANGES_DETECTED_CODE
    with mock.patch("cli.terraform_utils.terraform_plan", return_value=result):
        changed = tf_utils.terraform_state_has_changes(fake_env_path)
        assert changed is True
        out = capsys.readouterr().out
        assert "Changes detected" in out


def test_terraform_state_has_changes_error(capsys, fake_env_path):
    result = mock.Mock()
    result.returncode = 1
    with mock.patch("cli.terraform_utils.terraform_plan", return_value=result):
        changed = tf_utils.terraform_state_has_changes(fake_env_path)
        assert changed is False
        out = capsys.readouterr().out
        assert "Error occurred" in out


@pytest.mark.parametrize("destroy", [False, True])
def test_terraform_state_has_changes_dry_run(
    monkeypatch, capsys, fake_env_path, destroy
):
    # terraform_plan should be called, but its result ignored in dry_run
    plan_result = mock.Mock()
    monkeypatch.setattr(tf_utils, "terraform_plan", mock.Mock(return_value=plan_result))
    run_cmd_mock = mock.Mock()
    monkeypatch.setattr(tf_utils, "run_cmd", run_cmd_mock)
    changed = tf_utils.terraform_state_has_changes(
        fake_env_path, destroy=destroy, dry_run=True
    )
    assert changed is False
    out = capsys.readouterr().out
    assert "Dry-run mode" in out
    # Should call run_cmd with apply and dry_run True
    expected_cmd = ["terraform", "apply", "-auto-approve"]
    if destroy:
        expected_cmd.append("-destroy")
    run_cmd_mock.assert_called_with(
        expected_cmd,
        cwd=fake_env_path,
        dry_run=True,
        capture_output=False,
    )


def test_terraform_plan_returns_run_cmd_result(fake_env_path):
    fake_result = object()
    with mock.patch("cli.terraform_utils.run_cmd", return_value=fake_result):
        result = tf_utils.terraform_plan(fake_env_path, destroy=False, dry_run=False)
        assert result is fake_result


def test_terraform_apply_returns_run_cmd_result(fake_env_path):
    fake_result = object()
    with mock.patch("cli.terraform_utils.run_cmd", return_value=fake_result):
        result = tf_utils.terraform_apply(fake_env_path, destroy=True, dry_run=True)
        assert result is fake_result


def test_terraform_init_returns_run_cmd_result(fake_env_path):
    fake_result = object()
    with mock.patch("cli.terraform_utils.run_cmd", return_value=fake_result):
        result = tf_utils.terraform_init(fake_env_path, dry_run=False)
        assert result is fake_result


def test_terraform_validate_returns_run_cmd_result(fake_env_path):
    fake_result = object()
    with mock.patch("cli.terraform_utils.run_cmd", return_value=fake_result):
        result = tf_utils.terraform_validate(fake_env_path, dry_run=True)
        assert result is fake_result
