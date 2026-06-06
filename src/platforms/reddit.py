"""
Reddit 平台适配器 / Reddit Platform Adapter

通过解析Reddit的JSON API和旧版HTML页面获取热帖和搜索结果。
Fetches hot posts and search results via Reddit's JSON API and old HTML pages.
"""

import json
import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.platforms.base import BasePlatform, fetch_url


class RedditAdapter(BasePlatform):
    """
    Reddit 平台适配器。
    Reddit Platform Adapter.

    利用Reddit的公开JSON API获取子版块内容和搜索结果。
    Utilizes Reddit's public JSON API for subreddit content and search results.
    """

    name = "reddit"
    display_name = "Reddit"
    base_url = "https://www.reddit.com"

    def search(self, query, limit=10):
        """
        搜索Reddit内容。
        Search Reddit content.

        Args:
            query: 搜索关键词 / Search query
            limit: 结果数量 / Number of results

        Returns:
            list[dict]: 搜索结果 / Search results
        """
        results = []
        try:
            encoded = query.replace(" ", "+")
            # 使用Reddit JSON API / Use Reddit JSON API
            url = f"https://www.reddit.com/search.json?q={encoded}&limit={limit}&sort=relevance"
            headers = {
                "User-Agent": "OmniReach-CLI/0.1 (by /u/omnireach-bot)",
                "Accept": "application/json",
            }
            raw = fetch_url(url, timeout=self.timeout, headers=headers, proxy=self.proxy)
            data = json.loads(raw)
            posts = data.get("data", {}).get("children", [])
            for post in posts:
                d = post.get("data", {})
                title = self._clean_text(d.get("title", ""))
                content = self._clean_text(d.get("selftext", ""))
                if not content:
                    content = self._clean_text(d.get("link_flair_text", ""))
                author = d.get("author", "")
                url_link = d.get("url", "")
                ts = d.get("created_utc", 0)
                timestamp = ""
                if ts:
                    import datetime
                    timestamp = datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%dT%H:%M:%S")

                results.append(self._format_result(
                    title=title,
                    url=url_link,
                    author=f"u/{author}",
                    content=content[:500],
                    timestamp=timestamp,
                    metadata={
                        "subreddit": d.get("subreddit", ""),
                        "score": d.get("score", 0),
                        "num_comments": d.get("num_comments", 0),
                    },
                ))
        except Exception as e:
            print(f"  [{self.display_name}] 搜索失败: {e}")

        return results[:limit]

    def trending(self, limit=10):
        """
        获取Reddit热门内容（来自r/all和r/popular）。
        Get Reddit trending content (from r/all and r/popular).

        Args:
            limit: 结果数量 / Number of results

        Returns:
            list[dict]: 热门结果 / Trending results
        """
        results = []
        subreddits = ["all", "popular"]
        per_sub = max(1, limit // len(subreddits))

        for sub in subreddits:
            try:
                url = f"https://www.reddit.com/r/{sub}/hot.json?limit={per_sub}"
                headers = {
                    "User-Agent": "OmniReach-CLI/0.1 (by /u/omnireach-bot)",
                    "Accept": "application/json",
                }
                raw = fetch_url(url, timeout=self.timeout, headers=headers, proxy=self.proxy)
                data = json.loads(raw)
                posts = data.get("data", {}).get("children", [])
                for post in posts:
                    d = post.get("data", {})
                    title = self._clean_text(d.get("title", ""))
                    content = self._clean_text(d.get("selftext", ""))
                    author = d.get("author", "")
                    url_link = d.get("url", "")
                    ts = d.get("created_utc", 0)
                    timestamp = ""
                    if ts:
                        import datetime
                        timestamp = datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%dT%H:%M:%S")

                    results.append(self._format_result(
                        title=title,
                        url=url_link,
                        author=f"u/{author}",
                        content=content[:500],
                        timestamp=timestamp,
                        metadata={
                            "subreddit": d.get("subreddit", ""),
                            "score": d.get("score", 0),
                            "num_comments": d.get("num_comments", 0),
                        },
                    ))
            except Exception as e:
                print(f"  [{self.display_name}] 获取 r/{sub} 热门失败: {e}")

        return results[:limit]
