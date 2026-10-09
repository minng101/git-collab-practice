"""textstats 单元测试。

使用 Python 标准库 unittest 编写，无需安装第三方依赖：

    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# 把 src 目录加入模块搜索路径，使测试可以直接导入 stats
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from stats import (  # noqa: E402
    count_chars,
    count_lines,
    count_words,
    tokenize,
    word_frequencies,
)


class TestCountChars(unittest.TestCase):
    """count_chars 的行为约定。"""

    def test_counts_all_characters(self) -> None:
        self.assertEqual(count_chars("abc"), 3)

    def test_counts_whitespace_by_default(self) -> None:
        self.assertEqual(count_chars("a b"), 3)

    def test_can_ignore_whitespace(self) -> None:
        self.assertEqual(count_chars("a b\nc", ignore_whitespace=True), 3)

    def test_empty_text(self) -> None:
        self.assertEqual(count_chars(""), 0)


class TestCountLines(unittest.TestCase):
    """count_lines 的行为约定。

    这里的用例是版本回滚演示的关键：它们锁定了"以换行符结尾的文本
    不应多算一行"这一约定，因此能立刻捕获该行为的回归。
    """

    def test_empty_text_has_zero_lines(self) -> None:
        self.assertEqual(count_lines(""), 0)

    def test_single_line_without_trailing_newline(self) -> None:
        self.assertEqual(count_lines("abc"), 1)

    def test_trailing_newline_does_not_add_extra_line(self) -> None:
        """以换行符结尾时不应多算一行，这是容易被写错的地方。"""
        self.assertEqual(count_lines("abc\n"), 1)

    def test_two_lines(self) -> None:
        self.assertEqual(count_lines("abc\ndef"), 2)

    def test_two_lines_with_trailing_newline(self) -> None:
        self.assertEqual(count_lines("abc\ndef\n"), 2)

    def test_blank_line_is_counted(self) -> None:
        self.assertEqual(count_lines("abc\n\ndef"), 3)


class TestTokenize(unittest.TestCase):
    """tokenize 的词切分规则。"""

    def test_splits_on_whitespace_and_punctuation(self) -> None:
        self.assertEqual(tokenize("hello, world!"), ["hello", "world"])

    def test_keeps_apostrophe_inside_word(self) -> None:
        self.assertEqual(tokenize("don't"), ["don't"])

    def test_keeps_hyphen_inside_word(self) -> None:
        self.assertEqual(tokenize("well-known"), ["well-known"])

    def test_keeps_digits(self) -> None:
        self.assertEqual(tokenize("py3 version2"), ["py3", "version2"])

    def test_empty_text(self) -> None:
        self.assertEqual(tokenize(""), [])


class TestCountWords(unittest.TestCase):
    """count_words 的行为约定。"""

    def test_counts_words(self) -> None:
        self.assertEqual(count_words("one two three"), 3)

    def test_abbreviation_counts_as_one_word(self) -> None:
        self.assertEqual(count_words("don't stop"), 2)

    def test_empty_text(self) -> None:
        self.assertEqual(count_words(""), 0)


class TestWordFrequencies(unittest.TestCase):
    """word_frequencies 的行为约定。"""

    def test_counts_occurrences(self) -> None:
        result = word_frequencies("a b a")
        self.assertEqual(result, [("a", 2), ("b", 1)])

    def test_case_insensitive_by_default(self) -> None:
        result = word_frequencies("Apple apple APPLE")
        self.assertEqual(result, [("apple", 3)])

    def test_case_sensitive_mode(self) -> None:
        result = word_frequencies("Apple apple", case_sensitive=True)
        self.assertEqual(result, [("Apple", 1), ("apple", 1)])

    def test_ties_are_sorted_alphabetically(self) -> None:
        """同频次时按字典序升序，保证输出稳定可复现。"""
        result = word_frequencies("b a c")
        self.assertEqual(result, [("a", 1), ("b", 1), ("c", 1)])

    def test_top_n_limits_result(self) -> None:
        result = word_frequencies("a a a b b c", top_n=2)
        self.assertEqual(result, [("a", 3), ("b", 2)])

    def test_empty_text(self) -> None:
        self.assertEqual(word_frequencies(""), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)