# Annotation packet `8bec66320d554a6d`

Protocol: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`
Packet spec: `rq5_v1_blind_packet_spec_v2`

Judge only with the materials below. Do not seek external repositories or experimental results.

## Annotator question

Is Referenced artifact R1 materially necessary for completing THIS software engineering task in THIS repository snapshot?

## Anonymous snapshot

- Snapshot ID: `49d0202578f7eb0d`
- Reference type: `directory`
- Artifact alias: **Referenced artifact R1**

## Task brief

Engineering task (derived only from the pinned instruction text and snapshot signals):

Document title: AI Agent Instructions. Guidance Section: ### Directory Structure - `plugins/` - Product plugins, mounted at `/newspack-plugins/` in container - `themes/` - Themes, mounted at `/newspack-themes/` in container - `packages/` - Shared libraries (scripts, components, colors, icons) - `html/` - Main WordPress site, mounted at `/var/www/html` - `additional-sites-html/` - Additional WordPress sites - `manager-html/` - Newspack Manager site - `bin/` - Shell scripts mounted at `/var/scripts/` in container - `config/` - Apache, PHP, MySQL configuration ### Docker Services - `wordpress` (container: `newspack_dev`) - Apache + PHP + WordPress - `db` - MariaDB 11.8.6 - `mailhog` - Email capture at http://localhost:8025 - `adminer` - Database UI a Workflow: newspack-workspace is the Newspack monorepo. It contains all product plugins, themes, and shared packages in a single repository, plus a Docker-based local development environment with containerized PHP/Apache/MySQL. **This is a pnpm workspace.** Plugins live in `plugins/`, themes in `themes/`, shared packages (newspack-scripts, newspack-components, newspack-colors, newspack-icons) in `packages/`. All workspace packages share a single lockfile and hoisted dependencies. Instruction overview: This file provides guidance to AI coding agents working with code in this repository. It is the single source of truth for shared conventions across all Newspack repos. Tool-specific files (`CLAUDE.md`, `.github/copilot-instructions.md`, etc.) reference this file.

While performing this work, the instruction cites Referenced artifact R1. Your annotation question is whether that cited artifact is materially necessary for completing this task in the provided snapshot.

Verification command observed in the pinned repository manifests: `npm run lint`. Use this only as a snapshot signal of how the project checks work; do not assume other commands.

## Artifact role

Referenced artifact R1 is a repository artifact cited by the project instruction text (reference kind: directory). Its literal path string is withheld and shown as [[REF]] so treatment assignment cannot be inferred from path identity. Use the citation excerpts, task brief, and snapshot context below to judge relevance and necessity.

## Path policy

Path identity for the cited artifact and for contrast-only manipulated paths is replaced by [[REF]] using semantic whole-path tokenization (not substring replacement). Other snapshot paths may appear when they do not reveal treatment assignment. Do not infer experimental treatment from path placeholders.

## Instruction citation excerpts

### Excerpt 1

```
## Workspace Layout

### Directory Structure

- `plugins/<name>/` - Product plugins (12 total).
- `themes/<name>/` - Themes (newspack-theme, newspack-block-theme).
- `packages/<name>/` - Shared libraries (scripts, components, colors, icons).
- `repos/plugins/<name>/`, `repos/themes/<name>/` - Standalone/local plugin and theme checkouts that live outside the monorepo (e.g. private or customer-specific plugins, `newspack-manager`, licensed WooCommerce extensions). The `repos/plugins` and `repos/themes` directories are tracked (`.gitkeep`); anything you drop inside them is gitignored. Mounted at `[[REF]]` and symlinked into the active site (`wp-content/plugins/`, `wp-content/themes/`) by `bin/link-repos.sh`. **Any directory works with no registration** - `n` commands (`n build`, `n composer`, `n watch`, cwd-detection) discover `[[REF]]` checkouts by path, so there's no need to edit `bin/repos.sh`. If a name also exists in the monorepo `plugins/`/`themes/`, the **tracked copy wins** and the `[[REF]]` duplicate is skipped. Workflow: drop a real checkout in (clone/unzip directly, or `git worktree add`), build it, then `n restart`/`n start` to pick it up. A symlink *inside* `[[REF]]` pointing outside the workspace will dangle in the container - use a real directory.

