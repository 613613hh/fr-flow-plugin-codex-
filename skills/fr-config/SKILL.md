---
name: fr-config
description: 帆软决策平台自动化配置。核心是"如何配置"：账号、角色、页面权限等各类平台配置点（后期可继续追加数据连接、系统设置等）。当用户要求"配置平台""建账号角色""绑定权限""改配置"时触发。
---

# 帆软决策平台自动化配置（fr-config）

本技能是**决策平台配置的通用入口**，以"配置点"为单位组织。当前已覆盖：用户、角色、页面权限、数据层过滤。**后期任何新的配置点（数据连接、系统设置、定时调度、外观等）都追加到本技能新增章节**，保持"如何配置"的方法论统一。

遇到失败先读 `$FR_WORKSPACE/shared/KNOWLEDGE/ERROR_HANDLING.md`。

## 前置

- 帆软服务运行中（`$FR_SERVER_URL`，如 `http://localhost:8075`）。
- 有 admin 账号（`$FR_ADMIN_USER` / 密码见用户全局 CLAUDE.md）。
- playwright 可用：`$FR_WORKSPACE/foundation/tools/api_tester/node_modules/playwright`（chromium 已装）。

## 通用方法论（所有配置点的公共底座）

> 任何配置点都先走这套：playwright 登录 → 抓 token → 用 v10 API 查询确认 → 驱动 UI 或调 API 变更 → 用非 admin 账号验证。

1. **登录必须用 playwright**：登录密码是前端 RSA 加密的（请求体含 `encrypted:true`），curl 直接 POST 无效。登录页用户名/密码 input 按 placeholder 定位，登录按钮是 `div.login-button`（不是 button）。
2. **token 抓取**：监听请求头拿 `Authorization: Bearer ...`，后续调 v10 API 都要带；用完即弃，不入日志。
3. **决策平台 v10 API**（路径前缀 `/webroot/decision`，需要 `Authorization` 头，`Accept: application/json`）：
   - `GET /v10/users?page=&count=&keyword=&needAdmins=true` — 用户列表
   - `POST /v10/user` / `PUT /v10/user` — 创建/编辑用户（`reqByEncrypt`，body 加密 → 可靠路径是驱动 UI）
   - `DELETE /v10/users`，body `{"removeUserIds":[id]}` — 删除用户
   - `GET /v10/user/roles` — 角色列表
   - `GET /v10/department/root?privilegeType=2` — 报表权限管理页数据；`privilegeType=1` 目录/菜单权限
4. **UI 驱动通用技巧**：FineUI 的按钮很多是 `div`（`div.bi-text` 文本"确定"、`div.login-button`），不是 `<button>`；弹窗可见 `input:visible` 的索引要先 `evaluateAll` 确认，页面 chrome（搜索框/分页）占前面的索引，别填错。

---

## 配置点 1：用户（建号/查号/删号）

### 查看当前用户
```js
const r = await page.evaluate(async (tk) => {
  const res = await fetch('/webroot/decision/v10/users?page=1&count=30&needAdmins=true', { headers: { 'Authorization': tk, 'Accept': 'application/json' } });
  const j = await res.json();
  return (j.data && j.data.items || []).map(u => u.username + '/' + (u.realName||''));
}, token);
```

### 批量创建（驱动"用户管理→添加用户"）
- 进入 `http://localhost:8075/webroot/decision#management/user`，等 3~4s。
- 点 `page.getByText('添加用户', { exact: true }).first()` 打开弹窗。
- **弹窗内可见 input 索引**：`[0]` 页面搜索框、`[1]` 分页（别动）、`[2]` 用户名、`[3]` 姓名、`[4]` 密码(password)、`[5]` 手机、`[6]` 邮箱。
- 确认按钮：`page.locator('div.bi-text').filter({ hasText: /^确定$/ }).last()`。
- 创建后弹窗关闭并刷新；下一个账号重新点"添加用户"。

```js
const USERS = [['zhangwei','Zhang Wei'], ['lina','Li Na'], /* ... */];
for (const [username, realname] of USERS) {
  await page.getByText('添加用户', { exact: true }).first().click();
  await page.waitForTimeout(1800);
  const vis = page.locator('input:visible');
  await vis.nth(2).fill(username);
  await vis.nth(3).fill(realname);
  await vis.nth(4).fill('123456');
  await page.waitForTimeout(300);
  await page.locator('div.bi-text').filter({ hasText: /^确定$/ }).last().click();
  await page.waitForTimeout(2500);
}
```

- 演示密码统一 `123456`；交付时提醒上线前改密。
- 建错用 `DELETE /v10/users` + `{removeUserIds:[id]}` 清理，先 GET 按 keyword 找 id。

## 配置点 2：角色

