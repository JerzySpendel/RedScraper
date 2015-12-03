from redscraper.helpers import *


def test_is_relative():
    assert is_relative("/asdf") == True
    assert is_relative("path") == True
    assert is_relative("http://example.com") == False
    assert is_relative("http://example.com/") == False


def test_normalize_url():
    assert normalize_url("/sth", visited="http://example.com") == "http://example.com/sth"
    assert normalize_url("/sth", visited="http://example.com/") == "http://example.com/sth"


def test_make_generator_if_needed():
    v = 10

    def generator():
        yield v

    g1 = make_generator_if_needed(v)
    g2 = make_generator_if_needed(generator())
    assert next(g1) == v
    assert next(g2) == v
