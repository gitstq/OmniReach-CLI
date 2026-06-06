#!/usr/bin/env python3
"""
OmniReach-CLI - 轻量级终端AI Agent多平台互联网信息触达引擎
OmniReach-CLI - Lightweight CLI AI Agent Multi-Platform Internet Information Reach Engine

零外部依赖，纯标准库开发，Web scraping方式获取多平台内容。
Zero external dependencies, pure standard library, web scraping approach.

用法 / Usage:
    python omnireach.py search "关键词" --platform twitter,reddit --limit 10
    python omnireach.py trending --platform github,bilibili --limit 20
    python omnireach.py info --platform all
    python omnireach.py config --set proxy=http://127.0.0.1:7890
    python omnireach.py dashboard
"""

import argparse
import os
import sys
import time

# 确保项目根目录在路径中 / Ensure project root is in path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from src.config import Config
from src.processor import ContentProcessor
from src.exporter import Exporter
from src.llm import LLMClient
from src.ui.dashboard import (
    show_banner, show_platform_menu, format_results_table,
    format_result_detail, draw_progress, PLATFORM_REGISTRY,
    bold, green, yellow, red, cyan, dim,
)
from src.platforms.base import Colors

# ── 平台适配器注册 / Platform Adapter Registry ─────────────────────

def get_platform_adapters():
    """
    获取所有平台适配器实例的注册表。
    Get registry of all platform adapter instances.

    Returns:
        dict: 平台名 -> 适配器类映射 / Platform name -> adapter class mapping
    """
    from src.platforms.twitter import TwitterAdapter
    from src.platforms.reddit import RedditAdapter
    from src.platforms.youtube import YouTubeAdapter
    from src.platforms.github import GitHubAdapter
    from src.platforms.bilibili import BilibiliAdapter
    from src.platforms.zhihu import ZhihuAdapter
    from src.platforms.hackernews import HackerNewsAdapter
    from src.platforms.medium import MediumAdapter

    return {
        "twitter": TwitterAdapter,
        "reddit": RedditAdapter,
        "youtube": YouTubeAdapter,
        "github": GitHubAdapter,
        "bilibili": BilibiliAdapter,
        "zhihu": ZhihuAdapter,
        "hackernews": HackerNewsAdapter,
        "medium": MediumAdapter,
    }


# ── CLI命令处理 / CLI Command Handlers ─────────────────────────────

def cmd_search(args, config):
    """
    处理search命令。
    Handle the search command.

    Args:
        args: 命令行参数 / Command line arguments
        config: 配置对象 / Config object
    """
    query = args.query
    platforms = parse_platforms(args.platform, config)
    limit = args.limit
    export_fmt = args.export

    print(bold(f"\n  搜索 / Searching: \"{query}\""))
    print(f"  平台 / Platforms: {', '.join(platforms)}")
    print(f"  限制 / Limit: {limit}\n")

    adapters = get_platform_adapters()
    processor = ContentProcessor()
    all_results = []

    for i, platform_name in enumerate(platforms):
        if platform_name not in adapters:
            print(yellow(f"  [!] 未知平台 / Unknown platform: {platform_name}"))
            continue

        print(f"  {draw_progress(i, len(platforms), platform_name)}", end="", flush=True)

        try:
            adapter_cls = adapters[platform_name]
            adapter = adapter_cls(proxy=config.proxy, timeout=config.timeout)
            results = adapter.search(query, limit=limit)
            all_results.extend(results)
            print(f"\r  {green('✓')} {platform_name:15s} -> {len(results)} 条结果 / results")
        except Exception as e:
            print(f"\r  {red('✗')} {platform_name:15s} -> 失败 / failed: {e}")

    # 最终进度 / Final progress
    print(f"  {draw_progress(len(platforms), len(platforms), '完成/Done')}")

    # 后处理 / Post-processing
    all_results = processor.normalize_results(all_results)
    all_results = processor.deduplicate(all_results)

    # 关键词高亮 / Keyword highlighting
    if args.highlight:
        keywords = query.split()
        for item in all_results:
            item["title"] = processor.highlight_keywords(item["title"], keywords)
            item["content"] = processor.highlight_keywords(item["content"], keywords)

    # 显示结果 / Display results
    print(f"\n{bold(f'  共找到 {len(all_results)} 条结果 / Found {len(all_results)} results')}\n")
    if all_results:
        print(format_results_table(all_results))
        print()

        # 详细模式 / Verbose mode
        if args.verbose:
            for i, item in enumerate(all_results, 1):
                print(format_result_detail(item, i))
                print()

    # 导出 / Export
    if export_fmt:
        do_export(all_results, export_fmt, config, f"search_{query}")

    return all_results


