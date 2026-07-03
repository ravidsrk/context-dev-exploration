.PHONY: test demos integration install agent-loops dual-lang ts-probe ts-agent-loops monid-evidence verify

VENV_PY ?= .venv/bin/python
VENV_PIP ?= .venv/bin/pip

install:
	@test -x $(VENV_PY) || python3 -m venv .venv
	$(VENV_PIP) install -r requirements.txt
	cd typescript && npm install

test: install
	$(VENV_PY) -m pytest tests/ -v -m "not integration"

integration: install
	$(VENV_PY) -m pytest tests/ -v -m integration

demos:
	@bash -c 'source scripts/lib/ensure_env.sh && python scripts/run/demos.py'

agent-loops:
	./scripts/run/agent_loops.sh stripe.com

monid-evidence:
	./scripts/capture/monid_evidence.sh

dual-lang:
	./scripts/run/dual_lang_probes.sh

verify:
	./scripts/verify/verify.sh

evidence-reconcile:
	$(VENV_PY) scripts/verify/validate_agent_loop_evidence.py --reconcile-stale

ts-probe:
	cd typescript && npm run probe

ts-agent-loops:
	cd typescript && npm run scout-loop -- stripe.com
	cd typescript && npm run mcp-code-mode -- "Get stripe.com brand identity, design tokens, and site scale"