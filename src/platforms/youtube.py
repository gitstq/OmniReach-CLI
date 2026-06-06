"""
YouTube 平台适配器 / YouTube Platform Adapter

通过解析YouTube搜索结果页面获取视频信息。
Fetches video information by parsing YouTube search result pages.
"""

import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.platforms.base import BasePlatform, fetch_url, parse_html


class YouTubeAdapter(BasePlatform):
    """
    YouTube 平台适配器。
    YouTube Platform Adapter.

    通过解析YouTube搜索页面和热门页面获取视频信息。
    Fetches video info by parsing YouTube search and trending pages.
    """

    name = "youtube"
    display_name = "YouTube"
    base_url = "https://www.youtube.com"

    def search(self, query, limit=10):
        """
        搜索YouTube视频。
        Search YouTube videos.

        Args:
            query: 搜索关键词 / Search query
            limit: 结果数量 / Number of results

        Returns:
            list[dict]: 搜索结果 / Search results
        """
        results = []
        try:
            encoded = query.replace(" ", "+")
            url = f"https://www.youtube.com/results?search_query={encoded}"
            html = fetch_url(url, timeout=self.timeout, proxy=self.proxy)
            results = self._parse_search_results(html, limit)
        except Exception as e:
            print(f"  [{self.display_name}] 搜索失败: {e}")

        return results[:limit]

    def trending(self, limit=10):
        """
        获取YouTube热门视频。
        Get YouTube trending videos.

        Args:
            limit: 结果数量 / Number of results

        Returns:
            list[dict]: 热门结果 / Trending results
        """
        results = []
        try:
            url = "https://www.youtube.com/feed/trending"
            html = fetch_url(url, timeout=self.timeout, proxy=self.proxy)
            results = self._parse_search_results(html, limit)
        except Exception as e:
            print(f"  [{self.display_name}] 获取热门失败: {e}")

        return results[:limit]

    def _parse_search_results(self, html, limit):
        """
        解析YouTube搜索/热门结果页面。
        Parse YouTube search/trending result page.

        使用正则表达式从YouTube的初始数据中提取视频信息。
        Uses regex to extract video info from YouTube's initial data.

        Args:
            html: HTML内容 / HTML content
            limit: 结果数量限制 / Result count limit

        Returns:
            list[dict]: 解析结果 / Parsed results
        """
        results = []

        # 从YouTube的JSON数据中提取视频信息 / Extract video info from YouTube's JSON data
        # YouTube在页面中嵌入了JSON格式的视频数据
        video_ids = set()

        # 方法1: 从ytInitialData中提取 / Extract from ytInitialData
        pattern = r'"videoId":"([a-zA-Z0-9_-]{11})"'
        for match in re.finditer(pattern, html):
            vid = match.group(1)
            if vid not in video_ids:
                video_ids.add(vid)

        # 方法2: 从/watch?v=链接中提取 / Extract from /watch?v= links
        pattern2 = r'href="/watch\?v=([a-zA-Z0-9_-]{11})'
        for match in re.finditer(pattern2, html):
            vid = match.group(1)
            if vid not in video_ids:
                video_ids.add(vid)

        # 提取视频标题 / Extract video titles
        title_pattern = r'"title":\s*\{[^}]*"runs":\s*\[\{"text":\s*"([^"]+)"'
        titles = re.findall(title_pattern, html)

        # 提取频道名称 / Extract channel names
        channel_pattern = r'"channelName":\s*\{[^}]*"simpleText":\s*"([^"]+)"'
        channels = re.findall(channel_pattern, html)

        # 提取视图数和时长 / Extract view counts and durations
        view_pattern = r'"viewCountText":\s*\{[^}]*"simpleText":\s*"([^"]+)"'
        views = re.findall(view_pattern, html)

        duration_pattern = r'"lengthText":\s*\{[^}]*"simpleText":\s*"([^"]+)"'
        durations = re.findall(duration_pattern, html)

        for i, vid in enumerate(list(video_ids)[:limit]):
            title = titles[i] if i < len(titles) else f"YouTube Video {vid}"
            author = channels[i] if i < len(channels) else ""
            view_count = views[i] if i < len(views) else ""
            duration = durations[i] if i < len(durations) else ""

            results.append(self._format_result(
                title=self._clean_text(title),
                url=f"https://www.youtube.com/watch?v={vid}",
                author=self._clean_text(author),
                content=f"{view_count} | {duration}".strip() if view_count or duration else "",
                metadata={
                    "video_id": vid,
                    "views": view_count,
                    "duration": duration,
                },
            ))

        return results