def cmd_trending(args, config):
    """
    处理trending命令。
    Handle the trending command.

    Args:
        args: 命令行参数 / Command line arguments
        config: 配置对象 / Config object
    """
    platforms = parse_platforms(args.platform, config)
    limit = args.limit
    export_fmt = args.export

    print(bold(f"\n  获取热门 / Fetching trending"))
    print(f"  平台 / Platforms: {', '.join(platforms)}")
    print(f"  限制 / Limit: {limit}\n")

    adapters = get_platform_adapters()
    processor = ContentProcessor()
    all_results = []

    for i, platform_name in enumerate(platforms):
        if platform_name not in adapters:
            print(yellow(f"  [!] 未知平台 / Unknown platform: {platform_name}"))
            continue

        print(f"  {draw_progress(i, len(platforms), platform_name)}", end="", flush=True)

        try:
            adapter_cls = adapters[platform_name]
            adapter = adapter_cls(proxy=config.proxy, timeout=config.timeout)
            results = adapter.trending(limit=limit)
            all_results.extend(results)
            print(f"\r  {green('✓')} {platform_name:15s} -> {len(results)} 条结果 / results")
        except Exception as e:
            print(f"\r  {red('✗')} {platform_name:15s} -> 失败 / failed: {e}")

    print(f"  {draw_progress(len(platforms), len(platforms), '完成/Done')}")

    # 后处理 / Post-processing
    all_results = processor.normalize_results(all_results)
    all_results = processor.deduplicate(all_results)

    # 显示结果 / Display results
    print(f"\n{bold(f'  共找到 {len(all_results)} 条热门内容 / Found {len(all_results)} trending items')}\n")
    if all_results:
        print(format_results_table(all_results))
        print()

        if args.verbose:
            for i, item in enumerate(all_results, 1):
                print(format_result_detail(item, i))
                print()

    # 导出 / Export
    if export_fmt:
        do_export(all_results, export_fmt, config, "trending")

    return all_results


def cmd_info(args, config):
    """
    处理info命令，显示平台信息。
    Handle the info command, display platform information.

    Args:
        args: 命令行参数 / Command line arguments
        config: 配置对象 / Config object
    """
    platforms = parse_platforms(args.platform, config)

    print(bold("\n  OmniReach-CLI 平台信息 / Platform Info"))
    print(f"  版本 / Version: 0.1.0")
    print(f"  配置文件 / Config: {config.config_path}")
    print(f"  代理 / Proxy: {config.proxy or dim('未设置 / Not set')}")
    print(f"  超时 / Timeout: {config.timeout}s")
    print()

    # 显示平台菜单 / Show platform menu
    print(show_platform_menu(config.enabled_platforms))
    print()

    # 如果指定了具体平台，显示详细信息 / Show details for specific platforms
    if "all" not in platforms:
        adapters = get_platform_adapters()
        for name in platforms:
            if name in adapters:
                adapter = adapters[name](proxy=config.proxy, timeout=config.timeout)
                info = PLATFORM_REGISTRY.get(name, {})
                print(f"  {bold(info.get('name', name))}")
                print(f"    标识 / ID: {adapter.name}")
                print(f"    基础URL / Base URL: {adapter.base_url}")
                print(f"    状态 / Status: {green('已启用 / Enabled') if config.is_platform_enabled(name) else red('已禁用 / Disabled')}")
                print()

    # LLM状态 / LLM status
    llm_cfg = config.get("llm", {})
    if llm_cfg.get("enabled") and llm_cfg.get("api_key"):
        print(f"  LLM: {green('已配置 / Configured')} (model: {llm_cfg.get('model', 'N/A')})")
    else:
        print(f"  LLM: {dim('未配置 / Not configured')} (可选功能 / Optional)")


def cmd_config(args, config):
    """
    处理config命令，管理配置。
    Handle the config command, manage configuration.

    Args:
        args: 命令行参数 / Command line arguments
        config: 配置对象 / Config object
    """
    if args.set:
        # 设置配置值 / Set config value
        key, value = args.set.split("=", 1) if "=" in args.set else (args.set, "true")
        config.set(key, value)
        config.save()
        print(green(f"  配置已更新 / Config updated: {key} = {value}"))
        print(f"  配置文件 / Config file: {config.config_path}")

    elif args.get:
        # 获取配置值 / Get config value
        value = config.get(args.get)
        print(f"  {args.get} = {value}")

    elif args.list:
        # 列出所有配置 / List all config
        import json
        print(bold("\n  当前配置 / Current Configuration:"))
        print(json.dumps(config.all, indent=2, ensure_ascii=False))

    elif args.reset:
        # 重置配置 / Reset config
        if os.path.exists(config.config_path):
            os.remove(config.config_path)
            print(green(f"  配置已重置 / Config reset: {config.config_path}"))
        else:
            print(dim("  配置文件不存在 / Config file does not exist"))

    else:
        print(dim("  使用 --set, --get, --list 或 --reset 子命令"))
        print(dim("  Use --set, --get, --list, or --reset subcommand"))


