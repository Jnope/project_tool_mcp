import logging

from fastmcp import FastMCP

from src.utils.log import setup_logging
from src.project_theme import register_project_theme_tools
from src.quartz import register_quartz_tools
from src.board import register_board_tools

logger = logging.getLogger("mcp-for-tq")

mcp = FastMCP(
    "mcp-for-tq",
    instructions="TQ 管理 MCP 工具 — 调用TQ API创建和执行项目、课题、任务、模拟盘",
)

register_project_theme_tools(mcp)
register_quartz_tools(mcp)
register_board_tools(mcp)


if __name__ == "__main__":
    setup_logging()
    mcp.run(transport="stdio")
