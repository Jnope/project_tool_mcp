import logging

from fastmcp import FastMCP, Context

from src.utils.config import GET_BOARD_LIST_URL, ADD_BOARD_THEMES_URL
from src.utils.client import tq_client

logger = logging.getLogger("mcp-for-tq")


def register_board_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def get_board_list(
        ctx: Context = None,
    ) -> dict:
        """获取看板列表

        查看看板列表，返回所有可访问的看板信息。
        """
        if ctx:
            await ctx.info("正在获取看板列表")

        return await tq_client.get(GET_BOARD_LIST_URL)

    @mcp.tool()
    async def add_board_theme(
        board_id: str,
        theme_id: str,
        ctx: Context = None,
    ) -> dict:
        """添加主题到看板

        Args:
            board_id: 看板UUID（必填）
            theme_id: 主题UUID（必填）
        """
        if not board_id or not board_id.strip():
            return {"success": False, "error": "看板ID不能为空"}

        if not theme_id or not theme_id.strip():
            return {"success": False, "error": "主题ID不能为空"}

        if ctx:
            await ctx.info(f"正在为看板 {board_id} 添加主题")

        payload: dict = {
            "boardId": board_id.strip(),
            "themeIds": [theme_id.strip()],
        }

        return await tq_client.post(ADD_BOARD_THEMES_URL, json=payload)

