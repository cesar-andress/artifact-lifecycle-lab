# Annotation packet `b8695a2837b8211e`

Protocol: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`
Packet spec: `rq5_v1_blind_packet_spec_v2`

Judge only with the materials below. Do not seek external repositories or experimental results.

## Annotator question

Is Referenced artifact R1 materially necessary for completing THIS software engineering task in THIS repository snapshot?

## Anonymous snapshot

- Snapshot ID: `1581dc99057567c3`
- Reference type: `path`
- Artifact alias: **Referenced artifact R1**

## Task brief

Engineering task (derived only from the pinned instruction text and snapshot signals):

Document title: Workbench Tree Widgets Overview. Stated purpose: Use when asked to consume workbench tree widgets in VS Code. Purpose Section: The Workbench Tree Widgets provide high-level, workbench-integrated tree components that extend the base tree implementations with VS Code-specific functionality like context menus, keyboard navigation, theming, accessibility, and dependency injection integration. These widgets serve as the primary tree components used throughout the VS Code workbench for file explorers, debug views, search results, and other hierarchical data presentations. Instruction overview: **Location**: `src/vs/platform/list/browser/listService.ts` **Type**: Platform Services **Layer**: Platform

While performing this work, the instruction cites Referenced artifact R1. Your annotation question is whether that cited artifact is materially necessary for completing this task in the provided snapshot.

Verification command observed in the pinned repository manifests: `npm run test`. Use this only as a snapshot signal of how the project checks work; do not assume other commands.

## Artifact role

Referenced artifact R1 is a repository artifact cited by the project instruction text (reference kind: path). Its literal path string is withheld and shown as [[REF]] so treatment assignment cannot be inferred from path identity. Use the citation excerpts, task brief, and snapshot context below to judge relevance and necessity.

## Path policy

Path identity for the cited artifact and for contrast-only manipulated paths is replaced by [[REF]] using semantic whole-path tokenization (not substring replacement). Other snapshot paths may appear when they do not reveal treatment assignment. Do not infer experimental treatment from path placeholders.

## Instruction citation excerpts

### Excerpt 1

```
- **ResourceNavigator**: Handles file/resource opening with proper editor integration
- **IOpenEvent**: Event interface for resource opening with editor options
- **IWorkbench*TreeOptions**: Configuration interfaces extending base options with workbench features
- **IResourceNavigatorOptions**: Configuration for resource opening behavior

### Key Files

- **`src/vs/platform/list/browser/listService.ts`**: Contains all workbench tree widget implementations, shared workbench functionality (`WorkbenchTreeInternals`), and configuration utilities
	- `[[REF]]`: Unit tests for workbench trees
- **`src/vs/base/browser/ui/tree/objectTree.ts`**: Base implementation for static trees and compressible trees
	- `src/vs/base/test/browser/ui/tree/objectTree.test.ts`: Base tree tests
- **`src/vs/base/browser/ui/tree/asyncDataTree.ts`**: Base implementation for async trees with lazy loading support
	- `src/vs/base/test/browser/ui/tree/asyncDataTree.test.ts`: Async tree tests
- **`src/vs/base/browser/ui/tree/dataTree.ts`**: Base implementation for data-driven trees with explicit data sources
	- `src/vs/base/test/browser/ui/tree/dataTree.test.ts`: Data tree tests
