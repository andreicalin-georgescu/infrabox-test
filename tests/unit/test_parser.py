import contextlib
import sys
from io import StringIO

import pytest

from cli import parser


@pytest.mark.parametrize(
    "argv, expected",
    [
        (
            ["prog", "create", "dev"],
            {"command": "create", "environment": "dev", "dry_run": False},
        ),
        (
            ["prog", "create", "stage", "--dry-run"],
            {"command": "create", "environment": "stage", "dry_run": True},
        ),
        (
            ["prog", "destroy", "dev"],
            {"command": "destroy", "environment": "dev", "dry_run": False},
        ),
        (
            ["prog", "destroy", "stage", "--dry-run"],
            {"command": "destroy", "environment": "stage", "dry_run": True},
        ),
        (
            ["prog", "initialize"],
            {"command": "initialize", "environment": "dev", "dry_run": False},
        ),
        (
            ["prog", "initialize", "prod"],
            {"command": "initialize", "environment": "prod", "dry_run": False},
        ),
        (
            ["prog", "initialize", "stage", "--dry-run"],
            {"command": "initialize", "environment": "stage", "dry_run": True},
        ),
    ],
)
def test_parse_arguments_valid(monkeypatch, argv, expected):
    monkeypatch.setattr(sys, "argv", argv)
    args = parser.parse_arguments()
    for k, v in expected.items():
        assert getattr(args, k) == v


@pytest.mark.parametrize(
    "argv, error_text",
    [
        (["prog"], "the following arguments are required: command"),
        (["prog", "create"], "the following arguments are required: environment"),
        (["prog", "destroy"], "the following arguments are required: environment"),
        (["prog", "create", "bar"], "invalid choice: 'bar'"),
        (["prog", "destroy", "pseudo"], "invalid choice: 'pseudo'"),
        (["prog", "initialize", "foo"], "invalid choice: 'foo'"),
    ],
)
def test_parse_arguments_invalid(monkeypatch, argv, error_text):
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit) as excinfo:
        parser.parse_arguments()
    assert excinfo.value.code != 0
    # argparse prints errors to stderr
    # To check error message, capture sys.stderr
    stderr = StringIO()
    with contextlib.redirect_stderr(stderr):
        try:
            parser.parse_arguments()
        except SystemExit:
            pass
    assert error_text in stderr.getvalue()


def test_parse_arguments_help(monkeypatch):
    # Test that -h/--help prints help and exits
    for help_flag in ("-h", "--help"):
        monkeypatch.setattr(sys, "argv", ["prog", help_flag])
        with pytest.raises(SystemExit) as excinfo:
            parser.parse_arguments()
        assert excinfo.value.code == 0


def test_parse_arguments_extra_flags(monkeypatch):
    # Unknown flags should cause error
    monkeypatch.setattr(sys, "argv", ["prog", "create", "dev", "--unknown"])
    with pytest.raises(SystemExit):
        parser.parse_arguments()
