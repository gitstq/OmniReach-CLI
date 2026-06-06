<p align="center">
  <img src="https://img.shields.io/badge/Version-0.1.0-blue?style=flat-square" alt="Version" />
  <img src="https://img.shields.io/badge/Python-3.9+-green?style=flat-square" alt="Python" />
  <img src="https://img.shields.io/badge/License-MIT-orange?style=flat-square" alt="License" />
  <img src="https://img.shields.io/badge/Platforms-8-purple?style=flat-square" alt="Platforms" />
  <img src="https://img.shields.io/badge/Dependencies-Zero-success?style=flat-square" alt="Zero Dependencies" />
  <img src="https://img.shields.io/badge/OS-Cross%20Platform-informational?style=flat-square" alt="Cross Platform" />
</p>

<h1 align="center">🌐 OmniReach-CLI</h1>

<p align="center">
  <strong>轻量级终端AI Agent多平台互联网信息触达引擎</strong><br/>
  <em>Lightweight CLI AI Agent Multi-Platform Internet Information Reach Engine</em>
</p>

<p align="center">
  <a href="#-项目介绍--project-introduction">简体中文</a> •
  <a href="#-專案介紹--project-introduction-1">繁體中文</a> •
  <a href="#-project-introduction">English</a>
</p>

---

<a id="-项目介绍--project-introduction"></a>

## 🇨🇳 简体中文

### 🎉 项目介绍

**OmniReach-CLI** 是一款轻量级终端AI Agent多平台互联网信息触达引擎。它赋予AI Agent一双"慧眼"，能够从 **8大主流平台** 搜索和读取内容，**零API费用**，纯Web Scraping方式实现。

**解决的核心痛点**：
- 🔒 AI Agent无法直接访问互联网获取实时信息
- 💰 现有方案依赖昂贵的第三方API
- 🌐 多平台信息分散，缺乏统一采集入口
- 🛠️ 现有工具依赖复杂，部署门槛高

**自研差异化亮点**：
- ✅ **零外部依赖** — 纯Python标准库，无需pip install任何包
- ✅ **8大平台覆盖** — Twitter/X、Reddit、YouTube、GitHub、Bilibili、知乎、Hacker News、Medium
- ✅ **内置TUI仪表盘** — 美观的终端交互界面，彩色表格展示
- ✅ **智能内容处理** — 自动去重、关键词高亮、结构化提取
- ✅ **多格式导出** — JSON、CSV、Markdown、纯文本
- ✅ **可选LLM集成** — 支持OpenAI兼容API进行内容摘要
- ✅ **代理支持** — 完美适配中国大陆网络环境

### ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🌐 **多平台支持** | Twitter/X、Reddit、YouTube、GitHub、Bilibili、知乎、Hacker News、Medium |
| 🔍 **智能搜索** | 跨平台关键词搜索，统一结果格式 |
| 📈 **热门趋势** | 一键获取各平台热门/趋势内容 |
| 🎨 **TUI仪表盘** | ANSI彩色终端界面，交互式平台选择 |
| 📦 **多格式导出** | JSON / CSV / Markdown / 纯文本 |
| 🧠 **LLM摘要** | 可选集成LLM生成内容摘要 |
| 🔄 **自动去重** | 基于URL的智能去重机制 |
| 🌍 **代理支持** | HTTP/HTTPS代理，适配各种网络环境 |
| 📱 **跨平台** | Windows / macOS / Linux 全平台兼容 |
| ⚡ **零依赖** | 纯Python标准库，开箱即用 |

### 🚀 快速开始

**环境要求**：
- Python 3.9 或更高版本
- 无需安装任何第三方依赖

**安装步骤**：

```bash
# 克隆仓库
git clone https://github.com/gitstq/OmniReach-CLI.git
cd OmniReach-CLI

# 直接运行（无需安装依赖）
python omnireach.py --help
```

**基本用法**：

```bash
# 跨平台搜索
python omnireach.py search "AI agent" --platform twitter,reddit --limit 10

# 获取热门内容
python omnireach.py trending --platform github,bilibili --limit 20

# 查看平台信息
python omnireach.py info --platform all

# 搜索并导出为JSON
python omnireach.py search "Rust" --platform github --limit 5 --export json

# 启动交互式TUI仪表盘
python omnireach.py dashboard

# 配置代理（中国大陆用户推荐）
python omnireach.py config --set proxy=http://127.0.0.1:7890
```