- **`src/vs/base/browser/ui/tree/abstractTree.ts`**: Base tree foundation
- **`src/vs/base/browser/ui/tree/tree.ts`**: Core interfaces and types
```

## Repository tree excerpt (pinned snapshot)

```
"src/vs/workbench/services/search/test/node/fixtures/\303\274m laut\346\261\211\350\257\255/\346\261\211\350\257\255.txt"
.config/1espt/PipelineAutobaseliningConfig.yml
.config/configuration.winget
.config/guardian/.gdnsuppress
.devcontainer/Dockerfile
.devcontainer/README.md
.devcontainer/devcontainer-lock.json
.devcontainer/devcontainer.json
.devcontainer/install-vscode.sh
.devcontainer/post-create.sh
.editorconfig
.eslint-ignore
.eslint-plugin-local/README.md
.eslint-plugin-local/code-amd-node-module.ts
.eslint-plugin-local/code-declare-service-brand.ts
.eslint-plugin-local/code-ensure-no-disposables-leak-in-test.ts
.eslint-plugin-local/code-import-patterns.ts
.eslint-plugin-local/code-layering.ts
.eslint-plugin-local/code-limited-top-functions.ts
.eslint-plugin-local/code-must-use-result.ts
.eslint-plugin-local/code-must-use-super-dispose.ts
.eslint-plugin-local/code-no-any-casts.ts
.eslint-plugin-local/code-no-dangerous-type-assertions.ts
.eslint-plugin-local/code-no-deep-import-of-internal.ts
.eslint-plugin-local/code-no-global-document-listener.ts
.eslint-plugin-local/code-no-in-operator.ts
.eslint-plugin-local/code-no-localization-template-literals.ts
.eslint-plugin-local/code-no-localized-model-description.ts
.eslint-plugin-local/code-no-native-private.ts
.eslint-plugin-local/code-no-nls-in-standalone-editor.ts
.eslint-plugin-local/code-no-observable-get-in-reactive-context.ts
.eslint-plugin-local/code-no-potentially-unsafe-disposables.ts
.eslint-plugin-local/code-no-reader-after-await.ts
.eslint-plugin-local/code-no-runtime-import.ts
.eslint-plugin-local/code-no-standalone-editor.ts
.eslint-plugin-local/code-no-static-self-ref.ts
.eslint-plugin-local/code-no-test-async-suite.ts
.eslint-plugin-local/code-no-test-only.ts
.eslint-plugin-local/code-no-unexternalized-strings.ts
.eslint-plugin-local/code-no-unused-expressions.ts
.eslint-plugin-local/code-parameter-properties-must-have-explicit-accessibility.ts
.eslint-plugin-local/code-policy-localization-key-match.ts
.eslint-plugin-local/code-translation-remind.ts
.eslint-plugin-local/index.ts
.eslint-plugin-local/package.json
.eslint-plugin-local/tests/code-no-observable-get-in-reactive-context-test.ts
.eslint-plugin-local/tests/code-no-reader-after-await-test.ts
.eslint-plugin-local/tsconfig.json
.eslint-plugin-local/utils.ts
.eslint-plugin-local/vscode-dts-cancellation.ts
.eslint-plugin-local/vscode-dts-create-func.ts
.eslint-plugin-local/vscode-dts-event-naming.ts
.eslint-plugin-local/vscode-dts-interface-naming.ts
.eslint-plugin-local/vscode-dts-literal-or-types.ts
.eslint-plugin-local/vscode-dts-provider-naming.ts
.eslint-plugin-local/vscode-dts-string-type-literals.ts
.eslint-plugin-local/vscode-dts-use-export.ts
.eslint-plugin-local/vscode-dts-use-thenable.ts
.eslint-plugin-local/vscode-dts-vscode-in-comments.ts
.git-blame-ignore-revs
```

## Neighbouring paths

```
.github/instructions/chat.instructions.md
.github/instructions/disposable.instructions.md
.github/instructions/interactive.instructions.md
.github/instructions/learnings.instructions.md
.github/instructions/notebook.instructions.md
.github/instructions/observables.instructions.md
.github/instructions/telemetry.instructions.md
```

## Nearby documentation paths

```
.devcontainer/README.md
.eslint-plugin-local/README.md
.eslint-plugin-local/package.json
.vscode/extensions/vscode-selfhost-import-aid/package.json
.vscode/extensions/vscode-selfhost-test-provider/package.json
AGENTS.md
CONTRIBUTING.md
README.md
build/builtin/package.json
build/monaco/README-npm.md
```

## Nearby configuration paths

```
.config/1espt/PipelineAutobaseliningConfig.yml
.devcontainer/Dockerfile
.devcontainer/devcontainer-lock.json
.devcontainer/devcontainer.json
.eslint-plugin-local/package.json
.eslint-plugin-local/tsconfig.json
.github/ISSUE_TEMPLATE/config.yml
.github/classifier.json
.github/commands.json
.github/commands/codespaces_issue.yml
```

## Pinned snapshot file excerpts

### snapshot_file_1

```
---
description: Use when asked to consume workbench tree widgets in VS Code.
---