Each directory is a standalone WordPress plugin/theme that can be zipped and installed independently.

### Plugins and Themes

The Newspack product consists of these interconnected plugins and themes:

**Core Plugin:**
```

## Repository tree excerpt (pinned snapshot)

```
.claude/settings.json
.dockerignore
.github/CODEOWNERS
.github/CONTRIBUTING.md
.github/ISSUE_TEMPLATE/Bug_report.md
.github/ISSUE_TEMPLATE/Feature_request.md
.github/PULL_REQUEST_TEMPLATE.md
.github/copilot-instructions.md
.github/dependabot.yml
.github/labeler.yml
.github/scripts/finalize-package-versions.cjs
.github/scripts/notify-release.sh
.github/scripts/post-release.sh
.github/scripts/publish-baseline-releases.sh
.github/scripts/release-wporg.sh
.github/workflows/_release-wporg.yml
.github/workflows/auto-merge.yml
.github/workflows/changelog.yml
.github/workflows/ci.yml
.github/workflows/dependabot-branch-auto-update.yml
.github/workflows/pr-labels.yml
.github/workflows/publish-baseline-releases.yml
.github/workflows/release.yml
.github/workflows/sync-legacy.yml
.gitignore
.husky/pre-commit
.lintstagedrc.json
.npmrc
.nvmrc
[[REF]]
CLAUDE.md
Dockerfile
LICENSE
README.md
build-image-82.sh
build-image.sh
clone-repos.sh
composer.json
default.env
docker-compose-82.yml
docker-compose.yml
n
package.json
phpcs.xml
pnpm-lock.yaml
pnpm-workspace.yaml
```

## Neighbouring paths

_None listed in the minimal context window._

## Nearby documentation paths

```
.github/CONTRIBUTING.md
[[REF]]
CLAUDE.md
README.md
composer.json
package.json
packages/README.md
packages/colors/README.md
packages/colors/package.json
packages/components/README.md
```

## Nearby configuration paths

```
.claude/settings.json
.github/dependabot.yml
.github/labeler.yml
.github/workflows/_release-wporg.yml
.github/workflows/auto-merge.yml
.github/workflows/changelog.yml
.github/workflows/ci.yml
.github/workflows/dependabot-branch-auto-update.yml
.github/workflows/pr-labels.yml
.github/workflows/publish-baseline-releases.yml
```

## Pinned snapshot file excerpts

### snapshot_file_1

```
# AI Agent Instructions

This file provides guidance to AI coding agents working with code in this repository. It is the single source of truth for shared conventions across all Newspack repos. Tool-specific files (`CLAUDE.md`, `.github/copilot-instructions.md`, etc.) reference this file.

## Overview

newspack-workspace is the Newspack monorepo. It contains all product plugins, themes, and shared packages in a single repository, plus a Docker-based local development environment with containerized PHP/Apache/MySQL.

**This is a pnpm workspace.** Plugins live in `plugins/`, themes in `themes/`, shared packages (newspack-scripts, newspack-components, newspack-colors, newspack-icons) in `packages/`. All workspace packages share a single lockfile and hoisted dependencies.

## Workspace Layout

### Directory Structure

