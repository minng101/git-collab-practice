# git-collab-practice

Git 与远程仓库基础协作流程实践项目。

本项目用于练习从**远程仓库创建 → 克隆到本地 → 功能开发与提交 → 版本回滚 → 推送到远程 → 本地与远程一致性验证**的完整协作流程。

## 项目简介

`textstats` 是一个极简的文本统计工具，用于演示真实的功能迭代过程。当前支持：

- 统计字符数（含/不含空白）
- 统计行数
- 统计词数

选择这样一个"小而可运行"的项目，是为了让每一次提交都对应一个**可观察、可运行、可验证**的功能增量。

## 目录结构

```
git-collab-practice/
├── README.md           项目说明
├── .gitignore          Git 忽略规则
├── src/
│   ├── __init__.py
│   ├── stats.py        核心统计逻辑
│   └── cli.py          命令行入口
└── tests/              单元测试
```

## 快速开始

```bash
# 统计字符数、行数、词数
python src/cli.py --file README.md --chars --lines --words
```

## 许可证

MIT
