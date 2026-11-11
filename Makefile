.PHONY: test run clean

test:
	python3 -m unittest discover -s tests

run:
	python3 -m src.main --config test_config.toml

clean:
	rm -f *.svg *.d2
	rm -rf __pycache__ src/__pycache__ tests/__pycache__
