from urllib.parse import urlparse, urljoin
import inspect


def is_relative(url):
    return urlparse(url).netloc == ''


def normalize_url(url, visited=None):
    """
    Main usage is to change relative URL to absolute
    basing on last `visited` url
    :return: normalized url
    """
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
    """
    Returns the same generator if `f` is generator or
    generator yielding `f` otherwise
    :param f: function or function-generator
    :return: generator
    """
    def wrapper():
        if inspect.isgenerator(f):
            yield from f
        else:
            yield f

    return wrapper()
