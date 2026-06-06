"""
平台适配器基础模块 / Base Platform Adapter Module

定义所有平台适配器的抽象基类，统一接口规范。
Defines the abstract base class for all platform adapters with unified interface.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
from html.parser import HTMLParser


# ── ANSI 颜色码 / ANSI Color Codes ──────────────────────────────────
class Colors:
    """终端颜色常量 / Terminal color constants"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_BLUE = "\033[44m"


# ── 简易HTML解析器 / Simple HTML Parser ─────────────────────────────
class SimpleHTMLParser(HTMLParser):
    """
    轻量级HTML解析器，提取文本内容和链接。
    Lightweight HTML parser for extracting text content and links.
    """

    def __init__(self):
        super().__init__()
        self._text_parts = []
        self._links = []
        self._current_tag = None
        self._current_attrs = {}
        self._skip_tags = {"script", "style", "noscript", "svg", "path"}
        self._depth = 0

    def handle_starttag(self, tag, attrs):
        self._current_tag = tag
        self._current_attrs = dict(attrs)
        if tag in self._skip_tags:
            self._depth += 1
        if tag == "a" and self._depth == 0:
            href = self._current_attrs.get("href", "")
            if href:
                self._links.append(href)

    def handle_endtag(self, tag):
        if tag in self._skip_tags and self._depth > 0:
            self._depth -= 1
        if tag == self._current_tag:
            self._current_tag = None

    def handle_data(self, data):
        if self._depth == 0:
            text = data.strip()
            if text:
                self._text_parts.append(text)

    @property
    def text(self):
        """获取提取的纯文本 / Get extracted plain text"""
        return " ".join(self._text_parts)

    @property
    def links(self):
        """获取提取的链接列表 / Get extracted links"""
        return self._links


def parse_html(html_content):
    """
    解析HTML内容，返回纯文本和链接。
    Parse HTML content, return plain text and links.

    Args:
        html_content: HTML字符串 / HTML string

    Returns:
        tuple: (text, links) / (纯文本, 链接列表)
    """
    parser = SimpleHTMLParser()
    try:
        parser.feed(html_content)
    except Exception:
        pass
    return parser.text, parser.links


def extract_meta(html_content, tag="meta", attr_name="content", key_attr="name"):
    """
    从HTML中提取meta标签内容。
    Extract meta tag content from HTML.

    Args:
        html_content: HTML字符串 / HTML string
        tag: 标签名 / Tag name
        attr_name: 目标属性名 / Target attribute name
        key_attr: 键属性名 / Key attribute name

    Returns:
        dict: meta内容字典 / Meta content dictionary
    """
    result = {}

    class MetaParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.in_meta = False
            self.current_attrs = {}

        def handle_starttag(self, tag, attrs):
            if tag == "meta":
                self.current_attrs = dict(attrs)
                name = self.current_attrs.get(key_attr, "").lower()
                content = self.current_attrs.get(attr_name, "")
                if name and content:
                    result[name] = content

    try:
        p = MetaParser()
        p.feed(html_content)
    except Exception:
        pass
    return result


# ── HTTP请求工具 / HTTP Request Utilities ───────────────────────────
def fetch_url(url, timeout=15, headers=None, proxy=None):
    """
    发送HTTP GET请求，返回响应内容。
    Send HTTP GET request, return response content.

    Args:
        url: 请求URL / Request URL
        timeout: 超时秒数 / Timeout in seconds
        headers: 自定义请求头 / Custom headers
        proxy: 代理地址 / Proxy address (e.g. "http://127.0.0.1:7890")

    Returns:
        str: 响应文本 / Response text

    Raises:
        ConnectionError: 网络连接失败 / Network connection failed
        TimeoutError: 请求超时 / Request timeout
    """
    if headers is None:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

    req = urllib.request.Request(url, headers=headers)

    # 代理设置 / Proxy configuration
    proxy_handler = None
    if proxy:
        proxy_handler = urllib.request.ProxyHandler({
            "http": proxy,
            "https": proxy,
        })
    else:
        # 从环境变量读取代理 / Read proxy from environment variables
        http_proxy = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
        https_proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
        if http_proxy or https_proxy:
            proxy_dict = {}
            if http_proxy:
                proxy_dict["http"] = http_proxy
            if https_proxy:
                proxy_dict["https"] = https_proxy
            proxy_handler = urllib.request.ProxyHandler(proxy_dict)

    opener = urllib.request.build_opener(proxy_handler) if proxy_handler else urllib.request.build_opener()

    try:
        with opener.open(req, timeout=timeout) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            raw = resp.read()
            try:
                return raw.decode(charset)
            except (UnicodeDecodeError, LookupError):
                return raw.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        raise ConnectionError(f"HTTP {e.code}: {e.reason} - {url}")
    except urllib.error.URLError as e:
        raise ConnectionError(f"URL错误: {e.reason} - {url}")
    except TimeoutError:
        raise TimeoutError(f"请求超时 ({timeout}s): {url}")


# ── 平台适配器基类 / Base Platform Adapter ──────────────────────────
class BasePlatform:
    """
    平台适配器抽象基类。
    Abstract base class for platform adapters.

    所有平台适配器必须继承此类并实现 search() 和 trending() 方法。
    All platform adapters must inherit this class and implement search() and trending().
    """

    # 平台标识 / Platform identifier
    name: str = "base"
    # 平台显示名称 / Platform display name
    display_name: str = "Base Platform"
    # 平台基础URL / Platform base URL
    base_url: str = ""

    def __init__(self, proxy=None, timeout=15):
        """
        初始化平台适配器。
        Initialize platform adapter.

        Args:
            proxy: 代理地址 / Proxy address
            timeout: 请求超时 / Request timeout
        """
        self.proxy = proxy
        self.timeout = timeout

    def search(self, query, limit=10):
        """
        搜索内容。
        Search content.

        Args:
            query: 搜索关键词 / Search query
            limit: 返回结果数量 / Number of results to return

        Returns:
            list[dict]: 统一格式的结果列表 / Unified format result list
        """
        raise NotImplementedError(
            f"[{self.display_name}] search() 方法未实现 / search() not implemented"
        )

    def trending(self, limit=10):
        """
        获取热门/趋势内容。
        Get trending/popular content.

        Args:
            limit: 返回结果数量 / Number of results to return

        Returns:
            list[dict]: 统一格式的结果列表 / Unified format result list
        """
        raise NotImplementedError(
            f"[{self.display_name}] trending() 方法未实现 / trending() not implemented"
        )

    def _format_result(self, title, url, author="", content="",
                       timestamp="", metadata=None):
        """
        格式化单条结果为统一结构。
        Format a single result into unified structure.

        Args:
            title: 标题 / Title
            url: 链接 / URL
            author: 作者 / Author
            content: 内容摘要 / Content summary
            timestamp: 时间戳 / Timestamp
            metadata: 额外元数据 / Additional metadata

        Returns:
            dict: 统一格式结果 / Unified format result
        """
        return {
            "title": title.strip() if title else "",
            "url": url.strip() if url else "",
            "author": author.strip() if author else "",
            "content": content.strip() if content else "",
            "platform": self.name,
            "timestamp": timestamp or time.strftime("%Y-%m-%dT%H:%M:%S"),
            "metadata": metadata or {},
        }

    def _clean_text(self, text):
        """
        清理文本：去除多余空白和HTML实体。
        Clean text: remove extra whitespace and HTML entities.

        Args:
            text: 原始文本 / Raw text

        Returns:
            str: 清理后的文本 / Cleaned text
        """
        if not text:
            return ""
        # 常见HTML实体解码 / Common HTML entity decoding
        entities = {
            "&amp;": "&",
            "&lt;": "<",
            "&gt;": ">",
            "&quot;": '"',
            "&#39;": "'",
            "&nbsp;": " ",
        }
        for k, v in entities.items():
            text = text.replace(k, v)
        # 合并多余空白 / Merge extra whitespace
        import re
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.display_name})>"
