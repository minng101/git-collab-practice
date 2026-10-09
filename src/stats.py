"""文本统计核心逻辑。

本模块只负责"计算"，不涉及任何输入输出，便于单元测试。
"""

from __future__ import annotations


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
    lines = text.splitlines()
    return len(lines)


def count_words(text: str) -> int:
    """统计词数（以空白字符作为分隔）。"""
    return len(text.split())