def cmd_dashboard(args, config):
    """
    处理dashboard命令，启动交互式TUI仪表盘。
    Handle the dashboard command, launch interactive TUI dashboard.

    Args:
        args: 命令行参数 / Command line arguments
        config: 配置对象 / Config object
    """
    show_banner()
    print(show_platform_menu(config.enabled_platforms))
    print()

    print(bold("  交互式仪表盘 / Interactive Dashboard"))
    print(dim("  输入命令进行操作 / Enter commands to interact:"))
    print(f"    {cyan('search <关键词>')}  - 搜索内容 / Search content")
    print(f"    {cyan('trending')}         - 查看热门 / View trending")
    print(f"    {cyan('info')}             - 平台信息 / Platform info")
    print(f"    {cyan('export <格式>')}    - 导出上次结果 / Export last results")
    print(f"    {cyan('quit')}             - 退出 / Exit")
    print()

    last_results = []

    while True:
        try:
            prompt = f"{green('omnireach>')}"
            user_input = input(f"  {prompt} ").strip()

            if not user_input:
                continue

            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            argument = parts[1] if len(parts) > 1 else ""

            if command in ("quit", "exit", "q"):
                print(dim("\n  再见 / Goodbye!"))
                break

            elif command == "search" and argument:
                # 在仪表盘中执行搜索 / Execute search in dashboard
                args_obj = argparse.Namespace(
                    query=argument,
                    platform="all",
                    limit=10,
                    export=None,
                    highlight=True,
                    verbose=False,
                )
                last_results = cmd_search(args_obj, config)

            elif command == "trending":
                args_obj = argparse.Namespace(
                    platform="all",
                    limit=10,
                    export=None,
                    verbose=False,
                )
                last_results = cmd_trending(args_obj, config)

            elif command == "info":
                args_obj = argparse.Namespace(platform="all")
                cmd_info(args_obj, config)

            elif command == "export" and argument:
                if last_results:
                    do_export(last_results, argument, config, "dashboard_export")
                else:
                    print(yellow("  没有可导出的结果 / No results to export"))

            elif command == "help":
                print(f"    {cyan('search <关键词>')}  - 搜索内容 / Search content")
                print(f"    {cyan('trending')}         - 查看热门 / View trending")
                print(f"    {cyan('info')}             - 平台信息 / Platform info")
                print(f"    {cyan('export <格式>')}    - 导出上次结果 / Export last results")
                print(f"    {cyan('quit')}             - 退出 / Exit")

            else:
                print(yellow(f"  未知命令 / Unknown command: {command} (输入 help 查看帮助)"))

        except KeyboardInterrupt:
            print(dim("\n  再见 / Goodbye!"))
            break
        except EOFError:
            break


# ── 工具函数 / Utility Functions ──────────────────────────────────

def parse_platforms(platform_str, config):
    """
    解析平台参数字符串。
    Parse platform argument string.

    Args:
        platform_str: 平台字符串（逗号分隔或"all"）/ Platform string (comma-separated or "all")
        config: 配置对象 / Config object

    Returns:
        list: 平台名称列表 / Platform name list
    """
    all_platforms = list(get_platform_adapters().keys())

    if not platform_str or platform_str.lower() == "all":
        return config.enabled_platforms or all_platforms

    platforms = [p.strip().lower() for p in platform_str.split(",")]
    valid = [p for p in platforms if p in all_platforms]
    invalid = [p for p in platforms if p not in all_platforms]

    if invalid:
        print(yellow(f"  [!] 忽略未知平台 / Ignoring unknown platforms: {', '.join(invalid)}"))

    return valid if valid else config.enabled_platforms


def do_export(results, fmt, config, prefix="omnireach"):
    """
    执行结果导出。
    Execute result export.

    Args:
        results: 搜索结果 / Search results
        fmt: 导出格式 / Export format
        config: 配置对象 / Config object
        prefix: 文件名前缀 / Filename prefix
    """
    if not results:
        print(yellow("  没有可导出的结果 / No results to export"))
        return

    try:
        export_dir = config.get("export_dir", "./exports")
        exporter = Exporter(export_dir=export_dir)
        filepath = exporter.export(results, fmt=fmt, prefix=prefix)
        print(green(f"  导出成功 / Exported: {filepath}"))
    except ValueError as e:
        print(red(f"  导出失败 / Export failed: {e}"))
    except Exception as e:
        print(red(f"  导出失败 / Export failed: {e}"))


# ── 参数解析器 / Argument Parser ──────────────────────────────────

