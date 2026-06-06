"""
内容处理器模块 / Content Processor Module

对搜索结果进行去重、结构化提取、关键词高亮和内容摘要。
Deduplication, structured extraction, keyword highlighting, and content summarization
for search results.
"""

import re
import time
from urllib.parse import urlparse


class ContentProcessor:
    """
    内容处理器。
    Content processor.

    提供搜索结果的后处理功能：去重、清洗、摘要生成、关键词高亮。
    Provides post-processing for search results: dedup, cleaning, summarization, highlighting.
    """

    def __init__(self):
        self._seen_urls = set()
        self._seen_titles = set()

    def deduplicate(self, results):
        """
        对搜索结果进行去重。
        Deduplicate search results.

        基于URL和标题相似度进行去重。
        Deduplication based on URL and title similarity.

        Args:
            results: 搜索结果列表 / Search result list

        Returns:
            list: 去重后的结果列表 / Deduplicated result list
        """
        unique = []
        for item in results:
            url = item.get("url", "").rstrip("/")
            title = item.get("title", "").lower().strip()

            # URL完全匹配去重 / Exact URL match dedup
            if url and url in self._seen_urls:
                continue
            # 标题完全匹配去重 / Exact title match dedup
            if title and title in self._seen_titles:
                continue

            if url:
                self._seen_urls.add(url)
            if title:
                self._seen_titles.add(title)
            unique.append(item)

        return unique

    def clean_content(self, content, max_length=500):
        """
        清理和截断内容文本。
        Clean and truncate content text.

        Args:
            content: 原始内容 / Raw content
            max_length: 最大长度 / Maximum length

        Returns:
            str: 清理后的内容 / Cleaned content
        """
        if not content:
            return ""
        # 去除多余空白 / Remove extra whitespace
        content = re.sub(r"\s+", " ", content)
        content = content.strip()
        # 截断 / Truncate
        if len(content) > max_length:
            content = content[:max_length].rsplit(" ", 1)[0] + "..."
        return content

    def extract_summary(self, content, max_length=200):
        """
        基于文本截取生成简单摘要。
        Generate simple summary based on text truncation.

        不依赖LLM，使用首句或前N个字符作为摘要。
        No LLM dependency, uses first sentence or first N characters as summary.

        Args:
            content: 内容文本 / Content text
            max_length: 摘要最大长度 / Maximum summary length

        Returns:
            str: 摘要文本 / Summary text
        """
        if not content:
            return ""
        # 尝试按句号分割取首句 / Try splitting by period for first sentence
        sentences = re.split(r"[。！？.!?\n]", content)
        summary = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) >= 20:  # 至少20字符的句子 / At least 20 chars
                summary = sentence
                break
        if not summary:
            summary = content.strip()
        if len(summary) > max_length:
            summary = summary[:max_length].rsplit(" ", 1)[0] + "..."
        return summary

    def highlight_keywords(self, text, keywords, color_code="\033[33m"):
        """
        在文本中高亮关键词。
        Highlight keywords in text.

        Args:
            text: 原始文本 / Original text
            keywords: 关键词列表 / Keyword list
            color_code: ANSI颜色码 / ANSI color code

        Returns:
            str: 高亮后的文本 / Highlighted text
        """
        if not text or not keywords:
            return text
        reset = "\033[0m"
        for keyword in keywords:
            if not keyword:
                continue
            # 不区分大小写替换 / Case-insensitive replacement
            pattern = re.compile(
                re.escape(keyword), re.IGNORECASE
            )
            text = pattern.sub(
                f"{color_code}{keyword}{reset}", text
            )
        return text

    def normalize_results(self, results):
        """
        标准化搜索结果格式。
        Normalize search result format.

        确保所有结果包含必需字段。
        Ensure all results contain required fields.

        Args:
            results: 搜索结果列表 / Search result list

        Returns:
            list: 标准化后的结果列表 / Normalized result list
        """
        normalized = []
        for item in results:
            if not isinstance(item, dict):
                continue
            normalized.append({
                "title": str(item.get("title", "")).strip(),
                "url": str(item.get("url", "")).strip(),
                "author": str(item.get("author", "")).strip(),
                "content": self.clean_content(str(item.get("content", ""))),
                "platform": str(item.get("platform", "unknown")),
                "timestamp": str(item.get("timestamp", "")) or time.strftime("%Y-%m-%dT%H:%M:%S"),
                "metadata": item.get("metadata", {}),
            })
        return normalized

    def extract_domain(self, url):
        """
        从URL中提取域名。
        Extract domain from URL.

        Args:
            url: URL字符串 / URL string

        Returns:
            str: 域名 / Domain name
        """
        try:
            parsed = urlparse(url)
            return parsed.netloc or ""
        except Exception:
            return ""

    def reset(self):
        """
        重置去重状态。
        Reset deduplication state.
        """
        self._seen_urls.clear()
        self._seen_titles.clear()
