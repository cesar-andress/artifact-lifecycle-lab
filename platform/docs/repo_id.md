# Repository identifier normalization

See `platform/contracts/repo_id.py` for the implementation.

## Rules

1. Strip leading/trailing whitespace from the input URL.
2. **GitHub HTTPS URLs** normalize to `https://github.com/{owner}/{repo}` with
   lowercase owner and repo; a trailing `.git` on the repo segment is removed.
3. **Other URLs** lowercase scheme and host, remove trailing slashes, and strip a
   trailing `.git` suffix from the path.
4. **`repo_id`** is `sha256(normalized_url).hexdigest()[:16]`.

## Examples

| Input | Normalized URL |
|-------|----------------|
| `https://github.com/Org/Repo.git` | `https://github.com/org/repo` |
| `https://github.com/org/repo/` | `https://github.com/org/repo` |

Equivalent inputs yield the same `repo_id`. The registry CSV stores only
`repo_url`; `repo_id` is always derived at ingest time.
