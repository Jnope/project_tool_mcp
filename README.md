# mcp-for-tq

TQ MCP Server — 通过 Model Context Protocol 管理 TQ 平台的项目、课题、定时任务、模拟盘。

## 功能

- **项目**：创建项目、查询项目列表
- **课题**：新增课题（策略/因子/通用）、设置执行参数、执行课题
- **定时任务**：创建定时任务、关联课题、启动任务
- **模拟盘**：查询模拟盘列表
- **环境**：查询可用执行环境

## 安装

```bash
pip install dist/mcp_for_tq-0.1.0-py3-none-any.whl
```

## 配置

配置文件 `/etc/tq_profile`：

```ini
nginxIP=你的TQ网关IP
token=你的jupyterToken
```

也可通过同名环境变量配置。

## 使用

```bash
# 作为 MCP Server 运行（stdio 传输）
mcp-for-tq

# 或
python main.py
```

在 Cursor / Claude Desktop 等 MCP 客户端中配置该命令即可使用工具。