# Workbench Tree Widgets Overview

**Location**: `src/vs/platform/list/browser/listService.ts`
**Type**: Platform Services
**Layer**: Platform

## Purpose

The Workbench Tree Widgets provide high-level, workbench-integrated tree components that extend the base tree implementations with VS Code-specific functionality like context menus, keyboard navigation, theming, accessibility, and dependency injection integration. These widgets serve as the primary tree components used throughout the VS Code workbench for file explorers, debug views, search results, and other hierarchical data presentations.

## Scope

### Included Functionality
- **Context Integration**: Automatic context key management, focus handling, and VS Code theme integration
- **Resource Navigation**: Built-in support for opening files and resources with proper editor integration
- **Accessibility**: Complete accessibility provider integration with screen reader support
- **Keyboard Navigation**: Smart keyboard navigation with search-as-you-type functionality
- **Multi-selection**: Configurable multi-selection behavior with platform-appropriate modifier keys
- **Dependency Injection**: Full integration with VS Code's service container for automatic service injection
- **Configuration**: Automatic integration with user settings for tree behavior customization

### Integration Points
- **IInstantiationService**: For service injection and component creation
- **IContextKeyService**: For managing focus, selection, and tree state context keys
- **IListService**: For registering trees and managing workbench list lifecycle
- **IConfigurationService**: For reading tree configuration settings
- **Resource Navigators**: For handling file/resource opening with proper editor integration

