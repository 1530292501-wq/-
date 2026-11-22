# 岩仓亚里亚（Iwakura Aria）与我亲爱的暗精灵（My Darling Dark Elf）汉化补丁

这里提供两款游戏的 Windows 简体中文汉化补丁、补丁源文件、安装说明和 SHA-256 校验文件。

## 岩仓亚里亚汉化补丁 / Iwakura Aria

- [下载 Iwakura Aria 汉化补丁 v0.9.0-rc3（预发布）](https://github.com/1530292501-wq/iwakura-aria-my-darling-dark-elf-zh-cn/releases/tag/iwakura-aria-v0.9.0-rc3)
- 适配版本为 Windows x64 · Steam Build 19808494。[安装说明](iwakura-aria/README.md)

## 我亲爱的暗精灵汉化补丁 / My Darling Dark Elf

- [下载 My Darling Dark Elf 汉化补丁 v1.0 Portable](https://github.com/1530292501-wq/iwakura-aria-my-darling-dark-elf-zh-cn/releases/tag/my-darling-dark-elf-v1.0-portable)
- 适配版本为 Windows · Steam 游戏 1.0。[安装说明](my-darling-dark-elf/README.md)

在对应 [Release](https://github.com/1530292501-wq/iwakura-aria-my-darling-dark-elf-zh-cn/releases) 的 **Assets** 下载补丁 ZIP。使用同名 `.sha256` 附件核对下载文件，再按各自说明安装。`patch/` 目录包含用于维护的展开文件，`downloads/` 保留原始补丁归档。

## 版本与验证范围

- **岩仓亚里亚**：适用 Windows x64、Steam App 3197710、Build 19808494。包含官方人名修正和地图标签修正。已有安装、升级、还原及资源结构校验记录；全路线、全界面和地图运行显示仍未完成验证。处理 10,874 条资源记录，不等于 10,874 句译文；原有内容改写范围见补丁内索引。
- **我亲爱的暗精灵**：适用已测试的 Windows Steam 游戏版本 1.0。既有记录显示干净原版与旧修复版环境均通过 4,700 条正文映射和控制符检查，并验证了开场画面；未逐屏通关验证全部游戏。
- **本次入库（2026-10-27）**：重新核对现存补丁目录的 SHA-256，恢复缺失的最终 ZIP，检查 ZIP 完整性及逐文件字节一致性。本次没有重新运行游戏或修改译文。

各补丁的安装、卸载方法和兼容性要求以对应目录说明为准。[入库校验记录](import-verification.json) 和 [全仓文件 SHA-256](SHA256SUMS.txt) 可用于核对文件。

## 目录

```text
downloads/                 可直接安装的独立补丁 ZIP
iwakura-aria/patch/         岩仓亚里亚差分补丁及安装器源码
iwakura-aria/docs/          原有 rc3 验收记录
my-darling-dark-elf/patch/  Ren'Py 翻译层、字体与安装说明
```

## 文件归属

本仓库为非官方本地化补丁归档，需要用户自备适用版本的游戏。补丁不包含原版游戏执行程序、完整资源包或个人存档。随包字体和运行库保留各自许可证；未为游戏原作内容或第三方文件另行授予许可。

补丁内原有说明和验收记录保留原貌；其中“未公开上传”等表述描述原制作时的状态，本仓库记录的是上述日期的导入。
