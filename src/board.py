import logging

from fastmcp import FastMCP, Context

from src.utils.config import GET_BOARD_LIST_URL, ADD_BOARD_THEMES_URL, CREATE_BOARD_URL
from src.utils.client import tq_client

logger = logging.getLogger("mcp-for-tq")


def register_board_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def create_board(
        name: str,
        type: int = 0,
        comment: str = "",
        ctx: Context = None,
    ) -> dict:
        """创建看板

        Args:
            name: 看板名称（必填，不能为空）
            type: 看板类型：0=策略，1=因子，2=通用，默认0
            comment: 看板备注/描述，默认为空
        """
        if not name or not name.strip():
            return {"success": False, "error": "看板名不能为空"}
        if type not in (0, 1, 2):
            return {"success": False, "error": "看板类型必须为 0(策略)、1(因子) 或 2(通用)"}

        if ctx:
            await ctx.info(f"正在创建看板: {name}")

        payload = {
            "name": name.strip(),
            "type": type,
            "comment": comment,
        }

        return await tq_client.post(CREATE_BOARD_URL, json=payload)

    @mcp.tool()
    async def get_board_list(
        ctx: Context = None,
    ) -> dict:
        """获取看板列表

        Returns:
            list:
                type: 0：策略; 1: 因子; 2: 通用
        """
        if ctx:
            await ctx.info("正在获取看板列表")

        return await tq_client.get(GET_BOARD_LIST_URL)

    @mcp.tool()
    async def add_board_theme(
        board_id: str,
        quartz_id: str,
        theme_id: str,
        ctx: Context = None,
    ) -> dict:
        """添加定时任务下的主题到看板

        Args:
            board_id: 看板UUID（必填，可通过 get_board_list 获取）
            quartz_id: 定时任务jobKey（必填，可通过 get_quartz_list 获取）
            theme_id: 主题UUID（必填，可通过 get_quartz_themes 获取）
        """
        if not board_id or not board_id.strip():
            return {"success": False, "error": "看板ID不能为空"}

        if not quartz_id or not quartz_id.strip():
            return {"success": False, "error": "定时任务uuid不能为空"}

        if not theme_id or not theme_id.strip():
            return {"success": False, "error": "主题ID不能为空"}

        if ctx:
            await ctx.info(f"正在为看板 {board_id} 添加主题")

        payload: dict = {
            "boardId": board_id.strip(),
            "quartzId": quartz_id.strip(),
            "themeIds": [theme_id.strip()],
        }

        return await tq_client.post(ADD_BOARD_THEMES_URL, json=payload)