### Out of Scope
- Low-level tree rendering and virtualization (handled by base tree classes)
- Data management and async loading logic (provided by 
```

### snapshot_file_2

```
---
description: Chat feature area coding guidelines
---

## Adding chat/AI-related features

- When adding a new chat/AI feature like a new surface where chat or agents appear, a new AI command, etc, these features must not show up for users when they've disabled AI features. The best way to do this is to gate the feature on the context key `ChatContextKeys.enabled` via a when clause.
- When doing a code review for code that adds an AI feature, please ensure that the feature is properly gated.

## Learnings

```

### snapshot_file_3

```
---
description: Guidelines for writing code using IDisposable
---

Core symbols:
* `IDisposable`
	* `dispose(): void` - dispose the object
* `Disposable` (implements `IDisposable`) - base class for disposable objects
	* `this._store: DisposableStore`
	* `this._register<T extends IDisposable>(t: T): T`
		* Try to immediately register created disposables! E.g. `const someDisposable = this._register(new SomeDisposable())`
* `DisposableStore` (implements `IDisposable`)
	* `add<T extends IDisposable>(t: T): T`
	* `clear()`
* `toDisposable(fn: () => void): IDisposable` - helper to create a disposable from a function

* `MutableDisposable` (implements `IDisposable`)
	* `value: IDisposable | undefined`
	* `clear()`
	* A value that enters a mutable disposable (at least once) will be disposed the latest when the mutable disposable is disposed (or when the value is replaced or cleared).

## Learnings

```

### snapshot_file_4

```
---
description: Architecture documentation for VS Code interactive window component. Use when working in folder 
---

# Interactive Window

The interactive window component enables extensions to offer REPL like experience to its users. VS Code provides the user interface and extensions provide the execution environment, code completions, execution results rendering and so on.

The interactive window consists of notebook editor at the top and regular monaco editor at the bottom of the viewport. Extensions can extend the interactive window by leveraging the notebook editor API and text editor/document APIs:

* Extensions register notebook controllers for the notebook document in the interactive window through `vscode.notebooks.createNotebookController`. The notebook document has a special notebook view type `interactive`, which is contributed by the core instead of extensions. The registered notebook controller is responsible for execution.
* Extensions register auto complete provider for the bottom text editor through `vscode.languages.registerCompletionItemProvider`. The resource scheme for the text editor is `interactive-input` and the language used in the editor is determined by the notebook controller contributed by extensions.

Users can type in code in the text editor and after users pressing `Shift+Enter`, we will insert a new code cell into the notebook document with the content from the text editor. Then we will request execution for the newly inserted cell. The notebook controller will handle the execution just like it's in a normal notebook editor.

## Interactive Window Registration

Registering a new editor type in the workbench consists of two steps:

* Register an editor input factory which is responsible for resolving resources with given `glob` patterns. Here we register an `InteractiveEditorInput` for all resources with `vscode-interactive` scheme.
* Register an editor pane factory for the given editor input type. Here we register `InteractiveEdito
```

### snapshot_file_5

```
---
description: This document describes how to deal with learnings that you make. (meta instruction)
---

This document describes how to deal with learnings that you make.
It is a meta-instruction file.

Structure of learnings:
* Each instruction file has a "Learnings" section.
* Each learning has a 1-4 sentences description of the learning.

Example:
'''markdown
## Learnings
* Prefer `const` over `let` whenever possible
* Avoid `any` type
'''

When the user tells you "learn!", you should:
* extract a learning from the recent conversation
	* identify the problem that you created
	* identify why it was a problem
	* identify how you were told to fix it/how the user fixed it
	* reflect over it, maybe it can be generalized? Avoid too specific learnings.
* create a learning (1-4 sentences) from that
	* Write this out to the user and reflect over these sentences
	* then, add the reflected learning to the "Learnings" section of the most appropriate instruction file

```

### snapshot_file_6

```
---
description: Architecture documentation for VS Code notebook and interactive window components
---

# Notebook Architecture

This document describes the internal architecture of VS Code's notebook implementation.

## Model resolution

Notebook model resolution is handled by `NotebookService`. It resolves notebook models from the file system or other sources. The notebook model is a tree of cells, where each cell has a type (code or markdown) and a list of outputs.

## Viewport rendering (virtualization)

The notebook viewport is virtualized to improve performance. Only visible cells are rendered, and cells outside the viewport are recycled. The viewport rendering is handled by `NotebookCellList` which extends `WorkbenchList<CellViewModel>`.

![Viewport Rendering](./resources/notebook/viewport-rendering.drawio.svg)

The rendering has the following steps:

1. **Render Viewport** - Layout/render only the cells that are in the visible viewport
2. **Render Template** - Each cell type has a template (code cell, markdown cell) that is instantiated via `CodeCellRenderer` or `MarkupCellRenderer`
3. **Render Element** - The cell content is rendered into the template
4. **Get Dynamic Height** - Cell height is computed dynamically based on content (editor lines, outputs, etc.)
5. **Cell Parts Lifecycle** - Each cell has lifecycle parts that manage focus, selection, and other state

### Cell resize above viewport

When a cell above the viewport is resized (e.g., output grows), the viewport needs to be updated to maintain scroll position. This is handled by tracking scroll anchors.

![Cell Resize Above Viewport](./resources/notebook/cell-resize-above-viewport.drawio.svg)

## Cell Rendering

The notebook editor renders cells through a contribution system. Cell parts are organized into two categories via `CellPartsCollection`:

- **CellContentPart** - Non-floating elements rendered inside a cell synchronously to avoid flickering
  - `prepareRenderCell()` - Prepare model (no DOM
```

### snapshot_file_7

```
# Code - OSS Development Container

[![Open in Dev Containers](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=[repository])

This repository includes configuration for a development container for working with Code - OSS in a local container or using [GitHub Codespaces](https://github.com/features/codespaces).

> **Tip:** The default VNC password is `vscode`. The VNC server runs on port `5901` and a web client is available on port `6080`.

## Quick start - local

If you already have VS Code and Docker installed, you can click the badge above or [here](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=[repository]) to get started. Clicking these links will cause VS Code to automatically install the Dev Containers extension if needed, clone the source code into a container volume, and spin up a dev container for use.

1. Install Docker Desktop or Docker for Linux on your local machine. (See [docs](https://aka.ms/vscode-remote/containers/getting-started) for additional details.)

2. **Important**: Docker needs at least **4 Cores and 8 GB of RAM** to run a full build with **9 GB of RAM** being recommended. If you are on macOS, or are using the old Hyper-V engine for Windows, update these values for Docker Desktop by right-clicking on the Docker status bar item and going to **Preferences/Settings > Resources > Advanced**.

   > **Note:** The [Resource Monitor](https://marketplace.visualstudio.com/items?itemName=mutantdino.resourcemonitor) extension is included in the container so you can keep an eye on CPU/Memory in the status bar.

3. Install [Visual Studio Code Stable](https://code.visualstudio.com/) or [Insiders](https://code.visualstudio.com/insiders/) and the [Dev Containers](https://aka.ms/vscode-remote/download/containers) extension.

   ![Image of D
```

### snapshot_file_8

```
# Custom ESLint rules

We use a set of custom [ESLint](http://eslint.org) to enforce repo specific coding rules and styles. These custom rules are run in addition to many standard ESLint rules we enable in the project. Some example custom rules includes:

- Enforcing proper code layering
- Preventing checking in of `test.only(...)`
- Enforcing conventions in `vscode.d.ts`

Custom rules are mostly used for enforcing or banning certain coding patterns. We tend to leave stylistic choices up to area owners unless there's a good reason to enforce something project wide.

This doc provides a brief overview of how these rules are setup and how you can add a new one.

# Resources
- [ESLint rules](https://eslint.org/docs/latest/extend/custom-rules) — General documentation about writing eslint rules
- [TypeScript ASTs and eslint](https://typescript-eslint.io/blog/asts-and-typescript-eslint/) — Look at how ESLint works with TS programs
- [ESTree selectors](https://eslint.org/docs/latest/extend/selectors)  — Info about the selector syntax rules use to target specific nodes in an AST. Works similarly to css selectors.
- [TypeScript ESLint playground](https://typescript-eslint.io/play/#showAST=es) — Useful tool for figuring out the structure of TS programs and debugging custom rule selectors


# Custom Rule Configuration

Custom rules are defined in the `.eslint-plugin-local` folder. Each rule is defined in its own TypeScript file. These follow the naming convention:

- `code-RULE-NAME.ts` — General rules that apply to the entire repo.
- `vscode-dts-RULE-NAME.ts` — Rules that apply just to `vscode.d.ts`.

These rules are then enabled in the `eslint.config.js` file. This is the main eslint configuration for our repo. It defines a set of file scopes which rules should apply to files in those scopes.

For example, here's a configuration that enables the no `test.only` rule in all `*.test.ts` files in the VS Code repo:

'''ts
{
    // Define which files these rules apply to
    files
```

### snapshot_file_9

```
{
  "private": true,
  "type": "module",
  "scripts": {
    "typecheck": "tsgo -p tsconfig.json --noEmit"
  }
}

```

### snapshot_file_10

```
## DO NOT MODIFY THIS FILE MANUALLY. This is part of auto-baselining from 1ES Pipeline Templates. Go to [https://aka.ms/1espt-autobaselining] for more details.

pipelines:
  111:
    retail:
      source:
        credscan:
          lastModifiedDate: 2024-09-10
        eslint:
          lastModifiedDate: 2024-09-10
        psscriptanalyzer:
          lastModifiedDate: 2024-09-10
        armory:
          lastModifiedDate: 2024-09-10
        accessibilityinsights:
          lastModifiedDate: 2025-06-02
      binary:
        credscan:
          lastModifiedDate: 2025-02-04
        binskim:
          lastModifiedDate: 2025-02-04
        spotbugs:
          lastModifiedDate: 2025-02-04

```
