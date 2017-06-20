import typing
import functools
import inspect
import copy as copylib


__version__ = '0.0.1'
__author__ = """Michael Housh"""
__email__ = 'mhoush@houshhomeenergy.com'
__all__ = (
    'coroutine',
    'pipeline'
)


_Generic_Generator = typing.Generator[typing.Any, typing.Any, typing.Any]
PipelineGenerator = _Generic_Generator
CoroutineGenerator = _Generic_Generator
CoroutineFunction = typing.Callable[[typing.Any], CoroutineGenerator]
CopyFunc = typing.Callable[[typing.Any], typing.Any]


def coroutine(fn: CoroutineFunction) -> CoroutineFunction:
    """Decorator that marks a generator as a coroutine and automatically runs
    it up to the first ``yield`` when called.

    This adds the ability for a target generator to be passed in using the
    ``target`` kwarg.  The target should be a generator that is sent the
    processed output from the wrapped coroutine.  Which allows coroutines to be
    chained together and called in succession to create processing pipelines.

    :param fn:  The function to wrap.

    """
    try:
        fn._iscoroutine = True
    except AttributeError:
        pass

    @functools.wraps(fn)
    def coroutine_decorator(*args, target: CoroutineGenerator=None, **kwargs
                            ) -> CoroutineGenerator:

        if inspect.isgenerator(fn):
            generator = fn
        else:
            generator = fn(*args, **kwargs)

        next(generator)
        if target and inspect.isgenerator(target):
            return _targetable_coroutine(target, generator)
        return generator

    return coroutine_decorator


@coroutine
def _targetable_coroutine(target, gen):
    """Wraps a coroutine and sends the coroutine's output on to the target for
    further processing.

    """
    output = None
    while True:
        _input = yield output
        result = gen.send(_input)
        output = target.send(result)


def _reduce_func(target, genfunc, debug=False):
    """Used in the pipeline function to chain coroutines together.

    """
    if not getattr(genfunc, '_iscoroutine', False):
        genfunc = coroutine(genfunc)

    if debug:
        if target:
            target = pipeline_debugger(target, genfunc.__name__)
        return pipeline_debugger(genfunc(target=target), genfunc.__name__)

    return genfunc(target=target)


@coroutine
def pipeline_debugger(target: CoroutineGenerator, name: str=None
                      ) -> CoroutineGenerator:
    """Adds some print statements when sending data into a pipeline.  This
    wraps the incoming coroutines if the ``debug`` is set to ``True`` when
    createing a ``pipeline``.

    This will print the value's before it sends them as well as the values it
    recieves from the ``send`` method.

    """
    output = None
    name = name or target.__name__

    while True:
        _input = yield output
        output = _input

        ignore_names = ['pipeline_debugger', 'coroutine_decorator']

        if name not in ignore_names:
            print(f"PIPELINE DEBUGGER::Sending:: '{name}', '{output}'")

        output = target.send(output)

        if name not in ignore_names:
            print(f"PIPELINE DEBUGGER::RecievedFrom:: '{name}', '{output}'")


# TODO:  This pretty much breaks down with non mutable types.  Not sure thats
#        a problem for my use case, nor do know how to fix it, because it all
#        depends on how the generators are setup.
def pipeline(*generators, debug=False) -> PipelineGenerator:
    """Creates a processing pipeline chain out of coroutines or other pipelines.
    The coroutines will be called in order passing the output of the first to
    the second coroutine, and so on.

    This is equivalent to::

        >>> one(
                target=two(
                    target=three(...)
                )
            )

    Example::

        >>> pipe = pipeline(one, two, three)
        >>> pipe.send({'some': 'data'})


    :param generators:  The coroutines to create the pipeline with.
                        These should not be called/instantiated.  This method
                        does that setting the ``target`` kwarg appropriately.
                        If your coroutine takes arguments, then you should
                        wrap it with a ``functools.partial``, to create a
                        function that doesn't take any arguments except the
                        ``target`` kwarg.

    :param debug:  If ``True`` then we will wrap all the coroutines with the
                   :func:`pipeline_debugger`.  Which will print the input and
                    outputs of each call down the pipeline.

    """
    reduce_func = functools.partial(_reduce_func, debug=debug)
    return functools.reduce(reduce_func, reversed(generators), None)


@coroutine
def broadcast(*generators, copy: bool=False, copyfunc: CopyFunc=copylib.deepcopy
              ) -> CoroutineGenerator:
    """Sends the input to all the registered coroutines.  This is similar to
    the ``pipeline`` function, however the coroutines should not rely on any
    of the other coroutines to be finished.

    :param generators:  The register coroutines to use in the broadcast.  These
                        can be either coroutine functions or already running
                        coroutines.
    :param copy:  If ``True`` then we will call the ``copyfunc`` on the input
                  before sending it to each registered coroutine.  Default is
                  ``False``.
    :param copyfunc:  A callable that's used to return a copy of the
                      input.  The callable is called with one arg (the input).
                      Defaults to ``copy.deepcopy``.

    """
    while True:
        _input = yield
        for gen in generators:
            if callable(gen):
                gen = gen()
            data = copyfunc(_input) if copy is True else _input
            gen.send(data)
