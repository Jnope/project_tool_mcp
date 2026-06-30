import logging

from fastmcp import Context, FastMCP

from src.utils.client import tq_client
from src.utils.config import GET_ENV_LIST_URL

logger = logging.getLogger("mcp-for-tq")

def register_project_theme_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def get_env_list(
        ctx: Context = None,
    ) -> dict:
        """获取用户环境列表

        Returns:
            list:
                envStatus: 0:未启动，1:启动中，2:固化中，3:升级中，4:销毁中, 5:重启中，6:运行中,7:资源申请中,8:回滚中
        """
        if ctx:
            await ctx.info("正在获取环境列表")

        return await tq_client.get(GET_ENV_LIST_URL)
