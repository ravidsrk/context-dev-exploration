.PHONY: test demos integration install agent-loops dual-lang ts-probe ts-agent-loops monid-evidence

install:
	pip install -r requirements.txt
	cd typescript && npm install

test: install
	pytest tests/ -v -m "not integration"

integration: install
	pytest tests/ -v -m integration

demos:
	python scripts/run_demos.py

agent-loops:
	./scripts/run_agent_loops.sh stripe.com

monid-evidence:
	./scripts/capture_monid_evidence.sh

dual-lang:
	./scripts/run_dual_lang_probes.sh

ts-probe:
	cd typescript && npm run probe

ts-agent-loops:
	cd typescript && npm run scout-loop -- stripe.com
	cd typescript && npm run mcp-code-mode -- "Get stripe.com brand identity, design tokens, and site scale"