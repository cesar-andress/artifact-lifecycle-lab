# Annotation packet `018779556d23bf3f`

Protocol: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`
Packet spec: `rq5_v1_blind_packet_spec_v2`

Judge only with the materials below. Do not seek external repositories or experimental results.

## Annotator question

Is Referenced artifact R1 materially necessary for completing THIS software engineering task in THIS repository snapshot?

## Anonymous snapshot

- Snapshot ID: `3cedbe7ff909e350`
- Reference type: `path`
- Artifact alias: **Referenced artifact R1**

## Task brief

Engineering task (derived only from the pinned instruction text and snapshot signals):

Document title: Help Center App. Workflow: This app takes `[[REF]]` and bundles it into 6 separate webpack entry points deployed to `widgets.wp.com/help-center/`. Jetpack enqueues these bundles on various types of websites and pages (editor, wp-admin, logged out pages (/support and /forums), CIAB) Instruction overview: Build and deployment layer for the Help Center on Simple and Atomic sites. Most Help Center code lives in `packages/help-center/` — see `packages/help-center/[[INSTRUCTION]]` for the primary spec.

While performing this work, the instruction cites Referenced artifact R1. Your annotation question is whether that cited artifact is materially necessary for completing this task in the provided snapshot.

No automated verification command was identified from the pinned repository manifests. Judge necessity from the stated engineering task and the supplied snapshot materials only.

## Artifact role

Referenced artifact R1 is a repository artifact cited by the project instruction text (reference kind: path). Its literal path string is withheld and shown as [[REF]] so treatment assignment cannot be inferred from path identity. Use the citation excerpts, task brief, and snapshot context below to judge relevance and necessity.

## Path policy

Path identity for the cited artifact and for contrast-only manipulated paths is replaced by [[REF]] using semantic whole-path tokenization (not substring replacement). Other snapshot paths may appear when they do not reveal treatment assignment. Do not infer experimental treatment from path placeholders.

## Instruction citation excerpts

### Excerpt 1

```
# Help Center App

Build and deployment layer for the Help Center on Simple and Atomic sites. Most Help Center code lives in `packages/help-center/` — see `packages/help-center/[[INSTRUCTION]]` for the primary spec.

## Overview

This app takes `[[REF]]` and bundles it into 6 separate webpack entry points deployed to `widgets.wp.com/help-center/`. Jetpack enqueues these bundles on various types of websites and pages (editor, wp-admin, logged out pages (/support and /forums), CIAB)

## Entry Points

| Entry point                              | Context                                      |
| ---------------------------------------- | -------------------------------------------- |
| `help-center-gutenberg.js`               | Gutenberg editor (connected)                 |
| `help-center-gutenberg-disconnected.js`  | Gutenberg editor (disconnected from Jetpack) |
| `help-center-wp-admin.js`                | wp-admin bar (connected)                     |
```

### Excerpt 2

```
| ---------------------------------------- | -------------------------------------------- |
| `help-center-gutenberg.js`               | Gutenberg editor (connected)                 |
| `help-center-gutenberg-disconnected.js`  | Gutenberg editor (disconnected from Jetpack) |
| `help-center-wp-admin.js`                | wp-admin bar (connected)                     |
| `help-center-wp-admin-disconnected.js`   | wp-admin bar (disconnected from Jetpack)     |
| `help-center-customizer.js`              | Customizer                                   |
| `help-center-logged-out.js`              | Logged-out view                              |

Each entry point is a standalone JS file in the app root (e.g., `help-center-gutenberg.js`) that imports from `[[REF]]` and wires up the environment-specific bootstrap logic.

## Build & Sync Commands

