# Annotation packet `8819745939ade378`

Protocol: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`
Packet spec: `rq5_v1_blind_packet_spec_v2`

Judge only with the materials below. Do not seek external repositories or experimental results.

## Annotator question

Is Referenced artifact R1 materially necessary for completing THIS software engineering task in THIS repository snapshot?

## Anonymous snapshot

- Snapshot ID: `0d0bb8734581a071`
- Reference type: `directory`
- Artifact alias: **Referenced artifact R1**

## Task brief

Engineering task (derived only from the pinned instruction text and snapshot signals):

Document title: Stratus Red Team. Guidance Section: When you need to create or update new attack techniques, use the `create-attack-technique` skill. Instruction overview: Stratus Red Team is a CLI tool and Go library that allows you to easily detonate granular, real-world cloud attack techniques.

While performing this work, the instruction cites Referenced artifact R1. Your annotation question is whether that cited artifact is materially necessary for completing this task in the provided snapshot.

Verification command observed in the pinned repository manifests: `make test`. Use this only as a snapshot signal of how the project checks work; do not assume other commands.

## Artifact role

Referenced artifact R1 is a repository artifact cited by the project instruction text (reference kind: directory). Its literal path string is withheld and shown as [[REF]] so treatment assignment cannot be inferred from path identity. Use the citation excerpts, task brief, and snapshot context below to judge relevance and necessity.

## Path policy

Path identity for the cited artifact and for contrast-only manipulated paths is replaced by [[REF]] using semantic whole-path tokenization (not substring replacement). Other snapshot paths may appear when they do not reveal treatment assignment. Do not infer experimental treatment from path placeholders.

## Instruction citation excerpts

### Excerpt 1

```
## Guidelines for creating new attack techniques

When you need to create or update new attack techniques, use the `create-attack-technique` skill.

## Testing and developing locally

To run locally:
- `[[REF]]`
- `go run cmd/stratus/*.go COMMAND` (e.g. `go run cmd/stratus/*.go list` or `go run cmd/stratus/*.go detonate aws.persistence.admin-iam-user`)

To run unit tests, run `make test`.

To automatically generate attack technique documentation, use `make docs`.

## DON'T
```

## Repository tree excerpt (pinned snapshot)

```
.claude/skills/create-attack-technique/SKILL.md
.claude/skills/create-attack-technique/assets/sample-attack-technique.go
.claude/skills/create-attack-technique/references/provider-configs.md
.github/CODEOWNERS
.github/ISSUE_TEMPLATE/bug_report.md
.github/ISSUE_TEMPLATE/feature_request.md
.github/chainguard/self.release.create-pr.sts.yaml
.github/dependabot.yml
.github/pull_request_template.md
.github/workflows/docker.yml
.github/workflows/docs.yml
.github/workflows/release.yml
.github/workflows/scorecards.yml
.github/workflows/static-analysis.yml
.github/workflows/terraform-lint.yml
.github/workflows/test.yml
.gitignore
.goreleaser.yaml
[[REF]]
Dockerfile
Formula/stratus-red-team.rb
LICENSE
LICENSE-3rdparty.csv
Makefile
NOTICE
README.md
SECURITY.md
mkdocs.yml
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
[[REF]]
```

## Neighbouring paths

_None listed in the minimal context window._

## Nearby documentation paths

```
[[REF]]
Makefile
README.md
docs/contributing.md
examples/README.md
examples/basic/README.md
examples/basic/go.mod
examples/custom/README.md
examples/custom/go.mod
examples/detonate-and-dump-cloudtrail-logs/README.md
```

## Nearby configuration paths

```
.github/chainguard/self.release.create-pr.sts.yaml
.github/dependabot.yml
.github/workflows/docker.yml
.github/workflows/docs.yml
.github/workflows/release.yml
.github/workflows/scorecards.yml
.github/workflows/static-analysis.yml
.github/workflows/terraform-lint.yml
.github/workflows/test.yml
.goreleaser.yaml
```

## Pinned snapshot file excerpts

### snapshot_file_1

```
# Stratus Red Team

Stratus Red Team is a CLI tool and Go library that allows you to easily detonate granular, real-world cloud attack techniques.

## Guidelines for creating new attack techniques

When you need to create or update new attack techniques, use the `create-attack-technique` skill.

## Testing and developing locally

To run locally:
- `[[REF]]`
- `go run cmd/stratus/*.go COMMAND` (e.g. `go run cmd/stratus/*.go list` or `go run cmd/stratus/*.go detonate aws.persistence.admin-iam-user`)

To run unit tests, run `make test`.

To automatically generate attack technique documentation, use `make docs`.

## DON'T

- Don't directly change auto-generated documentation in `docs/attack-techniques/`.
```

### snapshot_file_2

```
package main

