# Zee Skills

[English](README.md)

Zee Skills 收集一些常用的 Agent Skills。它的用途很直接：把反复出现的工作流程整理成可复用的 agent 能力。

这里的 skill 不是写完就放着的提示词。真实任务会暴露很多问题：什么时候该触发、哪里容易失败、需要哪些证据、输出该达到什么标准。维护 skill，就是把这些问题写回说明、验证用例、eval、示例和打包方式里。

```text
practice
-> evidence
-> skill change
-> eval or validation case
-> better next run
```

## 这个仓库有什么

- [`meta-skills`](meta-skills/README.zh-CN.md)：创建、提炼、优化、评估和打包 Agent Skills。
- [`flomo-skills`](flomo-skills/README.md)：搜索、创建、编辑、导出和分析 flomo memos。
- [`codex-insights`](codex-insights/README.md)：从本地 Codex session 历史生成 Claude Code `/insights` 风格的使用洞察报告。
- [`gstack-style-doc`](gstack-style-doc/README.md)：生成 gstack 风格的技术文档。
- [`screenshot`](screenshot/README.md)：截取桌面、应用、窗口、区域或全屏截图。

每个文件夹的 README 会说明包含哪些 skill、怎么安装、适合在什么场景使用。

## 为什么有这个仓库

很多 agent workflow 都来自具体的一次实践：一次成功的 session、一次用户纠正、一个重复的 repo 操作、一个好用的 review 流程，或者某种稳定的研究习惯。它们如果只留在一段对话里，很快就会丢。

这个仓库用来把这些经验留下来：

- 把重复流程整理成可安装的 skill。
- 用真实执行痕迹和用户纠正来改进已有 skill。
- 增加 trigger tests 和 validation cases，让行为可以被审阅。
- 把领域知识放在真正会用到它的 workflow 附近。
- 打包 skill，让下一个 agent 能发现并使用。

`meta-skills` 是这套循环的核心。要从近期实践里创建新 skill，或者根据真实证据优化 project skill，先看它。

## 自迭代

改进 Agent Skills 不需要等到一次很大的人工 review。更实际的做法是每天看一小段真实 session，把高信号反馈转成 skill 维护任务。

在 Claude Code、Codex、OpenClaw，或者任何支持 scheduled work 的 agent runtime 里，可以创建两个自动化任务：

```text
看一下最近 30 个 Codex session，结合现有的 skills，有哪些新的需要 Conversation to Skill 吗？
```

```text
看一下最近 30 个 Codex session，结合现有的 skills，哪些 project skill 需要优化吗 Skill Optimizer？
```

这两个任务每天给你两类结果：

- 哪些重复实践值得提炼成新 skill。
- 哪些已有 skill 需要 patch、补边界、加 eval，或者做 benchmark。

报告必须基于证据。好的报告会指向真实 session、用户纠正、重复 workflow、failure class、缺失 trigger 或 validation gap。人只需要看高信号建议，然后批准值得合入的 patch。

```text
daily sessions
-> automated skill review reports
-> small human feedback
-> Conversation to Skill or Skill Optimizer patches
-> better skills for tomorrow's sessions
```

## 安装

安装你需要的文件夹：

```bash
npx skills add Undertone0809/zee-agent-skills/meta-skills
npx skills add Undertone0809/zee-agent-skills/flomo-skills
npx skills add Undertone0809/zee-agent-skills/codex-insights
npx skills add Undertone0809/zee-agent-skills/gstack-style-doc
npx skills add Undertone0809/zee-agent-skills/screenshot
```

`meta-skills` 和 `flomo-skills` 这类文件夹里有多个 skills。CLI 会让你选择安装一个、多个或全部。

## 常见工作流

从真实实践中创建新 skill：

```text
看一下最近 30 个 Codex session，结合现有的 skills，有哪些新的 workflow 应该变成 skill？
```

从使用证据中优化已有 skill：

```text
看一下最近 30 个 Codex session，结合现有的 skills，哪些 project skill 需要优化？
```

安装一个聚焦领域的 collection：

```bash
npx skills add Undertone0809/zee-agent-skills/meta-skills
```

## 仓库约定

- 顶层文件夹是维护中的 skill collections。
- 每个 collection 都有自己的 `README.md`。
- 嵌套 collection 使用文件夹级安装命令，不使用 repo root 安装命令。
- skill 尽量小而聚焦；triggers、workflow、边界、examples 和 validation cases 要写清楚。
