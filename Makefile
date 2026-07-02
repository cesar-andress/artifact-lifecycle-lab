PYTHON ?= python3.12
VENV ?= .venv
PIP := $(VENV)/bin/pip
PY := $(VENV)/bin/python

REGISTRY := data/registry/pilot_repos.csv
FAMILY := ai_conventions_v1
L1_EVENTS := data/l1/file_event_log/v1/events.parquet
L2_PANEL := data/derived/file_state_panel/v1/panel_T180.parquet
PROFILE_PARQUET := data/profiling/extraction_profile.parquet
PROFILE_CSV := data/profiling/extraction_profile.csv
CENSUS_STAMP := data/derived/adoption_census/v1/repo_census.parquet

FIG1_PDF := exports/e1/fig1.pdf
FIG1_CSV := exports/e1/fig1.csv
TABLE1 := exports/e1/table1.csv
E1_REPORT := exports/e1/e1_census.md
E1_PILOT_PERF := exports/e1/pilot_performance.md

E1_100_REGISTRY := data/registry/e1_100_repos.csv
E1_100_L1_DIR := data/l1/e1_100/v1
E1_100_PANEL_DIR := data/derived/file_state_panel/e1_100/v1
E1_100_CENSUS_DIR := data/derived/adoption_census/e1_100/v1
E1_100_WAVE := e1_100_v1
E1_100_EXPORT_DIR := exports/e1_100
E1_100_FIG1_PDF := $(E1_100_EXPORT_DIR)/fig1.pdf
E1_100_FIG1_CSV := $(E1_100_EXPORT_DIR)/fig1.csv
E1_100_TABLE1 := $(E1_100_EXPORT_DIR)/table1.csv
E1_100_REPORT := $(E1_100_EXPORT_DIR)/e1_census.md
E1_100_PERF := $(E1_100_EXPORT_DIR)/pilot_performance.md
E1_100_SUMMARY := $(E1_100_EXPORT_DIR)/cohort_summary.md

PAPER_ROOT ?= ../paper
PAPER_NOTE := $(PAPER_ROOT)/notes/pilot_performance.md

# Bounded development pilot (default: 3 repos, 120s timeouts via --skip-slow)
E1_PILOT_LIMIT ?= 3
INSPECTION_MODE ?= head-only

E1_1000_REGISTRY := data/registry/e1_1000_repos.csv
E1_1000_L1_DIR := data/l1/e1_1000/v1
E1_1000_PANEL_DIR := data/derived/file_state_panel/e1_1000/v1
E1_1000_CENSUS_DIR := data/derived/adoption_census/e1_1000/v1
E1_1000_WAVE := e1_1000_v1
E1_1000_REGISTRY_VERSION := e1_1000_v1
E1_1000_EXPORT_DIR := exports/e1_1000
E1_1000_FIG1_PDF := $(E1_1000_EXPORT_DIR)/fig1.pdf
E1_1000_FIG1_CSV := $(E1_1000_EXPORT_DIR)/fig1.csv
E1_1000_TABLE1 := $(E1_1000_EXPORT_DIR)/table1.csv
E1_1000_REPORT := $(E1_1000_EXPORT_DIR)/e1_census.md
E1_1000_PERF := $(E1_1000_EXPORT_DIR)/pilot_performance.md
E1_1000_SUMMARY := $(E1_1000_EXPORT_DIR)/cohort_summary.md
E1_1000_COHORT_DESIGN := $(E1_1000_EXPORT_DIR)/cohort_design.md
VSDLC_ELIGIBLE := $(HOME)/papers/vsdlc/vsdlc/data/interim/eligible_repos_enriched.jsonl
SECOND_FRAME := $(HOME)/papers/vsdlc/vsdlc/data/raw/second_frame_candidates.jsonl
GENERAL_OSS_POOL := data/registry/sources/general_oss_candidates.jsonl

