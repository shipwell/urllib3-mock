import re
from inspect import getargspec

import pytest
import requests
from requests.exceptions import ConnectionError
from requests.packages.urllib3.exceptions import ProtocolError, HTTPError

from urllib3_mock import Responses

responses = Responses('requests.packages.urllib3')


def assert_reset():
    assert len(responses._urls) == 0
    assert len(responses.calls) == 0


def assert_response(resp, body=None):
    assert resp.status_code == 200
    assert resp.headers['Content-Type'] == 'text/plain'
    assert resp.text == body


def test_response():
    @responses.activate
    def run():
        responses.add(responses.GET, '/', body=b'test')
        resp = requests.get('http://example.com')
        assert_response(resp, 'test')
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == '/'
        assert responses.calls[0].request.scheme == 'http'
        assert responses.calls[0].request.host == 'example.com'
        assert responses.calls[0].request.port == 80

        resp = requests.get('http://example.com?foo=bar')
        assert_response(resp, 'test')
        assert len(responses.calls) == 2
        assert responses.calls[1].request.url == '/?foo=bar'

    run()
    assert_reset()


def test_connection_error():
    @responses.activate
    def run():
        responses.add(responses.GET, '/')

        with pytest.raises(ConnectionError):
            requests.get('http://example.com/foo')

        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == '/foo'
        assert type(responses.calls[0].response) is ProtocolError

    run()
    assert_reset()


def test_match_querystring():
    @responses.activate
    def run():
        url = '/?test=1&foo=bar'
        responses.add(
            responses.GET, url,
            match_querystring=True, body=b'test')
        resp = requests.get('http://example.com?test=1&foo=bar')
        assert_response(resp, 'test')
        resp = requests.get('http://example.com?foo=bar&test=1')
        assert_response(resp, 'test')

    run()
    assert_reset()


def test_match_querystring_error():
    @responses.activate
    def run():
        responses.add(
            responses.GET, '/?test=1',
            match_querystring=True)

        with pytest.raises(ConnectionError):
            requests.get('http://example.com/foo/?test=2')

    run()
    assert_reset()


def test_match_querystring_regex():
    @responses.activate
    def run():
        """Note that `match_querystring` value shouldn't matter when passing a
        regular expression"""

        responses.add(
            responses.GET, re.compile(r'/foo/\?test=1'),
            body='test1', match_querystring=True)

        resp = requests.get('http://example.com/foo/?test=1')
        assert_response(resp, 'test1')

        responses.add(
            responses.GET, re.compile(r'/foo/\?test=2'),
            body='test2', match_querystring=False)

        resp = requests.get('http://example.com/foo/?test=2')
        assert_response(resp, 'test2')

    run()
    assert_reset()


def test_match_querystring_error_regex():
    @responses.activate
    def run():
        """Note that `match_querystring` value shouldn't matter when passing a
        regular expression"""

        responses.add(
            responses.GET, re.compile(r'/foo/\?test=1'),
            match_querystring=True)

        with pytest.raises(ConnectionError):
            requests.get('http://example.com/foo/?test=3')

        responses.add(
            responses.GET, re.compile(r'/foo/\?test=2'),
            match_querystring=False)

        with pytest.raises(ConnectionError):
            requests.get('http://example.com/foo/?test=4')

    run()
    assert_reset()


def test_accept_string_body():
    @responses.activate
    def run():
        url = 'http://example.com/'
        responses.add(
            responses.GET, '/', body='test')
        resp = requests.get(url)
        assert_response(resp, 'test')

    run()
    assert_reset()


def test_throw_connection_error_explicit():
    @responses.activate
    def run():
        url = 'http://example.com'
        exception = HTTPError('HTTP Error')
        responses.add(
            responses.GET, '/', exception)

        with pytest.raises(HTTPError) as HE:
            requests.get(url)

        assert str(HE.value) == 'HTTP Error'

    run()
    assert_reset()


def test_callback():
    body = b'test callback'
    status = 400
    headers = {'foo': 'bar'}
    url = 'http://example.com/'

    def request_callback(request):
        return (status, headers, body)

    @responses.activate
    def run():
        responses.add_callback(responses.GET, '/', request_callback)
        resp = requests.get(url)
        assert resp.text == "test callback"
        assert resp.status_code == status
        assert 'foo' in resp.headers
        assert resp.headers['foo'] == 'bar'

    run()
    assert_reset()


def test_regular_expression_url():
    @responses.activate
    def run():
        url = re.compile(r'/(.*\.)?examples?')
        responses.add(responses.GET, url, body=b'test')

        resp = requests.get('http://nowhere.invalid/example')
        assert_response(resp, 'test')

        resp = requests.get('https://nowhere.invalid/examples')
        assert_response(resp, 'test')

        resp = requests.get('http://nowhere.invalid/uk.example')
        assert_response(resp, 'test')

        with pytest.raises(ConnectionError):
            requests.get('http://nowhere.invalid/uk.exaaample')

    run()
    assert_reset()


def test_responses_as_context_manager():
    def run():
        with responses:
            responses.add(responses.GET, '/', body=b'test')
            resp = requests.get('http://example.com')
            assert_response(resp, 'test')
            assert len(responses.calls) == 1
            assert responses.calls[0].request.url == '/'

            resp = requests.get('http://example.com?foo=bar')
            assert_response(resp, 'test')
            assert len(responses.calls) == 2
            assert responses.calls[1].request.url == '/?foo=bar'

    run()
    assert_reset()


def test_activate_doesnt_change_signature():
    def test_function(a, b=None):
        return (a, b)

    decorated_test_function = responses.activate(test_function)
    assert getargspec(test_function) == getargspec(decorated_test_function)
    assert decorated_test_function(1, 2) == test_function(1, 2)
    assert decorated_test_function(3) == test_function(3)


def test_activate_doesnt_change_signature_for_method():
    class TestCase(object):

        def test_function(self, a, b=None):
            return (self, a, b)

    test_case = TestCase()
    argspec = getargspec(test_case.test_function)
    decorated_test_function = responses.activate(test_case.test_function)
    assert argspec == getargspec(decorated_test_function)
    assert decorated_test_function(1, 2) == test_case.test_function(1, 2)
    assert decorated_test_function(3) == test_case.test_function(3)
