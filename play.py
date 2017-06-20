#!/usr/bin/env python
from coroutine_utils import coroutine, pipeline
# import functools


@coroutine
def one():
    processed = {}
    while True:
        _input = yield processed
        processed = _input or {}
        processed['one'] = 'one'


@coroutine
def two():
    processed = {}
    while True:
        _input = yield processed
        processed = _input or {}
        processed['two'] = 'two'


@coroutine
def three():
    processed = {}
    while True:
        _input = yield processed
        processed = _input or {}
        processed['three'] = 'three'


pipe = pipeline(one, two, three, debug=True)


if __name__ == '__main__':
    data = {}
    x = pipe.send(data)

    print('*' * 30)
    print('output', x)
