"""
Bilibili 平台适配器 / Bilibili Platform Adapter

通过解析B站搜索API和热门页面获取视频信息。
Fetches video information by parsing Bilibili search API and trending pages.
"""

import json
import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.platforms.base import BasePlatform, fetch_url


class BilibiliAdapter(BasePlatform):
    """
    Bilibili 平台适配器。
    Bilibili Platform Adapter.

    通过B站的公开搜索API和热门API获取视频信息。
    Fetches video info via Bilibili's public search and trending APIs.
    """

    name = "bilibili"
    display_name = "Bilibili"
    base_url = "https://www.bilibili.com"

    def search(self, query, limit=10):
        """
        搜索B站视频。
        Search Bilibili videos.

        Args:
            query: 搜索关键词 / Search query
            limit: 结果数量 / Number of results

        Returns:
            list[dict]: 搜索结果 / Search results
        """
        results = []
        try:
            # 使用B站搜索API / Use Bilibili search API
            url = (
                f"https://api.bilibili.com/x/web-interface/search/all/v2"
                f"?keyword={query}&page=1&page_size={limit}"
            )
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Referer": "https://www.bilibili.com",
            }
            raw = fetch_url(url, timeout=self.timeout, headers=headers, proxy=self.proxy)
            data = json.loads(raw)

            if data.get("code") == 0:
                result_data = data.get("data", {}).get("result", [])
                for item in result_data[:limit]:
                    if item.get("result_type") != "video":
                        continue
                    result = item.get("data", {}) or item
                    title = self._clean_text(result.get("title", ""))
                    # 去除B站标题中的HTML标签 / Remove HTML tags from Bilibili titles
                    title = re.sub(r"<[^>]+>", "", title)
                    author = result.get("author", "") or result.get("author_name", "")
                    url_link = result.get("url", "") or result.get("arcurl", "")
                    if url_link and not url_link.startswith("http"):
                        url_link = f"https:{url_link}" if url_link.startswith("//") else f"https://www.bilibili.com{url_link}"
                    content = result.get("description", "") or result.get("desc", "")
                    content = self._clean_text(re.sub(r"<[^>]+>", "", content))
                    play = result.get("play", 0) or 0
                    danmaku = result.get("video_review", 0) or result.get("danmaku", 0) or 0
                    duration = result.get("duration", "") or ""
                    timestamp = result.get("pubdate", "") or result.get("pubdate_ts", "")

                    results.append(self._format_result(
                        title=title,
                        url=url_link,
                        author=author,
                        content=content[:300],
                        timestamp=str(timestamp),
                        metadata={
                            "play_count": play,
                            "danmaku_count": danmaku,
                            "duration": duration,
                        },
                    ))
        except Exception as e:
            print(f"  [{self.display_name}] 搜索失败: {e}")

        return results[:limit]

    def trending(self, limit=10):
        """
        获取B站热门视频。
        Get Bilibili trending/hot videos.

        Args:
            limit: 结果数量 / Number of results

        Returns:
            list[dict]: 热门结果 / Trending results
        """
        results = []
        try:
            # 使用B站热门API / Use Bilibili trending API
            url = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all"
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Referer": "https://www.bilibili.com",
            }
            raw = fetch_url(url, timeout=self.timeout, headers=headers, proxy=self.proxy)
            data = json.loads(raw)

            if data.get("code") == 0:
                list_data = data.get("data", {}).get("list", [])
                for item in list_data[:limit]:
                    title = self._clean_text(item.get("title", ""))
                    author = item.get("owner", {}).get("name", "")
                    url_link = item.get("url", "") or f"https://www.bilibili.com/video/{item.get('bvid', '')}"
                    desc = self._clean_text(item.get("desc", ""))
                    stat = item.get("stat", {})
                    play = stat.get("view", 0)
                    danmaku = stat.get("danmaku", 0)
                    likes = stat.get("like", 0)
                    duration = item.get("duration", "")
                    timestamp = item.get("pubdate", 0)
                    ts_str = ""
                    if timestamp:
                        import datetime
                        ts_str = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%dT%H:%M:%S")

                    results.append(self._format_result(
                        title=title,
                        url=url_link,
                        author=author,
                        content=desc[:300],
                        timestamp=ts_str,
                        metadata={
                            "play_count": play,
                            "danmaku_count": danmaku,
                            "likes": likes,
                            "duration": duration,
                            "bvid": item.get("bvid", ""),
                        },
                    ))
        except Exception as e:
            print(f"  [{self.display_name}] 获取热门失败: {e}")

        return results[:limit]
