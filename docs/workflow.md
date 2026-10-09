# Git 与远程仓库基础协作流程记录

本文档记录 `git-collab-practice` 项目从远程仓库创建到本地开发、版本回滚、推送同步的完整流程，可用于作业验收对照。

---

## 一、环境信息

| 项目 | 值 |
| --- | --- |
| 操作系统 | Windows |
| Git 版本 | `git version 2.55.0.windows.5` |
| Git 安装路径 | `D:\Git` |
| Python 版本 | `Python 3.14.7`（仅用标准库，无第三方依赖） |
| 远程平台 | GitHub |
| 远程仓库 | `https://github.com/minng101/git-collab-practice` |
| 本地路径 | `<工作区>\git-collab-practice` |
| 提交者身份 | `minng101 <1275211933@qq.com>` |

---

## 二、流程总览

```
① GitHub 创建公开仓库（勾选 Add README）
        ↓
② git clone 到本地
        ↓
③ 本地开发：多次功能提交（每个功能一次提交）
        ↓
④ 版本回滚：故意引入错误提交 → 测试暴露缺陷 → git revert 恢复
        ↓
⑤ git push 推送到远程
        ↓
⑥ 验证本地与远程的文件、分支、提交历史完全一致
```

---

## 三、关键操作与命令

### 1. 远程仓库创建

在 GitHub 上创建**公开**仓库 `git-collab-practice`，仓库名与本地项目名保持一致，初始化时勾选 **Add a README file**，使远程仓库自带一个初始提交。

### 2. 克隆到本地

```bash
git clone https://github.com/minng101/git-collab-practice.git
cd git-collab-practice
```

克隆后 `git log` 可以看到远程的 README 初始提交，此时本地分支 `master` 已自动与 `origin/master` 建立跟踪关系（`git status` 会显示 `Your branch is up to date with 'origin/master'`）。

### 3. 配置提交身份

```bash
git config --global user.name "minng101"
git config --global user.email "1275211933@qq.com"
```

### 4. 功能开发与分次提交

每次提交都对应一个可运行、可验证的功能增量，提交信息采用 `type: 摘要` + 详细正文的规范写法：

| 序号 | 提交信息摘要 | 内容 |
| --- | --- | --- |
| 1 | `chore: 初始化 textstats 项目骨架并实现基础文本统计` | 目录结构、README、.gitignore、`count_chars`/`count_lines`/`count_words`、CLI 入口 |
| 2 | `feat: 新增词频直方图输出与词切分规则` | 词切分正则、`tokenize`、`word_frequencies`、`--histogram`/`--top`/`--case-sensitive` |
| 3 | `test: 为文本统计核心逻辑补充 24 个单元测试` | 标准库 unittest 测试套件 |
| 4 | `fix: 优化行数统计的换行符处理逻辑` | **故意引入的错误提交**，见第四节 |
| 5 | `Revert "fix: 优化行数统计的换行符处理逻辑"` | **回滚提交**，撤销第 4 次提交 |
| 6 | `docs: 补充协作流程记录与使用说明` | 本文档 |

推送命令：

```bash
git push origin master
```

### 5. 查看状态与历史的常用命令

```bash
git status                 # 查看工作区与暂存区状态
git log --oneline --graph  # 以图形方式查看提交历史
git log --stat             # 查看每次提交改动的文件
git diff                   # 查看未暂存的改动
git diff --cached          # 查看已暂存待提交的改动
git remote -v              # 查看远程仓库地址
git branch -vv             # 查看本地分支及其跟踪的远程分支
```

---

## 四、版本回滚演示（核心环节）

### 4.1 故意引入错误

为了演示版本回滚，先故意引入一个**看起来合理但实际错误**的改动：把行数统计从"按行切分"改为"按换行符数量 +1"。

```diff
 def count_lines(text: str) -> int:
     """统计行数。

     约定：空文本为 0 行；以换行符结尾的文本不额外多算一行。
     """
     if not text:
         return 0
-    lines = text.splitlines()
-    return len(lines)
+    # 以换行符数量作为行数，处理文本时更直观
+    return text.count("\n") + 1
```

这个改动对 `"abc"` 这类不带结尾换行的文本是正确的，所以不容易在随手测试中暴露；但它**破坏了"以换行符结尾不多算一行"的既有约定**，属于典型的静默回归缺陷。

### 4.2 用测试暴露缺陷

```bash
python -m unittest discover -s tests -v
```