.PHONY: e1 e1-pilot e1-100 e1-1000 paper ingest panel e1-exports profile-report test install-paper \
	e1-pilot-extract e1-pilot-derive e1-pilot-exports e1-extract e1-derive e1-exports-run \
	e1-100-extract e1-100-derive e1-100-exports e1-100-performance e1-100-summary \
	e1-1000-registry e1-1000-extract e1-1000-derive e1-1000-exports e1-1000-performance e1-1000-summary e1-1000-qa \
	recover verify truth-pilot-p1 truth-pilot-p2 truth-pilot-go-no-go truth-pilots \
	truth-decay-rq1 truth-decay-rq2 truth-decay-rq3 truth-decay-rq4 truth-decay-rq5-prep truth-decay-born-stale-audit truth-decay-born-stale-autopsy truth-pilot-p3 truth-pilot-p4 truth-pilot-p5 pre-scaling-gates

e1: install-paper e1-extract e1-derive e1-exports-run profile-report

e1-pilot: install-paper e1-pilot-extract e1-pilot-derive e1-pilot-exports profile-report

e1-extract:
	$(PY) -m artifact_lab.ingest extract \
	  --registry $(REGISTRY) \
	  --family $(FAMILY) \
	  --inspection-mode $(INSPECTION_MODE)

e1-derive:
	$(PY) -m artifact_lab.derive panel --T 180

e1-exports-run:
	$(PY) -m artifact_lab.experiments.e1_adoption_census --no-export

e1-pilot-extract:
	$(PY) -m artifact_lab.ingest extract \
	  --registry $(REGISTRY) \
	  --family $(FAMILY) \
	  --limit $(E1_PILOT_LIMIT) \
	  --skip-slow \
	  --inspection-mode $(INSPECTION_MODE)

e1-pilot-derive:
	$(PY) -m artifact_lab.derive panel --T 180

e1-pilot-exports:
	$(PY) -m artifact_lab.experiments.e1_adoption_census --no-export

e1-100: install-paper e1-100-extract e1-100-derive e1-100-exports e1-100-performance e1-100-summary

e1-100-extract:
	$(PY) -m artifact_lab.ingest extract \
	  --registry $(E1_100_REGISTRY) \
	  --family $(FAMILY) \
	  --wave $(E1_100_WAVE) \
	  --events-dir $(E1_100_L1_DIR) \
	  --inspection-mode $(INSPECTION_MODE)

e1-100-derive:
	$(PY) -m artifact_lab.derive panel --T 180 --events $(E1_100_L1_DIR) --output $(E1_100_PANEL_DIR)

e1-100-exports:
	$(PY) -m artifact_lab.experiments.e1_adoption_census --no-export \
	  --l1 $(E1_100_L1_DIR) \
	  --census-dir $(E1_100_CENSUS_DIR) \
	  --registry $(E1_100_REGISTRY) \
	  --fig1-csv $(E1_100_FIG1_CSV) \
	  --fig1-pdf $(E1_100_FIG1_PDF) \
	  --table1 $(E1_100_TABLE1) \
	  --report $(E1_100_REPORT)

e1-100-performance:
	$(PY) -m artifact_lab.experiments.pilot_performance \
	  --registry $(E1_100_REGISTRY) \
	  --output $(E1_100_PERF)

e1-100-summary:
	$(PY) -m artifact_lab.experiments.e1_adoption_census.cohort_summary \
	  --registry $(E1_100_REGISTRY) \
	  --census-dir $(E1_100_CENSUS_DIR) \
	  --table1 $(E1_100_TABLE1) \
	  --output $(E1_100_SUMMARY)

e1-1000-registry:
	@test -f $(GENERAL_OSS_POOL) || $(PY) -m artifact_lab.registry.build_general_oss_pool
	$(PY) -m artifact_lab.registry.build_e1_1000 \
	  --vsdlc $(VSDLC_ELIGIBLE) \
	  --second-frame $(SECOND_FRAME) \
	  --general-oss $(GENERAL_OSS_POOL) \
	  --output $(E1_1000_REGISTRY) \
	  --cohort-design $(E1_1000_COHORT_DESIGN)

