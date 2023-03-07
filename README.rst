urllib3-mock
============

A utility library for mocking out the `urllib3`_ Python library.

This is an adaptation of the `responses`_ library.

.. image:: https://travis-ci.org/florentx/urllib3-mock.png?branch=master
	:target: https://travis-ci.org/florentx/urllib3-mock


.. _urllib3: https://urllib3.readthedocs.org/
.. _responses: https://github.com/getsentry/responses

Changes from florentx/urllib3-mock Upstream
-------------------------------------------

This applies a couple of important fixes from the unmaintained upstream:

1. Support for Python 3.11
2. Drop support for Python 2
3. Support for async functions

More information at https://github.com/florentx/urllib3-mock/pull/8


Response body as string
-----------------------

.. code-block:: python

    from urllib3_mock import Responses
    import requests

    responses = Responses('requests.packages.urllib3')

    @responses.activate
    def test_my_api():
        responses.add('GET', '/api/1/foobar',
                      body='{"error": "not found"}', status=404,
                      content_type='application/json')

        resp = requests.get('http://twitter.com/api/1/foobar')

        assert resp.json() == {"error": "not found"}

        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == '/api/1/foobar'
        assert responses.calls[0].request.host == 'twitter.com'
        assert responses.calls[0].request.scheme == 'http'

Request callback
----------------

.. code-block:: python

    import json

    from urllib3_mock import Responses
    import requests

    responses = Responses('requests.packages.urllib3')

    @responses.activate
    def test_calc_api():

        def request_callback(request):
            payload = json.loads(request.body)
            resp_body = {'value': sum(payload['numbers'])}
            headers = {'request-id': '728d329e-0e86-11e4-a748-0c84dc037c13'}
            return (200, headers, json.dumps(resp_body))

        responses.add_callback('POST', '/sum',
                               callback=request_callback,
                               content_type='application/json')

        resp = requests.post(
            'http://calc.com/sum',
            json.dumps({'numbers': [1, 2, 3]}),
            headers={'content-type': 'application/json'},
        )

        assert resp.json() == {'value': 6}

        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == '/sum'
        assert responses.calls[0].request.host == 'calc.com'
        assert (
            responses.calls[0].response.headers['request-id'] ==
            '728d329e-0e86-11e4-a748-0c84dc037c13'
        )

Instead of passing a string URL into `responses.add` or `responses.add_callback`
you can also supply a compiled regular expression.

.. code-block:: python

    import re
    from urllib3_mock import Responses
    import requests

    responses = Responses('requests.packages.urllib3')

    # Instead of
    responses.add('GET', '/api/1/foobar',
                  body='{"error": "not found"}', status=404,
                  content_type='application/json')

    # You can do the following
    url_re = re.compile(r'/api/\d+/foobar')
    responses.add('GET', url_re,
                  body='{"error": "not found"}', status=404,
                  content_type='application/json')

A response can also throw an exception as follows.

.. code-block:: python

    from urllib3_mock import Responses
    from requests.packages.urllib3.exceptions import HTTPError

    exception = HTTPError('Something went wrong')

    responses = Responses('requests.packages.urllib3')
    responses.add('GET', '/api/1/foobar',
                  body=exception)
    # All calls to 'http://twitter.com/api/1/foobar' will throw exception.
