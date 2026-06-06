"""
LLM集成模块 / LLM Integration Module

可选的LLM摘要生成，支持OpenAI兼容API。
Optional LLM summarization, supports OpenAI-compatible API.

通过环境变量或配置文件设置API密钥和端点。
Configure API key and endpoint via environment variables or config file.
非强制依赖，不配置也能正常使用核心功能。
Non-mandatory dependency; core features work without configuration.
"""

import json
import os
import urllib.request
import urllib.error


class LLMClient:
    """
    LLM客户端。
    LLM Client.

    支持OpenAI兼容API的轻量级客户端。
    Lightweight client for OpenAI-compatible APIs.
    """

    def __init__(self, api_key="", base_url="https://api.openai.com/v1",
                 model="gpt-3.5-turbo", max_tokens=500, timeout=30):
        """
        初始化LLM客户端。
        Initialize LLM client.

        Args:
            api_key: API密钥 / API key
            base_url: API基础URL / API base URL
            model: 模型名称 / Model name
            max_tokens: 最大生成token数 / Max generation tokens
            timeout: 请求超时 / Request timeout
        """
        self.api_key = api_key or os.environ.get("OMNIREACH_LLM_API_KEY", "")
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.max_tokens = max_tokens
        self.timeout = timeout
        self._available = bool(self.api_key)

    @property
    def available(self):
        """LLM是否可用 / Whether LLM is available"""
        return self._available

    def summarize(self, text, max_length=200):
        """
        使用LLM生成文本摘要。
        Generate text summary using LLM.

        Args:
            text: 原始文本 / Original text
            max_length: 摘要最大长度 / Maximum summary length

        Returns:
            str: 摘要文本，不可用时返回截断文本 / Summary text, or truncated text if unavailable
        """
        if not self._available or not text:
            # LLM不可用时，返回简单截断 / Return simple truncation when LLM unavailable
            if text and len(text) > max_length:
                return text[:max_length] + "..."
            return text or ""

        prompt = (
            f"请用简洁的中文总结以下内容，不超过{max_length}个字符：\n\n"
            f"Please summarize the following content concisely in Chinese, "
            f"no more than {max_length} characters:\n\n"
            f"{text[:2000]}"
        )

        try:
            response = self._chat(prompt)
            return response.strip() if response else text[:max_length] + "..."
        except Exception as e:
            # 失败时回退到截断 / Fallback to truncation on failure
            return text[:max_length] + "..."

    def _chat(self, prompt):
        """
        发送聊天请求到OpenAI兼容API。
        Send chat request to OpenAI-compatible API.

        Args:
            prompt: 提示词 / Prompt

        Returns:
            str: 模型回复 / Model response

        Raises:
            ConnectionError: API请求失败 / API request failed
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一个内容摘要助手。请简洁准确地总结内容。"},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": self.max_tokens,
            "temperature": 0.3,
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        # 代理支持 / Proxy support
        proxy = os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY") or ""
        if proxy:
            proxy_handler = urllib.request.ProxyHandler({
                "http": proxy,
                "https": proxy,
            })
            opener = urllib.request.build_opener(proxy_handler)
        else:
            opener = urllib.request.build_opener()

        try:
            with opener.open(req, timeout=self.timeout) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                choices = result.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
                return ""
        except urllib.error.HTTPError as e:
            raise ConnectionError(f"LLM API HTTP错误: {e.code} {e.reason}")
        except urllib.error.URLError as e:
            raise ConnectionError(f"LLM API连接错误: {e.reason}")
        except (json.JSONDecodeError, KeyError) as e:
            raise ConnectionError(f"LLM API响应解析失败: {e}")

    def batch_summarize(self, items, content_key="content", summary_key="summary"):
        """
        批量生成摘要。
        Batch generate summaries.

        Args:
            items: 结果列表 / Result list
            content_key: 内容字段名 / Content field name
            summary_key: 摘要字段名 / Summary field name

        Returns:
            list: 添加了摘要字段的结果列表 / Result list with summary field added
        """
        if not self._available:
            return items

        for item in items:
            content = item.get(content_key, "")
            if content:
                item[summary_key] = self.summarize(content)
            else:
                item[summary_key] = ""
        return items

    def __repr__(self):
        status = "available" if self._available else "unavailable"
        return f"<LLMClient(model={self.model}, status={status})>"
