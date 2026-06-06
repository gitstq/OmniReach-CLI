"""
TUI仪表盘模块 / TUI Dashboard Module

使用纯终端字符绘制的交互式仪表盘，支持彩色输出、表格展示、平台选择等。
Interactive dashboard using pure terminal characters with color output,
table display, and platform selection.
"""

import os
import sys
import time

# 确保可以导入父模块 / Ensure parent module import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.platforms.base import Colors


# ── 终端工具函数 / Terminal Utility Functions ───────────────────────

def supports_color():
    """
    检测终端是否支持彩色输出。
    Detect whether terminal supports color output.
    """
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("OMNIREACH_NO_COLOR"):
        return False
    if not hasattr(sys.stdout, "isatty"):
        return False
    if not sys.stdout.isatty():
        return False
    # Windows需要ANSI支持 / Windows needs ANSI support
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            return bool(kernel32.GetConsoleMode(kernel32.GetStdHandle(-11)))
        except Exception:
            return False
    return True

COLOR_ENABLED = supports_color()


def colorize(text, color_code):
    """
    为文本添加ANSI颜色。
    Add ANSI color to text.

    Args:
        text: 原始文本 / Original text
        color_code: ANSI颜色码 / ANSI color code

    Returns:
        str: 着色后的文本 / Colored text
    """
    if COLOR_ENABLED and color_code:
        return f"{color_code}{text}{Colors.RESET}"
    return text


def bold(text):
    """加粗文本 / Bold text"""
    return colorize(text, Colors.BOLD)


def dim(text):
    """暗淡文本 / Dim text"""
    return colorize(text, Colors.DIM)


def red(text):
    """红色文本 / Red text"""
    return colorize(text, Colors.RED)


def green(text):
    """绿色文本 / Green text"""
    return colorize(text, Colors.GREEN)


def yellow(text):
    """黄色文本 / Yellow text"""
    return colorize(text, Colors.YELLOW)


def blue(text):
    """蓝色文本 / Blue text"""
    return colorize(text, Colors.BLUE)


def cyan(text):
    """青色文本 / Cyan text"""
    return colorize(text, Colors.CYAN)


def magenta(text):
    """品红色文本 / Magenta text"""
    return colorize(text, Colors.MAGENTA)


# ── 表格绘制 / Table Drawing ────────────────────────────────────────

def draw_table(headers, rows, col_widths=None, max_col_width=50):
    """
    在终端绘制格式化表格。
    Draw formatted table in terminal.

    Args:
        headers: 表头列表 / Header list
        rows: 数据行列表 / Data row list
        col_widths: 列宽列表 / Column width list
        max_col_width: 最大列宽 / Maximum column width

    Returns:
        str: 表格字符串 / Table string
    """
    if not headers:
        return ""

    num_cols = len(headers)

    # 计算列宽 / Calculate column widths
    if col_widths is None:
        col_widths = []
        for i, header in enumerate(headers):
            max_w = len(header)
            for row in rows:
                if i < len(row):
                    cell = str(row[i])
                    max_w = max(max_w, len(cell))
            col_widths.append(min(max_w + 2, max_col_width))

    # 构建分隔线 / Build separator line
    sep_parts = []
    for w in col_widths:
        sep_parts.append("-" * w)
    separator = "+" + "+".join(sep_parts) + "+"

    # 构建表头 / Build header row
    header_parts = []
    for i, h in enumerate(headers):
        cell = str(h).ljust(col_widths[i])[:col_widths[i]]
        header_parts.append(cell)
    header_line = "|" + "|".join(header_parts) + "|"

    # 构建数据行 / Build data rows
    data_lines = []
    for row in rows:
        row_parts = []
        for i in range(num_cols):
            cell = str(row[i]) if i < len(row) else ""
            cell = cell.ljust(col_widths[i])[:col_widths[i]]
            row_parts.append(cell)
        data_lines.append("|" + "|".join(row_parts) + "|")

    # 组合表格 / Assemble table
    lines = [separator, header_line, separator]
    for line in data_lines:
        lines.append(line)
    lines.append(separator)

    return "\n".join(lines)


def truncate_text(text, max_length=40):
    """
    截断文本并添加省略号。
    Truncate text and add ellipsis.

    Args:
        text: 原始文本 / Original text
        max_length: 最大长度 / Maximum length

    Returns:
        str: 截断后的文本 / Truncated text
    """
    if not text:
        return ""
    text = str(text).replace("\n", " ").replace("\r", "")
    if len(text) > max_length:
        return text[:max_length - 3] + "..."
    return text


# ── 结果格式化展示 / Result Formatting Display ──────────────────────

def format_results_table(results, show_index=True):
    """
    将搜索结果格式化为终端表格。
    Format search results as terminal table.

    Args:
        results: 搜索结果列表 / Search result list
        show_index: 是否显示序号 / Whether to show index

    Returns:
        str: 格式化表格字符串 / Formatted table string
    """
    if not results:
        return dim("  (无结果 / No results)")

    headers = []
    if show_index:
        headers.append("#")
    headers.extend(["标题/Title", "平台/Platform", "作者/Author", "链接/URL"])

    rows = []
    for i, item in enumerate(results, 1):
        row = []
        if show_index:
            row.append(str(i))
        row.append(truncate_text(item.get("title", ""), 40))
        row.append(truncate_text(item.get("platform", ""), 12))
        row.append(truncate_text(item.get("author", ""), 15))
        row.append(truncate_text(item.get("url", ""), 50))
        rows.append(row)

    return draw_table(headers, rows)


