import pytest
import functools
import coroutine_utils


def test_sanity():
    assert True


def non_wrapped_gen():
    processed = {}
    while True:
        _input = yield processed
        processed = _input


@coroutine_utils.coroutine
def coroutine_gen():
    processed = {}
    while True:
        _input = yield processed
        processed = _input


@coroutine_utils.coroutine
def target(key='target'):
    processed = {}
    while True:
        _input = yield processed
        if _input:
            processed = _input
            processed[key] = True
            callorder = processed.get('callorder', None)
            if callorder is not None:
                callorder.append(key)


def test_coroutine():
    # set's a flag on wrapped function
    assert coroutine_gen._iscoroutine is True

    g = coroutine_gen()

    # sending in a generator, just returns the generator
    # when called.
    x = coroutine_utils.coroutine(g)
    assert x() == g

    data = {'a': 'a'}
    assert g.send(data) == data

    ng = non_wrapped_gen()
    with pytest.raises(TypeError):
        ng.send(data)

    ng.send(None)
    assert ng.send(data) == data

    g = coroutine_gen(target=target())
    assert 'target' not in data
    g.send(data)
    assert data['target'] is True


def test_pipeline():
    g = coroutine_utils.pipeline(
        coroutine_gen,
        target,
    )

    data = {'a': 'a'}
    res = g.send(data)
    assert res['target'] is True


def test_pipeline_with_a_pipeline():
    pipe1 = coroutine_utils.pipeline(
        coroutine_gen,
        functools.partial(target, key='pipe1'),
        debug=True
    )

    pipe2 = coroutine_utils.pipeline(
        pipe1,
        functools.partial(target, key='pipe2'),
        debug=True
    )

    pipe3 = coroutine_utils.pipeline(
        pipe2,
        functools.partial(target, key='pipe3'),
        debug=True
    )

    data = {'a': 'a', 'callorder': []}

    res = pipe3.send(data)
    assert res['pipe1'] is True
    assert res['pipe2'] is True
    assert res['pipe3'] is True

    assert res['callorder'] == ['pipe1', 'pipe2', 'pipe3']


def test_broadcast():

    gen1 = target('1')
    gen2 = target('2')
    gen3 = functools.partial(target, '3')

    broadcast_pipe = coroutine_utils.broadcast(
        gen1,
        gen2,
        gen3
    )

    data = {'a': 'a'}
    broadcast_pipe.send(data)

    for k in range(1, 4):
        assert data[str(k)] is True

    data2 = {'a': 'a'}

    broadcast_pipe = coroutine_utils.broadcast(
        gen1,
        gen2,
        gen3,
        copy=True
    )
    broadcast_pipe.send(data2)

    assert data == data
    assert next(gen1) == {'a': 'a', '1': True}
    assert next(gen2) == {'a': 'a', '2': True}