import (
	"errors"
	"[repository]/v2/pkg/stratus"
	"[repository]/v2/pkg/stratus/runner"
	"github.com/spf13/cobra"
	"log"
	"os"
)

var flagForceCleanup bool
var flagCleanupAll bool

func buildCleanupCmd() *cobra.Command {
	cleanupCmd := &cobra.Command{
		Use:                   "cleanup [attack-technique-id]... | --all",
		Aliases:               []string{"clean"},
		Short:                 "Cleans up any leftover infrastructure or configuration from a TTP.",
		Example:               "stratus cleanup aws.defense-evasion.cloudtrail-stop\nstratus cleanup --all",
		DisableFlagsInUseLine: true,
		Args: func(cmd *cobra.Command, args []string) error {
			if len(args) == 0 && flagCleanupAll {
				if !flagCleanupAll {
					return errors.New("pass the ID of the technique to clean up, or --all")
				}
				return nil
			}

			// Ensure the technique IDs are valid
			_, err := resolveTechniques(args)

			return err
		},
		ValidArgsFunction: func(cmd *cobra.Command, args []string, toComplete string) ([]string, cobra.ShellCompDirective) {
			return getTechniquesCompletion(toComplete), cobra.ShellCompDirectiveNoFileComp
		},
		RunE: func(cmd *cobra.Command, args []string) error {
			if len(args) > 0 {
				techniques, _ := resolveTechniques(args)
				doCleanupCmd(techniques)
				return nil
			} else if flagCleanupAll {
				// clean up all techniques that are not in the COLD state
				doCleanupAllCmd()
				return nil
			} else {
				return errors.New("pass the ID of the technique to clean up, or --all")
			}
		},
	}
	cleanupCmd.Flags().BoolVarP(&flagForceCleanup, "force", "f", false, "Force cleanup even if the technique is already COLD")
	cleanupCmd.Flags().BoolVarP(&flagCleanupAll, "all", "", false, "Clean up all techniques that are not in COLD state")
	return cleanupCmd
}

