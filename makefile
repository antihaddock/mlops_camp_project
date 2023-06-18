.PHONY: install test lint clean

install:
    @pipenv install --dev

test:
    @pipenv run pytest

lint:
    @pipenv run flake8

clean:
    @pipenv --rm