结果：**24 项测试中 2 项失败**

```
FAIL: test_trailing_newline_does_not_add_extra_line
AssertionError: 2 != 1

FAIL: test_two_lines_with_trailing_newline
AssertionError: 3 != 2

Ran 24 tests in 0.001s
FAILED (failures=2)
```

这正是第 3 次提交中专门锁定"结尾换行不额外计数"的用例发挥作用的地方 —— 回归被立刻捕获，而不是等到线上才发现。

### 4.3 执行回滚

```bash
git revert HEAD --no-edit
```

生成反向提交 `Revert "fix: 优化行数统计的换行符处理逻辑"`，其内容与缺陷提交互为镜像：

```diff
-    # 以换行符数量作为行数，处理文本时更直观
-    return text.count("\n") + 1
+    lines = text.splitlines()
+    return len(lines)
```

### 4.4 验证恢复

```bash
python -m unittest discover -s tests -v
```

结果：**24 项测试全部通过**

```
Ran 24 tests in 0.001s
OK
```

### 4.5 为什么用 revert 而不是 reset

| 操作 | 原理 | 适用场景 |
| --- | --- | --- |
| `git reset --hard HEAD~1` | **移动分支指针**，丢弃提交，重写历史 | 提交**尚未推送**，只有自己在本地犯错 |
| `git revert HEAD` | **新增一个反向提交**来抵消改动，不改写历史 | 提交**已经推送**，或其他人可能已基于它工作 |

本项目采用 `revert`，因为该错误提交属于共享历史的一部分；如果强行 `reset` 再强推（`push -f`），会让其他协作者本地历史错乱。`revert` 保留了"犯错 → 发现 → 修复"的完整轨迹，这正是版本控制应有的可追溯性。

> 补充：如果错误提交只在本地、尚未推送，也可以用 `git reset --hard <正确提交>` 快速丢弃，操作更干净。判断依据始终是**这段历史是否已经公开**。

---

## 五、本地与远程一致性验证

推送完成后，通过以下方式确认本地与远程完全同步。

### 5.1 确认工作区干净

```bash
git status
# On branch master
# Your branch is up to date with 'origin/master'.
# nothing to commit, working tree clean
```

### 5.2 比较本地与远程提交哈希

```bash
git rev-parse HEAD            # 本地 HEAD 的完整哈希
git rev-parse origin/master   # 远程跟踪分支的完整哈希
```

两者**必须完全相同**，说明提交历史逐字节一致。

### 5.3 直接查询远程仓库真实状态

不使用本地缓存，直接读取远程的 ref 与提交列表，避免"本地自说自话"：

```bash
git ls-remote origin          # 远程所有引用的真实哈希
git fetch origin              # 拉取远程最新对象
git log origin/master --oneline   # 远程分支上的提交历史
```

### 5.4 比较文件清单，确认无遗漏

```bash
# 列出本地 HEAD 追踪的所有文件
git ls-tree -r --name-only HEAD

# 列出远程跟踪分支追踪的所有文件
git ls-tree -r --name-only origin/master
```

两份清单需完全一致。此外用 `git status` 应得到 `working tree clean`，表示没有任何未提交或未推送的内容。

### 5.5 干净的克隆验证（最严格的验证方式）

最彻底的做法是**把远程仓库重新克隆到一个干净目录**，然后比对两边的文件树与提交历史。若完全一致，即可证明远程仓库完整包含了所有内容，无关本地状态。

---

## 六、验收标准对照

| 验收要求 | 完成情况 |
| --- | --- |
| （1）远程仓库包含完整项目文件与清晰提交历史，至少 3 次有意义的代码提交 | 共 6 次提交，覆盖骨架搭建、功能开发、测试补充、缺陷修复、版本回滚、文档补充，每次提交均附详细说明 |
| （2）展示完整版本控制流程：初始提交、功能开发提交、版本回滚操作 | 初始提交 + 2 次功能提交 + 1 次测试提交 + 1 次错误提交 + 1 次 revert 回滚提交 |
| （3）验证本地与远程内容完全同步，无文件遗漏或版本不一致 | 通过 `git status`、`git rev-parse`、`git ls-remote`、`git ls-tree` 及干净克隆比对五重验证 |
| （4）体现从远程仓库克隆、本地开发、版本控制到代码推送的标准协作模式 | 从 GitHub 创建仓库并克隆起步，本地开发后推送，全程使用标准分支与远程跟踪机制 |
