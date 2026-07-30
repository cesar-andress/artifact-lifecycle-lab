# Annotation packet `5cdb19823812fea3`

Protocol: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`
Packet spec: `rq5_v1_blind_packet_spec_v2`

Judge only with the materials below. Do not seek external repositories or experimental results.

## Annotator question

Is Referenced artifact R1 materially necessary for completing THIS software engineering task in THIS repository snapshot?

## Anonymous snapshot

- Snapshot ID: `29302f69216d5acf`
- Reference type: `path`
- Artifact alias: **Referenced artifact R1**

## Task brief

Engineering task (derived only from the pinned instruction text and snapshot signals):

Document title: Blaze Dashboard Standalone App. Purpose Section: SPA embedded inside wp-admin (via Jetpack plugin and Blaze Ads plugin) to manage WP Blaze advertising campaigns. Not a standalone website — always rendered within a WordPress admin context. Owned by Ads Engineering team (#ads-engineering Slack, Linear team ADS). Guidance Section: - Entry: `src/app.jsx` → boots Redux store, sets theme, registers routes via page.js with hashbang (`#!`) routing - Most business logic lives OUTSIDE this app in `client/my-sites/promote-post-i2/` (shared with Calypso). Controllers, components, and hooks are imported from there. - This app is a thin wrapper: config loading, theming, routing setup, page.js middleware - Three theme modes determined by config flags: `jetpack` (default), `wpcom` (`is_running_in_blaze_plugin`), `woo` (`is_running_in_woo_site`) — see `src/themes.js` - Setup mode (`blaze_setup_mode` config flag) redirects to `/setup/` for disconnected sites - Gridicon: uses `no-asset` variant (SVG sprite loaded separately by Jetpac

While performing this work, the instruction cites Referenced artifact R1. Your annotation question is whether that cited artifact is materially necessary for completing this task in the provided snapshot.

No automated verification command was identified from the pinned repository manifests. Judge necessity from the stated engineering task and the supplied snapshot materials only.

## Artifact role

Referenced artifact R1 is a repository artifact cited by the project instruction text (reference kind: path). Its literal path string is withheld and shown as [[REF]] so treatment assignment cannot be inferred from path identity. Use the citation excerpts, task brief, and snapshot context below to judge relevance and necessity.

## Path policy

Path identity for the cited artifact and for contrast-only manipulated paths is replaced by [[REF]] using semantic whole-path tokenization (not substring replacement). Other snapshot paths may appear when they do not reveal treatment assignment. Do not infer experimental treatment from path placeholders.

## Instruction citation excerpts

### Excerpt 1

```
- Built by TeamCity automatically on every trunk commit. Artifacts at `widgets.wp.com/blaze-dashboard/v1`
- Production release to WPCOM: SSH to sandbox → `bin/install-plugin.sh blaze-dashboard trunk --release` → push WPCOM PR → merge → deploy
- If blaze package compatibility breaks, bump version folder (v1 → v1.1, v2, etc.) and update version code in Jetpack blaze package and WPCOM `bin/install_plugin.sh`
- i18n text domain: `blaze-dashboard`

## Development

- Sandbox sync: `yarn dev --sync` (requires `wpcom-sandbox` host in `~/.ssh/config`, point `widgets.wp.com` to sandbox IP in `[[REF]]`)
- Local with Jetpack: `BLAZE_DASHBOARD_PACKAGE_PATH=/path/to/jetpack/projects/packages/blaze yarn dev`
- Test at: `/wp-admin/tools.php?page=advertising`
- Jurassic Ninja sites work for quick testing

## Key Fieldguide Articles

- Blaze Dashboard: `fieldguide.automattic.com/blaze-dashboard/`
- Developer Onboarding: `fieldguide.automattic.com/wordpress-blaze-developer-onboarding/`
```

## Repository tree excerpt (pinned snapshot)