e1-1000: install-paper e1-1000-registry e1-1000-extract e1-1000-derive e1-1000-exports e1-1000-performance e1-1000-summary

e1-1000-extract:
	$(PY) -m artifact_lab.ingest extract \
	  --registry $(E1_1000_REGISTRY) \
	  --family $(FAMILY) \
	  --wave $(E1_1000_WAVE) \
	  --registry-version $(E1_1000_REGISTRY_VERSION) \
	  --events-dir $(E1_1000_L1_DIR) \
	  --inspection-mode $(INSPECTION_MODE)

e1-1000-derive:
	$(PY) -m artifact_lab.derive panel --T 180 --events $(E1_1000_L1_DIR) --output $(E1_1000_PANEL_DIR)

e1-1000-exports:
	$(PY) -m artifact_lab.experiments.e1_adoption_census --no-export \
	  --l1 $(E1_1000_L1_DIR) \
	  --census-dir $(E1_1000_CENSUS_DIR) \
	  --registry $(E1_1000_REGISTRY) \
	  --fig1-csv $(E1_1000_FIG1_CSV) \
	  --fig1-pdf $(E1_1000_FIG1_PDF) \
	  --table1 $(E1_1000_TABLE1) \
	  --report $(E1_1000_REPORT)

e1-1000-performance:
	$(PY) -m artifact_lab.experiments.pilot_performance \
	  --registry $(E1_1000_REGISTRY) \
	  --output $(E1_1000_PERF)

e1-1000-summary:
	$(PY) -m artifact_lab.experiments.e1_adoption_census.cohort_summary \
	  --registry $(E1_1000_REGISTRY) \
	  --census-dir $(E1_1000_CENSUS_DIR) \
	  --table1 $(E1_1000_TABLE1) \
	  --output $(E1_1000_SUMMARY)

e1-1000-qa:
	$(PY) -m artifact_lab.experiments.e1_adoption_census.qa \
	  --registry $(E1_1000_REGISTRY) \
	  --census-dir $(E1_1000_CENSUS_DIR) \
	  --profiles $(PROFILE_PARQUET) \
	  --expected-rows 1000

recover:
	$(PY) -m artifact_lab.execution recover \
	  --registry $(E1_1000_REGISTRY) \
	  --family $(FAMILY) \
	  --wave $(E1_1000_WAVE) \
	  --events-dir $(E1_1000_L1_DIR) \
	  --registry-version $(E1_1000_REGISTRY_VERSION)

verify:
	$(PY) -m artifact_lab.execution verify \
	  --registry $(E1_1000_REGISTRY) \
	  --family $(FAMILY) \
	  --wave $(E1_1000_WAVE) \
	  --events-dir $(E1_1000_L1_DIR)

TRUTH_PILOT_EXPORT := exports/truth_pilot
TRUTH_PILOT_N ?= 400
TRUTH_PILOT_N_MIN ?= 300
TRUTH_PILOT_N_MAX ?= 500

truth-pilot-p1:
	$(PY) -m artifact_lab.experiments.truth_pilots p1 \
	  --output-dir $(TRUTH_PILOT_EXPORT) \
	  --n-samples $(TRUTH_PILOT_N) \
	  --n-min $(TRUTH_PILOT_N_MIN) \
	  --n-max $(TRUTH_PILOT_N_MAX)

truth-pilot-p2:
	$(PY) -m artifact_lab.experiments.truth_pilots p2 \
	  --output-dir $(TRUTH_PILOT_EXPORT)

truth-pilot-go-no-go:
	$(PY) -m artifact_lab.experiments.truth_pilots go-no-go \
	  --output-dir $(TRUTH_PILOT_EXPORT)

