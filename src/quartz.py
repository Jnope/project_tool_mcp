import logging

from fastmcp import FastMCP, Context

from src.utils.config import (
    GET_QUARTZ_LIST_URL,
    CREATE_QUARTZ_URL,
    ADD_QUARTZ_THEMES_URL,
    START_QUARTZ_URL,
)
from src.utils.client import tq_client

logger = logging.getLogger("mcp-for-tq")


def register_quartz_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def get_quartz_list(
        theme_type: int | None = None,
        team_id: int | None = None,
        ctx: Context = None,
    ) -> dict:
        """获取增量跟踪（定时任务）列表

        Args:
            theme_type: 主题类型筛选：0=策略，1=因子，2=通用（可选）
            team_id: 团队ID（可选）
        """
        if ctx:
            await ctx.info("正在获取定时任务列表")

        params: dict = {}
        if theme_type is not None:
            params["themeType"] = theme_type
        if team_id is not None:
            params["teamId"] = team_id

        return await tq_client.get(GET_QUARTZ_LIST_URL, params=params or None)

    @mcp.tool()
    async def create_quartz(
        job_name: str,
        env_id: int | None = None,
        is_solid: int = 0,
        schedule_frequency: int = 0,
        days: list[int] | None = None,
        hours: list[int] | None = None,
        minute: int = 0,
        range: list[str] | None = None,
        warning_mail: str = "",
        env_info: str = "",
        ctx: Context = None,
    ) -> dict:
        """创建增量跟踪（定时任务）

        Args:
            job_name: 任务名（必填，不能为空）
            env_id: 执行环境ID（可选）
            is_solid: 0=不固化，1=固化，默认0
            schedule_frequency: 0=普通任务，1=常驻任务，默认0
            days: 执行天数，[0]=每天，[1-7]=周日至周六（可选）
            hours: 执行小时，0-23，24=每小时，仅普通任务（可选）
            minute: 执行分钟，0-59，仅普通任务，默认0
            range: 执行时段，如["11:00","12:00"]，仅常驻任务（可选）
            warning_mail: 告警邮箱（可选）
            env_info: 环境信息（可选）
        """
        if not job_name or not job_name.strip():
            return {"success": False, "error": "任务名不能为空"}

        if ctx:
            await ctx.info(f"正在创建定时任务: {job_name}")

        payload: dict = {
            "jobName": job_name.strip(),
            "isSolid": is_solid,
            "scheduleFrequency": schedule_frequency,
            "minute": minute,
        }
        if env_id is not None:
            payload["envId"] = env_id
        if days is not None:
            payload["days"] = days
        if hours is not None:
            payload["hours"] = hours
        if range is not None:
            payload["range"] = range
        if warning_mail:
            payload["warningMail"] = warning_mail
        if env_info:
            payload["envInfo"] = env_info

        return await tq_client.post(CREATE_QUARTZ_URL, json=payload)

    @mcp.tool()
    async def add_quartz_themes(
        quartz_id: str,
        project_ids: list[str] | None = None,
        exclude_theme_ids: list[str] | None = None,
        theme_ids: list[str] | None = None,
        ctx: Context = None,
    ) -> dict:
        """为定时任务添加主题

        Args:
            quartz_id: 定时任务ID（必填）
            project_ids: 项目ID列表，添加项目下所有可添加的主题（可选）
            exclude_theme_ids: 排除的主题ID列表（可选）
            theme_ids: 待添加的主题ID列表（可选）
        """
        if not quartz_id or not quartz_id.strip():
            return {"success": False, "error": "定时任务ID不能为空"}

        if ctx:
            await ctx.info(f"正在为定时任务 {quartz_id} 添加主题")

        payload: dict = {"quartzId": quartz_id.strip()}
        if project_ids is not None:
            payload["projectIds"] = project_ids
        if exclude_theme_ids is not None:
            payload["excludeThemeIds"] = exclude_theme_ids
        if theme_ids is not None:
            payload["themeIds"] = theme_ids

        return await tq_client.post(ADD_QUARTZ_THEMES_URL, json=payload)

    @mcp.tool()
    async def start_quartz(
        job_key: str,
        ctx: Context = None,
    ) -> dict:
        """启动定时任务

        Args:
            job_key: 任务key（必填，通过 get_quartz_list 获取的 jobKey 字段）
        """
        if not job_key or not job_key.strip():
            return {"success": False, "error": "任务key不能为空"}

        if ctx:
            await ctx.info(f"正在启动定时任务: {job_key}")

        params = {"jobKey": job_key.strip()}
        return await tq_client.get(START_QUARTZ_URL, params=params)