# Solotalk Space

**Solotalk Space** 网站的 monorepo 仓库。

## 概述

Solotalk Space 由以下部分组成：

- **主页** —— 宣传着陆页
- **下载页** —— 软件下载页面
- **试题分享（核心）** —— 类似论坛的平台，用户自行上传试题资源供他人使用

关键特性：

- **下载无需登录。** 通过按 IP 限流（nginx + 应用层双重防护）防止爬取和流量滥用。
- **上传需要登录。** 上传者提交资源时必须填写相关信息。
- **管理员审核。** 资源经管理员审核通过后才能公开下载；管理员可随时封禁任何资源。
- **免责声明。** 所有资源均由用户上传，网站不对其内容负责；如涉及侵权请联系我们删除。

## 技术栈

| 部分 | 技术 |
| --- | --- |
| 后端 | FastAPI（Python），使用 uv 管理依赖，PyInstaller 打包为单文件二进制 |
| 前端 | Vue 3 + Vite + Naive UI，使用 pnpm 管理依赖 |
| 数据库 | MySQL 8.0.44，使用 Alembic 进行迁移 |
| 部署 | nginx（反向代理 + 静态托管 + IP 限流） |

## 仓库结构

```
apps/
  api/        # FastAPI 后端
  web/        # Vue 3 前端
packages/     # 共享包（占位）
deploy/       # nginx 配置示例、数据库迁移/部署脚本、备份脚本、.env.example
```

## 交付产物

- 后端二进制（PyInstaller 单文件构建）
- 前端静态构建产物
- nginx 配置示例
- MySQL 8.0.44 迁移与部署脚本
- 自动备份脚本（数据库 + 上传文件）

## 配置

数据库连接信息及其他环境相关配置通过 `.env` 文件以环境变量方式载入（参见 `deploy/.env.example`）。切勿提交真实的 `.env` 文件。

## 文档

- [ARCHITECTURE.md](ARCHITECTURE.md) —— 系统架构
- [CONTRIBUTE.md](CONTRIBUTE.md) —— 贡献指南，**写代码前必读**
