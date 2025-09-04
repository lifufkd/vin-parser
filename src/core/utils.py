from urllib.parse import urlparse, urlunparse
import re
from loguru import logger


def format_proxy(proxy_url: str) -> dict | None:
    pattern = re.compile(
        r'^(?P<scheme>https?|socks5?|socks4)://'
        r'(?:((?P<username>[^:]+):(?P<password>[^@]+)@)?)?'
        r'(?P<ip>[^:]+):(?P<port>\d+)$'
    )

    match = pattern.match(proxy_url)
    if not match:
        return None

    scheme = match.group('scheme')
    ip = match.group('ip')
    port = match.group('port')

    result = {
        "server": f"{scheme}://{ip}:{port}"
    }

    if match.group("username") and match.group("password"):
        result["username"] = match.group("username")
        result["password"] = match.group("password")

    return result
