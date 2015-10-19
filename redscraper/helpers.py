from urllib.parse import urlparse, urljoin
import inspect
import functools


def is_relative(url):
    return urlparse(url).netloc == ''


def normalize_url(url, visited=None):
    try:
        url = url.strip()
        if visited is None:
            return url.strip()
        url_parse = urlparse(url)
        visited_parse = urlparse(visited)
        if url_parse.scheme == '' and url_parse.netloc == '':
            return urljoin(visited, url)
        return url
    except:
        raise Exception("URL couldn't be normalized")


def make_generator_if_needed(f):

    def wrapper():
        if inspect.isgenerator(f):
            yield from f
        else:
            yield f

    return wrapper()