```
.circleci/config.yml
.claude/agents/playwright-test-generator.md
.claude/agents/playwright-test-healer.md
.claude/agents/playwright-test-planner.md
.claude/rules/dashboard-testing.md
.claude/settings.json
.claude/skills/dashboard-create-screen/SKILL.md
.cursor/commands/create-pr.md
.cursor/rules/dashboard-testing.mdc
.cursor/worktrees.json
.dockerignore
.editorconfig
.eslintignore
.eslintrc.js
.git-blame-ignore-revs
apps/README.md
apps/blaze-dashboard/.eslintrc.js
[[REF]]
apps/blaze-dashboard/CLAUDE.md
apps/blaze-dashboard/README.md
apps/blaze-dashboard/filter-json-config-loader.js
apps/blaze-dashboard/package.json
apps/blaze-dashboard/webpack.config.js
```

## Neighbouring paths

```
apps/blaze-dashboard/.eslintrc.js
apps/blaze-dashboard/CLAUDE.md
apps/blaze-dashboard/README.md
apps/blaze-dashboard/filter-json-config-loader.js
apps/blaze-dashboard/package.json
apps/blaze-dashboard/webpack.config.js
```

## Nearby documentation paths

```
.teamcity/README
.teamcity/pom.xml
[[INSTRUCTION]]
CLAUDE.md
README.md
apps/README.md
apps/agents-manager/README.md
apps/agents-manager/package.json
[[REF]]
apps/blaze-dashboard/CLAUDE.md
```

## Nearby configuration paths

```
.circleci/config.yml
.claude/settings.json
.cursor/worktrees.json
.github/ISSUE_TEMPLATE/bug_report.yml
.github/ISSUE_TEMPLATE/feature_request.yml
.github/ISSUE_TEMPLATE/flaky-e2e-spec-report.yml
.github/ISSUE_TEMPLATE/simple-atomic-parity.yml
.github/ISSUE_TEMPLATE/task.yml
.github/ISSUE_TEMPLATE/tooling_request.yml
.github/actions/build-design-system-docs/action.yml
```

## Pinned snapshot file excerpts

### snapshot_file_1

```
# Blaze Dashboard Standalone App

## Purpose

SPA embedded inside wp-admin (via Jetpack plugin and Blaze Ads plugin) to manage WP Blaze advertising campaigns. Not a standalone website — always rendered within a WordPress admin context.

Owned by Ads Engineering team (#ads-engineering Slack, Linear team ADS).

## Architecture

- Entry: `src/app.jsx` → boots Redux store, sets theme, registers routes via page.js with hashbang (`#!`) routing
- Most business logic lives OUTSIDE this app in `client/my-sites/promote-post-i2/` (shared with Calypso). Controllers, components, and hooks are imported from there.
- This app is a thin wrapper: config loading, theming, routing setup, page.js middleware
- Three theme modes determined by config flags: `jetpack` (default), `wpcom` (`is_running_in_blaze_plugin`), `woo` (`is_running_in_woo_site`) — see `src/themes.js`
- Setup mode (`blaze_setup_mode` config flag) redirects to `/setup/` for disconnected sites
- Gridicon: uses `no-asset` variant (SVG sprite loaded separately by Jetpack host)
- Webpack replaces `calypso/components/formatted-header` with local `src/components/generic-header`

## External Systems

- **DSP** (Demand Side Platform, `github.tumblr.net/Tumblr/a8c-dsp`): Node.js backend + React widget for campaign creation. Config keys: `dsp_stripe_pub_key`, `dsp_widget_js_src`
- **Jetpack Blaze package** (`github.com/Automattic/jetpack/tree/trunk/projects/packages/blaze`): PHP controllers that proxy all DSP API calls through Jetpack REST API (`/jetpack/v4/blaze-app/...`). Dashboard version must stay compatible with shipped blaze package version.
- **Blaze Ads plugin** (`github.com/Automattic/blaze-ads`): Standalone WP plugin that also loads this dashboard, uses Jetpack Connect + Sync modules
- **Billing**: `adpurchase.wordpress.com` (WooCommerce instance with Stripe)
- **WPCOM proxy**: For WordPress.com context, API calls go through `public-api.wordpress.com`

## Build & Deploy

- Built by TeamCity automatically on every trunk 
```

### snapshot_file_2

```
const { nodeConfig } = require( '@automattic/calypso-eslint-overrides' );

