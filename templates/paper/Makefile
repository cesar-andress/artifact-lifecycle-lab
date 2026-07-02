# Paper repository — consumes artifact exports only. No mining.

MAIN ?= main.tex
LATEXMK ?= latexmk

.PHONY: pdf clean

pdf:
	@if [ ! -f "$(MAIN)" ]; then \
		echo "No $(MAIN) found — skipping LaTeX compile"; \
		exit 0; \
	else \
		$(LATEXMK) -pdf -interaction=nonstopmode $(MAIN); \
	fi

clean:
	@if [ -f "$(MAIN)" ]; then $(LATEXMK) -C $(MAIN); fi
