"""Blob store deduplication tests."""

from platform.store.blobs import BlobStore


def test_blob_deduplication(tmp_path):
    store = BlobStore(tmp_path / "blobs")
    content = b"# agent rules\n"
    sha1 = store.put_text(content)
    sha2 = store.put_text(content)
    assert sha1 == sha2
    assert store.has(sha1)
    files = list((tmp_path / "blobs").rglob("*"))
    assert len([f for f in files if f.is_file()]) == 1


def test_rejects_binary(tmp_path):
    store = BlobStore(tmp_path / "blobs")
    try:
        store.put_text(b"hello\x00world")
        raised = False
    except ValueError:
        raised = True
    assert raised