module.exports = {
	env: {
		browser: true,
	},
	overrides: [
		{
			files: [ './bin/**/*', './webpack.config.js' ],
			...nodeConfig,
		},
	],
};

```

### snapshot_file_3

```
@[[INSTRUCTION]]

```

### snapshot_file_4

```
# Blaze Dashboard App

Blaze Dashboard is built as a standalone application to be used inside Jetpack, and in the future, into WooCommerce. The Jetpack counterpart of the project is in [here](https://github.com/Automattic/jetpack/tree/trunk/projects/packages/blaze).

## Hiarachy

'''
.
└── src/
    ├── components/       ← blaze dashboard app only components. For now there is only a layout component.
    ├── page-middleware/  ← page.js integration with React and everything
    ├── app.js            ← entry point
    └── routes.js         ← page.js routes
'''

## Routing

It utilizes the [hashbang (#!) in page.js](https://github.com/visionmedia/page.js), however it doesn't work out of the box, because we are using hardcoded paths in Calypso, so some tricks are done in Jetpack to intercept the anchor clicks and convert them to hashbangs.

'''
$("#wpcom").on('click', 'a', function (e) {
	const link = e && e.currentTarget && e.currentTarget.attributes && e.currentTarget.attributes.href && e.currentTarget.attributes.href.value;
	if( link && ! link.startsWith( 'http' ) ) {
		location.hash = `#!${link}`;
		return false;
	}
});
'''

## Gridicon

The `Gridicon` in `@automattic/components` leverages `<use>` to load SVG sprites and has issues when loading from CDN (i.e. other than the main domain). So we had to replace with one that doesn't load the SVG sprite file - `packages/components/src/gridicon/no-asset.tsx` - and then in Jetpack, we load it separately:

'''
$.get("https://widgets.wp.com/blaze-dashboard/common/gridicons-506499ddac13811fee8e.svg", function(data) {
	var div = document.createElement("div");
	div.innerHTML = new XMLSerializer().serializeToString(data.documentElement);
	div.style = 'display: none';
	document.body.insertBefore(div, document.body.childNodes[0]);
});
'''

## Building

### Production

'''bash
cd apps/blaze-dashboard
yarn build
'''

### Development with local Jetpack

1. Ensure you have a working local Jetpack installation
2. Run `BLAZE_DASHBOARD_P
```

### snapshot_file_5

```
/**
 * The loader parses a config file and filters out the keys needed by the app, so that we don't load the whole config file.
 * @param {*} source Content of source file.
 * @returns filtered content of source file.
 */
module.exports = function ( source ) {
	const sourceObject = JSON.parse( source );
	const targetObject = {};
	const options = this.getOptions();
	if ( options.keys && options.keys.length > 0 ) {
		let key;
		for ( key of options.keys ) {
			targetObject[ key ] = sourceObject[ key ];
		}
	}

	return JSON.stringify( targetObject );
};

```

### snapshot_file_6

```
{
	"name": "@automattic/blaze-dashboard",
	"version": "0.1.0",
	"description": "Blaze dashboard served within wp-admin via the Jetpack plugin.",
	"main": "dist/build.min.js",
	"sideEffects": true,
	"repository": {
		"type": "git",
		"url": "git://github.com/Automattic/wp-calypso.git",
		"directory": "apps/blaze-dashboard"
	},
	"private": true,
	"author": "Automattic Inc.",
	"license": "GPL-2.0-or-later",
	"bugs": {
		"url": "https://github.com/Automattic/wp-calypso/issues"
	},
	"homepage": "https://github.com/Automattic/wp-calypso",
	"scripts": {
		"clean": "npx rimraf dist",
		"build": "NODE_ENV=production yarn dev",
		"build:stats": "calypso-build",
		"teamcity:build-app": "yarn run build",
		"dev": "yarn run calypso-apps-builder --localPath dist --remotePath /home/wpcom/public_html/widgets.wp.com/blaze-dashboard/v1",
		"show-stats": "NODE_ENV=production EMIT_STATS=true yarn build",
		"translate": "rm -rf dist/strings && mkdir -p dist && wp-babel-makepot '../../{client,packages,apps}/**/*.{js,jsx,ts,tsx}' --ignore '**/node_modules/**,**/test/**,**/*.d.ts' --base '../../' --dir './dist/strings' --output './dist/blaze-dashboard-strings.pot' && build-app-languages --stringsFilePath='./dist/blaze-dashboard-strings.pot'"
	},
	"dependencies": {
		"@automattic/accessible-focus": "workspace:^",
		"@automattic/calypso-config": "workspace:^",
		"@automattic/calypso-polyfills": "workspace:^",
		"@automattic/calypso-router": "workspace:^",
		"@automattic/calypso-url": "workspace:^",
		"@automattic/components": "workspace:^",
		"@automattic/i18n-utils": "workspace:^",
		"@automattic/number-formatters": "^1.1.0",
		"@tanstack/react-query": "^5.83.0",
		"@wordpress/components": "^30.9.0",
		"@wordpress/data": "^10.23.0",
		"@wordpress/element": "^6.23.0",
		"@wordpress/icons": "^10.23.0",
		"calypso": "workspace:^",
		"clsx": "^2.1.1",
		"debug": "^4.4.1",
		"i18n-calypso": "workspace:^",
		"moment": "^2.30.1",
		"prop-types": "^15.8.1",
		"react": "^18.3.1",
		"react-dom": "^18
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

## Apps

- **Help Center** (`apps/help-center`) — build/deploy layer that bundles `packages/help-center` into webpack entry points served from `widgets.wp.com`.

## Development

'''bash
# Setup
yarn install

# Build and start the dev server
yarn start

# Build and start the dev server for the Dashboard client only.
yarn start-dashboard
'''

## Testing instructions

> **Note**: E2E tests require a local Calypso development instance to be running.

`
```

### snapshot_file_10

```
version: 2.1

orbs:
  win: circleci/windows@5.0.0

references:
  defaults: &defaults
    working_directory: ~/wp-calypso
    docker:
      - image: cimg/node:22.9.0
    environment:
      CIRCLE_ARTIFACTS: /tmp/artifacts
      CIRCLE_TEST_REPORTS: /tmp/test_results
      PLAYWRIGHT_SKIP_DOWNLOAD: 'true'
      SKIP_TSC: 'true'
      NODE_OPTIONS: --max-old-space-size=3072
      npm_config_cache: /home/circleci/.cache/yarn
  desktop_defaults: &desktop_defaults
    working_directory: ~/wp-calypso

  setup-results-and-artifacts: &setup-results-and-artifacts
    name: Create Directories for Results and Artifacts
    command: |
      mkdir -p                                  \
        "$CIRCLE_ARTIFACTS/notifications-panel" \
        "$CIRCLE_ARTIFACTS/screenshots"         \
        "$CIRCLE_ARTIFACTS/wpcom-block-editor"  \
        "$CIRCLE_TEST_REPORTS/client"           \
        "$CIRCLE_TEST_REPORTS/eslint"           \
        "$CIRCLE_TEST_REPORTS/integration"      \
        "$CIRCLE_TEST_REPORTS/packages"         \
        "$CIRCLE_TEST_REPORTS/server"           \
        "$CIRCLE_TEST_REPORTS/e2ereports"       \
        "$HOME/jest-cache"

  # Git cache
  #
  # Calypso is a big repository with a lot of history. It can take a long time to do a full checkout.
  # By including the `.git` directory in the cache, we can speed things up by only needing to update
  # the local repository.
  #
  # We cache on the branch and revision, falling back to origin/HEAD, or any recent cache.
  #
  # More about the CircleCI cache: https://circleci.com/docs/2.0/caching
  restore-git-cache: &restore-git-cache
    name: Restore git cache
    keys:
      - v{{ .Environment.GLOBAL_CACHE_PREFIX }}-v2-git-{{ .Branch }}-{{ .Revision }}
      - v{{ .Environment.GLOBAL_CACHE_PREFIX }}-v2-git-{{ .Branch }}
      - v{{ .Environment.GLOBAL_CACHE_PREFIX }}-v2-git-trunk
      - v{{ .Environment.GLOBAL_CACHE_PREFIX }}-v2-git
  update-git: &update-git
    name: Update all branches
    command: git fe
```
