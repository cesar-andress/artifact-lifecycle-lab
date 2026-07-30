# Annotation packet `e2642ac6cb4568a4`

Protocol: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`
Packet spec: `rq5_v1_blind_packet_spec_v2`

Judge only with the materials below. Do not seek external repositories or experimental results.

## Annotator question

Is Referenced artifact R1 materially necessary for completing THIS software engineering task in THIS repository snapshot?

## Anonymous snapshot

- Snapshot ID: `353c0dfdd2030a91`
- Reference type: `directory`
- Artifact alias: **Referenced artifact R1**

## Task brief

Engineering task (derived only from the pinned instruction text and snapshot signals):

Document title: [[INSTRUCTION]]. Instruction overview: This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

While performing this work, the instruction cites Referenced artifact R1. Your annotation question is whether that cited artifact is materially necessary for completing this task in the provided snapshot.

No automated verification command was identified from the pinned repository manifests. Judge necessity from the stated engineering task and the supplied snapshot materials only.

## Artifact role

Referenced artifact R1 is a repository artifact cited by the project instruction text (reference kind: directory). Its literal path string is withheld and shown as [[REF]] so treatment assignment cannot be inferred from path identity. Use the citation excerpts, task brief, and snapshot context below to judge relevance and necessity.

## Path policy

Path identity for the cited artifact and for contrast-only manipulated paths is replaced by [[REF]] using semantic whole-path tokenization (not substring replacement). Other snapshot paths may appear when they do not reveal treatment assignment. Do not infer experimental treatment from path placeholders.

## Instruction citation excerpts

### Excerpt 1

```
| ------------ | ---------- | ---------------------------------------- | ---------------------------------------------------------------------- |
| Raspberry Pi | `pi.mk`    | `PLATFORM_PI`                            | libgpiod, builds all external submodules, fppoled/fppcapedetect/fpprtc |
| BeagleBone   | `bb.mk`    | `PLATFORM_BBB` or `PLATFORM_BB64`        | PRU support, NEON SIMD (32-bit), fppoled/fppcapedetect                 |
| macOS        | `osx.mk`   | `PLATFORM_OSX`                           | clang++, CoreAudio framework, `.dylib` extension                       |
| Linux        | `linux.mk` | `PLATFORM_DEBIAN`/`PLATFORM_UBUNTU`/etc. | Docker detection skips OLED/cape/RTC builds                            |

## Plugin Compatibility

External plugins (`[[REF]]`) are compiled separately and link against FPP headers. When modifying public headers (especially `fpp-pch.h`, `commands/Commands.h`, `Plugin.h`, `Plugins.h`, or any header included by channel output plugins), preserve backward compatibility:

- Do not remove or rename public macros, classes, or functions that plugins may depend on. If cleaning up internally, keep the old symbol as an alias/empty define with a comment.
- `HTTP_RESPONSE_CONST` in `fpp-pch.h` is an example: FPP's own code no longer uses it, but it's kept as an empty `#define` for plugin compatibility.
- Channel output plugins implement `ChannelOutput` or `ThreadedChannelOutput` and are loaded via `dlopen()`. Changes to these base class interfaces will break all plugins.

## Code Style

- **C++**: Configured via `.clang-format`. 4-space indent, no tabs, Allman-ish braces (custom), no column limit, C++20/23 standard.
```

## Repository tree excerpt (pinned snapshot)

```
.clang-format
.claude/architecture.md
.claude/channel-output.md
.claude/core-infrastructure.md
.claude/hardware-plugins-scripts.md
.claude/overlays.md
.claude/playlist-commands-media.md
.github/FUNDING.yml
.github/ISSUE_TEMPLATE/bug_report.md
.github/ISSUE_TEMPLATE/feature_request.md
[[REF]]
.github/workflows/build-images.yml
.github/workflows/docker-build.yml
.gitignore
.gitmodules
.prettierrc
.vscode/build.sh
.vscode/c_cpp_properties.json
.vscode/extensions.json
.vscode/launch.json
.vscode/settings.json
.vscode/tasks.json
CLAUDE.md
```

## Neighbouring paths

```
.github/FUNDING.yml
```

## Nearby documentation paths

```
CLAUDE.md
README.md
SD/README.Armbian
SD/README.BB64
SD/README.BBB
SD/README.Debian
SD/README.RaspberryPi
SD/README.md
capes/drivers/bb64/Makefile
capes/drivers/bbb/Makefile
```

## Nearby configuration paths

```
.github/FUNDING.yml
.github/workflows/build-images.yml
.github/workflows/docker-build.yml
.vscode/c_cpp_properties.json
.vscode/extensions.json
.vscode/launch.json
.vscode/settings.json
.vscode/tasks.json
Docker/Dockerfile
Docker/docker-compose-dev.yml
```

## Pinned snapshot file excerpts

### snapshot_file_1

```
# [[INSTRUCTION]]

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FPP (Falcon Player) is a lightweight, optimized sequence player for LED lighting control, designed for Raspberry Pi and BeagleBone SBCs. It speaks E1.31, DDP, DMX, ArtNet, KiNet, Pixelnet, and Renard protocols and can drive LED panels and WS2811 pixel strings via hardware capes. It also supports MQTT for remote control and integration.