- `plugins/<name>/` - Product plugins (12 total).
- `themes/<name>/` - Themes (newspack-theme, newspack-block-theme).
- `packages/<name>/` - Shared libraries (scripts, components, colors, icons).
- `repos/plugins/<name>/`, `repos/themes/<name>/` - Standalone/local plugin and theme checkouts that live outside the monorepo (e.g. private or customer-specific plugins, `newspack-manager`, licensed WooCommerce extensions). The `repos/plugins` and `repos/themes` directories are tracked (`.gitkeep`); anything you drop inside them is gitignored. Mounted at `[[REF]]` and symlinked into the active site (`wp-content/plugins/`, `wp-content/themes/`) by `bin/link-repos.sh`. **Any directory works with no registration** - `n` commands (`n build`, `n composer`, `n watch`, cwd-detection) discover `[[REF]]` checkouts by path, so there's no need to edit `bin/repos.sh`. If a name also exists in the monorepo `plugins/`/`themes/`, the **tracked copy wins** and the `[[REF]]` duplicate is skipped. Workflow: drop a real checkout in (clone/unzip directly, or `git worktree add`), build it, then `n restart`/`n start` to pick it up. A symlink *inside* `[[REF]]` pointing outside th
```

### snapshot_file_2

```
# Contributing to Newspack

Thank you for your interest in contributing to Newspack! These guidelines explain how the contribution process works.

**Please don't use the issue tracker for support questions or general inquiries.**

## Bug reports

**[To disclose a security issue, submit a report via HackerOne.](https://hackerone.com/automattic)**

To report a bug, [open a new issue](https://github.com/Automattic/newspack-workspace/issues/new?template=Bug_report.md). Please include:

- Steps to reproduce the issue.
- What you expected to happen.
- What actually happened.
- Details about your environment (WordPress version, PHP version, etc.).
- Screenshots if applicable.

## Feature requests

Feature requests can be [submitted to our issue tracker](https://github.com/Automattic/newspack-workspace/issues/new?template=Feature_request.md). Please search for similar ones in the closed issues before submitting.

## Pull requests

Create a pull request to the `main` branch. Please test and provide an explanation for your changes.

Guidelines:

- Follow the [WordPress Coding Standards](https://make.wordpress.org/core/handbook/best-practices/coding-standards/php/) and the [VIP Go Coding Standards](https://vip.wordpress.com/documentation/vip-go/code-review-blockers-warnings-notices/).
- Use conventional commits (`feat:`, `fix:`, etc.) for your commit messages.
- Run `pnpm install` at the root to set up the workspace and pre-commit hooks.
- Don't modify changelog files or `.pot` translation files. These are auto-generated.

### Code review

Every PR should be reviewed and approved by someone other than the author. Everyone is encouraged to review PRs and add feedback, regardless of experience level.

### Development setup

See the [README](../README.md) and [[[INSTRUCTION]]](../[[INSTRUCTION]]) for development environment setup, build commands, and testing instructions.

## License

Newspack is licensed under [GNU General Public License v2 (or later)](../LICENSE). All contributions must be
```

### snapshot_file_3

```
@[[REF]]

```

### snapshot_file_4

```
{
  "enabledPlugins": {
    "newspack@newspack-devkit": true,
    "context7@claude-plugins-official": true,
    "linear@claude-plugins-official": true,
    "figma@claude-plugins-official": true
  },
  "extraKnownMarketplaces": {
    "newspack-devkit": {
      "source": {
        "source": "github",
        "repo": "Automattic/newspack-devkit"
      }
    }
  }
}

```

### snapshot_file_5

```
version: 2

updates:
  # Root npm dependencies (pnpm workspace).
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
    # Group minor/patch updates to reduce PR noise.
    groups:
      minor-and-patch:
        update-types:
          - "minor"
          - "patch"

  # Root composer dependencies (PHPCS, PHPUnit, etc.).
  - package-ecosystem: "composer"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"

  # GitHub Actions.
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"

  # Per-plugin production composer deps (only plugins that have them).
  - package-ecosystem: "composer"
    directory: "plugins/newspack-plugin"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
  - package-ecosystem: "composer"
    directory: "plugins/newspack-ads"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
  - package-ecosystem: "composer"
    directory: "plugins/newspack-newsletters"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
  - package-ecosystem: "composer"
    directory: "plugins/newspack-popups"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"

```

### snapshot_file_6

```
needs-changelog:
 - base-branch: ['main', 'alpha', 'release']

```