### 📖 详细使用指南

#### 搜索命令

```bash
# 基本搜索
python omnireach.py search "关键词"

# 指定平台（逗号分隔）
python omnireach.py search "关键词" --platform twitter,reddit,youtube

# 限制结果数量
python omnireach.py search "关键词" --limit 20

# 导出结果
python omnireach.py search "关键词" --export json --output results.json
python omnireach.py search "关键词" --export csv --output results.csv
python omnireach.py search "关键词" --export markdown --output results.md
python omnireach.py search "关键词" --export text --output results.txt

# 启用LLM摘要（需配置API）
python omnireach.py search "关键词" --summarize
```

#### 热门趋势

```bash
# 获取所有平台热门
python omnireach.py trending

# 指定平台
python omnireach.py trending --platform hackernews,github

# 获取更多结果
python omnireach.py trending --limit 50
```

#### 配置管理

```bash
# 查看当前配置
python omnireach.py config --list

# 设置代理
python omnireach.py config --set proxy=http://127.0.0.1:7890

# 设置超时时间
python omnireach.py config --set timeout=30

# 启用/禁用平台
python omnireach.py config --set platforms.twitter.enabled=false

# 重置配置
python omnireach.py config --reset
```

#### LLM集成（可选）

通过环境变量配置LLM：

```bash
export OMNIREACH_LLM_API_KEY="your-api-key"
export OMNIREACH_LLM_BASE_URL="https://api.openai.com/v1"
export OMNIREACH_LLM_MODEL="gpt-3.5-turbo"
```

或通过配置文件 `~/.omnireach/config.json`：

```json
{
  "llm": {
    "api_key": "your-api-key",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-3.5-turbo",
    "enabled": true
  }
}
```

### 💡 设计思路与迭代规划

**设计理念**：
- **极简主义** — 零外部依赖，一个Python文件即可运行
- **统一接口** — 所有平台适配器实现相同的 `search()` 和 `trending()` 接口
- **可扩展性** — 新增平台只需创建一个适配器文件并注册
- **隐私优先** — 所有数据本地处理，不上传任何用户信息

**技术选型原因**：
- Python标准库：确保零依赖、最大兼容性
- urllib + html.parser：避免requests/beautifulsoup等外部依赖
- ANSI转义码：实现终端彩色输出无需额外库

**后续迭代计划**：
- [ ] 🔄 支持更多平台（抖音、Instagram、LinkedIn等）
- [ ] 📊 搜索结果数据分析与可视化
- [ ] 🤖 更深度的LLM集成（自动分类、情感分析）
- [ ] 📡 实时监控模式（定时抓取特定关键词）
- [ ] 🔌 插件系统（自定义平台适配器）
- [ ] 🌐 Web界面版本

### 📦 打包与部署指南

本项目为CLI工具类项目，无需打包发布。

**直接使用**：
```bash
git clone https://github.com/gitstq/OmniReach-CLI.git
cd OmniReach-CLI
python omnireach.py --help
```

**安装为全局命令（可选）**：
```bash
cd OmniReach-CLI
pip install -e .
omnireach --help
```

### 🤝 贡献指南

欢迎贡献代码！请遵循以下规范：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

**提交规范**：遵循 Angular Commit Convention
- `feat:` 新增功能
- `fix:` 修复问题
- `docs:` 文档更新
- `refactor:` 代码重构
- `style:` 代码格式调整
- `test:` 测试相关
- `chore:` 构建/工具链相关

### 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源。

---

<a id="-專案介紹--project-introduction-1"></a>

## 🇹🇼 繁體中文

### 🎉 專案介紹

**OmniReach-CLI** 是一款輕量級終端AI Agent多平台網際網路資訊觸達引擎。它賦予AI Agent一雙「慧眼」，能夠從 **8大主流平台** 搜尋和讀取內容，**零API費用**，純Web Scraping方式實現。

