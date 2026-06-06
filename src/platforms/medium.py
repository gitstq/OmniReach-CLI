"""
Medium 平台适配器 / Medium Platform Adapter

通过解析Medium热门页面获取文章信息。
Fetches article information by parsing Medium trending/popular pages.
"""

import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.platforms.base import BasePlatform, fetch_url, parse_html


class MediumAdapter(BasePlatform):
    """
    Medium 平台适配器。
    Medium Platform Adapter.

    通过解析Medium热门话题页面和搜索结果获取文章信息。
    Fetches article info by parsing Medium trending topic pages and search results.
    """

    name = "medium"
    display_name = "Medium"
    base_url = "https://medium.com"

    def search(self, query, limit=10):
        """
        搜索Medium文章。
        Search Medium articles.

        Args:
            query: 搜索关键词 / Search query
            limit: 结果数量 / Number of results

        Returns:
            list[dict]: 搜索结果 / Search results
        """
        results = []
        try:
            encoded = query.replace(" ", "+")
            url = f"https://medium.com/search?q={encoded}"
            html = fetch_url(url, timeout=self.timeout, proxy=self.proxy)
            results = self._parse_search_results(html, limit)
        except Exception as e:
            print(f"  [{self.display_name}] 搜索失败: {e}")

        return results[:limit]

    def trending(self, limit=10):
        """
        获取Medium热门文章。
        Get Medium trending/popular articles.

        Args:
            limit: 结果数量 / Number of results

        Returns:
            list[dict]: 热门结果 / Trending results
        """
        results = []
        topics = [
            "technology",
            "programming",
            "artificial-intelligence",
        ]

        for topic in topics:
            try:
                url = f"https://medium.com/tag/{topic}/recommended"
                html = fetch_url(url, timeout=self.timeout, proxy=self.proxy)
                items = self._parse_tag_page(html, limit)
                results.extend(items)
                if len(results) >= limit:
                    break
            except Exception as e:
                print(f"  [{self.display_name}] 获取 {topic} 热门失败: {e}")

        return results[:limit]

    def _parse_search_results(self, html, limit):
        """
        解析Medium搜索结果页面。
        Parse Medium search result page.

        Args:
            html: HTML内容 / HTML content
            limit: 结果数量限制 / Result count limit

        Returns:
            list[dict]: 解析结果 / Parsed results
        """
        results = []

        # Medium搜索结果嵌入在window.__INITIAL_STATE__中
        # Search results are embedded in window.__INITIAL_STATE__
        state_pattern = r'window\.__INITIAL_STATE__\s*=\s*({.+?});</script>'
        match = re.search(state_pattern, html, re.DOTALL)

        if match:
            try:
                import json
                # 清理JSON字符串 / Clean JSON string
                state_str = match.group(1)
                # 替换undefined为null / Replace undefined with null
                state_str = re.sub(r'\bundefined\b', 'null', state_str)
                state = json.loads(state_str)

                # 尝试从state中提取搜索结果 / Try extracting search results from state
                if isinstance(state, dict):
                    for key, value in state.items():
                        if isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                if isinstance(sub_value, list):
                                    for item in sub_value[:limit]:
                                        if isinstance(item, dict):
                                            title = item.get("title", "")
                                            url_link = item.get("url", "")
                                            author = item.get("author", "") or item.get("creator", "")
                                            if title:
                                                results.append(self._format_result(
                                                    title=self._clean_text(title),
                                                    url=url_link,
                                                    author=str(author),
                                                    content=self._clean_text(item.get("preview", ""))[:300],
                                                    metadata={"source": "search_api"},
                                                ))
            except Exception:
                pass

        # 备用方法：从HTML中提取文章链接 / Fallback: extract article links from HTML
        if not results:
            results = self._parse_tag_page(html, limit)

        return results[:limit]

    def _parse_tag_page(self, html, limit):
        """
        解析Medium标签页面（热门文章）。
        Parse Medium tag page (trending articles).

        Args:
            html: HTML内容 / HTML content
            limit: 结果数量限制 / Result count limit

        Returns:
            list[dict]: 解析结果 / Parsed results
        """
        results = []

        # 提取文章链接 / Extract article links
        # Medium文章链接格式: /@username/article-slug-id
        article_pattern = r'href="(/@[^/]+/[a-z0-9-]+-[a-f0-9]{10,})"'
        article_links = list(set(re.findall(article_pattern, html)))

        # 提取文章标题 / Extract article titles
        title_pattern = r'<h[23][^>]*>([^<]{10,100})</h[23]>'
        titles = re.findall(title_pattern, html)

        # 提取作者 / Extract authors
        author_pattern = r'href="(/@[^/"]+)"'
        authors = list(set(re.findall(author_pattern, html)))

        for i, link in enumerate(article_links[:limit]):
            title = titles[i] if i < len(titles) else f"Medium Article"
            author = ""
            if i < len(authors):
                author = authors[i].lstrip("/@")

            results.append(self._format_result(
                title=self._clean_text(title),
                url=f"https://medium.com{link}",
                author=author,
                content="",
                metadata={"source": "tag_page"},
            ))

        return results
