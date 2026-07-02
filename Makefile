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

PAPER_ROOT := ../paper
PAPER_NOTE := $(PAPER_ROOT)/notes/pilot_performance.md

# Bounded development pilot (default: 3 repos, 120s timeouts via --skip-slow)
E1_PILOT_LIMIT ?= 3

.PHONY: e1 e1-pilot paper ingest panel e1-exports profile-report test install-paper e1-pilot-extract e1-pilot-derive e1-pilot-exports

e1: install-paper ingest panel e1-exports profile-report

e1-pilot: install-paper e1-pilot-extract e1-pilot-derive e1-pilot-exports profile-report

e1-pilot-extract:
	$(PY) -m artifact_lab.ingest extract \
	  --registry $(REGISTRY) \
	  --family $(FAMILY) \
	  --limit $(E1_PILOT_LIMIT) \
	  --skip-slow

e1-pilot-derive:
	$(PY) -m artifact_lab.derive panel --T 180

e1-pilot-exports:
	$(PY) -m artifact_lab.experiments.e1_adoption_census --no-export

ingest: $(L1_EVENTS)

panel: $(L2_PANEL)

e1-exports: $(FIG1_PDF) $(FIG1_CSV) $(TABLE1) $(E1_REPORT)

profile-report: $(PAPER_NOTE)

install-paper:
	$(PIP) install -e ".[dev,paper]"

$(L1_EVENTS): $(REGISTRY)
	$(PY) -m artifact_lab.ingest extract --registry $(REGISTRY) --family $(FAMILY)

$(L2_PANEL): $(L1_EVENTS)
	$(PY) -m artifact_lab.derive panel --T 180

$(FIG1_PDF) $(FIG1_CSV) $(TABLE1) $(E1_REPORT): $(L2_PANEL)
	$(PY) -m artifact_lab.experiments.e1_adoption_census --no-export

$(PAPER_NOTE): $(PROFILE_PARQUET)
	$(PY) -m artifact_lab.experiments.pilot_performance

$(PROFILE_CSV): $(PROFILE_PARQUET)
	@true

paper:
	@mkdir -p $(PAPER_ROOT)/figures $(PAPER_ROOT)/tables $(PAPER_ROOT)/notes
	@test -f $(FIG1_PDF) || (echo "missing $(FIG1_PDF); run make e1 or make e1-pilot first" && exit 1)
	cp $(FIG1_PDF) $(PAPER_ROOT)/figures/fig1.pdf
	cp $(FIG1_CSV) $(PAPER_ROOT)/figures/fig1.csv
	cp $(TABLE1) $(PAPER_ROOT)/tables/table1.csv
	$(MAKE) -C $(PAPER_ROOT) pdf

test:
	$(PY) -m pytest artifact_lab/tests -q