**解決的核心痛點**：
- 🔒 AI Agent無法直接存取網際網路獲取即時資訊
- 💰 現有方案依賴昂貴的第三方API
- 🌐 多平台資訊分散，缺乏統一採集入口
- 🛠️ 現有工具依賴複雜，部署門檻高

**自研差異化亮點**：
- ✅ **零外部依賴** — 純Python標準庫，無需pip install任何套件
- ✅ **8大平台覆蓋** — Twitter/X、Reddit、YouTube、GitHub、Bilibili、知乎、Hacker News、Medium
- ✅ **內建TUI儀表板** — 美觀的終端互動介面，彩色表格展示
- ✅ **智慧內容處理** — 自動去重、關鍵字高亮、結構化提取
- ✅ **多格式匯出** — JSON、CSV、Markdown、純文字
- ✅ **可選LLM整合** — 支援OpenAI相容API進行內容摘要
- ✅ **代理支援** — 完美適配中國大陸網路環境

### ✨ 核心特性

| 特性 | 說明 |
|------|------|
| 🌐 **多平台支援** | Twitter/X、Reddit、YouTube、GitHub、Bilibili、知乎、Hacker News、Medium |
| 🔍 **智慧搜尋** | 跨平台關鍵字搜尋，統一結果格式 |
| 📈 **熱門趨勢** | 一鍵獲取各平台熱門/趨勢內容 |
| 🎨 **TUI儀表板** | ANSI彩色終端介面，互動式平台選擇 |
| 📦 **多格式匯出** | JSON / CSV / Markdown / 純文字 |
| 🧠 **LLM摘要** | 可選整合LLM生成內容摘要 |
| 🔄 **自動去重** | 基於URL的智慧去重機制 |
| 🌍 **代理支援** | HTTP/HTTPS代理，適配各種網路環境 |
| 📱 **跨平台** | Windows / macOS / Linux 全平台相容 |
| ⚡ **零依賴** | 純Python標準庫，開箱即用 |

### 🚀 快速開始

**環境要求**：
- Python 3.9 或更高版本
- 無需安裝任何第三方依賴

**安裝步驟**：

```bash
# 克隆倉庫
git clone https://github.com/gitstq/OmniReach-CLI.git
cd OmniReach-CLI

# 直接運行（無需安裝依賴）
python omnireach.py --help
```

**基本用法**：

```bash
# 跨平台搜尋
python omnireach.py search "AI agent" --platform twitter,reddit --limit 10

# 獲取熱門內容
python omnireach.py trending --platform github,bilibili --limit 20

# 查看平台資訊
python omnireach.py info --platform all

# 搜尋並匯出為JSON
python omnireach.py search "Rust" --platform github --limit 5 --export json

# 啟動互動式TUI儀表板
python omnireach.py dashboard

# 設定代理（中國大陸使用者推薦）
python omnireach.py config --set proxy=http://127.0.0.1:7890
```

### 📖 詳細使用指南

#### 搜尋命令

```bash
# 基本搜尋
python omnireach.py search "關鍵字"

# 指定平台（逗號分隔）
python omnireach.py search "關鍵字" --platform twitter,reddit,youtube

# 限制結果數量
python omnireach.py search "關鍵字" --limit 20

# 匯出結果
python omnireach.py search "關鍵字" --export json --output results.json
python omnireach.py search "關鍵字" --export csv --output results.csv
python omnireach.py search "關鍵字" --export markdown --output results.md
python omnireach.py search "關鍵字" --export text --output results.txt

# 啟用LLM摘要（需設定API）
python omnireach.py search "關鍵字" --summarize
```

#### 熱門趨勢

```bash
# 獲取所有平台熱門
python omnireach.py trending

# 指定平台
python omnireach.py trending --platform hackernews,github

# 獲取更多結果
python omnireach.py trending --limit 50
```

#### 設定管理

```bash
# 查看當前設定
python omnireach.py config --list

# 設定代理
python omnireach.py config --set proxy=http://127.0.0.1:7890

# 設定逾時時間
python omnireach.py config --set timeout=30

# 啟用/停用平台
python omnireach.py config --set platforms.twitter.enabled=false

# 重置設定
python omnireach.py config --reset
```

#### LLM整合（可選）

