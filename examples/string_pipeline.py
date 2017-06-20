#!/usr/bin/env python
import typing
import coroutine_utils
import functools
import collections


@coroutine_utils.coroutine
def _remove_special_characters(*chars):
    processed: typing.List[str] = None
    while True:
        _input = yield processed
        if _input:
            processed = _input
            for i in range(len(processed)):
                processed[i]  = ''.join(s for s in processed[i]
                                        if s not in chars)


@coroutine_utils.coroutine
def remove_stars_commas_and_exclamations():
    """Remove '*', ',', and '!' characters from all the input strings.

    """
    return _remove_special_characters('*', ',', '!')


@coroutine_utils.coroutine
def remove_white_space():
    """Remove ' ', '\n', '\t' characters from the input strings.

    """
    return _remove_special_characters(' ', '\n', '\t')


@coroutine_utils.coroutine
def uppercase_string():
    """Uppercase all the input strings

    """
    processed: typing.List[str] = None
    while True:
        _input = yield processed
        if _input:
            processed = _input
            for i in range(len(processed)):
                processed[i] = processed[i].upper()


def run(gen, data, title):

    title = title.upper()
    print('*' * 50)
    print(f'{title}')
    print('*' * 50)
    print()

    result = gen.send(data)

    print(f'RESULT: {result}')
    print('-' * 50)
    print()


if __name__ == '__main__':

    pipeline = coroutine_utils.pipeline(
        remove_stars_commas_and_exclamations,
        remove_white_space,
        uppercase_string,
        debug=True
    )

    data = [
        ' ** hello, ** world !',
        '****************Foo !!!!!!!!!!! Bar,,,,,,,,,,',
        ',!*!,,, barbaz, !!***'
    ]

    pipedata = list(data)
    run(pipeline, pipedata, 'EXAMPLE PIPELINE')


    no_specials = remove_stars_commas_and_exclamations()
    no_space = remove_white_space()
    upper = uppercase_string()

    broadcast = coroutine_utils.broadcast(
        no_specials,
        no_space,
        upper,
    )

    bdata = list(data)
    run(broadcast, bdata, 'EXAMPLE BROADCAST')
    print('bdata', bdata)