'''bash
# Dev build + sync to sandbox (use during development)
cd apps/help-center
yarn dev --sync
```

## Repository tree excerpt (pinned snapshot)

```
.buildkite/commands/build-desktop-linux.sh
.buildkite/commands/build-desktop-mac.sh
.buildkite/pipeline.yml
.circleci/config.yml
.claude/agents/playwright-test-generator.md
.claude/agents/playwright-test-healer.md
.claude/agents/playwright-test-planner.md
.claude/rules/dashboard-testing.md
.claude/settings.json
.claude/skills/calypso-react-query-migration/SKILL.md
.claude/skills/calypso-react-query-migration/mutations.md
.claude/skills/calypso-react-query-migration/redux-cleanup.md
.claude/skills/calypso-react-query-migration/test-scaffolding.md
.claude/skills/calypso-security-alerts/SKILL.md
.claude/skills/dashboard-create-screen/SKILL.md
.claude/skills/fix-e2e-tests/SKILL.md
.claude/skills/fix-e2e-tests/baseline-failures.sh
.claude/skills/fix-e2e-tests/setup-token.sh
.claude/skills/help-center-ui-test/SKILL.md
.claude/skills/reader-protocol-pr-review/SKILL.md
.claude/skills/reader-protocol-pr-review/references/common-smells.md
.claude/skills/stepper-flow/SKILL.md
.codex/config.toml
.cursor/commands/create-pr.md
.cursor/rules/dashboard-testing.mdc
.cursor/worktrees.json
.dockerignore
.editorconfig
.eslintignore
apps/README.md
[[REF]]
apps/help-center/CLAUDE.md
apps/help-center/README.md
apps/help-center/async-help-center.jsx
apps/help-center/config.js
apps/help-center/help-center-ciab-admin.jsx
apps/help-center/help-center-customizer.jsx
apps/help-center/help-center-gutenberg-disconnected.jsx
apps/help-center/help-center-gutenberg.jsx
apps/help-center/help-center-logged-out.js
apps/help-center/help-center-wp-admin-disconnected.js
apps/help-center/help-center-wp-admin.jsx
apps/help-center/help-center.scss
apps/help-center/help-icon.svg
apps/help-center/package.json
apps/help-center/postcss.config.js
apps/help-center/utils.js
apps/help-center/webpack.config.js
```

## Neighbouring paths

```
apps/help-center/CLAUDE.md
apps/help-center/README.md
apps/help-center/async-help-center.jsx
apps/help-center/config.js
apps/help-center/help-center-ciab-admin.jsx
apps/help-center/help-center-customizer.jsx
apps/help-center/help-center-gutenberg-disconnected.jsx
apps/help-center/help-center-gutenberg.jsx
apps/help-center/help-center-logged-out.js
apps/help-center/help-center-wp-admin-disconnected.js
apps/help-center/help-center-wp-admin.jsx
apps/help-center/help-center.scss
apps/help-center/help-icon.svg
apps/help-center/package.json
apps/help-center/postcss.config.js
apps/help-center/utils.js
apps/help-center/webpack.config.js
```

## Nearby documentation paths

```
.teamcity/README
.teamcity/pom.xml
[[INSTRUCTION]]
CLAUDE.md
README.md
apps/README.md
apps/agents-manager/[[INSTRUCTION]]
apps/agents-manager/CLAUDE.md
apps/agents-manager/README.md
apps/agents-manager/package.json
```

## Nearby configuration paths

```
.buildkite/pipeline.yml
.circleci/config.yml
.claude/settings.json
.codex/config.toml
.cursor/worktrees.json
.github/ISSUE_TEMPLATE/bug_report.yml
.github/ISSUE_TEMPLATE/feature_request.yml
.github/ISSUE_TEMPLATE/flaky-e2e-spec-report.yml
.github/ISSUE_TEMPLATE/simple-atomic-parity.yml
.github/ISSUE_TEMPLATE/task.yml
```

## Pinned snapshot file excerpts

### snapshot_file_1

```
# Help Center App

Build and deployment layer for the Help Center on Simple and Atomic sites. Most Help Center code lives in `packages/help-center/` — see `packages/help-center/[[INSTRUCTION]]` for the primary spec.

## Overview

This app takes `[[REF]]` and bundles it into 6 separate webpack entry points deployed to `widgets.wp.com/help-center/`. Jetpack enqueues these bundles on various types of websites and pages (editor, wp-admin, logged out pages (/support and /forums), CIAB)

## Entry Points

| Entry point                              | Context                                      |
| ---------------------------------------- | -------------------------------------------- |
| `help-center-gutenberg.js`               | Gutenberg editor (connected)                 |
| `help-center-gutenberg-disconnected.js`  | Gutenberg editor (disconnected from Jetpack) |
| `help-center-wp-admin.js`                | wp-admin bar (connected)                     |
| `help-center-wp-admin-disconnected.js`   | wp-admin bar (disconnected from Jetpack)     |
| `help-center-customizer.js`              | Customizer                                   |
| `help-center-logged-out.js`              | Logged-out view                              |

Each entry point is a standalone JS file in the app root (e.g., `help-center-gutenberg.js`) that imports from `[[REF]]` and wires up the environment-specific bootstrap logic.

## Build & Sync Commands

'''bash
# Dev build + sync to sandbox (use during development)
cd apps/help-center
yarn dev --sync

