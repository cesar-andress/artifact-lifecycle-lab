# Annotation packet `a38973860e5d4712`

Protocol: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`
Packet spec: `rq5_v1_blind_packet_spec_v2`

Judge only with the materials below. Do not seek external repositories or experimental results.

## Annotator question

Is Referenced artifact R1 materially necessary for completing THIS software engineering task in THIS repository snapshot?

## Anonymous snapshot

- Snapshot ID: `9e54242c358f3dbd`
- Reference type: `path`
- Artifact alias: **Referenced artifact R1**

## Task brief

Engineering task (derived only from the pinned instruction text and snapshot signals):

Document title: [[INSTRUCTION]]. Guidance Section: ### Module Structure The app is split into ~26 `PV*` Swift Package frameworks. Key modules: - **PVLibrary** — Data models, Realm persistence, game database, CloudKit sync - **PVCoreBridge** — Protocol/bridge between app and emulator cores - **PVCoreBridgeRetro** — RetroArch-specific core bridge - **PVCoreLoader** — Dynamic loading of emulator core packages - **PVEmulatorCore** — Base classes for emulator implementations - **PVUI** — SwiftUI-based shared UI components - **PVSettings** — User preferences - **PVCoreAudio / PVAudio** — Audio engine and playback - **PVSupport** — Shared utilities - **PVLogging** — Logging infrastructure (CocoaLumberjack-based) - **PVPrimitives** — Base data types Instruction overview: This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

While performing this work, the instruction cites Referenced artifact R1. Your annotation question is whether that cited artifact is materially necessary for completing this task in the provided snapshot.

No automated verification command was identified from the pinned repository manifests. Judge necessity from the stated engineering task and the supplied snapshot materials only.

## Artifact role

Referenced artifact R1 is a repository artifact cited by the project instruction text (reference kind: path). Its literal path string is withheld and shown as [[REF]] so treatment assignment cannot be inferred from path identity. Use the citation excerpts, task brief, and snapshot context below to judge relevance and necessity.

## Path policy

Path identity for the cited artifact and for contrast-only manipulated paths is replaced by [[REF]] using semantic whole-path tokenization (not substring replacement). Other snapshot paths may appear when they do not reveal treatment assignment. Do not infer experimental treatment from path placeholders.

## Instruction citation excerpts

### Excerpt 1

```
## Project Overview

Provenance is a multi-platform emulator frontend for iOS/tvOS supporting 60+ retro gaming systems. Written primarily in Swift with Objective-C/C++ bridge layers for emulator cores.

## Build & Development

### Prerequisites
- Xcode 16.2 (`[[REF]]`)
- Ruby + Bundler (for fastlane)
- `make setup` to install all dependencies

### Code Signing
Copy `CodeSigning.xcconfig.sample` to `CodeSigning.xcconfig` and fill in your developer account details.

