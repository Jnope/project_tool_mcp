import logging
import os
import re
from typing import Any

from pydantic import computed_field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

logger = logging.getLogger("mcp-for-tq")

TQ_PROFILE_PATH = "/etc/tq_profile"


def _load_tq_profile(path: str = TQ_PROFILE_PATH) -> dict[str, str]:
    """从 /etc/tq_profile 读取 shell 风格的变量定义（key=value）。

    支持以下格式：
      - KEY=VALUE
      - export KEY=VALUE
      - KEY="VALUE"  / KEY='VALUE'  （引号会被去除）

    Returns:
        变量名到变量值的映射字典；文件不存在或读取失败时返回空字典。
    """
    result: dict[str, str] = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                m = re.match(
                    r"""(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)""",
                    line,
                )
                if not m:
                    continue
                key, raw_val = m.group(1), m.group(2)
                val = raw_val.strip()
                if len(val) >= 2 and (
                    (val.startswith('"') and val.endswith('"'))
                    or (val.startswith("'") and val.endswith("'"))
                ):
                    val = val[1:-1]
                result[key] = val
    except FileNotFoundError:
        logger.warning(f"配置文件 {path} 不存在，将使用环境变量或默认值")
    except Exception as e:
        logger.error(f"读取 {path} 失败: {e}", exc_info=True)
    return result


class TqProfileSettingsSource(PydanticBaseSettingsSource):
    """从 /etc/tq_profile 读取配置的自定义 settings source。"""

    def __init__(self, settings_cls: type[BaseSettings]) -> None:
        super().__init__(settings_cls)
        self._data = _load_tq_profile()

    def get_field_value(
        self, field: Any, field_name: str
    ) -> tuple[Any, str, bool]:
        value = self._data.get(field_name)
        return value, field_name, False

    def __call__(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        for field_name in self.settings_cls.model_fields:
            if field_name in self._data:
                d[field_name] = self._data[field_name]
        return d


def _pop_proxy() -> None:
    for _key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        os.environ.pop(_key, None)
    os.environ.setdefault("NO_PROXY", "*")
    os.environ.setdefault('no_proxy', "*")


_pop_proxy()


class Settings(BaseSettings):
    """应用配置。

    优先级：/etc/tq_profile > 环境变量 > 默认值。
    """

    model_config = SettingsConfigDict(extra="ignore")

    nginxIP: str = ""
    token: str = ""

    @computed_field
    @property
    def base_url(self) -> str:
        if self.nginxIP:
            return f"http://{self.nginxIP}/tqlab"
        return "http://172.18.192.75:8091/tqlab"

    @computed_field
    @property
    def create_project_url(self) -> str:
        return f"{self.base_url}/project/createProject"

    @computed_field
    @property
    def add_project_theme_url(self) -> str:
        return f"{self.base_url}/project/addProjectTheme"

    @computed_field
    @property
    def get_project_list_url(self) -> str:
        return f"{self.base_url}/project/getProjectList"

    @computed_field
    @property
    def get_env_list_url(self) -> str:
        return f"{self.base_url}/env/getEnvList"

    @computed_field
    @property
    def set_theme_run_param_url(self) -> str:
        return f"{self.base_url}/project/setThemeRunParam"

    @computed_field
    @property
    def execute_theme_url(self) -> str:
        return f"{self.base_url}/project/executeTheme"

    @computed_field
    @property
    def get_quartz_list_url(self) -> str:
        return f"{self.base_url}/project/quartz/getQuartzList"

    @computed_field
    @property
    def create_quartz_url(self) -> str:
        return f"{self.base_url}/project/quartz/createQuartz"

    @computed_field
    @property
    def add_quartz_themes_url(self) -> str:
        return f"{self.base_url}/project/quartz/addThemes"

    @computed_field
    @property
    def start_quartz_url(self) -> str:
        return f"{self.base_url}/project/quartz/startQuartz"

    @computed_field
    @property
    def get_board_list_url(self) -> str:
        return f"{self.base_url}/board/getBoardList"

    @computed_field
    @property
    def jupyter_token(self) -> str:
        return self.token or "b97bbd24-5a61-4f58-a13f-23e1af69e378"

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (init_settings, TqProfileSettingsSource(settings_cls), env_settings)


settings = Settings()

CREATE_PROJECT_URL = settings.create_project_url
ADD_PROJECT_THEME_URL = settings.add_project_theme_url
GET_PROJECT_LIST_URL = settings.get_project_list_url
GET_ENV_LIST_URL = settings.get_env_list_url
SET_THEME_RUN_PARAM_URL = settings.set_theme_run_param_url
EXECUTE_THEME_URL = settings.execute_theme_url
GET_QUARTZ_LIST_URL = settings.get_quartz_list_url
CREATE_QUARTZ_URL = settings.create_quartz_url
ADD_QUARTZ_THEMES_URL = settings.add_quartz_themes_url
START_QUARTZ_URL = settings.start_quartz_url
GET_BOARD_LIST_URL = settings.get_board_list_url
JUPYTER_TOKEN = settings.jupyter_token

logger.info(f"CREATE_PROJECT_URL = {CREATE_PROJECT_URL}")
logger.info(f"ADD_PROJECT_THEME_URL = {ADD_PROJECT_THEME_URL}")
logger.info(f"GET_PROJECT_LIST_URL = {GET_PROJECT_LIST_URL}")
logger.info(f"GET_ENV_LIST_URL = {GET_ENV_LIST_URL}")
logger.info(f"SET_THEME_RUN_PARAM_URL = {SET_THEME_RUN_PARAM_URL}")
logger.info(f"EXECUTE_THEME_URL = {EXECUTE_THEME_URL}")
logger.info(f"GET_QUARTZ_LIST_URL = {GET_QUARTZ_LIST_URL}")
logger.info(f"CREATE_QUARTZ_URL = {CREATE_QUARTZ_URL}")
logger.info(f"ADD_QUARTZ_THEMES_URL = {ADD_QUARTZ_THEMES_URL}")
logger.info(f"START_QUARTZ_URL = {START_QUARTZ_URL}")
logger.info(f"GET_BOARD_LIST_URL = {GET_BOARD_LIST_URL}")
