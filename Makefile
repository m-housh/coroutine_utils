.PHONY: tests

tests:
	py.test -v --cov coroutine_utils --cov-report term-missing tests.py

run-tox:
	tox

build-tox:
	docker build -t coroutine_utils:tox .

test-all: build-tox
	docker run -it --rm coroutine_utils:tox
