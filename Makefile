.PHONY: check version lint run publish-test publish clean

lint:
				pylint aqara

test: lint
				pytest

run:
				python3 main.py

version: check
				@VERSION=$(shell git describe --tags | sort | head -1) envsubst < setup.py.tmpl > setup.py

check:
				@git describe --tags > /dev/null

publish-test: test version
				VERSION=$(TAG) python setup.py sdist upload -r pypitest

publish: test version
				VERSION=$(TAG) python setup.py sdist upload -r pypi

clean:
				find . -name "*.pyc" | xargs -I {} rm -v "{}"
