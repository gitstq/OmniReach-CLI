"""
Hacker News 平台适配器 / Hacker News Platform Adapter

通过Hacker News公开API获取热帖和搜索结果。
Fetches hot posts and search results via Hacker News public API.
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.platforms.base import BasePlatform, fetch_url


class HackerNewsAdapter(BasePlatform):
    """
    Hacker News 平台适配器。
    Hacker News Platform Adapter.

    利用Hacker News的Firebase API获取热门帖子和搜索结果。
    Utilizes Hacker News Firebase API for hot posts and search results.
    """

    name = "hackernews"
    display_name = "Hacker News"
    base_url = "https://news.ycombinator.com"
    # HN Firebase API
    api_base = "https://hacker-news.firebaseio.com/v0"

    def search(self, query, limit=10):
        """
        搜索Hacker News内容（通过Algolia HN Search API）。
        Search Hacker News content (via Algolia HN Search API).

        Args:
            query: 搜索关键词 / Search query
            limit: 结果数量 / Number of results

        Returns:
            list[dict]: 搜索结果 / Search results
        """
        results = []
        try:
            # 使用Algolia的HN搜索API / Use Algolia HN Search API
            encoded = query.replace(" ", "+")
            url = (
                f"https://hn.algolia.com/api/v1/search"
                f"?query={encoded}&hitsPerPage={limit}"
            )
            headers = {
                "User-Agent": "OmniReach-CLI/0.1",
                "Accept": "application/json",
            }
            raw = fetch_url(url, timeout=self.timeout, headers=headers, proxy=self.proxy)
            data = json.loads(raw)

            hits = data.get("hits", [])
            for hit in hits[:limit]:
                title = self._clean_text(hit.get("title", "") or hit.get("story_title", ""))
                url_link = hit.get("url", "") or ""
                if not url_link:
                    story_id = hit.get("objectID", "")
                    url_link = f"https://news.ycombinator.com/item?id={story_id}"
                author = hit.get("author", "")
                content = self._clean_text(hit.get("comment_text", "") or "")
                if not content:
                    # 使用story_text或截取标题 / Use story_text or truncate title
                    content = self._clean_text(hit.get("story_text", ""))[:300]
                points = hit.get("points", 0)
                num_comments = hit.get("num_comments", 0)
                created = hit.get("created_at", "")

                results.append(self._format_result(
                    title=title,
                    url=url_link,
                    author=author,
                    content=content[:300],
                    timestamp=created,
                    metadata={
                        "points": points,
                        "num_comments": num_comments,
                    },
                ))
        except Exception as e:
            print(f"  [{self.display_name}] 搜索失败: {e}")

        return results[:limit]

    def trending(self, limit=10):
        """
        获取Hacker News热门帖子。
        Get Hacker News top/hot posts.

        Args:
            limit: 结果数量 / Number of results

        Returns:
            list[dict]: 热门结果 / Trending results
        """
        results = []
        try:
            # 获取Top Stories ID列表 / Get Top Stories ID list
            url = f"{self.api_base}/topstories.json"
            headers = {"User-Agent": "OmniReach-CLI/0.1"}
            raw = fetch_url(url, timeout=self.timeout, headers=headers, proxy=self.proxy)
            story_ids = json.loads(raw)[:limit]

            # 逐个获取帖子详情 / Fetch each story detail
            for sid in story_ids:
                try:
                    item_url = f"{self.api_base}/item/{sid}.json"
                    raw_item = fetch_url(item_url, timeout=10, headers=headers, proxy=self.proxy)
                    item = json.loads(raw_item)

                    title = self._clean_text(item.get("title", ""))
                    url_link = item.get("url", "") or f"https://news.ycombinator.com/item?id={sid}"
                    author = item.get("by", "")
                    score = item.get("score", 0)
                    descendants = item.get("descendants", 0)
                    ts = item.get("time", 0)
                    timestamp = ""
                    if ts:
                        import datetime
                        timestamp = datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%dT%H:%M:%S")

                    results.append(self._format_result(
                        title=title,
                        url=url_link,
                        author=author,
                        content=f"Score: {score} | Comments: {descendants}",
                        timestamp=timestamp,
                        metadata={
                            "score": score,
                            "num_comments": descendants,
                            "hn_id": sid,
                        },
                    ))
                except Exception:
                    continue
        except Exception as e:
            print(f"  [{self.display_name}] 获取热门失败: {e}")

        return results[:limit]