透過環境變數設定LLM：

```bash
export OMNIREACH_LLM_API_KEY="your-api-key"
export OMNIREACH_LLM_BASE_URL="https://api.openai.com/v1"
export OMNIREACH_LLM_MODEL="gpt-3.5-turbo"
```

或透過設定檔 `~/.omnireach/config.json`：

```json
{
  "llm": {
    "api_key": "your-api-key",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-3.5-turbo",
    "enabled": true
  }
}
```

### 💡 設計思路與迭代規劃

**設計理念**：
- **極簡主義** — 零外部依賴，一個Python檔案即可運行
- **統一介面** — 所有平台適配器實現相同的 `search()` 和 `trending()` 介面
- **可擴展性** — 新增平台只需建立一個適配器檔案並註冊
- **隱私優先** — 所有資料本地處理，不上傳任何使用者資訊

**後續迭代計畫**：
- [ ] 🔄 支援更多平台（抖音、Instagram、LinkedIn等）
- [ ] 📊 搜尋結果資料分析與視覺化
- [ ] 🤖 更深度的LLM整合（自動分類、情感分析）
- [ ] 📡 即時監控模式（定時抓取特定關鍵字）
- [ ] 🔌 插件系統（自訂平台適配器）
- [ ] 🌐 Web介面版本

### 📦 打包與部署指南

本專案為CLI工具類專案，無需打包發佈。

**直接使用**：
```bash
git clone https://github.com/gitstq/OmniReach-CLI.git
cd OmniReach-CLI
python omnireach.py --help
```

**安裝為全域命令（可選）**：
```bash
cd OmniReach-CLI
pip install -e .
omnireach --help
```

### 🤝 貢獻指南

歡迎貢獻程式碼！請遵循以下規範：

1. Fork 本倉庫
2. 建立特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 建立Pull Request

**提交規範**：遵循 Angular Commit Convention
- `feat:` 新增功能
- `fix:` 修復問題
- `docs:` 文件更新
- `refactor:` 程式碼重構
- `style:` 程式碼格式調整
- `test:` 測試相關
- `chore:` 建構/工具鏈相關

### 📄 開源協議

本專案基於 [MIT License](LICENSE) 開源。

---

<a id="-project-introduction"></a>

## 🇬🇧 English

### 🎉 Project Introduction

**OmniReach-CLI** is a lightweight terminal AI Agent multi-platform internet information reach engine. It gives AI Agents "eyes to see" across **8 major platforms**, searching and reading content with **zero API costs** through pure web scraping.

**Core Problems Solved**:
- 🔒 AI Agents cannot directly access the internet for real-time information
- 💰 Existing solutions rely on expensive third-party APIs
- 🌐 Information is scattered across platforms with no unified collection entry point
- 🛠️ Existing tools have complex dependencies and high deployment barriers

**Self-Developed Differentiation Highlights**:
- ✅ **Zero External Dependencies** — Pure Python standard library, no pip install needed
- ✅ **8 Platform Coverage** — Twitter/X, Reddit, YouTube, GitHub, Bilibili, Zhihu, Hacker News, Medium
- ✅ **Built-in TUI Dashboard** — Beautiful terminal interactive interface with colored tables
- ✅ **Smart Content Processing** — Auto-deduplication, keyword highlighting, structured extraction
- ✅ **Multi-format Export** — JSON, CSV, Markdown, Plain Text
- ✅ **Optional LLM Integration** — OpenAI-compatible API for content summarization
- ✅ **Proxy Support** — Perfectly adapts to various network environments

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🌐 **Multi-Platform** | Twitter/X, Reddit, YouTube, GitHub, Bilibili, Zhihu, Hacker News, Medium |
| 🔍 **Smart Search** | Cross-platform keyword search with unified result format |
| 📈 **Trending Content** | One-click access to trending/hot content from each platform |
| 🎨 **TUI Dashboard** | ANSI colored terminal UI with interactive platform selection |
| 📦 **Multi-Format Export** | JSON / CSV / Markdown / Plain Text |
| 🧠 **LLM Summary** | Optional LLM integration for content summarization |
| 🔄 **Auto Dedup** | URL-based intelligent deduplication mechanism |
| 🌍 **Proxy Support** | HTTP/HTTPS proxy for various network environments |
| 📱 **Cross-Platform** | Windows / macOS / Linux compatible |
| ⚡ **Zero Dependencies** | Pure Python standard library, ready to use |