- 查看：`GET /v10/user/roles`（返回 `customRoles` / `depRoles`）。
- 新建/编辑：`管理系统 → 用户管理 → 角色`（UI 驱动），或按需要调 v10 API。
- 角色用于配置点 3 的页面权限，或供页面内 `$fine_role` 判断（参考 whmigrantworkerspay 的 `湖北农民工-管理员` 用法）。

## 配置点 3：页面权限（两种模型，先和用户确认）

- **A. SQL 数据过滤（无角色，推荐给纯查询页）**：查询页所有人可进；页面自动带 `p_cur_user=$fine_username`，数据层 SQL `user_no='${trim(p_cur_user)}'` 过滤（非空才过滤），admin 例外看全部。只建账号，不建角色、不做页面绑定。
- **B. 平台报表权限（有角色）**：`管理系统 → 权限管理 → 报表权限` 把角色绑到具体 reportlet（`privilegeType=2`），未授权直接打不开。
- 模型 A 生效前提：**账号用户名 = 数据表 `user_no` 字段值**（例：种子数据 `user_no='zhangwei'`，账号用户名也必须是 `zhangwei`）。

## 配置点 4：数据层配合（模型 A 的落地）

- 数据层 `user_no` 过滤：改 `project.yaml` 的 `contracts.datasets`，给 `*_qry`/`*_total` 加 `p_cur_user` 参数 + `${if(len(trim(p_cur_user))==0, "", " AND user_no = '" + trim(p_cur_user) + "'")}`，再 `node meta/build_data.mjs` 重建数据 CPT（**不手改 CPT**）。
- 页面侧：`FR.remoteEvaluate('=$fine_username')`，非 admin 时把 `{ name:'p_cur_user', type:'String', value: curUser }` 拼进查询/总数参数；无 `user_no` 列的对象（如保证人）不传。**管理员判定用角色**：`$fine_role` 数组里是否含指定系统管理员角色（如 `武汉分行投贷后管理系统-系统管理员`），不要按用户名。

## 配置点 5：决策平台目录（菜单）——建目录节点 / 挂报表入口

**接口（v10，已从真实抓包 添加目录.har 验证）**：

| 操作 | 接口 | 请求体 |
|---|---|---|
| 建目录节点 | `POST /v10/{父节点id}/directory` | `{"text":"目录名","description":"","deviceType":1}` → 响应 `data.id`=新节点id |
| 校验模板路径 | `POST /v10/templates/batch` | `["postloan_new/pages/xxx/xxx.cpt"]` |
| 加报表入口 | `POST /v10/{节点id}/templates` | `[{ "id":"<报表路径>", "text":"显示名", "name":"显示名", "open":true, "description":"", "path":"<报表路径>", "deviceType":1, "showType":0, "parameters":[] }]` |

**查目录树**：`GET /v10/view/entry/tree` → `data[]` 每个节点 `{id, pId, text, path, entryType}`（entryType 3=目录节点，102=报表入口）。

**直接调 API 即可，无需驱动 UI**（比点"目录管理"树稳得多）。**现成助手**：`$FR_WORKSPACE/foundation/tools/api_tester/dir_add.js`
```bash
node dir_add.js add-directory <父节点id> "参数管理"          # 建目录节点，打印新 id
node dir_add.js add-templates <节点id> "报表路径|显示名,报表路径|显示名"   # 批量挂报表
node dir_add.js 任意                            # 查看用法
```
助手逻辑：playwright 登录 admin → 抓 `Authorization` token → 依次调上述 3 个接口（先 templates/batch 校验路径，再逐个 add-templates）。

**坑**：
- 目录树的节点 id 每次会话/环境不同，动手前先 `GET /v10/view/entry/tree` 拿当前 id（别用历史 HAR 里的）。
- 报表路径 = 相对 reportlets 根（如 `postloan_new/pages/param_mng/busi_type_mng.cpt`）。
- 已存在的入口重复 POST 会再建一条（无幂等），加之前先查树确认。

---

## 新增配置点的规范（给后续使用）

1. 每个配置点独立一章，结构固定：**接口/关键事实 → 驱动步骤（带可用代码）→ 验证**。
2. 公共底座（登录/token/API 约定）只维护一份，配置点不要重复写。
3. 变更类操作（建号、删号、改权限）先查当前状态、列清单、和用户确认再动手；不可逆操作尤其小心。
4. 记下踩过的坑（元素定位、字段错位、API body 格式等），让下次更快。

## 注意事项

- 创建/删除账号是**不可逆操作**：先列出当前用户，确认清单再动手；删除前看清楚目标。
- token 是敏感凭证，用完即弃，不写进日志或入库。
- 不打印数据库密码。
- 账号清单、密码策略、权限模型（A/B）都要先和用户确认，不要自行拍板。
