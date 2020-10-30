scripts := $(wildcard ic_azure/*.py)
tests := $(wildcard tests/*.py)

all: clean checkstyle htmlcov dist

checkstyle: $(scripts) $(tests) setup.py
	find . -name "*.py" -exec pycodestyle \{\} \; | tee checkstyle

.coverage: $(scripts) $(tests)
	coverage run --source ic_azure -m unittest discover -s tests/

test: .coverage
	coverage report -m

htmlcov: .coverage
	coverage html

dist: $(scripts) $(tests) setup.py
	python3 setup.py sdist --format=gztar

clean:
	find . -name "*.pyc" -delete
	rm -rf *.egg-info
	rm -rf dist
	rm -rf htmlcov
	rm -f .coverage
	rm -f checkstyle
