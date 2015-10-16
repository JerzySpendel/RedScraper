from urllib.parse import urlparse, urljoin


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
            # return '{}://{}{}'.format(visited_parse.scheme, visited_parse.netloc, url_parse.path)
            return urljoin(visited, url)
        return url
    except:
        raise Exception("URL couldn't be normalized")
