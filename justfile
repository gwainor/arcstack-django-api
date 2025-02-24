help:
    just --list

test:
    poetry run pytest

test-cov:
    poetry run pytest --cov=arcstack_api --cov-report=term-missing tests

run-test-file:
    poetry run python test.py