truth-pilots: truth-pilot-p1 truth-pilot-p2 truth-pilot-go-no-go

truth-pilot-p3:
	$(PY) -m artifact_lab.experiments.truth_pilots p3 \
	  --output-dir $(TRUTH_PILOT_EXPORT)

truth-pilot-p4:
	$(PY) -m artifact_lab.experiments.truth_pilots p4 \
	  --output-dir $(TRUTH_PILOT_EXPORT)

truth-pilot-p5:
	$(PY) -m artifact_lab.experiments.truth_pilots p5 \
	  --output-dir $(TRUTH_PILOT_EXPORT)

pre-scaling-gates: truth-pilot-p3 truth-pilot-p4 truth-pilot-p5

truth-decay-rq1: install-paper
	$(PY) -m artifact_lab.experiments.truth_decay rq1 \
	  --output-dir exports/truth_decay_pilot

truth-decay-rq2: install-paper
	$(PY) -m artifact_lab.experiments.truth_decay rq2 \
	  --output-dir exports/truth_decay_pilot

truth-decay-rq3: install-paper
	$(PY) -m artifact_lab.experiments.truth_decay rq3 \
	  --output-dir exports/truth_decay_pilot

truth-decay-rq4: install-paper
	$(PY) -m artifact_lab.experiments.truth_decay rq4 \
	  --output-dir exports/truth_decay_pilot

truth-decay-rq5-prep: install-paper
	$(PY) -m artifact_lab.experiments.truth_decay rq5-prep \
	  --output-dir exports/truth_decay_pilot

truth-decay-born-stale-audit: install-paper
	$(PY) -m artifact_lab.experiments.truth_decay born-stale-audit \
	  --output-dir exports/truth_decay_pilot

truth-decay-born-stale-autopsy: install-paper
	$(PY) -m artifact_lab.experiments.truth_decay born-stale-autopsy \
	  --output-dir exports/truth_decay_pilot

ingest: $(L1_EVENTS)

panel: $(L2_PANEL)

e1-exports: $(FIG1_PDF) $(FIG1_CSV) $(TABLE1) $(E1_REPORT)

profile-report:
	$(PY) -m artifact_lab.experiments.pilot_performance

install-paper:
	$(PIP) install -e ".[dev,paper]"

$(L1_EVENTS): $(REGISTRY)
	$(PY) -m artifact_lab.ingest extract --registry $(REGISTRY) --family $(FAMILY) --inspection-mode $(INSPECTION_MODE)

$(L2_PANEL): $(L1_EVENTS)
	$(PY) -m artifact_lab.derive panel --T 180

$(FIG1_PDF) $(FIG1_CSV) $(TABLE1) $(E1_REPORT): $(L2_PANEL)
	$(PY) -m artifact_lab.experiments.e1_adoption_census --no-export

$(E1_PILOT_PERF): $(PROFILE_PARQUET)
	$(PY) -m artifact_lab.experiments.pilot_performance

$(PROFILE_CSV): $(PROFILE_PARQUET)
	@true

paper:
	@mkdir -p $(PAPER_ROOT)/figures $(PAPER_ROOT)/tables $(PAPER_ROOT)/notes
	@test -f $(FIG1_PDF) || (echo "missing $(FIG1_PDF); run make e1 or make e1-pilot first" && exit 1)
	cp $(FIG1_PDF) $(PAPER_ROOT)/figures/fig1.pdf
	cp $(FIG1_CSV) $(PAPER_ROOT)/figures/fig1.csv
	cp $(TABLE1) $(PAPER_ROOT)/tables/table1.csv
	@test -f $(E1_PILOT_PERF) && cp $(E1_PILOT_PERF) $(PAPER_ROOT)/notes/pilot_performance.md || echo "note: $(E1_PILOT_PERF) not found; skipping performance note copy"
	$(MAKE) -C $(PAPER_ROOT) pdf

test:
	$(PY) -m pytest artifact_lab/tests -q
