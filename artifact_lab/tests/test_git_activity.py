"""Git activity and concurrency design tests."""

from __future__ import annotations

import subprocess
from unittest.mock import patch

from artifact_lab.contracts.concurrency import (
    DEFAULT_NETWORK_CONCURRENCY,
    MAX_NETWORK_CONCURRENCY,
    default_local_concurrency,
)
from artifact_lab.ingest.git_activity import (
    GitActivityStats,
    classify_git_command,
    record_git_subprocess,
    track_git_activity,
)
from artifact_lab.ingest.git_utils import run_git


def test_classify_git_command():
    assert classify_git_command(["git", "clone", "url"]) == "network"
    assert classify_git_command(["git", "fetch"]) == "network"
    assert classify_git_command(["git", "show", "sha:path"]) == "lazy_blob"
    assert classify_git_command(["git", "log", "--all"]) == "local"


def test_record_git_subprocess_accumulates():
    stats = GitActivityStats()
    record_git_subprocess(["git", "clone"], elapsed_s=1.5, stdout_bytes=0, stats=stats)
    record_git_subprocess(["git", "log"], elapsed_s=2.0, stdout_bytes=0, stats=stats)
    record_git_subprocess(["git", "show", "x:y"], elapsed_s=0.5, stdout_bytes=100, stats=stats)
    assert stats.n_git_subprocesses == 3
    assert stats.n_lazy_blob_fetches == 1
    assert stats.git_network_wait_s == 2.0
    assert stats.git_local_wait_s == 2.0
    assert stats.bytes_from_git == 100


def test_run_git_records_via_context():
    with track_git_activity() as stats:
        with patch("artifact_lab.ingest.git_utils.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["git", "log"],
                returncode=0,
                stdout="ok\n",
                stderr="",
            )
            run_git(["git", "log"], timeout=10)
    assert stats.n_git_subprocesses == 1
    assert stats.git_local_wait_s > 0


def test_concurrency_defaults_are_bounded():
    assert DEFAULT_NETWORK_CONCURRENCY == 2
    assert MAX_NETWORK_CONCURRENCY == 2
    assert default_local_concurrency() >= 1


def test_golden_fixture_records_git_subprocesses(tmp_path):
    from artifact_lab.ingest.profiling import PhaseTimings, ResourceMetrics
    from artifact_lab.ingest.extract import extract_repo_events
    from artifact_lab.store.blobs import BlobStore
    from artifact_lab.tests.golden_repo import build_golden_bare_repo

    bare = build_golden_bare_repo(tmp_path)
    resources = ResourceMetrics()
    with track_git_activity() as git_stats:
        events = extract_repo_events(
            bare,
            repo_id="golden",
            repo_url="https://github.com/golden/fixture",
            family="ai_conventions_v1",
            extraction_wave="test",
            detector_version="1.0.0",
            blob_store=BlobStore(tmp_path / "blobs"),
            git_timeout=60,
            timings=PhaseTimings(),
            resources=resources,
        )
        resources.n_git_subprocesses = git_stats.n_git_subprocesses
        resources.n_lazy_blob_fetches = git_stats.n_lazy_blob_fetches
        resources.git_network_wait_s = git_stats.git_network_wait_s
        resources.git_local_wait_s = git_stats.git_local_wait_s
    assert len(events) >= 2
    assert resources.n_git_subprocesses > 0
    assert resources.local_cpu_s > 0
