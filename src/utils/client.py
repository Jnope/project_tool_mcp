import logging
from typing import Any

import httpx

from src.utils.config import JUPYTER_TOKEN

logger = logging.getLogger("mcp-for-tq")

ERROR_MESSAGES = {
    1: "调用错误",
    2: "无权限",
    302001: "认证失败",
}


class TqClient:
    """TQ后端统一HTTP客户端，自动携带jupyterToken并解析ResultEntity响应。

    code: 0=成功, 1=调用错误, 2=无权限, 302001=认证失败
    """

    def __init__(self, token: str = JUPYTER_TOKEN, timeout: int = 60) -> None:
        self._headers = {
            "Content-Type": "application/json",
            "jupyterToken": token,
        }
        self._timeout = timeout

    def _parse_result(self, result: dict[str, Any]) -> dict:
        code = result.get("code", -1)
        message = result.get("message", "")
        data = result.get("data")

        if code == 0:
            return {"success": True, "data": data}

        error_desc = ERROR_MESSAGES.get(code, f"未知错误码 {code}")
        error_msg = f"{error_desc}: {message}" if message else error_desc
        logger.error(f"TQ后端返回错误: code={code}, message={message}")
        return {"success": False, "error": error_msg, "code": code}

    def _handle_error(self, e: Exception) -> dict:
        if isinstance(e, httpx.HTTPStatusError):
            logger.error(f"HTTP错误: {e}")
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
            }
        logger.error(f"请求失败: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

    async def _request(
        self,
        method: str,
        url: str,
        *,
        json: dict | None = None,
        params: dict | None = None,
    ) -> dict:
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.request(
                    method, url, json=json, params=params, headers=self._headers
                )
                resp.raise_for_status()
                result = resp.json()
            return self._parse_result(result)
        except Exception as e:
            return self._handle_error(e)

    async def get(
        self, url: str, *, params: dict | None = None
    ) -> dict:
        return await self._request("GET", url, params=params)

    async def post(
        self, url: str, *, json: dict | None = None
    ) -> dict:
        return await self._request("POST", url, json=json)

    async def delete(
        self, url: str, *, params: dict | None = None
    ) -> dict:
        return await self._request("DELETE", url, params=params)

    async def put(
        self, url: str, *, json: dict | None = None
    ) -> dict:
        return await self._request("PUT", url, json=json)


tq_client = TqClient()
