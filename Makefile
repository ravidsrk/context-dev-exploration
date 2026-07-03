.PHONY: test demos integration install

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v -m "not integration"

integration:
	pytest tests/ -v -m integration

demos:
	python scripts/run_demos.py