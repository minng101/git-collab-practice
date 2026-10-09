#!/usr/bin/env bash
#
# verify-sync.sh —— 验证本地仓库与远程仓库是否完全同步
#
# 检查项：
#   1. 工作区是否干净（没有未提交的改动）
#   2. 本地 HEAD 与远程分支的提交哈希是否一致（提交历史完全相同）
#   3. 本地与远程的文件清单是否一致（无文件遗漏或多余）
#   4. 本地是否存在未推送的提交
#
# 用法：
#   bash scripts/verify-sync.sh                 # 默认验证 origin/main
#   bash scripts/verify-sync.sh origin main     # 指定远程与分支
#
# 退出码：0 表示完全同步；1 表示存在不一致。

set -uo pipefail

REMOTE="${1:-origin}"
BRANCH="${2:-main}"

PASS=0
FAIL=0

ok()   { printf '  [OK]   %s\n' "$1"; PASS=$((PASS + 1)); }
bad()  { printf '  [FAIL] %s\n' "$1"; FAIL=$((FAIL + 1)); }
info() { printf '  [INFO] %s\n' "$1"; }

# 切换到仓库根目录，使脚本可在任意位置调用
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -z "${REPO_ROOT}" ]; then
    # 当前目录不是仓库时，尝试用脚本自身位置推断仓库根目录
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    REPO_ROOT="$(git -C "${SCRIPT_DIR}" rev-parse --show-toplevel 2>/dev/null)"
fi
if [ -z "${REPO_ROOT}" ]; then
    echo "错误：找不到 Git 仓库。请在仓库目录内运行，或确认脚本位于仓库中。" >&2
    exit 1
fi
cd "${REPO_ROOT}" || {
    echo "错误：无法进入仓库目录 ${REPO_ROOT}" >&2
    exit 1
}

echo "=============================================="
echo " 本地 / 远程 仓库一致性验证"
echo "=============================================="
echo " 仓库路径 : $(pwd)"
info "远程名称 : ${REMOTE}"
info "分支名称 : ${BRANCH}"
echo

# --- 前置检查：远程分支是否存在 -------------------------------------------
echo "[前置] 获取远程最新状态"
if ! git fetch --quiet "${REMOTE}" 2>/dev/null; then
    echo "错误：无法连接远程 '${REMOTE}'，请检查网络与远程配置。" >&2
    exit 1
fi
REMOTE_REF="refs/remotes/${REMOTE}/${BRANCH}"
if ! git rev-parse --verify --quiet "${REMOTE_REF}" >/dev/null; then
    echo "错误：远程分支 '${REMOTE}/${BRANCH}' 不存在。" >&2
    echo "      请确认分支名，或先执行：git push -u ${REMOTE} ${BRANCH}" >&2
    exit 1
fi
ok "远程分支 ${REMOTE}/${BRANCH} 存在"

# --- 检查 1：工作区干净 ---------------------------------------------------
echo
echo "[1/4] 检查工作区状态"
if [ -z "$(git status --porcelain)" ]; then
    ok "工作区干净，没有未提交的改动"
else
    bad "工作区存在未提交的改动："
    git status --short | sed 's/^/         /'
fi

# --- 检查 2：提交哈希一致 -------------------------------------------------
echo
echo "[2/4] 检查提交历史"
LOCAL_SHA="$(git rev-parse HEAD)"
REMOTE_SHA="$(git rev-parse "${REMOTE_REF}")"
info "本地 HEAD        : ${LOCAL_SHA}"
info "${REMOTE}/${BRANCH} : ${REMOTE_SHA}"
if [ "${LOCAL_SHA}" = "${REMOTE_SHA}" ]; then
    ok "提交哈希完全一致，历史逐字节相同"
else
    bad "提交哈希不一致，本地与远程历史存在差异"
    echo "         本地领先远程的提交："
    git log --oneline "${REMOTE_REF}..HEAD" | sed 's/^/           /' || true
    echo "         远程领先本地的提交："
    git log --oneline "HEAD..${REMOTE_REF}" | sed 's/^/           /' || true
fi

# --- 检查 3：文件清单一致 -------------------------------------------------
echo
echo "[3/4] 检查文件清单"
LOCAL_TREE="$(git ls-tree -r --name-only HEAD)"
REMOTE_TREE="$(git ls-tree -r --name-only "${REMOTE_REF}")"
LOCAL_COUNT="$(printf '%s\n' "${LOCAL_TREE}" | grep -c . || true)"
REMOTE_COUNT="$(printf '%s\n' "${REMOTE_TREE}" | grep -c . || true)"
info "本地文件数 : ${LOCAL_COUNT}"
info "远程文件数 : ${REMOTE_COUNT}"
if [ "${LOCAL_TREE}" = "${REMOTE_TREE}" ]; then
    ok "文件清单完全一致，无遗漏或多出的文件"
    printf '%s\n' "${LOCAL_TREE}" | sed 's/^/           /'
else
    bad "文件清单不一致"
    # 借助临时文件比较（进程替换在部分 bash 环境下不可用）
    TMP_LOCAL="$(mktemp)"
    TMP_REMOTE="$(mktemp)"
    printf '%s\n' "${LOCAL_TREE}"  | sort > "${TMP_LOCAL}"
    printf '%s\n' "${REMOTE_TREE}" | sort > "${TMP_REMOTE}"
    echo "         仅存在于本地："
    comm -23 "${TMP_LOCAL}" "${TMP_REMOTE}" | sed 's/^/           /'
    echo "         仅存在于远程："
    comm -13 "${TMP_LOCAL}" "${TMP_REMOTE}" | sed 's/^/           /'
    rm -f "${TMP_LOCAL}" "${TMP_REMOTE}"
fi

# --- 检查 4：是否存在未推送提交 -------------------------------------------
echo
echo "[4/4] 检查未推送的提交"
UNPUSHED="$(git log --oneline "${REMOTE_REF}..HEAD" | wc -l | tr -d ' ')"
if [ "${UNPUSHED}" = "0" ]; then
    ok "没有未推送的提交，全部提交已同步到远程"
else
    bad "存在 ${UNPUSHED} 个未推送的提交"
fi

# --- 汇总 -----------------------------------------------------------------
echo
echo "=============================================="
echo " 验证汇总"
echo "=============================================="
echo " 提交历史 : $(git log --oneline | wc -l | tr -d ' ') 次提交"
echo " 已跟踪文件 : ${LOCAL_COUNT} 个"
echo " 通过 ${PASS} 项，失败 ${FAIL} 项"
echo "=============================================="

if [ "${FAIL}" -eq 0 ]; then
    echo " 结论：本地与远程完全同步 ✓"
    exit 0
fi

echo " 结论：本地与远程存在差异 ✗"
exit 1
