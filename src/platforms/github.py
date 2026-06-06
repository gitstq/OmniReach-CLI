"""
GitHub 平台适配器 / GitHub Platform Adapter

通过解析GitHub Trending页面和搜索API获取仓库信息。
Fetches repository information by parsing GitHub Trending page and search API.
"""

import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.platforms.base import BasePlatform, fetch_url, parse_html


class GitHubAdapter(BasePlatform):
    """
    GitHub 平台适配器。
    GitHub Platform Adapter.

    通过解析GitHub Trending页面和搜索结果获取热门仓库。
    Fetches trending repos via GitHub Trending page and search results.
    """

    name = "github"
    display_name = "GitHub"
    base_url = "https://github.com"

    def search(self, query, limit=10):
        """
        搜索GitHub仓库。
        Search GitHub repositories.

        Args:
            query: 搜索关键词 / Search query
            limit: 结果数量 / Number of results

        Returns:
            list[dict]: 搜索结果 / Search results
        """
        results = []
        try:
            encoded = query.replace(" ", "+")
            url = f"https://github.com/search?q={encoded}&type=repositories"
            html = fetch_url(url, timeout=self.timeout, proxy=self.proxy)
            results = self._parse_search_results(html, limit)
        except Exception as e:
            print(f"  [{self.display_name}] 搜索失败: {e}")

        return results[:limit]

    def trending(self, limit=10):
        """
        获取GitHub Trending仓库。
        Get GitHub Trending repositories.

        Args:
            limit: 结果数量 / Number of results

        Returns:
            list[dict]: 热门仓库 / Trending repos
        """
        results = []
        try:
            url = "https://github.com/trending"
            html = fetch_url(url, timeout=self.timeout, proxy=self.proxy)
            results = self._parse_trending(html, limit)
        except Exception as e:
            print(f"  [{self.display_name}] 获取Trending失败: {e}")

        return results[:limit]

    def _parse_trending(self, html, limit):
        """
        解析GitHub Trending页面。
        Parse GitHub Trending page.

        Args:
            html: HTML内容 / HTML content
            limit: 结果数量限制 / Result count limit

        Returns:
            list[dict]: 解析结果 / Parsed results
        """
        results = []

        # 提取仓库条目 / Extract repo entries
        # GitHub Trending页面的仓库条目结构
        article_pattern = r'<article class="Box-row">(.*?)</article>'
        articles = re.findall(article_pattern, html, re.DOTALL)

        for article in articles[:limit]:
            try:
                # 仓库名 / Repo name
                repo_match = re.search(r'<h2[^>]*>.*?<a[^>]*href="(/[^"]+)"', article, re.DOTALL)
                repo_path = repo_match.group(1).strip() if repo_match else ""

                # 仓库描述 / Repo description
                desc_match = re.search(r'<p class="col-9[^"]*">\s*(.*?)\s*</p>', article, re.DOTALL)
                description = self._clean_text(desc_match.group(1)) if desc_match else ""

                # 编程语言 / Programming language
                lang_match = re.search(r'itemprop="programmingLanguage">\s*(\w+)\s*<', article)
                language = lang_match.group(1).strip() if lang_match else ""

                # Star数 / Star count
                star_match = re.search(r'href="/[^/]+/[^/]+/stargazers"[^>]*>\s*<svg[^>]*>.*?(\d[\d,]*)\s*', article, re.DOTALL)
                stars = star_match.group(1).strip() if star_match else "0"

                # Fork数 / Fork count
                fork_match = re.search(r'href="/[^/]+/[^/]+/forks"[^>]*>\s*<svg[^>]*>.*?(\d[\d,]*)\s*', article, re.DOTALL)
                forks = fork_match.group(1).strip() if fork_match else "0"

                # 今日Star / Today's stars
                today_match = re.search(r'(\d[\d,]*)\s*stars today', article)
                today_stars = today_match.group(1).strip() if today_match else ""

                if repo_path:
                    repo_name = repo_path.lstrip("/")
                    results.append(self._format_result(
                        title=repo_name,
                        url=f"https://github.com{repo_path}",
                        author=repo_name.split("/")[0] if "/" in repo_name else "",
                        content=description[:300],
                        metadata={
                            "language": language,
                            "stars": stars,
                            "forks": forks,
                            "today_stars": today_stars,
                        },
                    ))
            except Exception:
                continue

        return results

    def _parse_search_results(self, html, limit):
        """
        解析GitHub搜索结果页面。
        Parse GitHub search results page.

        Args:
            html: HTML内容 / HTML content
            limit: 结果数量限制 / Result count limit

        Returns:
            list[dict]: 解析结果 / Parsed results
        """
        results = []

        # 从搜索结果中提取仓库链接和描述 / Extract repo links and descriptions from search results
        repo_pattern = r'<a[^>]*href="(/[^"]+)"[^>]*class="v-align-middle"'
        repo_links = re.findall(repo_pattern, html)

        desc_pattern = r'<p class="mb-1[^"]*">\s*(.*?)\s*</p>'
        descriptions = re.findall(desc_pattern, html, re.DOTALL)

        lang_pattern = r'itemprop="programmingLanguage">\s*(\w+)\s*<'
        languages = re.findall(lang_pattern, html)

        star_pattern = r'href="/[^/]+/[^/]+/stargazers"[^>]*>\s*\n?\s*([\d,]+)\s*'
        stars_list = re.findall(star_pattern, html)

        for i, link in enumerate(repo_links[:limit]):
            if "/search?" in link or "/orgs/" in link:
                continue
            repo_name = link.lstrip("/")
            desc = descriptions[i] if i < len(descriptions) else ""
            lang = languages[i] if i < len(languages) else ""
            star_count = stars_list[i] if i < len(stars_list) else "0"

            results.append(self._format_result(
                title=repo_name,
                url=f"https://github.com{link}",
                author=repo_name.split("/")[0] if "/" in repo_name else "",
                content=self._clean_text(desc)[:300],
                metadata={
                    "language": lang,
                    "stars": star_count,
                },
            ))

        return results
