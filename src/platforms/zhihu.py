"""
知乎平台适配器 / Zhihu Platform Adapter

通过解析知乎热榜页面获取热门内容。
Fetches trending content by parsing Zhihu hot list page.
"""

import json
import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.platforms.base import BasePlatform, fetch_url


class ZhihuAdapter(BasePlatform):
    """
    知乎平台适配器。
    Zhihu Platform Adapter.

    通过知乎的公开API和页面解析获取热榜和搜索结果。
    Fetches hot list and search results via Zhihu's public API and page parsing.
    """

    name = "zhihu"
    display_name = "知乎"
    base_url = "https://www.zhihu.com"

    def search(self, query, limit=10):
        """
        搜索知乎内容。
        Search Zhihu content.

        Args:
            query: 搜索关键词 / Search query
            limit: 结果数量 / Number of results

        Returns:
            list[dict]: 搜索结果 / Search results
        """
        results = []
        try:
            # 使用知乎搜索API / Use Zhihu search API
            url = (
                f"https://www.zhihu.com/api/v4/search_v3?t=general"
                f"&q={query}&correction=1&offset=0&limit={limit}"
                f"&filter_fields=question.answer_count,author"
                f"&lc_id=0"
            )
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Referer": "https://www.zhihu.com",
                "Accept": "application/json",
            }
            raw = fetch_url(url, timeout=self.timeout, headers=headers, proxy=self.proxy)
            data = json.loads(raw)

            items = data.get("data", [])
            for item in items[:limit]:
                try:
                    obj = item.get("object", {}) or item
                    # 问题类型 / Question type
                    q_type = item.get("type", "")
                    highlight = item.get("highlight", "")

                    if q_type == "search_result":
                        title = self._clean_text(obj.get("title", "") or obj.get("name", ""))
                        url_link = obj.get("url", "")
                        if url_link and not url_link.startswith("http"):
                            url_link = f"https://www.zhihu.com{url_link}"
                        author = ""
                        excerpt = self._clean_text(obj.get("excerpt", "") or highlight)
                        content = excerpt[:300]

                        results.append(self._format_result(
                            title=title,
                            url=url_link,
                            author=author,
                            content=content,
                            metadata={"type": q_type},
                        ))
                except Exception:
                    continue
        except Exception as e:
            print(f"  [{self.display_name}] 搜索失败: {e}")

        return results[:limit]

    def trending(self, limit=10):
        """
        获取知乎热榜。
        Get Zhihu hot list.

        Args:
            limit: 结果数量 / Number of results

        Returns:
            list[dict]: 热门结果 / Trending results
        """
        results = []
        try:
            # 使用知乎热榜API / Use Zhihu hot list API
            url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=30"
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Referer": "https://www.zhihu.com",
                "Accept": "application/json",
            }
            raw = fetch_url(url, timeout=self.timeout, headers=headers, proxy=self.proxy)
            data = json.loads(raw)

            items = data.get("data", [])
            for i, item in enumerate(items[:limit]):
                try:
                    target = item.get("target", {})
                    title = self._clean_text(target.get("title", ""))
                    question_id = target.get("id", "")
                    url_link = f"https://www.zhihu.com/question/{question_id}"
                    excerpt = self._clean_text(target.get("excerpt", ""))
                    author_info = target.get("author", {}) or {}
                    author = author_info.get("name", "")

                    # 热度值 / Heat value
                    detail_text = item.get("detail_text", "")

                    results.append(self._format_result(
                        title=title,
                        url=url_link,
                        author=author,
                        content=excerpt[:300],
                        metadata={
                            "heat": detail_text,
                            "rank": i + 1,
                        },
                    ))
                except Exception:
                    continue
        except Exception as e:
            # 尝试备用方法：解析网页版热榜 / Try fallback: parse web hot list
            try:
                results = self._parse_hot_page(limit)
            except Exception as e2:
                print(f"  [{self.display_name}] 获取热榜失败: {e} / {e2}")

        return results[:limit]

    def _parse_hot_page(self, limit):
        """
        解析知乎热榜网页版（备用方法）。
        Parse Zhihu hot list web page (fallback method).

        Args:
            limit: 结果数量限制 / Result count limit

        Returns:
            list[dict]: 解析结果 / Parsed results
        """
        results = []
        url = "https://www.zhihu.com/hot"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        }
        html = fetch_url(url, timeout=self.timeout, headers=headers, proxy=self.proxy)

        # 从初始数据中提取热榜 / Extract hot list from initial data
        pattern = r'"title":"([^"]+)".*?"excerpt":"([^"]*)"'
        matches = re.findall(pattern, html)

        for i, (title, excerpt) in enumerate(matches[:limit]):
            title = self._clean_text(title.replace("\\u", "\\u"))
            excerpt = self._clean_text(excerpt.replace("\\u", "\\u"))
            # 解码Unicode转义 / Decode unicode escapes
            try:
                title = title.encode("utf-8").decode("unicode_escape")
                excerpt = excerpt.encode("utf-8").decode("unicode_escape")
            except Exception:
                pass

            results.append(self._format_result(
                title=title,
                url=f"https://www.zhihu.com/search?type=content&q={title}",
                author="",
                content=excerpt[:300],
                metadata={"rank": i + 1},
            ))

        return results
