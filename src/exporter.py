"""
导出模块 / Exporter Module

支持将搜索结果导出为 JSON、CSV、Markdown、纯文本格式。
Supports exporting search results to JSON, CSV, Markdown, and plain text formats.
"""

import csv
import io
import json
import os
import time


class Exporter:
    """
    结果导出器。
    Result exporter.

    支持多种格式的搜索结果导出。
    Supports multiple export formats for search results.
    """

    def __init__(self, export_dir="./exports"):
        """
        初始化导出器。
        Initialize exporter.

        Args:
            export_dir: 导出目录 / Export directory
        """
        self.export_dir = export_dir

    def _ensure_dir(self):
        """确保导出目录存在 / Ensure export directory exists"""
        os.makedirs(self.export_dir, exist_ok=True)

    def _generate_filename(self, prefix, extension):
        """
        生成带时间戳的文件名。
        Generate filename with timestamp.

        Args:
            prefix: 文件名前缀 / Filename prefix
            extension: 文件扩展名 / File extension

        Returns:
            str: 完整文件路径 / Full file path
        """
        self._ensure_dir()
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.{extension}"
        return os.path.join(self.export_dir, filename)

    def export_json(self, results, filename=None):
        """
        导出为JSON格式。
        Export to JSON format.

        Args:
            results: 搜索结果列表 / Search result list
            filename: 自定义文件名 / Custom filename

        Returns:
            str: 导出文件路径 / Export file path
        """
        filepath = filename or self._generate_filename("omnireach_results", "json")
        self._ensure_dir()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        return filepath

    def export_csv(self, results, filename=None):
        """
        导出为CSV格式。
        Export to CSV format.

        Args:
            results: 搜索结果列表 / Search result list
            filename: 自定义文件名 / Custom filename

        Returns:
            str: 导出文件路径 / Export file path
        """
        filepath = filename or self._generate_filename("omnireach_results", "csv")
        self._ensure_dir()

        if not results:
            # 写入空CSV带表头 / Write empty CSV with headers
            with open(filepath, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["title", "url", "author", "content", "platform", "timestamp"])
            return filepath

        fieldnames = ["title", "url", "author", "content", "platform", "timestamp"]
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for item in results:
                writer.writerow({
                    k: v.replace("\n", " ").replace("\r", "") if isinstance(v, str) else v
                    for k, v in item.items()
                })
        return filepath

    def export_markdown(self, results, filename=None, title="OmniReach 搜索结果"):
        """
        导出为Markdown格式。
        Export to Markdown format.

        Args:
            results: 搜索结果列表 / Search result list
            filename: 自定义文件名 / Custom filename
            title: 文档标题 / Document title

        Returns:
            str: 导出文件路径 / Export file path
        """
        filepath = filename or self._generate_filename("omnireach_results", "md")
        self._ensure_dir()

        lines = [
            f"# {title}\n",
            f"> 导出时间: {time.strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"> 结果数量: {len(results)}\n",
            "---\n",
        ]

        for i, item in enumerate(results, 1):
            lines.append(f"## {i}. {item.get('title', '无标题')}\n")
            lines.append(f"- **平台**: {item.get('platform', 'unknown')}")
            lines.append(f"- **作者**: {item.get('author', '未知')}")
            lines.append(f"- **时间**: {item.get('timestamp', '')}")
            lines.append(f"- **链接**: {item.get('url', '')}")
            content = item.get("content", "")
            if content:
                lines.append(f"\n> {content}\n")
            lines.append("---\n")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return filepath

    def export_text(self, results, filename=None, title="OmniReach 搜索结果"):
        """
        导出为纯文本格式。
        Export to plain text format.

        Args:
            results: 搜索结果列表 / Search result list
            filename: 自定义文件名 / Custom filename
            title: 文档标题 / Document title

        Returns:
            str: 导出文件路径 / Export file path
        """
        filepath = filename or self._generate_filename("omnireach_results", "txt")
        self._ensure_dir()

        separator = "=" * 60
        lines = [
            separator,
            f"  {title}",
            f"  导出时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"  结果数量: {len(results)}",
            separator,
            "",
        ]

        for i, item in enumerate(results, 1):
            lines.append(f"[{i}] {item.get('title', '无标题')}")
            lines.append(f"    平台: {item.get('platform', 'unknown')}")
            lines.append(f"    作者: {item.get('author', '未知')}")
            lines.append(f"    时间: {item.get('timestamp', '')}")
            lines.append(f"    链接: {item.get('url', '')}")
            content = item.get("content", "")
            if content:
                lines.append(f"    摘要: {content}")
            lines.append("")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return filepath

    def export(self, results, fmt="json", filename=None, title="OmniReach 搜索结果"):
        """
        根据格式导出结果。
        Export results in specified format.

        Args:
            results: 搜索结果列表 / Search result list
            fmt: 导出格式 (json/csv/markdown/text) / Export format
            filename: 自定义文件名 / Custom filename
            title: 文档标题 / Document title

        Returns:
            str: 导出文件路径 / Export file path

        Raises:
            ValueError: 不支持的格式 / Unsupported format
        """
        exporters = {
            "json": lambda: self.export_json(results, filename),
            "csv": lambda: self.export_csv(results, filename),
            "markdown": lambda: self.export_markdown(results, filename, title),
            "md": lambda: self.export_markdown(results, filename, title),
            "text": lambda: self.export_text(results, filename, title),
            "txt": lambda: self.export_text(results, filename, title),
        }

        if fmt not in exporters:
            raise ValueError(
                f"不支持的导出格式: {fmt}。支持的格式: {', '.join(exporters.keys())}\n"
                f"Unsupported format: {fmt}. Supported: {', '.join(exporters.keys())}"
            )

        return exporters[fmt]()
