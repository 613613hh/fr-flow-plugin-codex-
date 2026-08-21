# fr-flow-plugin-codex

面向 Codex 的 FineReport 11 前端开发插件，覆盖 PC、移动端、数据层、展示层、需求管理、版本变更、内网发布和端到端测试。

## 插件结构

```text
fr-flow-plugin-codex-/
├─ .codex-plugin/plugin.json   # Codex 插件清单
├─ skills/                     # 唯一技能源码目录
├─ foundation/                 # CPT 骨架、脚手架和测试工具
├─ public_cpt/                 # 公共 CPT 资源
├─ scripts/                    # 数据、展示和环境工具
├─ hooks/                      # 可选的项目级权限守卫脚本
├─ schemas/                    # dev_task/qa_task 校验模式
├─ shared/                     # FineReport 公共知识库
└─ docs/                       # 安装、配置和部署文档
```

业务项目不放在本仓库中。请将 `whmigrantworkerspay` 等项目放在独立的 FineReport `reportlets` 工作区，插件安装后即可在该工作区使用。

## 技能

```text
/fr                       # 入口说明（也可直接用自然语言触发）
/fr-pm <项目名>            # 需求和任务契约
/fr-data-dev <项目名>     # 数据层 CPT、接口和存储过程
/fr-display-dev <项目名>  # PC React/Ant Design 页面
/fr-qa <项目名>           # PC 端到端验收
/fr-change <项目名>       # 已有项目版本变更
/fr-release <项目名>      # 内网离线发布包
/frm                      # 移动端入口
/frm-pm <项目名>          # 移动端需求
/frm-display-dev <项目名> # 移动端页面
/frm-qa <项目名>          # 移动端验收
```

说明：Codex Skill 的 `/fr` 是触发提示，不是由插件清单注册的内置斜杠命令。若客户端未将斜杠文本路由到技能，请使用自然语言，例如“使用 fr-flow-plugin:fr 查看技能列表”，或使用 `$fr-flow-plugin:fr`（客户端支持时）。

## 安装和工作区

插件仓库与 FineReport 工作区分离。插件安装后由 Codex 管理版本缓存，不需要复制到 `WEB-INF/reportlets`。在目标工作区配置 `.codex/env.json` 或项目环境变量，使技能获得以下路径：

```text
FR_WORKSPACE       插件安装目录
FR_PROJECTS_DIR    项目源码目录
FR_REPORTLETS      FineReport CPT 部署目录
FR_SERVER_URL      FineReport 服务地址
```

不要提交包含密码的 `.fr.yaml`；使用 `.fr.yaml.example` 作为模板。

## 开发、变更和发布

前端页面严格遵循：

```text
JSX → MJS → CPT
```

JSX 是唯一人工维护的源文件。MJS 是构建中间产物，已经嵌入 CPT 后不进入最终发布包。CPT 必须由工具链生成，禁止手工修改编译内容。

`fr-change` 负责变更范围、构建、CPT 重生成、验证和 Git 版本标记。`fr-release` 负责生成项目内的离线发布 ZIP：

```text
fr-release-v1.2.0.zip
├─ report-a.cpt
├─ report-b.cpt
└─ procedures.sql   # 仅本次涉及存储过程变更时存在
```

SQL 必须是最新的完整存储过程快照；没有存储过程变更时省略 SQL。最终包禁止包含 JSX、MJS、备份文件、日志、Mock 文件和其他无关文件。

## Hook 说明

`hooks/permission-guard.js` 是可选的项目级权限守卫脚本，源码随插件版本管理，但不会因为安装插件而自动修改每个人的 Codex 工作区权限。需要启用时，请按 `docs/INSTALL.md` 将它配置到目标工作区的 Codex Hook 配置中；不同成员可以使用不同的 `FR_PROJECTS_DIR` 和 `FR_REPORTLETS`。

## 异常处理

所有技能统一读取 `shared/KNOWLEDGE/ERROR_HANDLING.md`。其中规定了环境、依赖、JSX/MJS/CPT、数据库、QA 和 Release 异常的分类、自动修复范围、重试次数、停止条件和必须向用户确认的操作。遇到问题时，AI 应先按该协议处理，再报告原因和下一步，不得跳过校验或伪造成功。

## 版本

插件使用 Git Tag 发布，例如 `v3.2.0`。修改技能、脚本或 Hook 后先执行插件校验，再更新插件版本并推送 Tag。
