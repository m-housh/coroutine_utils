Coroutine Utils
===============


A small package that has some coroutine utilities.  This is not ``async/await``,
coroutines.  This is for native generator based coroutines.


Features
--------

    - Python >= 3.6


Usage
-----

::
    >>> import coroutine_utils

Wrapping a coroutine generator allows it to be called and run to the first yield
statement automatically (avoids having to call ``next(gen)`` befor sending it 
values).  It also watches for a ``target`` kwarg passed in when calling the
wrapped coroutine.  If a ``target`` coroutine is passed in, then it will be
``sent`` the output of the wrapped function.  This allows the building of
processing pipelines.


Example::    

    >>> @coroutine_utils.coroutine
        def mycoro():

            output = None

            while True:
                _input = yield output

                if _input and 'a' in _input:
                    output = _input
                    print(f'mycoro::recieved: {_input}')
                    output['a'] = 'foo'
                    print(f'mycoro::output: {output}')


    >>> m = mycoro()
    >>> data = {'a': 'a'}
    >>> m.send(data)
    mycoro::recieved: {'a': 'a'}
    mycoro::output: {'a': 'foo'}
    {'a': 'foo'}
    >>> print(data)
    {'a': 'foo'}