## Build System

The project uses Make. The primary Makefile is `src/Makefile`, which includes fragments from `src/makefiles/`.

'''bash
# Build everything (from src/ directory)
cd src && make

# Build targets
make              # default optimized build (-O3, -g1 on master)
make debug        # debug build (-g -DDEBUG)
make asan         # address sanitizer build
make tsan         # thread sanitizer build

# Clean
make clean        # remove all build artifacts
make cleanfpp     # remove just fpp artifacts (keeps PCH)
'''

Platform is auto-detected: macOS uses clang/clang++, Linux uses g++. On macOS, Homebrew dependencies are expected at `/opt/homebrew` (ARM) or `/usr/local` (Intel). Linker preference: mold > gold > default ld. Precompiled headers used unless DISTCC_HOSTS is set.

### macOS Setup

Run `SD/FPP_Install_Mac.sh` from a directory that will serve as the media directory. It installs Homebrew and all required dependencies (php, httpd, ffmpeg, ccache, SDL2, zstd, taglib, mosquitto, jsoncpp, libhttpserver, graphicsmagick, libusb).

### Key Build Artifacts

- `libfpp.so` (`.dylib` on macOS) — core shared library with most functionality
- `fppd` — main daemon, links against libfpp
- `fpp` — CLI tool (connects to fppd via domain socket)
- `fppmm` — memory map utility
- `fppoled` — OLED display driver (Pi/BBB only)
- `fppcapedetect` — hardware cape auto-detection (Pi/BBB)
- `fpprtc` — real-time clock utility
- `fppinit` — FPP initialization
- `fsequtils` — FSEQ file utilities
- Channe
```

### snapshot_file_2

```
# These are supported funding model platforms

github: # Replace with up to 4 GitHub Sponsors-enabled usernames e.g., [user1, user2]
patreon: # Replace with a single Patreon username
open_collective: # Replace with a single Open Collective username
ko_fi: # Replace with a single Ko-fi username
tidelift: # Replace with a single Tidelift platform-name/package-name e.g., npm/babel
community_bridge: # Replace with a single Community Bridge project-name e.g., cloud-foundry
liberapay: # Replace with a single Liberapay username
issuehunt: # Replace with a single IssueHunt username
otechie: # Replace with a single Otechie username
lfx_crowdfunding: # Replace with a single LFX Crowdfunding project-name e.g., cloud-foundry
custom: ["https://www.paypal.com/donate/?hosted_button_id=ASF9XYZ2V2F5G"] # Replace with up to 4 custom sponsorship URLs e.g., ['link1', 'link2']

```

### snapshot_file_3

```
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FPP (Falcon Player) is a lightweight, optimized sequence player for LED lighting control, designed for Raspberry Pi and BeagleBone SBCs. It speaks E1.31, DDP, DMX, ArtNet, KiNet, Pixelnet, and Renard protocols and can drive LED panels and WS2811 pixel strings via hardware capes. It also supports MQTT for remote control and integration.

## Build System

The project uses Make. The primary Makefile is `src/Makefile`, which includes fragments from `src/makefiles/`.

