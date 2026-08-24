---
name: fr-cloud-dev
description: |
  FineReport 云平台接口开发与排查技能。当需求涉及 myFR.js、myFR.callCloud、cloudUrl、flowservice 或 IIBS 报文时使用。
  负责从生产 CPT/JSX/MJS 和项目接口文档还原调用契约，编写或修改云平台调用代码，并验证接口路径、请求报文、响应处理和错误提示。
---

# FineReport 云平台交互开发

## 适用边界

本技能处理 FineReport 加壳页面通过 `myFR.callCloud` 调用项目云平台接口的场景。它与通用外部 HTTP 代理不同：

- `myFR.callCloud`：调用项目的 `flowservice` 云平台接口。
- `/api/report` + `api_agent.cpt`：调用普通外部 HTTP API。
- `/api/data` + `*_data.cpt`：调用本地数据库数据层。

如果项目已经存在可运行版本，优先以生产 CPT、对应 JSX/MJS、接口文档和回归脚本为准，不凭空套用 `api_agent` 模式。

## 工作流程

1. 读取项目的 `docs/dev_task.json`、接口文档、现有 `pages/*.jsx`、`pages/*.mjs` 和部署用 `pages/*.cpt`。
2. 搜索并确认以下运行时信息：`myFR.js` 加载地址、`cloudUrl`、`prjId`、`fine_username`、`servletURL`、接口码和业务参数。
3. 优先复用项目已有的初始化和 `callCloud` 包装函数；新增页面必须保持同一套初始化契约。
4. 确认接口调用格式：`myFR.callCloud(interfaceNo, payload, onSuccess, onError)`。接口码和业务参数必须来自项目接口契约，不能猜测。
5. 对成功和失败分别处理：成功回调中的业务体、`respCode`/`respMsg`、网络错误、`myFR.js` 加载失败和初始化失败都要覆盖。
6. 遵循已有项目的源码链路：修改 JSX 后生成 MJS，再生成 CPT；禁止直接手工修改编译后的 CPT。
7. 在测试环境使用项目已有的 mock 或浏览器回归脚本验证请求 URL、请求体和响应回调；生产环境验证时不得打印密码、完整令牌或敏感业务数据。

## 标准运行时初始化

生产页面通常从 FineReport 服务端加载 `/js/myFR.js`，然后设置项目上下文：

```javascript
function cloudReady() {
    if (typeof window.myFR === 'undefined') return false;
    try {
        myFR.cloudUrl = myFR.getParam('cloudUrl');
        myFR.prjId = '项目名';
        myFR.fine_username = FR.remoteEvaluate('=$fine_username') || '';
        myFR.servletURL = FR.remoteEvaluate('=servletURL');
        myFR.inited = true;
        return !!(myFR.cloudUrl && myFR.prjId && myFR.fine_username);
    } catch (e) {
        return false;
    }
}
```

不要把开发 mock 地址当作生产配置。`cloudUrl` 应优先由 `myFR.getParam('cloudUrl')` 或项目运行环境提供；只有项目明确要求时才使用本地 fallback。

## 调用格式

```javascript
function callCloud(interfaceNo, payload, onOk, onErr) {
    if (!cloudReady()) {
        if (onErr) onErr('云平台未就绪');
        return;
    }
    myFR.callCloud(interfaceNo, payload, onOk, onErr);
}

callCloud('接口码', { account: account }, function(body) {
    // 处理成功业务体
}, function(message) {
    // 展示业务失败或网络失败
});
```

`myFR.callCloud` 会根据 `prjId` 和接口码访问类似下面的路径，并封装 IIBS 请求体：

```text
/{prjId}/flowservice/json/flow_{prjId}_{interfaceNo}
```

请求体通常为：

```json
{"iibs":{"req":{"body":{}}}}
```

具体字段、响应结构和接口码必须读取项目自己的契约文档。详细检查项见 [myfr-callcloud.md](references/myfr-callcloud.md)。

## 变更和验收红线

- 不把云平台接口改写成 `/api/data` 或 `/api/report`。
- 不在页面中硬编码完整云平台接口地址；使用 `myFR` 的项目上下文和接口码。
- 不绕过项目已有的权限、用户身份和 `servletURL` 初始化逻辑。
- 不把账号、密码、令牌和完整生产报文写入日志、mock 文件或测试报告。
- 业务写操作必须有明确的用户确认、幂等/重复操作提示和失败反馈。
- 若 `myFR.js` 缺失、接口码未定义、响应契约不明或生产请求未验证，停止并报告缺失项，不猜测接口行为。

## 按需读取

- [references/myfr-callcloud.md](references/myfr-callcloud.md)：调用链、报文、响应和排查清单。开发或排查 `myFR.callCloud` 时读取。
- 项目自己的接口文档：以项目实际接口码和业务字段为最终契约。
