# flomo-skills

> "笔记记了 3 年，但真正回头看的次数很少。"

我有几千条 flomo 笔记，也还在每天继续写。问题是，每次要写周报、做复盘，或者回答“最近在想什么”，我还是会手动翻笔记。

flomo-skills 解决的不是“怎么记笔记”。它让 agent 能直接读你的 flomo：搜索、创建、修改、导出，也可以基于一段时间的 memo 做自我分析。

## 30 秒启动

```bash
npx skills add Undertone0809/zee-agent-skills/flomo-skills
```

安装时可以在 CLI 里选择需要的 flomo skill；不需要给每个 skill 单独跑安装命令。

装完后可以直接说：

> "帮我总结最近一周关于 AI 的想法"

> "记一条 memo，尽量复用我现有的 tag"

> "基于我的笔记，分析我最近到底在想什么"

agent 会直接操作你的 flomo。你不需要复制粘贴。

## 核心工作流

### 场景 1：查一段笔记

你说：

> "上周我记的关于 meeting 的笔记"

`flomo-local-api`（Mac）会：

- 读取本地登录态并调用 flomo API。
- 返回匹配 memo，按时间倒序排列。
- 高亮关键词，方便继续追问或修改。

你继续说：

> "把第三条改一下，加上待办"

`flomo-local-api` 会更新那条 memo，并优先复用你现有的 tag。

Mac 上通常不需要打开浏览器。本地 API 更快，也不依赖 Web UI 的页面结构。

### 场景 2：看最近的思考模式

你说：

> "基于我的 flomo，分析一下我最近在想什么"

`flomo-insight` 会拉取一段时间内的笔记，找反复出现的主题、意图和行动之间的断点，以及你多次提到但没有后续的事情。

你还可以追问：

> "把那个'想做的事但没跟进'的部分展开说说"

它适合回答这种问题：

- 最近反复出现的主题是什么？
- 哪些想法只停在“想”，没有进入行动？
- 哪些情绪或问题总在同一种场景里出现？

这不是简单的关键词搜索。它更像一次基于笔记的复盘。

### 场景 3：导出素材

你说：

> "把 2025 年的笔记按季度导出，我要喂给 NotebookLM"

`flomo-memo-to-markdown` 会把 memo 导出成 Markdown，按时间拆分，并处理标签、链接和附件引用。适合把 flomo 里的长期记录整理给 NotebookLM 或其他阅读工具。

## 你的 flomo skill 组

| Command | 适合场景 | 能做什么 |
| --- | --- | --- |
| `flomo-local-api` | Mac 上的高频查询和轻量编辑 | 查、记、改、总结、tag 分析 |
| `flomo-web-crud` | Windows / 非 Mac，或需要浏览器路径时 | 查、记、改、删 |
| `flomo-memo-to-markdown` | 批量导出 | 导出 Markdown、整理 NotebookLM 素材 |
| `flomo-insight` | 复盘和自我分析 | 主题分析、盲区识别、行动建议 |

## 路由规则

Mac 用户优先装 `flomo-local-api`。它走本地登录态，速度快，也更适合频繁使用。

Windows 或非 Mac 用户装 `flomo-web-crud`。它通过浏览器自动化完成类似操作。

功能差异主要有一处：`flomo-web-crud` 支持删除 memo；`flomo-local-api` 出于安全边界不提供删除。

## 为什么拆成几个 skills

把所有能力塞进一个 skill，表面上简单，实际使用时会混在一起。查笔记、浏览器操作、批量导出、自我分析，依赖的工具和风险边界都不一样。

| 场景 | 走哪条路 | 原因 |
| --- | --- | --- |
| Mac 上快速查笔记 | `local-api` | 本地调用，不依赖 UI。 |
| Windows 上操作 | `web-crud` | 走浏览器路径，适合跨平台。 |
| 导出 Markdown | `memo-to-markdown` | 独立批处理场景，不需要和 CRUD 耦合。 |
| 自我分析 | `insight` | 这是 interpret，不是 query，需要专门的工作流。 |

`flomo-local-api` 还有一个小优势：它会先读你现有的 tag 体系，再优先复用成熟标签。长期用下来，标签不会被 agent 随手造乱。

## Flomo Insight 能做什么

你很难记住几千条笔记里写过什么，更难记住自己反复说过但没有做的事。

`flomo-insight` 主要看三类信号：

1. 重复模式：某个情绪、项目或人名在一段时间里反复出现，而且总和同一种场景绑定。

2. 意图和行动断裂：你多次写“想学 Rust”，但后续没有任何一条 memo 提到开始练习。

3. 隐形主题：你没有打 `#career` 标签，但最近很多 memo 都在谈升职、跳槽、收入或“值不值得”。

它不会只告诉你“最常出现的词是什么”。更有用的问题通常是：你在什么地方反复卡住？哪些事情一直被你写下来，却没有进入下一步？

## 和 flomo 官方 AI insight 的区别

官方 AI insight 更像月度摘要：这个月写了多少、常见关键词是什么、主题大概有哪些。它适合快速回顾。

`flomo-insight` 更适合追问模式本身。

| 官方 AI insight | flomo-insight |
| --- | --- |
| "你本月提到'焦虑'5次" | "这 5 次里有 4 次和周一有关，但没有一次提到提前准备" |
| 给你标签云 | 找意图和行动之间的断点 |
| 静态报告，看完即止 | 可以继续追问“为什么总是这样”或“最近 30 天有没有变化” |
| 基于表层关键词 | 基于行为模式和叙事结构 |

如果你只是想知道上个月记录了什么，官方 insight 够用。

如果你想复盘自己为什么总是在同一个问题上循环，`flomo-insight` 更合适。

## 典型场景速查

| 你想做什么 | 装这个 | 一句话命令 |
| --- | --- | --- |
| 查最近 30 天反复写什么 | `flomo-local-api` | "帮我总结最近 30 天的笔记主题" |
| 快速记一条并沿用已有 tag | `flomo-local-api` | "记一条 memo，关于 XXX" |
| Windows 上查改笔记 | `flomo-web-crud` | "查找并修改昨天的 memo" |
| 删掉一条 memo | `flomo-web-crud` | "删除标题为 XXX 的笔记" |
| 导出 2025 年笔记给 NotebookLM | `flomo-memo-to-markdown` | "导出 2025 笔记，按季度拆分" |
| 分析自己最近在想什么 | `flomo-insight` | "基于我的 flomo，分析我最近的状态" |
| 把困惑变成行动建议 | `flomo-insight` | "从我笔记里找盲区，给行动建议" |

## 安装

```bash
npx skills add Undertone0809/zee-agent-skills/flomo-skills
```

安装时可以选择全部安装，也可以只选择当前需要的 skill。

## Skill 源码路径

- [`flomo-local-api`](.agents/skills/flomo-local-api/SKILL.md)
- [`flomo-web-crud`](.agents/skills/flomo-web-crud/SKILL.md)
- [`flomo-memo-to-markdown`](.agents/skills/flomo-memo-to-markdown/SKILL.md)
- [`flomo-insight`](.agents/skills/flomo-insight/SKILL.md)

## 为什么做这个

flomo 很适合随手记录，但“记录下来”和“以后真的用上”是两回事。笔记越多，手动回顾越难。那些反复出现的想法、长期没有推进的计划、同一类情绪背后的触发点，也不会自己浮出来。

flomo-skills 的价值就在这里：让 agent 帮你把旧笔记重新拿出来用。查找、整理、导出是基础；更重要的是，它能帮你看见长期记录里的模式。