'''bash
# Build everything (from src/ directory)
cd src && make

# Build targets
make              # default optimized build (-O3, -g1 on master)
make debug        # debug build (-g -DDEBUG)
make asan         # address sanitizer build
make tsan         # thread sanitizer build

# Clean
make clean        # remove all build artifacts
make cleanfpp     # remove just fpp artifacts (keeps PCH)
'''

Platform is auto-detected: macOS uses clang/clang++, Linux uses g++. On macOS, Homebrew dependencies are expected at `/opt/homebrew` (ARM) or `/usr/local` (Intel). Linker preference: mold > gold > default ld. Precompiled headers used unless DISTCC_HOSTS is set.

### macOS Setup

Run `SD/FPP_Install_Mac.sh` from a directory that will serve as the media directory. It installs Homebrew and all required dependencies (php, httpd, ffmpeg, ccache, SDL2, zstd, taglib, mosquitto, jsoncpp, libhttpserver, graphicsmagick, libusb).

### Key Build Artifacts

- `libfpp.so` (`.dylib` on macOS) — core shared library with most functionality
- `fppd` — main daemon, links against libfpp
- `fpp` — CLI tool (connects to fppd via domain socket)
- `fppmm` — memory map utility
- `fppoled` — OLED display driver (Pi/BBB only)
- `fppcapedetect` — hardware cape auto-detection (Pi/BBB)
- `fpprtc` — real-time clock utility
- `fppinit` — FPP initialization
- `fsequtils` — FSEQ file utilities
- Channel output plugi
```

### snapshot_file_4

```
# FPP - Falcon Player

The Falcon Player (FPP) is a lightweight, optimized, feature-rich sequence player designed to
run on low-cost Single Board Computers (SBC). It was originally created to run on the $35
Raspberry Pi, hence the middle 'P' in the short name but now the FPP supports many more
systems. It is still mostly commonly used on a Raspberry Pi (Zero, 2, 3, 4, 5) or a Beagle Bone (Black, Green, Pocket).
The FPP shorthand is still used but it is now just called Falcon Player.

FPP aims to be controller agnostic, it can talk E1.31,
DDP, DMX, Pixelnet, and Renard to hardware from multiple hardware vendors. Using various capes, FPP
can also be a controller on P5 and P10 Matrixes, or strings of ws2811 pixels.

FPP is intended to be used on Raspberry Pi and Beagle based SBC (single board computers).  These are the only platforms 'supported'.

Docker, other SBCs eg Orange Pi, PC hardware, virtual machines, Debian, Ubuntu installs etc are not 'supported'.

Useful Links:

