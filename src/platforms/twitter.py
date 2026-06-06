"""
Twitter/X 平台适配器 / Twitter/X Platform Adapter

通过Nitter实例或直接解析Twitter搜索页面获取内容。
Fetches content via Nitter instances or direct Twitter search page parsing.
"""

import re
import json
from html.parser import HTMLParser

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.platforms.base import BasePlatform, fetch_url, parse_html


# Nitter公共实例列表 / List of public Nitter instances
NITTER_INSTANCES = [
    "nitter.net",
    "nitter.privacydev.net",
    "nitter.poast.org",
]


class TwitterAdapter(BasePlatform):
    """
    Twitter/X 平台适配器。
    Twitter/X Platform Adapter.

    通过Nitter实例获取公开推文内容。
    Fetches public tweet content via Nitter instances.
    """

    name = "twitter"
    display_name = "Twitter/X"
    base_url = "https://twitter.com"

    def __init__(self, proxy=None, timeout=15):
        super().__init__(proxy=proxy, timeout=timeout)
        self._working_instance = None

    def _get_nitter_instance(self):
        """
        查找可用的Nitter实例。
        Find a working Nitter instance.

        Returns:
            str: 可用实例的基础URL / Base URL of working instance
        """
        if self._working_instance:
            return self._working_instance

        for instance in NITTER_INSTANCES:
            try:
                url = f"https://{instance}"
                fetch_url(url, timeout=5, proxy=self.proxy)
                self._working_instance = url
                return url
            except Exception:
                continue

        # 回退到第一个实例 / Fallback to first instance
        self._working_instance = f"https://{NITTER_INSTANCES[0]}"
        return self._working_instance

    def search(self, query, limit=10):
        """
        搜索Twitter/X内容。
        Search Twitter/X content.

        Args:
            query: 搜索关键词 / Search query
            limit: 结果数量 / Number of results

        Returns:
            list[dict]: 搜索结果 / Search results
        """
        results = []
        try:
            base = self._get_nitter_instance()
            encoded_query = query.replace(" ", "+")
            url = f"{base}/search?f=tweets&q={encoded_query}"
            html = fetch_url(url, timeout=self.timeout, proxy=self.proxy)
            results = self._parse_nitter_results(html, limit)
        except Exception as e:
            print(f"  [{self.display_name}] 搜索失败: {e}")

        return results[:limit]

    def trending(self, limit=10):
        """
        获取Twitter/X热门内容。
        Get Twitter/X trending content.

        Args:
            limit: 结果数量 / Number of results

        Returns:
            list[dict]: 热门结果 / Trending results
        """
        results = []
        try:
            base = self._get_nitter_instance()
            url = f"{base}/search?f=tweets&q=lang%3Aen&since=2024-01-01"
            html = fetch_url(url, timeout=self.timeout, proxy=self.proxy)
            results = self._parse_nitter_results(html, limit)
        except Exception as e:
            print(f"  [{self.display_name}] 获取热门失败: {e}")

        return results[:limit]

    def _parse_nitter_results(self, html, limit):
        """
        解析Nitter搜索结果页面。
        Parse Nitter search result page.

        Args:
            html: HTML内容 / HTML content
            limit: 结果数量限制 / Result count limit

        Returns:
            list[dict]: 解析结果 / Parsed results
        """
        results = []

        class TweetParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.tweets = []
                self.current_tweet = None
                self.in_tweet_body = False
                self.in_tweet_content = False
                self.in_author = False
                self.capture_text = False

            def handle_starttag(self, tag, attrs):
                attrs_dict = dict(attrs)
                cls = attrs_dict.get("class", "")

                if "timeline-item" in cls:
                    self.current_tweet = {"title": "", "url": "", "author": "", "content": ""}
                    self.in_tweet_body = True

                if self.in_tweet_body and tag == "a":
                    href = attrs_dict.get("href", "")
                    if href.startswith("/"):
                        full_url = f"https://twitter.com{href}"
                        if not self.current_tweet.get("url"):
                            self.current_tweet["url"] = full_url
                    if "username" in cls or "fullname" in cls:
                        self.in_author = True

                if self.in_tweet_body and "tweet-content" in cls:
                    self.in_tweet_content = True
                    self.capture_text = True

            def handle_endtag(self, tag):
                if self.in_tweet_content and tag == "div":
                    self.in_tweet_content = False
                    self.capture_text = False
                if self.in_author and tag == "a":
                    self.in_author = False
                if self.in_tweet_body and tag == "div":
                    if self.current_tweet and self.current_tweet.get("content"):
                        self.tweets.append(self.current_tweet)
                    self.current_tweet = None
                    self.in_tweet_body = False

            def handle_data(self, data):
                if self.capture_text and self.current_tweet is not None:
                    if self.in_author:
                        self.current_tweet["author"] += data
                    elif self.in_tweet_content:
                        text = data.strip()
                        if text:
                            if not self.current_tweet["title"]:
                                self.current_tweet["title"] = text[:100]
                            self.current_tweet["content"] += text + " "

        try:
            parser = TweetParser()
            parser.feed(html)
            for tweet in parser.tweets:
                content = self._clean_text(tweet.get("content", ""))
                title = self._clean_text(tweet.get("title", content[:80]))
                results.append(self._format_result(
                    title=title or content[:80],
                    url=tweet.get("url", ""),
                    author=tweet.get("author", ""),
                    content=content[:300],
                    metadata={"source": "nitter"},
                ))
        except Exception:
            pass

        return results[:limit]
