.PHONY: test demos integration install agent-loops dual-lang ts-probe

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v -m "not integration"

integration:
	pytest tests/ -v -m integration

demos:
	python scripts/run_demos.py

agent-loops:
	./scripts/run_agent_loops.sh stripe.com

dual-lang:
	./scripts/run_dual_lang_probes.sh

ts-probe:
	cd typescript && npm run probe