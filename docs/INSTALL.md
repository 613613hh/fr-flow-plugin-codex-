# Codex 安装与工作区配置

## 1. 从 GitHub 安装

仓库地址：

```text
https://github.com/613613hh/fr-flow-plugin-codex-.git
```

使用 Codex 的插件安装入口安装仓库。安装成功后，Codex 会把插件放入用户级插件缓存目录；不要把插件源码复制到 FineReport 的 `WEB-INF/reportlets` 目录。

安装后应能看到 11 个技能：

```text
fr-flow-plugin:fr
fr-flow-plugin:fr-change
fr-flow-plugin:fr-data-dev
fr-flow-plugin:fr-display-dev
fr-flow-plugin:fr-pm
fr-flow-plugin:fr-qa
fr-flow-plugin:fr-release
fr-flow-plugin:frm
fr-flow-plugin:frm-display-dev
fr-flow-plugin:frm-pm
fr-flow-plugin:frm-qa
```

## 2. 配置 FineReport 工作区

插件本体和业务项目分离。建议结构：

```text
插件安装缓存/插件源码
└─ fr-flow-plugin-codex-

FineReport 工作区
└─ WEB-INF/reportlets/
   ├─ .codex/
   └─ whmigrantworkerspay/
```

在工作区中准备环境配置，至少提供：

```text
FR_WORKSPACE       插件根目录
FR_PROJECTS_DIR    项目源码目录
FR_REPORTLETS      FineReport 的 reportlets 部署目录
FR_SERVER_URL      FineReport 服务地址
FR_PREVIEW_PATH    报表预览路径前缀
FR_MYSQL_HOST      数据库主机
FR_MYSQL_PORT      数据库端口
FR_MYSQL_DATABASE  数据库名
FR_MYSQL_USER      数据库用户
```

密码只保存在本机配置中，不要提交到 GitHub。

## 3. 技能触发

Codex Skill 不一定会把 SKILL.md 中的 `/fr` 文本注册成 UI 内置斜杠命令。优先使用自然语言或完整技能名：

```text
使用 fr-flow-plugin:fr 查看帆软开发流程
使用 fr-flow-plugin:fr-change 修改 whmigrantworkerspay
使用 fr-flow-plugin:fr-release 发布 whmigrantworkerspay
```

如果当前客户端支持显式技能语法，也可以使用：

```text
$fr-flow-plugin:fr
$fr-flow-plugin:fr-release
```

## 4. 可选 Hook

插件包含：

```text
hooks/permission-guard.js
```

它是可选的工作区权限守卫，不会在安装插件时自动修改用户配置。启用前请确认当前 Codex 版本支持项目级 Hook 配置，并将命令路径改为本机插件实际路径：

```text
node <插件安装目录>/hooks/permission-guard.js
```

脚本通过环境变量或 `.fr.yaml` 查找 `FR_REPORTLETS`，保护插件源码目录，同时允许修改项目和报表部署目录。不同成员应使用各自的绝对路径，不能把开发机路径写死在仓库中。

## 5. 验证

安装后先验证技能可发现，再执行一个只读请求：

```text
使用 fr-flow-plugin:fr，列出当前插件包含的技能和发布流程
```

涉及项目变更时使用：

```text
使用 fr-flow-plugin:fr-change 检查项目状态，不要修改文件
```

## 6. 发布规则

项目变更遵循：

```text
JSX → MJS → CPT
```

内网发布只允许由 `fr-release` 生成压缩包，包内包含两个最终 CPT，以及在存储过程发生变更时附带的最新 `procedures.sql`。MJS 不进入最终包。
