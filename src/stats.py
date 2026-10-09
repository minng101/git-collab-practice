"""文本统计核心逻辑。

本模块只负责"计算"，不涉及任何输入输出，便于单元测试。
"""

from __future__ import annotations

import re
from collections import Counter

# 词切分规则：连续的字母/数字（允许内部含 ' 或 -）视为一个词
WORD_PATTERN = re.compile(r"[A-Za-z0-9]+(?:['\-][A-Za-z0-9]+)*")

# 直方图默认最多渲染的柱子数量
DEFAULT_TOP_N = 10


def count_chars(text: str, ignore_whitespace: bool = False) -> int:
    """统计字符数。

    Args:
        text: 待统计的文本。
        ignore_whitespace: 为 True 时不把空白字符计入总数。

    Returns:
        字符总数。
    """
    if ignore_whitespace:
        return sum(1 for ch in text if not ch.isspace())
    return len(text)


def count_lines(text: str) -> int:
    """统计行数。

    约定：空文本为 0 行；以换行符结尾的文本不额外多算一行。
    """
    if not text:
        return 0
    # 以换行符数量作为行数，处理文本时更直观
    return text.count("\n") + 1


def tokenize(text: str) -> list[str]:
    """把文本切分为词列表。

    规则：连续的字母与数字构成一个词，词内部允许出现单引号或连字符
    （例如 don't、well-known）。这样可以把常见英文缩写正确地当作一个词，
    而不是被拆成 don 和 t。
    """
    return WORD_PATTERN.findall(text)


def count_words(text: str) -> int:
    """统计词数。"""
    return len(tokenize(text))


def word_frequencies(
    text: str, *, case_sensitive: bool = False, top_n: int | None = None
) -> list[tuple[str, int]]:
    """统计词频。

    Args:
        text: 待统计的文本。
        case_sensitive: 为 False 时忽略大小写（默认）。
        top_n: 只返回出现次数最多的前 N 个词；None 表示返回全部。

    Returns:
        按出现次数降序排列的 (词, 次数) 列表；次数相同时按词字母序升序。
    """
    words = tokenize(text)
    if not case_sensitive:
        words = [w.lower() for w in words]

    # 先按词字典序排序，保证相同时次下的输出顺序稳定可复现
    counter = Counter(sorted(words))
    ranked = sorted(counter.items(), key=lambda item: (-item[1], item[0]))

    if top_n is not None:
        return ranked[:top_n]
    return ranked