# Production build + sync (use before deploying)
cd apps/help-center
yarn build --sync
'''

Both commands use `calypso-apps-builder` to compile webpack bundles and sync them to `widgets.wp.com/help-center/` on your sandbox.

## Sandbox Testing

1. Sandbox `widgets.wp.com` (the sites themselves do not need sandboxing).
2. Run `yarn dev --sync` from `apps/help-center/`.
3. Visit any Simple, Atomic, or CIAB site.
4. Open the Help 
```

### snapshot_file_2

```
@[[INSTRUCTION]]

```

### snapshot_file_3

```
# Help Center

<kbd><img width="417" alt="image" src="https://github.com/Automattic/wp-calypso/assets/17054134/05e99f88-59ea-4303-889c-bd6b9cc52ce7"></kbd>

The Help Center is the main tool our customers use to reach for support.

## Development

The Help Center is a bit complicated because it runs in multiple different environments.

1. In Calypso.
2. In Simple sites
   - as a plugin to Gutenberg editor.
   - as a wpadminbar menu item.
3. In Atomic sites
   - as a plugin to Gutenberg editor.
     - A plugin when the site is connected to Jetpack.
     - A minimal plugin when the site is disconnected from Jetpack. This plugiy simple links to wp.com/help.
   - as a wpadminbar menu item.
     - A menu item that opens the Help Center when connected to Jetpack.
     - A minimal plugin when the site is disconnected from Jetpack. This plugiy simple links to wp.com/help.

### How to debug the Help Center

#### In Calypso

Follow the classic Calypso development setup. Run `yarn start` and edit away. Nothing else should be needed.

#### In Simple sites

1. cd into `apps/help-center`.
2. run `yarn dev --sync`.
3. Sandbox your site and `widgets.wp.com`.
4. Your changes should be reflected on the site live.

#### In Atomic sites

If you only interested in making JS and CSS changes, you're in luck; you don't need to worry about running Jetpack. You can follow the same instructions of simple sites.

> [!IMPORTANT]
> If you make changes to the \*.asset.json files, i.e add or remove dependencies, these files won't be synced with the site as Jetpack pulls these files via network. And since Jetpack pulls from production and not your sandbox, you'll have to deploy first for these changes to take effect.

If you do want to modify PHP files. Please follow the development process of [`jetpack-mu-plugin`](https://github.com/Automattic/jetpack/blob/trunk/projects/packages/jetpack-mu-wpcom/README.md).

### Translations

Translation are uploaded to widgets.wp.com/help-center/languages. They'r
```

### snapshot_file_4

```
/* global helpCenterData */
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { dispatch } from '@wordpress/data';
import { createRoot } from 'react-dom/client';

export default function loadHelpCenter() {
	if ( document.getElementById( 'jetpack-help-center' ) ) {
		return Promise.resolve();
	}
	const queryClient = new QueryClient();
	const container = document.createElement( 'div' );
	container.id = 'jetpack-help-center';
	document.body.appendChild( container );
	const botProps = helpCenterData.isCommerceGarden
		? { newInteractionsBotSlug: 'ciab-workflow-support_chat' }
		: {};

	return import( '[[REF]]' ).then( ( { default: HelpCenter } ) =>
		createRoot( container ).render(
			<QueryClientProvider client={ queryClient }>
				<HelpCenter
					locale={ helpCenterData.locale }
					sectionName={ helpCenterData.sectionName || 'gutenberg-editor' }
					currentUser={ helpCenterData.currentUser }
					site={ helpCenterData.site }
					hasPurchases={ false }
					onboardingUrl="https://wordpress.com/start"
					handleClose={ () => dispatch( 'automattic/help-center' ).setShowHelpCenter( false ) }
					product={ helpCenterData.isCommerceGarden ? 'commerce-garden' : undefined }
					{ ...botProps }
				/>
			</QueryClientProvider>
		)
	);
}

```

### snapshot_file_5

```
/* global helpCenterData */
const isProxied = typeof helpCenterData !== 'undefined' && helpCenterData?.isProxied;
const isCIAB = typeof helpCenterData !== 'undefined' && helpCenterData?.isCommerceGarden;
const envValue = isProxied && ! isCIAB ? 'staging' : 'production';

window.configData = {
	env_id: envValue,
	env: envValue,
	features: {
		'help/gpt-response': true,
	},
	wapuu: false,
	i18n_default_locale_slug: 'en',
};

```

### snapshot_file_6

```
/* global __i18n_text_domain__, helpCenterData */
import './config';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import apiFetch from '@wordpress/api-fetch';
import { dispatch, select, subscribe } from '@wordpress/data';
import { useState, useEffect } from '@wordpress/element';
import { __ } from '@wordpress/i18n';
import { createRoot } from 'react-dom/client';
import './help-center.scss';
import wpcomRequest, { canAccessWpcomApis } from 'wpcom-proxy-request';

function useCurrentRoute() {
	const [ route, setRoute ] = useState(
		() => window.location.pathname + window.location.search + window.location.hash
	);

	useEffect( () => {
		const updateRoute = () => {
			setRoute( window.location.pathname + window.location.search + window.location.hash );
		};

		const originalPushState = window.history.pushState;
		const originalReplaceState = window.history.replaceState;

		window.history.pushState = function ( ...args ) {
			originalPushState.apply( this, args );
			updateRoute();
		};
		window.history.replaceState = function ( ...args ) {
			originalReplaceState.apply( this, args );
			updateRoute();
		};

		window.addEventListener( 'popstate', updateRoute );

		return () => {
			window.history.pushState = originalPushState;
			window.history.replaceState = originalReplaceState;
			window.removeEventListener( 'popstate', updateRoute );
		};
	}, [] );

	return route;
}

function HelpCenterWithRouteTracking( { HelpCenter } ) {
	const currentRoute = useCurrentRoute();
	const botProps = helpCenterData.isCommerceGarden
		? { newInteractionsBotSlug: 'ciab-workflow-support_chat' }
		: {};

	return (
		<HelpCenter
			locale={ helpCenterData.locale }
			sectionName={ helpCenterData.sectionName || 'gutenberg-editor' }
			currentUser={ helpCenterData.currentUser }
			site={ helpCenterData.site }
			hasPurchases={ false }
			onboardingUrl="https://wordpress.com/start"
			handleClose={ () => dispatch( 'automattic/help-center' ).setShowHelpCenter( false
```

### snapshot_file_7

```
The archive contains settings for a TeamCity project.

To edit the settings in IntelliJ Idea, open the pom.xml and
select the 'Open as a project' option.

If you want to move this dsl to version control, save it in the
.teamcity directory.
```

### snapshot_file_8

```
<?xml version="1.0"?>
<project>
  <modelVersion>4.0.0</modelVersion>
  <name>calypso Config DSL Script</name>
  <groupId>calypso</groupId>
  <artifactId>calypso_dsl</artifactId>
  <version>1.0-SNAPSHOT</version>

  <parent>
    <groupId>org.jetbrains.teamcity</groupId>
    <artifactId>configs-dsl-kotlin-parent</artifactId>
    <version>1.0-SNAPSHOT</version>
  </parent>

  <repositories>
    <repository>
      <id>jetbrains-all</id>
      <url>https://download.jetbrains.com/teamcity-repository</url>
      <snapshots>
        <enabled>true</enabled>
      </snapshots>
    </repository>
    <repository>
      <id>teamcity-server</id>
      <url>https://teamcity.a8c.com/app/dsl-plugins-repository</url>
      <snapshots>
        <enabled>true</enabled>
      </snapshots>
    </repository>
  </repositories>

  <pluginRepositories>
    <pluginRepository>
      <id>JetBrains</id>
      <url>https://download.jetbrains.com/teamcity-repository</url>
    </pluginRepository>
  </pluginRepositories>

  <build>
    <sourceDirectory>${basedir}</sourceDirectory>
    <plugins>
      <plugin>
        <artifactId>kotlin-maven-plugin</artifactId>
        <groupId>org.jetbrains.kotlin</groupId>
        <version>${kotlin.version}</version>

        <configuration/>
        <executions>
          <execution>
            <id>compile</id>
            <phase>process-sources</phase>
            <goals>
              <goal>compile</goal>
            </goals>
          </execution>
          <execution>
            <id>test-compile</id>
            <phase>process-test-sources</phase>
            <goals>
              <goal>test-compile</goal>
            </goals>
          </execution>
        </executions>
      </plugin>
      <plugin>
        <groupId>org.jetbrains.teamcity</groupId>
        <artifactId>teamcity-configs-maven-plugin</artifactId>
        <version>${teamcity.dsl.version}</version>
        <configuration>
          <format>kotlin</format>
          <dstDir>target/generated-conf
```

### snapshot_file_9

```
# [[INSTRUCTION]]

## Repository layout

- client/ — main application clients, deployed as single-page React apps.
- packages/ — shared libraries across clients.
- apps/ — standalone mini-apps, deployed separately.

## Clients

- **Calypso** — the classic WordPress.com hosting dashboard, sharing data using Redux and split via Webpack section chunks.
  - client/my-sites — per-site management; deprecated in favor of the Dashboard client
  - client/my-sites/checkout — checkout flow
  - client/me/purchases — purchase management
  - client/landing/stepper — onboarding/signup flows (site creation, domain purchase, migration wizards)
  - client/reader — WordPress.com Reader: feed streams, discover, conversations, likes, lists, following management
  - Shared infra: client/components, client/state, client/lib, client/layout
- **Jetpack Cloud** (client/jetpack-cloud) — reuses Calypso shared infra (client/state, client/components).
- **A8C for Agencies** (client/a8c-for-agencies) — reuses Calypso shared infra.
- **Dashboard** (client/dashboard) — the new multi-site dashboard. Self-contained: does not reuse Calypso client code. Has its own components, data fetching (TanStack Query), and routing (TanStack Router).
  - client/dashboard/me/billing-purchases — billing & purchase management

## Packages

- **Help Center** (`packages/help-center`) — shared component library for WordPress.com support. Also deployed via `apps/help-center/` to `widgets.wp.com`.
- **Image Studio** (`packages/image-studio`) — AI-powered image editing and generation
- **Block Notes** (`packages/block-notes`) — AI-powered block commenting system for WordPress
- **Calypso Products** (`packages/calypso-products`) — ⚠️ **Avoid.** Deprecated/frozen: a bloated client-side duplicate of product data the backend already owns. Don't add to it; prefer backend-driven data (e.g. `@automattic/api-queries`). See `packages/calypso-products/[[INSTRUCTION]]`.

## Apps

- **Help Center** (`apps/help-center`) — build/deploy layer that b
```

### snapshot_file_10

```
# yaml-language-server: $schema=https://raw.githubusercontent.com/buildkite/pipeline-schema/main/schema.json
---

steps:
  # Skip on `ainfra-*` branches: the gated build steps below already
  # run `yarn install` as part of their build script, so running it
  # again here would just duplicate the work.
  - label: ":desktop_computer: Desktop yarn install"
    branches: "!ainfra-*"
    notify:
      - github_commit_status:
          context: Desktop / yarn install
    agents:
      queue: mac
    env:
      IMAGE_ID: xcode-26.4.1
      PLAYWRIGHT_SKIP_DOWNLOAD: 'true'
      SKIP_TSC: 'true'
      COREPACK_ENABLE_DOWNLOAD_PROMPT: 0
    plugins:
      - automattic/nvm#0.6.0
    command: |
      set -euo pipefail

      cd desktop
      corepack enable
      yarn install --immutable --inline-builds

  # The desktop build is resource-intensive and this repo runs many
  # builds; we don't want to pay for it on every commit, especially
  # while the CircleCI -> Buildkite port is still in development.
  # Gate it on `ainfra-*` branches until the port is stabilized.
  - label: ":desktop_computer: Build desktop (mac, unsigned)"
    branches: ainfra-*
    notify:
      - github_commit_status:
          context: Desktop / Build (mac, unsigned)
    agents:
      queue: mac
    env:
      IMAGE_ID: xcode-26.4.1
    plugins:
      - automattic/nvm#0.6.0
    command: .buildkite/commands/build-desktop-mac.sh
    artifact_paths:
      - desktop/release/*

  - label: ":desktop_computer: Build desktop (linux, unsigned)"
    branches: ainfra-*
    notify:
      - github_commit_status:
          context: Desktop / Build (linux, unsigned)
    agents:
      queue: default
    plugins:
      - automattic/nvm#0.6.0
    command: .buildkite/commands/build-desktop-linux.sh
    artifact_paths:
      - desktop/release/*

```