def format_result_detail(item, index=0):
    """
    格式化单条结果的详细信息。
    Format detailed info for a single result.

    Args:
        item: 单条结果 / Single result
        index: 序号 / Index

    Returns:
        str: 详细信息字符串 / Detail string
    """
    lines = []
    if index:
        lines.append(bold(f"  [{index}]"))
    lines.append(bold(f"  标题: {item.get('title', 'N/A')}"))
    lines.append(f"  平台: {cyan(item.get('platform', 'unknown'))}")
    lines.append(f"  作者: {item.get('author', 'unknown')}")
    lines.append(f"  时间: {item.get('timestamp', '')}")
    lines.append(f"  链接: {blue(item.get('url', ''))}")
    content = item.get("content", "")
    if content:
        lines.append(f"  摘要: {dim(content[:200])}")
    metadata = item.get("metadata", {})
    if metadata:
        meta_parts = [f"{k}={v}" for k, v in metadata.items() if v]
        if meta_parts:
            lines.append(f"  元数据: {dim(', '.join(meta_parts[:5]))}")
    return "\n".join(lines)


# ── 平台选择菜单 / Platform Selection Menu ─────────────────────────

# 平台信息 / Platform info
PLATFORM_REGISTRY = {
    "twitter": {"name": "Twitter/X", "icon": "T", "color": Colors.CYAN},
    "reddit": {"name": "Reddit", "icon": "R", "color": Colors.RED},
    "youtube": {"name": "YouTube", "icon": "Y", "color": Colors.RED},
    "github": {"name": "GitHub", "icon": "G", "color": Colors.WHITE},
    "bilibili": {"name": "Bilibili", "icon": "B", "color": Colors.CYAN},
    "zhihu": {"name": "知乎", "icon": "Z", "color": Colors.BLUE},
    "hackernews": {"name": "Hacker News", "icon": "H", "color": Colors.YELLOW},
    "medium": {"name": "Medium", "icon": "M", "color": Colors.WHITE},
}


def show_platform_menu(enabled_platforms=None):
    """
    显示平台选择菜单。
    Show platform selection menu.

    Args:
        enabled_platforms: 已启用的平台列表 / Enabled platform list

    Returns:
        str: 格式化菜单字符串 / Formatted menu string
    """
    lines = [
        bold("  ┌─────────────────────────────────────────┐"),
        bold("  │     OmniReach 平台选择 / Platform Select    │"),
        bold("  └─────────────────────────────────────────┘"),
        "",
    ]

    for key, info in PLATFORM_REGISTRY.items():
        enabled = enabled_platforms is None or key in enabled_platforms
        status = green("  ON ") if enabled else red(" OFF")
        icon = info["icon"]
        name = info["name"]
        lines.append(f"    [{icon}] {name:20s} {status}  ({key})")

    lines.append("")
    lines.append(dim("  提示: 使用 --platform 参数指定平台，如 --platform twitter,reddit"))
    lines.append(dim("  Tip: Use --platform flag, e.g. --platform twitter,reddit"))

    return "\n".join(lines)


# ── 进度条 / Progress Bar ──────────────────────────────────────────

def draw_progress(current, total, prefix="进度/Progress", width=30):
    """
    绘制终端进度条。
    Draw terminal progress bar.

    Args:
        current: 当前进度 / Current progress
        total: 总数 / Total
        prefix: 前缀文本 / Prefix text
        width: 进度条宽度 / Progress bar width

    Returns:
        str: 进度条字符串 / Progress bar string
    """
    if total == 0:
        pct = 100
    else:
        pct = int(current * 100 / total)
    filled = int(width * current / max(total, 1))
    bar = "█" * filled + "░" * (width - filled)
    return f"\r  {prefix}: [{green(bar)}] {pct}% ({current}/{total})"


# ── Banner / Logo ──────────────────────────────────────────────────

def show_banner():
    """
    显示OmniReach CLI的启动Banner。
    Show OmniReach CLI startup banner.
    """
    banner = f"""
{cyan('╔══════════════════════════════════════════════════════════╗')}
{cyan('║')}                                                          {cyan('║')}
{bold('║')}    {green('O')} {green('m')} {green('n')} {green('i')} {green('R')} {green('e')} {green('a')} {green('c')} {green('h')} {green('-')} {green('C')} {green('L')} {green('I')}  {bold('║')}
{bold('║')}    {dim('轻量级终端AI Agent多平台互联网信息触达引擎')}            {bold('║')}
{bold('║')}    {dim('Lightweight CLI Multi-Platform Info Engine')}        {bold('║')}
{cyan('║')}                                                          {cyan('║')}
{cyan('╚══════════════════════════════════════════════════════════╝')}
"""
    print(banner)