### Building
'''bash
```

## Repository tree excerpt (pinned snapshot)

```
"UITesting/UITesting/Assets.xcassets/AppIcon.appiconset/DALL\302\267E 2024-11-24 17.16.52 - A mosaic of pixel-perfect 16-bit style sprites inspired by classic Sega and Atari consoles. The sprites feature characters, objects, and game elements.png"
.all-contributorsrc
.bundle/config
.codiumignore
.cursorignore
.github/CODEOWNERS
.github/FUNDING.yml
.github/ISSUE_TEMPLATE/bug-report.md
.github/ISSUE_TEMPLATE/feature-request.md
.github/PULL_REQUEST_TEMPLATE.md
.github/auto_assign.yml
.github/labeler.yml
.github/workflows/attach_build_products.yml
.github/workflows/build.yml
.github/workflows/codesee-arch-diagram.yml
.github/workflows/disabled/assignee-to-reviewer.yml
.github/workflows/disabled/autosquash.yml
.github/workflows/disabled/contributors.yml
.github/workflows/disabled/danger.yml
.github/workflows/disabled/greet-contributors.yml
.github/workflows/disabled/release-notes-preview.yml
.github/workflows/disabled/xcodebuild.yml
.github/workflows/rebase.yml
.github/workflows/swiftlint.yml
.github/workflows/swiftlint_autocorrect.yml
.gitignore
.gitmodules
.swiftformat
.swiftlint.yml
.xcode-version
Build-iOS.xcconfig
Build-tvOS.xcconfig
Build-watchOS.xcconfig
Build.xcconfig
CHANGELOG.md
[[REF]]
CONTRIBUTORS.md
CodeSigning.xcconfig.sample
DEVELOPER.md
Dangerfile.swift
ExportOptions.plist
Gemfile
Gemfile.lock
LICENSE.md
Makefile
Package.swift
PrivacyInfo.xcprivacy
Provenance-Scade.nimble-project
README.md
README_SIRI_SHORTCUTS.md
SYSTEMS.md
TODO.md
URL_SCHEME_EXAMPLES.md
appcenter-post-clone.sh
azure-archive.yml
azure-pipelines.yml
azure.sh
modules
project.yml
rename_moltenvk.sh
```

## Neighbouring paths

_None listed in the minimal context window._

## Nearby documentation paths

```
[[REF]]
Cores/Atari800/README.md
Cores/BeetlePSX/cmake/Makefile
Cores/Citra/cmake/README
Cores/Citra/lib/vma/CMakeLists.txt
Cores/Citra/lib/vma/README.md
Cores/Citra/lib/vma/src/CMakeLists.txt
Cores/Citra/lib/vma/src/Shaders/CMakeLists.txt
Cores/Citra/lib/vma/tools/GpuMemDumpVis/README.md
Cores/DosBox/cmake/Makefile
```

## Nearby configuration paths

```
.github/FUNDING.yml
.github/auto_assign.yml
.github/labeler.yml
.github/workflows/attach_build_products.yml
.github/workflows/build.yml
.github/workflows/codesee-arch-diagram.yml
.github/workflows/disabled/assignee-to-reviewer.yml
.github/workflows/disabled/autosquash.yml
.github/workflows/disabled/contributors.yml
.github/workflows/disabled/danger.yml
```

## Pinned snapshot file excerpts

### snapshot_file_1

```
# [[INSTRUCTION]]

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Provenance is a multi-platform emulator frontend for iOS/tvOS supporting 60+ retro gaming systems. Written primarily in Swift with Objective-C/C++ bridge layers for emulator cores.

## Build & Development

### Prerequisites
- Xcode 16.2 (`[[REF]]`)
- Ruby + Bundler (for fastlane)
- `make setup` to install all dependencies

### Code Signing
Copy `CodeSigning.xcconfig.sample` to `CodeSigning.xcconfig` and fill in your developer account details.

### Building
'''bash
make open          # Open Provenance.xcworkspace in Xcode
make ios           # Update submodules + build iOS
make tvos          # Update submodules + build tvOS
make update        # Pull + update submodules + install gems
make test          # Run tests via fastlane
'''

Build from Xcode: open `Provenance.xcworkspace` and select a scheme. Start with `Provenance-Lite` (fastest build) before moving to `Provenance-Release` or `Provenance-XL (Release)`.

**Note:** Initial builds may fail because some source files are generated lazily at compile time. Retry if Xcode gets the build order wrong on first build.

### Schemes
- **Provenance-Lite (AppStore)** — lightweight, fewer cores
- **Provenance (AppStore)** — standard release
- **Provenance-XL (Release)** — includes more RetroArch and native cores
- Each has iOS and tvOS variants

### CI
GitHub Actions (`.github/workflows/build.yml`) builds all target variants on push/PR to `develop` and `master`.

## Architecture

### Module Structure
The app is split into ~26 `PV*` Swift Package frameworks. Key modules:

- **PVLibrary** — Data models, Realm persistence, game database, CloudKit sync
- **PVCoreBridge** — Protocol/bridge between app and emulator cores
- **PVCoreBridgeRetro** — RetroArch-specific core bridge
- **PVCoreLoader** — Dynamic loading of emulator core packages
- **PVEmulatorCore** — Base classes fo
```

### snapshot_file_2

```
Atari800-Core
=============

Provenance EMU Core plugin with Atari800 to support Atari 5200 emulation 

```

### snapshot_file_3

```
DEBUG = 0
FRONTEND_SUPPORTS_RGB565 = 0
HAVE_OPENGL = 1
GLES = 1
GLES3 = 1 # HW renderer now supported on GLES3
HAVE_VULKAN = 0
HAVE_JIT = 0
HAVE_CHD = 1
HAVE_CDROM = 0
HAVE_LIGHTREC = 1
LINK_STATIC_LIBCPLUSPLUS = 1
THREADED_RECOMPILER = 1
LIGHTREC_DEBUG = 0
LIGHTREC_LOG_LEVEL = 3

CORE_DIR := .
HAVE_GRIFFIN = 0

SPACE :=
SPACE := $(SPACE) $(SPACE)
BACKSLASH :=
BACKSLASH := \$(BACKSLASH)
filter_out1 = $(filter-out $(firstword $1),$1)
filter_out2 = $(call filter_out1,$(call filter_out1,$1))

GIT_VERSION ?= " $(shell git rev-parse --short HEAD || echo unknown)"
ifneq ($(GIT_VERSION)," unknown")
   FLAGS += -DGIT_VERSION=\"$(GIT_VERSION)\"
endif

ifeq ($(platform),)
   platform = unix
   ifeq ($(shell uname -s),)
      platform = win
   else ifneq ($(findstring Darwin,$(shell uname -s)),)
      platform = osx
      arch     = intel
      ifeq ($(shell uname -p),powerpc)
         arch = ppc
      endif
   else ifneq ($(findstring MINGW,$(shell uname -s)),)
      platform = win
   endif
else ifneq (,$(findstring armv,$(platform)))
   override platform += unix
endif

ifneq ($(platform), osx)
   ifeq ($(findstring Haiku,$(shell uname -s)),)
      PTHREAD_FLAGS = -lpthread
   endif
endif
platform = ios-arm64
NEED_CD = 1
NEED_TREMOR = 1
NEED_BPP = 32
NEED_DEINTERLACER = 1
NEED_THREADING = 1
SET_HAVE_HW = 0
CORE_DEFINE := -DWANT_PSX_EMU
TARGET_NAME := mednafen_psx

ifeq ($(HAVE_HW), 1)
   HAVE_VULKAN = 1
   HAVE_OPENGL = 1
   SET_HAVE_HW = 1
endif

ifeq ($(HAVE_VULKAN), 1)
   SET_HAVE_HW = 1
endif

ifeq ($(HAVE_OPENGL), 1)
   SET_HAVE_HW = 1
endif

ifeq ($(SET_HAVE_HW), 1)
   FLAGS += -DHAVE_HW
   TARGET_NAME := mednafen_psx_hw
endif

ifneq ($(LIGHTREC_DEBUG), 0)
   DEBUG = 1
   FLAGS += -DLIGHTREC_DEBUG
   ifeq ($(LIGHTREC_DEBUG), 2)
      FLAGS += -DLIGHTREC_VERY_DEBUG
   endif
endif

# Unix
ifneq (,$(findstring unix,$(platform)))
   TARGET := $(TARGET_NAME)_libretro.so
   fpic   := -fPIC
   ifneq ($(findstring SunOS,$(shell uname -a)),)
      GREP = ggrep
      SHARED := -s
```

### snapshot_file_4

```
# These are supported funding model platforms

github: [JoeMatt]
patreon: provenance
open_collective: provenanceemu
buy_me_a_coffee: joemattiello
ko_fi: # Replace with a single Ko-fi username
tidelift: # Replace with a single Tidelift platform-name/package-name e.g., npm/babel
community_bridge: # Replace with a single Community Bridge project-name e.g., cloud-foundry
liberapay: # Replace with a single Liberapay username
issuehunt: # Replace with a single IssueHunt username
otechie: # Replace with a single Otechie username
lfx_crowdfunding: # Replace with a single LFX Crowdfunding project-name e.g., cloud-foundry
custom: # Replace with up to 4 custom sponsorship URLs e.g., ['link1', 'link2']

```

### snapshot_file_5

```
# Set to true to add reviewers to pull requests
addReviewers: true

# Set to true to add assignees to pull requests
addAssignees: true

# A list of reviewers to be added to pull requests (GitHub user name)
reviewers:
  - JoeMatt
  # - jasarien
  - sevdestruct
  - mrjschulte
# A number of reviewers added to the pull request
# Set 0 to add all the reviewers (default: 0)
numberOfReviewers: 0

# A list of assignees, overrides reviewers if set
assignees:
  - JoeMatt
  # - jasarien


# A number of assignees to add to the pull request
# Set to 0 to add all of the assignees.
# Uses numberOfReviewers if unset.
numberOfAssignees: 1

# A list of keywords to be skipped the process that add reviewers if pull requests include it
# skipKeywords:
  - wip
  - Bump
```

### snapshot_file_6

```
# Number of labels to fetch (optional). Defaults to 20
numLabels: 20
# These labels will not be used even if the issue contains them (optional). 
# Pass a blank array if no labels are to be excluded.
# excludeLabels: []
excludeLabels:
  - confirmed-bug
  - confirmed-fix

```