def build_parser():
    """
    构建命令行参数解析器。
    Build command line argument parser.

    Returns:
        argparse.ArgumentParser: 参数解析器 / Argument parser
    """
    parser = argparse.ArgumentParser(
        prog="omnireach",
        description=(
            "OmniReach-CLI - 轻量级终端AI Agent多平台互联网信息触达引擎\n"
            "Lightweight CLI AI Agent Multi-Platform Internet Information Reach Engine\n\n"
            "支持平台 / Supported Platforms: Twitter/X, Reddit, YouTube, GitHub, "
            "Bilibili, 知乎, Hacker News, Medium"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例 / Examples:\n"
            "  omnireach search \"AI agent\" --platform twitter,reddit --limit 10\n"
            "  omnireach trending --platform github,bilibili --limit 20\n"
            "  omnireach info --platform all\n"
            "  omnireach config --set proxy=http://127.0.0.1:7890\n"
            "  omnireach dashboard\n"
        ),
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令 / Available commands")

    # search 子命令 / search subcommand
    search_parser = subparsers.add_parser(
        "search", help="搜索内容 / Search content across platforms"
    )
    search_parser.add_argument(
        "query", type=str, help="搜索关键词 / Search query"
    )
    search_parser.add_argument(
        "--platform", "-p", type=str, default="all",
        help="目标平台，逗号分隔 / Target platforms, comma-separated (default: all)"
    )
    search_parser.add_argument(
        "--limit", "-l", type=int, default=10,
        help="每个平台的返回数量 / Results per platform (default: 10)"
    )
    search_parser.add_argument(
        "--export", "-e", type=str, default=None,
        choices=["json", "csv", "markdown", "md", "text", "txt"],
        help="导出格式 / Export format"
    )
    search_parser.add_argument(
        "--highlight", action="store_true", default=True,
        help="高亮搜索关键词 / Highlight search keywords (default: true)"
    )
    search_parser.add_argument(
        "--no-highlight", dest="highlight", action="store_false",
        help="不高亮关键词 / Don't highlight keywords"
    )
    search_parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="显示详细结果 / Show detailed results"
    )

    # trending 子命令 / trending subcommand
    trending_parser = subparsers.add_parser(
        "trending", help="获取热门内容 / Get trending content"
    )
    trending_parser.add_argument(
        "--platform", "-p", type=str, default="all",
        help="目标平台 / Target platforms (default: all)"
    )
    trending_parser.add_argument(
        "--limit", "-l", type=int, default=10,
        help="每个平台的返回数量 / Results per platform (default: 10)"
    )
    trending_parser.add_argument(
        "--export", "-e", type=str, default=None,
        choices=["json", "csv", "markdown", "md", "text", "txt"],
        help="导出格式 / Export format"
    )
    trending_parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="显示详细结果 / Show detailed results"
    )

    # info 子命令 / info subcommand
    info_parser = subparsers.add_parser(
        "info", help="显示平台和配置信息 / Show platform and config info"
    )
    info_parser.add_argument(
        "--platform", "-p", type=str, default="all",
        help="查看的平台 / Platforms to inspect (default: all)"
    )

    # config 子命令 / config subcommand
    config_parser = subparsers.add_parser(
        "config", help="管理配置 / Manage configuration"
    )
    config_group = config_parser.add_mutually_exclusive_group()
    config_group.add_argument(
        "--set", type=str, default=None,
        help="设置配置项 / Set config (e.g. --set proxy=http://127.0.0.1:7890)"
    )
    config_group.add_argument(
        "--get", type=str, default=None,
        help="获取配置项 / Get config value"
    )
    config_group.add_argument(
        "--list", action="store_true",
        help="列出所有配置 / List all config"
    )
    config_group.add_argument(
        "--reset", action="store_true",
        help="重置为默认配置 / Reset to default config"
    )

    # dashboard 子命令 / dashboard subcommand
    subparsers.add_parser(
        "dashboard", help="启动交互式TUI仪表盘 / Launch interactive TUI dashboard"
    )

    return parser


# ── 主入口 / Main Entry Point ───────────────────────────────────────

def main():
    """
    主入口函数。
    Main entry point function.
    """
    parser = build_parser()
    args = parser.parse_args()

    # 加载配置 / Load configuration
    config = Config()

    # 无命令时显示帮助 / Show help when no command
    if not args.command:
        parser.print_help()
        print()
        return

    # 分发命令 / Dispatch command
    try:
        if args.command == "search":
            cmd_search(args, config)
        elif args.command == "trending":
            cmd_trending(args, config)
        elif args.command == "info":
            cmd_info(args, config)
        elif args.command == "config":
            cmd_config(args, config)
        elif args.command == "dashboard":
            cmd_dashboard(args, config)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        print(f"\n{dim('  操作已取消 / Operation cancelled')}")
    except Exception as e:
        print(f"\n{red(f'  错误 / Error: {e}')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