func doCleanupCmd(techniques []*stratus.AttackTechnique) {
	workerCount := len(techniques)
	techniquesChan := make(chan *stratus.AttackTechnique, workerCou
```

### snapshot_file_3

```
package main

import (
	"errors"
	"[repository]/v2/internal/utils"
	"[repository]/v2/pkg/stratus"
	"[repository]/v2/pkg/stratus/runner"
	"os"
	"strings"

	"github.com/spf13/cobra"
)

var detonateForce bool
var detonateCleanup bool

func buildDetonateCmd() *cobra.Command {
	detonateCmd := &cobra.Command{
		Use:   "detonate attack-technique-id [attack-technique-id]...",
		Short: "Detonate one or multiple attack techniques",
		Example: strings.Join([]string{
			"stratus detonate aws.defense-evasion.cloudtrail-stop",
			"stratus detonate aws.defense-evasion.cloudtrail-stop --cleanup",
		}, "\n"),
		DisableFlagsInUseLine: true,
		PreRunE: func(cmd *cobra.Command, args []string) error {
			if len(args) == 0 {
				cmd.Help()
				os.Exit(0)
			}
			return nil
		},
		Args: func(cmd *cobra.Command, args []string) error {
			if len(args) == 0 {
				return errors.New("you must specify at least one attack technique")
			}
			_, err := resolveTechniques(args)
			return err
		},
		ValidArgsFunction: func(cmd *cobra.Command, args []string, toComplete string) ([]string, cobra.ShellCompDirective) {
			return getTechniquesCompletion(toComplete), cobra.ShellCompDirectiveNoFileComp
		},
		Run: func(cmd *cobra.Command, args []string) {
			techniques, _ := resolveTechniques(args)
			doDetonateCmd(techniques, detonateCleanup)
		},
	}
	detonateCmd.Flags().BoolVarP(&detonateCleanup, "cleanup", "", false, "Clean up the infrastructure that was spun up as part of the technique prerequisites")
	//detonateCmd.Flags().BoolVarP(&detonateNoWarmup, "no-warmup", "", false, "Do not spin up prerequisite infrastructure or configuration. Requires that 'warmup' was used before.")
	detonateCmd.Flags().BoolVarP(&detonateForce, "force", "f", false, "Force detonation in cases where the technique is not idempotent and has already been detonated")

	return detonateCmd
}
func doDetonateCmd(techniques []*stratus.AttackTechnique, cleanup bool) {
	
```

### snapshot_file_4

```
package main

import (
	"fmt"
	"[repository]/v2/pkg/stratus"
	"[repository]/v2/pkg/stratus/mitreattack"
	"github.com/fatih/color"
	"github.com/jedib0t/go-pretty/v6/table"
	"github.com/spf13/cobra"
	"log"
	"strings"
)

var listPlatform string
var listMitreAttackTactic string

func buildListCmd() *cobra.Command {
	listCmd := &cobra.Command{
		Use:   "list",
		Short: "List attack techniques",
		Example: strings.Join([]string{
			"stratus list",
			"stratus list --platform aws --mitre-attack-tactic persistence",
		}, "\n"),
		Run: func(cmd *cobra.Command, args []string) {
			doListCmd(listMitreAttackTactic, listPlatform)
		},
	}
	listCmd.Flags().StringVarP(&listPlatform, "platform", "", "", "Filter on specific platform")
	listCmd.Flags().StringVarP(&listMitreAttackTactic, "mitre-attack-tactic", "", "", "Filter on a specific MITRE ATT&CK tactic.")
	return listCmd
}

func doListCmd(mitreAttackTactic string, platform string) {
	filter := stratus.AttackTechniqueFilter{}
	if platform != "" {
		platform, err := stratus.PlatformFromString(platform)
		if err != nil {
			log.Fatal(err)
		}
		filter.Platform = platform
	}
	if mitreAttackTactic != "" {
		tactic, err := mitreattack.AttackTacticFromString(mitreAttackTactic)
		if err != nil {
			log.Fatal(err)
		}
		filter.Tactic = tactic
	}
	techniques := stratus.GetRegistry().GetAttackTechniques(&filter)
	t := GetDisplayTable()
	t.AppendHeader(table.Row{"Technique ID", "Technique name", "Platform", "MITRE ATT&CK Tactic"})

	for i := range techniques {
		displayName := techniques[i].ID
		if friendlyName := techniques[i].FriendlyName; friendlyName != "" {
			displayName = friendlyName
		}
		t.AppendRow(table.Row{
			techniques[i].ID,
			displayName,
			techniques[i].Platform,
			getTacticsString(techniques[i].MitreAttackTactics),
		})
	}

	fmt.Println()
	fmt.Println(color.CyanString("View the list of all available attack techniques at: https://stratus-red-team.cloud/attack-techniques/list
```

### snapshot_file_5

```
package main

import (
	_ "[repository]/v2/internal/attacktechniques"
	"github.com/spf13/cobra"
	"log"
	"os"
)

var rootCmd = &cobra.Command{
	Use: "stratus",
}

func init() {
	setupLogging()

	listCmd := buildListCmd()
	showCmd := buildShowCmd()
	warmupCmd := buildWarmupCmd()
	detonateCmd := buildDetonateCmd()
	revertCmd := buildRevertCmd()
	statusCmd := buildStatusCmd()
	cleanupCmd := buildCleanupCmd()
	versionCmd := buildVersionCmd()

	rootCmd.AddCommand(listCmd)
	rootCmd.AddCommand(showCmd)
	rootCmd.AddCommand(warmupCmd)
	rootCmd.AddCommand(detonateCmd)
	rootCmd.AddCommand(revertCmd)
	rootCmd.AddCommand(statusCmd)
	rootCmd.AddCommand(cleanupCmd)
	rootCmd.AddCommand(versionCmd)
}

func setupLogging() {
	log.SetOutput(os.Stdout)
}

func main() {
	rootCmd.Execute()
}

```

### snapshot_file_6

```
BUILD_VERSION := dev-snapshot

MAKEFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
ROOT_DIR := $(dir $(MAKEFILE_PATH))

# Use go modules
export GO111MODULE=on

# Define binaries directory
BIN_DIR := $(ROOT_DIR)/bin

# Define go flags
GOFLAGS := -ldflags="-X main.BuildVersion=$(BUILD_VERSION) -w"

.PHONY: build docs test thirdparty-licenses mocks

# Default target
all: build

build:
	@echo "Building Stratus..."
	@cd v2 && go build $(GOFLAGS) -o $(BIN_DIR)/stratus cmd/stratus/*.go
	@echo "Build completed. Binaries are saved in $(BIN_DIR)"

docs:
	@echo "Generating documentation..."
	@cd v2 && go run ./tools/ ../docs
	@echo "Documentation generated successfully."

test:
	@echo "Running tests..."
	@cd v2 && go test ./... -v
	@echo "Tests completed successfully."

thirdparty-licenses:
	@echo "Retrieving third-party licenses..."
	@cd v2 && go get github.com/google/go-licenses
	@cd v2 && go install github.com/google/go-licenses
	@cd v2 && $(GOPATH)/bin/go-licenses csv [repository]/v2/cmd/stratus | sort > $(ROOT_DIR)/LICENSE-3rdparty.csv
	@echo "Third-party licenses retrieved and saved to $(ROOT_DIR)/LICENSE-3rdparty.csv"

mocks:
	@echo "Generating mocks..."
	@cd v2 && mockery --name=StateManager --dir internal/state --output internal/state/mocks
	@cd v2 && mockery --name=TerraformManager --dir pkg/stratus/runner --output pkg/stratus/runner/mocks
	@cd v2 && mockery --name=FileSystem --structname FileSystemMock --dir internal/state --output internal/state/mocks
	@echo "Mocks generated successfully."

```

### snapshot_file_7

```
# Stratus Red Team

[![made-with-Go](https://img.shields.io/badge/Made%20with-Go-1f425f.svg)](http://golang.org)  [![Tests](https://github.com/DataDog/stratus-red-team/actions/workflows/test.yml/badge.svg)](https://github.com/DataDog/stratus-red-team/actions/workflows/test.yml) [![static analysis](https://github.com/DataDog/stratus-red-team/actions/workflows/static-analysis.yml/badge.svg)](https://github.com/DataDog/stratus-red-team/actions/workflows/static-analysis.yml) [![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/DataDog/stratus-red-team/badge)](https://api.securityscorecards.dev/projects/github.com/DataDog/stratus-red-team) [![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/6530/badge)](https://bestpractices.coreinfrastructure.org/projects/6530)

<p align="center">
  <img src="./docs/logo.png" alt="Stratus Red Team" width="300" />
</p>

Stratus Red Team is "[Atomic Red Team](https://github.com/redcanaryco/atomic-red-team)™" for the cloud, allowing to emulate offensive attack techniques in a granular and self-contained manner.

<p align="center">
  <a href="https://github.com/DataDog/stratus-red-team/raw/main/docs/demo.gif">
    <img src="./docs/demo.gif" alt="Terminal recording" />
  </a>
</p>

Read the announcement blog posts:
- https://www.datadoghq.com/blog/cyber-attack-simulation-with-stratus-red-team/
- https://blog.christophetd.fr/introducing-stratus-red-team-an-adversary-emulation-tool-for-the-cloud/

## Getting Started

Stratus Red Team is a self-contained Go binary.

See the documentation at **[stratus-red-team.cloud](https://stratus-red-team.cloud/)**:
- [Stratus Red Team Concepts](https://stratus-red-team.cloud/user-guide/getting-started/#concepts)

- [Installing Stratus Red Team](https://stratus-red-team.cloud/user-guide/getting-started/#installation) - Homebrew formula, Docker image and pre-built binaries available

- [Available Attack Techniques](https://stratus-red-team.cloud/attack-techniqu
```

### snapshot_file_8

```
issuer: https://token.actions.githubusercontent.com

subject_pattern: repo:DataDog/stratus-red-team:ref:refs/(heads/main|tags/.*)

claim_pattern:
  event_name: push
  ref: refs/(heads/main|tags/.*)
  # ref_protected: "true" # Can't set this because GH API is not reliable on tag protection status. Cf https://github.com/orgs/community/discussions/142985
  job_workflow_ref: DataDog/stratus-red-team/.github/workflows/release.yml@refs/(heads/main|tags/.*)

permissions:
  contents: write
  pull_requests: write

```

### snapshot_file_9

```
version: 2
updates:
- package-ecosystem: "docker"
  directory: "/"
  schedule:
    interval: "monthly"
- package-ecosystem: "github-actions"
  directory: "/"
  schedule:
    interval: "monthly"

```

### snapshot_file_10

```
name: docker

on:
  push:
    tags:
      - "*"

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: datadog/stratus-red-team

permissions:
  contents: read

jobs:
  docker-build-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - name: Harden Runner
        uses: step-security/harden-runner@f4a75cfd619ee5ce8d5b864b0d183aff3c69b55a
        with:
          egress-policy: block
          allowed-endpoints: >
            auth.docker.io:443
            dl-cdn.alpinelinux.org:443
            ghcr.io:443
            github.com:443
            pipelines.actions.githubusercontent.com:443
            pkg-containers.githubusercontent.com:443
            production.cloudflare.docker.com:443
            proxy.golang.org:443
            sum.golang.org:443            
            registry-1.docker.io:443
            storage.googleapis.com:443
            *.actions.githubusercontent.com:443

      - name: Checkout
        uses: actions/checkout@8e8c483db84b4bee98b60c0593521ed34d9990e8 # v6.0.1
        with:
          fetch-depth: 0

      - name: Log into registry ${{ env.REGISTRY }}
        uses: docker/login-action@74a5d142397b4f367a81961eba4e8cd7edddf772
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push Docker image
        uses: docker/build-push-action@263435318d21b8e681c14492fe198d362a7d2c83
        with:
          context: .
          push: true
          build-args: |
            VERSION=${{ github.ref_name }}
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.ref_name }}
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest

```