- [Documentation in Github](./docs/README.md)
- [Falcon Player website](https://www.falconplayer.com)
- [Falcon Christmas forums](http://falconchristmas.com/forum/)
- [Falcon Player sub-forum](http://falconchristmas.com/forum/index.php/board,8.0.html)
- [Wiki](http://falconchristmas.com/wiki/index.php/Main_Page)

```

### snapshot_file_5

```
Installing FPP on Armbian
==========================

This documents installing FPP on top of an existing Armbian system. For
generic Debian / Ubuntu / NUC installs see SD/README.Debian. For images
that FPP itself produces and ships, see SD/README.md and the per-platform
build scripts (no Armbian image build is shipped today).

Supported releases
------------------

- Armbian based on Debian 13 (Trixie)
- Armbian based on Ubuntu 24.04

Older Armbian (Bullseye / Bookworm / Ubuntu 22.04 base) is no longer
supported. Download the most recent stable Armbian build for your board
from https://www.armbian.com/. Prefer the "minimal" / "cli" image variant
if available; desktop variants install fine but waste a lot of disk.

Hardware caveats
----------------

FPP on Armbian gets you a basic player -- E1.31 / DDP / sound output should
work on most boards. Caveats vary per board:

- Hats / capes for pixels or LED panels are unlikely to work without
  board-specific GPIO/SPI overlays. The FPP cape autodetect logic targets
  Pi and BeagleBone hardware.
- HDMI output may need /boot/armbianEnv.txt tweaks to enable a framebuffer.
  Search the Armbian forums for your specific board.
- Hardware-accelerated video decode usually doesn't work; software decode
  via VLC works for SD content but high-def will likely stutter.
- For Le Potato, VLC sometimes wants explicit DRI args:
    --kms-device /dev/dri/card1 --kms-connector HDMI-A-1 --kms-drm-chroma XR24

eMMC installs
-------------

If the board has eMMC and you want FPP installed there, use `armbian-config`
to copy the running system to eMMC. Easier to do before installing FPP
(less data to copy), but you can also install on SD first then mass-copy
the SD-running install to eMMC across multiple devices.

Thermal note
------------

The compile (especially building VLC from source) pegs all cores at 100%
for a long time. Boards without a heatsink/fan can hit thermal-shutdown
mid-install. If that happens, you have to restart from a fresh
```

### snapshot_file_6

```
#############################################################################
# Build FPP SD card images for Pi, Pi64, BBB, and BB64.
#
# Runs:
#   - workflow_dispatch: manual trigger with optional version string
#   - schedule:          nightly at 04:00 UTC
#   - push (tag v*):     release build; results are attached to a GitHub
#                        release named from the tag
#
# Strategy:
#   - Pi64 / BB64 build on GitHub's free arm64 runners (native, fast)
#   - Pi  / BBB  build on x86_64 runners via qemu-arm-static (slow, but
#     avoids needing self-hosted hardware)
#
# All four build scripts use FPP_SRC_DIR pointing at the checkout, so local
# changes in the tree are picked up without needing to push first.
#############################################################################

name: Build Images

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'FPP version string (blank = nightly-YYYYMMDD)'
        required: false
        default: ''
      platforms:
        description: 'Comma-separated subset of platforms to build (blank = all)'
        required: false
        default: ''
  schedule:
    - cron: '0 4 * * *'
  push:
    tags:
      - 'v*'

# A manual re-run on the same ref should cancel a running build to avoid
# wasting a 2-hour qemu job when you realize you tagged the wrong commit.
concurrency:
  group: build-images-${{ github.ref }}
  cancel-in-progress: true

jobs:
  prep:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.ver.outputs.version }}
      is_release: ${{ steps.ver.outputs.is_release }}
      is_nightly: ${{ steps.ver.outputs.is_nightly }}
    steps:
      - name: Determine version string
        id: ver
        run: |
          # Tag push -> release build, version from tag
          if [ "${{ github.event_name }}" = "push" ] && [[ "$GITHUB_REF" == refs/tags/v* ]]; then
            V="${GITHUB_REF#refs/tags/v}"
            echo "is_release=true" >> "$GITHUB_OUTPUT"
            echo "is_nightl
```

### snapshot_file_7

```
name: Build and Publish Docker

on:
  # Run when pushes to branch or create new Tag
  push:
    branches:
      - '*'
    paths-ignore:
      - 'docs/**'
      - '*.md'
  create:
    tags:
      - '*'

jobs:
  # define job to build and publish docker image
  build-and-push-docker-image:
    name: Build Docker image and push to repositories
    # run only when code is compiling and tests are passing
    runs-on: ubuntu-latest

    # steps to perform in job
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up QEMU
        run: sudo apt-get update && sudo apt-get install qemu-user-static -y
        
      # setup Docker buld action
      - name: Set up Docker Buildx
        id: buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to DockerHub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Extract branch name
        shell: bash
        run: |
          TAG="latest"
          case $GITHUB_REF in refs/heads/*)
          TAG=${GITHUB_REF#refs/heads/};;
          esac

          case $GITHUB_REF in refs/tags/*)
          TAG=${GITHUB_REF#refs/tags/};
          esac

          echo "##[set-output name=branch;]$TAG"
        id: extract_branch

      - name: PrepareReg Names
        shell: bash
        run: echo IMAGE_REPOSITORY=$(echo ${{ github.repository_owner }} | tr '[:upper:]' '[:lower:]') >> $GITHUB_ENV
        id: extract_repository

      - name: Build image and push to Docker Hub 
        uses: docker/build-push-action@v6
        with:
          # relative path to the place where source code with Dockerfile is located
          context: .
          file: ./Docker/Dockerfile
          build-args: "FPPBRANCH=${{ steps.extract_branch.outputs.branch }}"
          # Note: tags has to be all lower-case
          platforms: linux/amd64,linux/arm64,linux/arm/v7
          tags: ${{ env.IMAGE_R
```