### 🚀 Quick Start

**Requirements**:
- Python 3.9 or higher
- No third-party dependencies needed

**Installation**:

```bash
# Clone the repository
git clone https://github.com/gitstq/OmniReach-CLI.git
cd OmniReach-CLI

# Run directly (no dependency installation needed)
python omnireach.py --help
```

**Basic Usage**:

```bash
# Cross-platform search
python omnireach.py search "AI agent" --platform twitter,reddit --limit 10

# Get trending content
python omnireach.py trending --platform github,bilibili --limit 20

# View platform info
python omnireach.py info --platform all

# Search and export as JSON
python omnireach.py search "Rust" --platform github --limit 5 --export json

# Launch interactive TUI dashboard
python omnireach.py dashboard

# Configure proxy
python omnireach.py config --set proxy=http://127.0.0.1:7890
```

### 📖 Detailed Usage Guide

#### Search Command

```bash
# Basic search
python omnireach.py search "keyword"

# Specify platforms (comma-separated)
python omnireach.py search "keyword" --platform twitter,reddit,youtube

# Limit results
python omnireach.py search "keyword" --limit 20

# Export results
python omnireach.py search "keyword" --export json --output results.json
python omnireach.py search "keyword" --export csv --output results.csv
python omnireach.py search "keyword" --export markdown --output results.md
python omnireach.py search "keyword" --export text --output results.txt

# Enable LLM summary (requires API configuration)
python omnireach.py search "keyword" --summarize
```

#### Trending Content

```bash
# Get trending from all platforms
python omnireach.py trending

# Specify platforms
python omnireach.py trending --platform hackernews,github

# Get more results
python omnireach.py trending --limit 50
```

#### Configuration Management

```bash
# View current config
python omnireach.py config --list

# Set proxy
python omnireach.py config --set proxy=http://127.0.0.1:7890

# Set timeout
python omnireach.py config --set timeout=30

# Enable/disable platforms
python omnireach.py config --set platforms.twitter.enabled=false

# Reset config
python omnireach.py config --reset
```

#### LLM Integration (Optional)

Configure via environment variables:

```bash
export OMNIREACH_LLM_API_KEY="your-api-key"
export OMNIREACH_LLM_BASE_URL="https://api.openai.com/v1"
export OMNIREACH_LLM_MODEL="gpt-3.5-turbo"
```

Or via config file `~/.omnireach/config.json`:

```json
{
  "llm": {
    "api_key": "your-api-key",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-3.5-turbo",
    "enabled": true
  }
}
```

### 💡 Design Philosophy & Roadmap

**Design Principles**:
- **Minimalism** — Zero external dependencies, runs with a single Python file
- **Unified Interface** — All platform adapters implement the same `search()` and `trending()` interface
- **Extensibility** — Add new platforms by creating an adapter file and registering it
- **Privacy First** — All data processed locally, no user information uploaded

**Roadmap**:
- [ ] 🔄 More platforms (TikTok, Instagram, LinkedIn, etc.)
- [ ] 📊 Search result data analysis & visualization
- [ ] 🤖 Deeper LLM integration (auto-classification, sentiment analysis)
- [ ] 📡 Real-time monitoring mode (scheduled keyword scraping)
- [ ] 🔌 Plugin system (custom platform adapters)
- [ ] 🌐 Web interface version

### 📦 Packaging & Deployment

This is a CLI tool project — no packaging or release needed.

**Direct Usage**:
```bash
git clone https://github.com/gitstq/OmniReach-CLI.git
cd OmniReach-CLI
python omnireach.py --help
```

**Install as Global Command (Optional)**:
```bash
cd OmniReach-CLI
pip install -e .
omnireach --help
```

### 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

**Commit Convention**: Follow Angular Commit Convention
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation update
- `refactor:` Code refactoring
- `style:` Code style adjustment
- `test:` Test related
- `chore:` Build/toolchain related

### 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">gitstq</a>
</p>
