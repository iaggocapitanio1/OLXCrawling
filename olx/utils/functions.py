def get_or_create_error_dir():
    """
    Creates the error directory if it doesn't exist
    :return:
    """
    import os
    from olx import settings
    os.makedirs(settings.ERROR_DIR, exist_ok=True)
    return settings.ERROR_DIR


def get_error_path(failure):
    """
    Returns the error path for the screenshot
    :param failure:
    :return:
    """
    import hashlib
    import os
    filename_hash = hashlib.md5(failure.request.url.encode()).hexdigest()
    error_dir = get_or_create_error_dir()
    error_path = os.path.join(error_dir, f"error-{filename_hash}.png")
    return error_path


def get_page_number_from_url(url: str) -> int:
    """
    Returns the page number from the url
    :param self:
    :param url:
    :return:
    """
    from urllib.parse import urlparse, parse_qs
    query = urlparse(url).query
    page_number = parse_qs(query).get('o', [0])[0]

    try:
        return int(page_number)
    except ValueError:
        return 0