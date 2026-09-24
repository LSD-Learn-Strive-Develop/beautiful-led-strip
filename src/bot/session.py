"""Telegram sessions with HTTP, HTTPS and SOCKS proxy support."""

import ssl
from urllib.parse import urlsplit

import certifi
from aiogram.client.session.aiohttp import AiohttpSession


class TelegramSession(AiohttpSession):
    """Extend aiogram's proxy connector with verified TLS to HTTPS proxies."""

    def _setup_proxy_connector(self, proxy) -> None:
        if not isinstance(proxy, str) or urlsplit(proxy).scheme != "https":
            super()._setup_proxy_connector(proxy)
            return

        parsed = urlsplit(proxy)
        # The connector uses HTTP CONNECT inside the TLS connection. Explicitly
        # retain the HTTPS default port when passing its HTTP URL to aiogram.
        netloc = parsed.netloc if parsed.port is not None else parsed.netloc + ":443"
        connect_url = parsed._replace(scheme="http", netloc=netloc).geturl()
        super()._setup_proxy_connector(connect_url)
        tls = ssl.create_default_context(cafile=certifi.where())
        self._connector_init.update(proxy_ssl=tls, ssl=tls)
        self._proxy = proxy
