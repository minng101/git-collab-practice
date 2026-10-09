# git-collab-practice

Git 与远程仓库基础协作流程实践项目。

本项目用于练习从**远程仓库创建 → 克隆到本地 → 功能开发与提交 → 版本回滚 → 推送到远程 → 本地与远程一致性验证**的完整协作流程。

## 项目简介

`textstats` 是一个极简的文本统计工具，用于演示真实的功能迭代过程。当前支持：

- 统计字符数（含/不含空白）
- 统计行数
- 统计词数
- 输出词频直方图（Top N）

选择这样一个"小而可运行"的项目，是为了让每一次提交都对应一个**可观察、可运行、可验证**的功能增量，而不是空洞的占位文件。

## 目录结构

```
git-collab-practice/
├── README.md           项目说明
├── .gitignore          Git 忽略规则
├── src/
│   ├── __init__.py
│   ├── stats.py        核心统计逻辑
│   └── cli.py          命令行入口
├── tests/
│   └── test_stats.py   单元测试
└── docs/
    └── workflow.md     协作流程记录
```

## 快速开始

```bash
# 统计字符数、行数、词数
python src/cli.py --file README.md --chars --lines --words

# 输出词频直方图（默认 Top 10）
python src/cli.py --file README.md --histogram

# 输出词频最高的 5 个词，并区分大小写
python src/cli.py --file README.md --histogram --top 5 --case-sensitive

# 运行单元测试
python -m pytest tests/ -v
```

## 词切分规则

词切分使用正则 `[A-Za-z0-9]+(?:['\-][A-Za-z0-9]+)*`，即：

- 连续的字母或数字构成一个词；
- 词内部允许出现单引号或连字符，因此 `don't`、`well-known` 会被正确识别为**一个词**，而不是被拆成 `don` 和 `t`；
- 统计词频时默认忽略大小写，`Apple`、`apple`、`APPLE` 会合并计数。

## 版本历史

| 提交 | 内容 |
| --- | --- |
| 初始提交 | 搭建项目骨架、README、.gitignore，实现基础文本统计 |
| 功能一 | 新增词频直方图输出与词切分规则 |
| 错误引入 | 故意引入行数统计回归缺陷，用于演示版本回滚 |
| 回滚 | 使用 `git revert` 撤销错误提交，恢复正确状态 |
| 收尾 | 补充单元测试与协作流程文档 |

详细的协作流程与回滚操作记录见 [docs/workflow.md](docs/workflow.md)。

## 许可证

MIT
