# MOD 来源标识 / MOD distribution provenance

本项目的独立 MOD 下载包自 2026-10-20 起增加 **Jimmy6Smiles** 来源标识。
它标识分发来源和对应内容，不主张第三方或相机原厂组件的原创权，不覆盖或撤销原有许可。

## 包内内容

- ZIP 注释：作者、项目地址和来源标记修订号。
- `SOURCE_ATTRIBUTION.txt`：中英文来源及第三方权利声明。
- `SOURCE_ORIGIN.json`：原始包 SHA-256、原始成员内容指纹、MOD 清单信息与发布标签。
- `SOURCE_ORIGIN.ed25519`：对来源清单原始字节的 Ed25519 签名。
- `SOURCE_ORIGIN_PUBLIC_KEY.pem`：验证公钥；请与本仓库独立发布的 [公钥](MOD_ORIGIN_PUBLIC_KEY.pem) 核对，不能只信任待验证包自己提供的公钥。

公钥 PEM 文件 SHA-256（精确文件字节）：

```text
575dd226368fbc673611ebae5073be85af12abf5c5d4dfe77d5fb6e728f46cdf
```

Ed25519 原始 32 字节公钥 SHA-256：

```text
1288c2a763f2807df826e9266267c19f58c81e4f541543f15fa9ac6083b87c4c
```

## 验证及限制

下载公钥后，Windows 可用 `Get-FileHash .\MOD_ORIGIN_PUBLIC_KEY.pem -Algorithm SHA256` 核对 PEM 文件指纹。使用支持 Ed25519 的验证工具，以该可信公钥核验 `SOURCE_ORIGIN.ed25519` 对 `SOURCE_ORIGIN.json` 原始字节的签名；再逐项比对清单中 `original_entries` 的 SHA-256、`manager_metadata` 及 `notice_sha256`。签名通过不等于无需检查包内成员与清单是否一致。

普通安装器仍执行原有安装包校验，本次没有给安装器增加签名强制验证。来源签名不等于安全保证、实机验收或 Windows/macOS 代码签名。

本次仅增加分发层来源信息及相应外层校验项，**未修改机身程序、内部 bundle、部署文件、照片或第三方署名**。旧安装记录依赖的内部包标识保持不变；已经正常安装的用户无需重装。版本号和已知问题定位不变，稳定版仍为 1.2.4-rc2。

独立 MOD 附件和安装器压缩包内附 MOD 均已补齐来源标识，文件名保持不变；有变更的 MOD、ZIP 及相关下载 SHA-256 已更新。安装器可执行文件和 Mac 应用内部文件保持原字节。无内附 MOD 的安装器 ZIP 不需要变更。第三方保留的旧包可能没有此标识，不能仅因此判断为伪造。

标识可以被删除；这不是 DRM、反调试、联网追踪或不可移除水印。它用于辨认和核验来源，不能阻止复制或保证他人无法冒充。签名私钥不随下载包或源码公开。

## English

Standalone MOD downloads now identify **Jimmy6Smiles** as their distribution source. The signed manifest records the original package and member hashes, metadata and release tag. This does not claim authorship of vendor or third-party components or override their licenses.

Use the independently published public key above, verify the Ed25519 signature over the exact `SOURCE_ORIGIN.json` bytes, then compare member hashes, manager metadata and notice hash against the actual package. A key supplied only by an untrusted package is not a trust anchor.

Only MOD envelope attribution and corresponding archive checksums changed. Runtime binaries, inner bundle, deployment files, photographs and existing third-party notices are untouched. Existing installations need no reinstall. Both standalone and installer-bundled MODs now carry attribution. Installer executables and Mac application contents are unchanged; archives without bundled MODs remain unchanged. The manager has not gained mandatory provenance-signature enforcement.

Attribution is removable and is not DRM or a guarantee of safety, device validation or anti-copy protection. Historical genuine packages may lack it.
