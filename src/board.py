import logging

from fastmcp import FastMCP, Context

from src.utils.config import GET_BOARD_LIST_URL
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