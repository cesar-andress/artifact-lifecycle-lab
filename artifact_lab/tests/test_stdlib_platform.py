"""Verify stdlib platform is not shadowed by artifact_lab."""

import platform as stdlib_platform


def test_stdlib_platform_module_is_available():
    assert hasattr(stdlib_platform, "python_implementation")
    assert stdlib_platform.python_implementation() in {"CPython", "PyPy", "Jython", "IronPython"}
