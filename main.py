import logging

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession

from src.utils.config import CREATE_PROJECT_URL, ADD_PROJECT_THEME_URL
from src.utils.client import tq_client
from src.utils.log import setup_logging

logger = logging.getLogger("mcp-for-tq")

mcp = FastMCP(
    "mcp-for-tq",
    instructions="TQ 管理 MCP 工具 — 调用TQ API创建和执行项目、课题、任务、模拟盘",
)


@mcp.tool()
async def create_project(
    project_name: str,
    comment: str = "",
    path: str = "",
    ctx: Context[ServerSession, None] = None,
) -> dict:
    """创建研究项目

    Args:
        project_name: 项目名称（必填，不能为空）
        comment: 项目备注/描述，默认为空
        path: 项目路径（包含项目文件夹），默认为空
    """
    if not project_name or not project_name.strip():
        return {"success": False, "error": "项目名不能为空"}

    if not path or not path.strip():
        path = project_name

    if ctx:
        await ctx.info(f"正在创建项目: {project_name}")

    payload = {
        "projectName": project_name.strip(),
        "comment": comment,
        "path": path,
    }

    return await tq_client.post(CREATE_PROJECT_URL, json=payload)


@mcp.tool()
async def add_project_theme(
    project_id: str,
    name: str,
    type: int,
    comment: str = "",
    ctx: Context[ServerSession, None] = None,
) -> dict:
    """为项目新增主题（策略/因子/通用）

    Args:
        project_id: 所属项目ID（必填）
        name: 主题名称（必填，不能为空）
        type: 主题类型：0=策略，1=因子，2=通用（必填）
        comment: 主题备注/描述，默认为空
    """
    if not project_id or not project_id.strip():
        return {"success": False, "error": "项目ID不能为空"}
    if not name or not name.strip():
        return {"success": False, "error": "主题名不能为空"}
    if type not in (0, 1, 2):
        return {"success": False, "error": "主题类型必须为 0(策略)、1(因子) 或 2(通用)"}

    if ctx:
        await ctx.info(f"正在为项目 {project_id} 创建主题: {name}")

    payload = {
        "projectId": project_id.strip(),
        "name": name.strip(),
        "type": type,
        "comment": comment,
    }

    return await tq_client.post(ADD_PROJECT_THEME_URL, json=payload)


if __name__ == "__main__":
    setup_logging()
    mcp.run(transport="stdio")
