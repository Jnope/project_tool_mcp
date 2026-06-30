import logging

from fastmcp import FastMCP, Context

from src.utils.config import (
    CREATE_PROJECT_URL,
    ADD_PROJECT_THEME_URL,
    GET_PROJECT_LIST_URL,
    GET_PROJECT_THEME_LIST_URL,
    SET_THEME_RUN_PARAM_URL,
    EXECUTE_THEME_URL,
)
from src.utils.client import tq_client

logger = logging.getLogger("mcp-for-tq")


def register_project_theme_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def get_project_list(
        name: str = "",
        page_num: int = 1,
        page_size: int = 10,
        ctx: Context = None,
    ) -> dict:
        """获取用户研究项目列表（分页）

        Args:
            name: 项目名称关键词（模糊搜索），默认为空（查全部）
            page_num: 页码，从1开始，默认1
            page_size: 每页条数，默认10

        Returns:
            uuid: 项目uuid
        """
        if page_num < 1:
            page_num = 1
        if page_size < 1:
            page_size = 10

        if ctx:
            await ctx.info(f"正在查询项目列表: 第{page_num}页, 每页{page_size}条")

        payload = {
            "name": name,
            "pageNum": page_num,
            "pageSize": page_size,
        }

        return await tq_client.post(GET_PROJECT_LIST_URL, json=payload)

    @mcp.tool()
    async def create_project(
        project_name: str,
        comment: str = "",
        ctx: Context = None,
    ) -> dict:
        """创建研究项目

        Args:
            project_name: 项目名称（必填，不能为空）
            comment: 项目备注/描述，默认为空
        """
        if not project_name or not project_name.strip():
            return {"success": False, "error": "项目名不能为空"}

        if ctx:
            await ctx.info(f"正在创建项目: {project_name}")

        payload = {
            "projectName": project_name.strip(),
            "comment": comment,
            "path": project_name,
        }

        return await tq_client.post(CREATE_PROJECT_URL, json=payload)

    @mcp.tool()
    async def add_project_theme(
        project_id: str,
        name: str,
        type: int,
        comment: str = "",
        ctx: Context = None,
    ) -> dict:
        """为研究项目新增主题（策略/因子/通用）

        Args:
            project_id: 所属项目uuid（必填，可通过 get_project_list 获取）
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

    @mcp.tool()
    async def get_project_theme_list(
        project_id: str,
        name: str = "",
        type: int = -1,
        page_num: int = 1,
        page_size: int = 10,
        ctx: Context = None,
    ) -> dict:
        """获取项目下的主题列表（分页）

        Args:
            project_id: 项目uuid（必填，可通过 get_project_list 获取）
            name: 主题名称关键词（模糊搜索），默认为空（查全部）
            type: 主题类型筛选：0=策略，1=因子，2=通用；默认-1表示不筛选
            page_num: 页码，从1开始，默认1
            page_size: 每页条数，默认10

        Returns:
            pageInfo:
                list:
                    runStatus: 0：未执行，1：执行中，2：执行失败，3：超时，4：等待中，5：执行成功
        """
        if not project_id or not project_id.strip():
            return {"success": False, "error": "项目ID不能为空"}
        if page_num < 1:
            page_num = 1
        if page_size < 1:
            page_size = 10

        if ctx:
            await ctx.info(f"正在查询项目 {project_id} 的主题列表: 第{page_num}页, 每页{page_size}条")

        payload: dict = {
            "projectId": project_id.strip(),
            "name": name.strip(),
            "type": None if type == -1 else type,
            "pageNum": page_num,
            "pageSize": page_size,
        }

        return await tq_client.post(GET_PROJECT_THEME_LIST_URL, json=payload)

    @mcp.tool()
    async def set_theme_run_param(
        theme_id: str,
        lab: int,
        cmd: str = "",
        env_info: str = "",
        ctx: Context = None,
    ) -> dict:
        """设置主题执行参数

        Args:
            theme_id: 主题uuid（必填，可通过 get_project_theme_list 获取）
            lab: 执行环境ID（必填，可通过 get_env_list 获取）
            cmd: 执行命令，默认为空
            env_info: 环境信息，默认为空
        """
        if not theme_id or not theme_id.strip():
            return {"success": False, "error": "主题ID不能为空"}

        if not lab:
            return {"success": False, "error": "环境不能为空"}

        if not cmd or not cmd.strip():
            return {"success": False, "error": "命令不能为空"}

        if ctx:
            await ctx.info(f"正在设置主题 {theme_id} 的执行参数")

        payload = {
            "themeId": theme_id.strip(),
            "lab": lab,
            "cmd": cmd.strip(),
            "envInfo": env_info,
        }

        return await tq_client.post(SET_THEME_RUN_PARAM_URL, json=payload)

    @mcp.tool()
    async def execute_theme(
        theme_id: str,
        ctx: Context = None,
    ) -> dict:
        """执行主题

        Args:
            theme_id: 主题uuid（必填，可通过 get_project_theme_list 获取）
        """
        if not theme_id or not theme_id.strip():
            return {"success": False, "error": "主题ID不能为空"}

        if ctx:
            await ctx.info(f"正在执行主题: {theme_id}")

        params = {"themeId": theme_id.strip()}

        return await tq_client.get(EXECUTE_THEME_URL, params=params)

    
