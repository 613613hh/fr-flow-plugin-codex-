# myFR.callCloud 参考

## 需要从项目确认的变量

| 变量 | 来源 | 用途 |
|---|---|---|
| `cloudUrl` | `myFR.getParam('cloudUrl')` 或运行环境 | 云平台基础地址 |
| `prjId` | 项目契约 | 拼接项目 flowservice 路径 |
| `fine_username` | `FR.remoteEvaluate('=$fine_username')` 或项目现有实现 | 识别当前 FineReport 用户 |
| `servletURL` | `FR.remoteEvaluate('=servletURL')` | 保留 FineReport 运行上下文 |

不要打印这些变量中的敏感值；排查时只记录是否存在、主机和项目标识等非敏感信息。

## 请求链

```text
页面加载
  -> GET {FineReport根路径}/js/myFR.js
  -> 设置 myFR.cloudUrl / prjId / fine_username / servletURL
  -> myFR.callCloud(interfaceNo, payload, success, error, isJson)
  -> POST /{prjId}/flowservice/json/flow_{prjId}_{interfaceNo}
  -> { iibs: { req: { body: payload } } }
```

`myFR.js` 是 FineReport 运行环境提供的实现。项目源码通常只负责加载它、设置上下文并调用公开的 `callCloud` 方法；不要复制或重写其中的内部实现。

## 调用签名与隐藏行为

完整签名：`myFR.callCloud(code, body, succCb, failCb, isJson = false)`。

| 参数 | 说明 |
|---|---|
| `code` | 接口码。以 `flow_` 开头直接拼完整服务名，否则拼 `flow_{prjId}_{code}` |
| `body` | 业务参数对象。会被原地改写：自动注入 `operator = fine_username`；请求体包装为 `{ iibs: { req: { body } } }` |
| `succCb` | 仅 `respCode == "00000"` 时调用，入参 `resp.body`；缺省 toast「接口调用成功」 |
| `failCb` | 仅业务失败（非 `00000`）时调用，入参 `respMsg`；网络错误不触发 failCb，只 toast「接口调用失败」 |
| `isJson` | 第 5 参，默认 `false`。`true` 时强制 `Content-Type: application/json;charset=UTF-8` |

`isJson` 必要性：myFR.js 默认按端口判断 Content-Type——`cloudUrl` 端口为 9032 时走 `x-www-form-urlencoded`，其余走 json。为统一稳定，页面 `callCloud` 包装函数应固定传 `true`（见 SKILL.md 调用格式）。

其他注意：

- `body` 传 `null`/`undefined` 会在注入 `operator` 时抛异常，必须传对象。
- 调用期间 `myFR.maskShow()` 弹全屏遮罩，请求超时 50s。
- 排查时以浏览器网络请求确认 `Content-Type` 和请求体是否符合 IIBS 契约。

## 响应处理

常见 IIBS 响应结构：

```json
{"iibs":{"resp":{"head":{"respCode":"00000","respMsg":"接口调用成功"},"body":{}}}}
```

至少区分：

1. `respCode === '00000'`：成功，读取 `resp.body`。
2. 非 `00000`：业务失败，展示 `respMsg`，不要当作成功刷新状态。
3. `onError` 回调：网络错误、跨域错误、脚本加载失败或平台调用失败。
4. 空 body：根据项目契约判断是否是合法成功响应，不能统一当成异常。

## 生产项目学习方法

对已有生产项目，按以下顺序比对：

1. JSX：看页面如何加载和初始化 `myFR`。
2. MJS：确认编译后的 JavaScript 与 JSX 逻辑一致。
3. CPT：确认部署产物实际包含同样的调用代码。
4. 项目接口文档：确认接口码、请求字段、响应码和业务含义。
5. 浏览器网络记录或已有回归脚本：确认最终 URL、HTTP 方法和请求体。

若 JSX、MJS、CPT 不一致，以源码链路为修复对象，重新生成 CPT；不要直接编辑 CPT。

## 排查清单

- 页面 URL 是否带 `op=write`，确保 FineReport 页面脚本正常执行。
- `/js/myFR.js` 是否能从当前 FineReport 服务加载。
- `myFR` 是否存在，`cloudUrl`、`prjId`、`fine_username` 是否已初始化。
- `prjId` 是否与云平台项目名一致。
- 接口码是否存在于项目接口契约，参数名称和大小写是否一致。
- 最终请求是否命中 `/{prjId}/flowservice/json/flow_{prjId}_{接口码}`。
- 请求是否使用 IIBS `iibs.req.body` 包装。
- 请求 Content-Type 是否为 `application/json;charset=UTF-8`（`callCloud` 第 5 参 `isJson=true`）。
- 成功判断是否使用项目契约规定的 `respCode`，而不是只判断 HTTP 200。
- 失败时是否向用户反馈 `respMsg`，并避免重复提交。
