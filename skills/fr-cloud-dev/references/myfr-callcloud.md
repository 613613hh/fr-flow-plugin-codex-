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
  -> myFR.callCloud(interfaceNo, payload, success, error)
  -> POST /{prjId}/flowservice/json/flow_{prjId}_{interfaceNo}
  -> { iibs: { req: { body: payload } } }
```

`myFR.js` 是 FineReport 运行环境提供的实现。项目源码通常只负责加载它、设置上下文并调用公开的 `callCloud` 方法；不要复制或重写其中的内部实现。

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
- 成功判断是否使用项目契约规定的 `respCode`，而不是只判断 HTTP 200。
- 失败时是否向用户反馈 `respMsg`，并避免重复提交。
