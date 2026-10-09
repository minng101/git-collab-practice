"""textstats 命令行入口。

用法示例：
    python src/cli.py --file README.md --chars --lines --words
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 允许以脚本方式直接运行时导入同级模块
sys.path.insert(0, str(Path(__file__).resolve().parent))

from stats import (  # noqa: E402
    DEFAULT_TOP_N,
    count_chars,
    count_lines,
    count_words,
    word_frequencies,
)

# 直方图中每个计数单位对应的方块字符
BAR_BLOCK = "\u2588"


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="textstats",
        description="统计文本文件的字符数、行数与词数。",
    )
    parser.add_argument("--file", required=True, help="待统计的文本文件路径")
    parser.add_argument("--chars", action="store_true", help="输出字符数")
    parser.add_argument("--lines", action="store_true", help="输出行数")
    parser.add_argument("--words", action="store_true", help="输出词数")
    parser.add_argument("--histogram", action="store_true", help="输出词频直方图")
    parser.add_argument(
        "--top",
        type=int,
        default=DEFAULT_TOP_N,
        metavar="N",
        help=f"直方图只显示词频最高的 N 个词（默认 {DEFAULT_TOP_N}）",
    )
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="统计词频时区分大小写（默认忽略大小写）",
    )
    return parser


def render_histogram(
    frequencies: list[tuple[str, int]], width: int = 40
) -> str:
    """把词频数据渲染成文本直方图。

    Args:
        frequencies: (词, 次数) 列表，假定已按次数降序排列。
        width: 最长词条对应的方块数量。

    Returns:
        可直接打印的多行字符串。
    """
    if not frequencies:
        return "（没有可统计的词）"

    max_count = max(count for _, count in frequencies)
    label_width = max(len(word) for word, _ in frequencies)

    lines = []
    for word, count in frequencies:
        # 按最大值等比缩放，最少画一个方块，保证低频词也可见
        blocks = max(1, round(count / max_count * width))
        lines.append(f"{word:>{label_width}} | {BAR_BLOCK * blocks} {count}")
    return "\n".join(lines)



def main(argv: list[str] | None = None) -> int:
    """程序主入口，返回进程退出码。"""
    parser = build_parser()
    args = parser.parse_args(argv)

    path = Path(args.file)
    if not path.is_file():
        print(f"错误：找不到文件 {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")

    # 未指定任何统计项时，默认输出全部指标
    if not (args.chars or args.lines or args.words or args.histogram):
        args.chars = args.lines = args.words = True

    if args.chars:
        print(f"字符数（含空白）：{count_chars(text)}")
        print(f"字符数（不含空白）：{count_chars(text, ignore_whitespace=True)}")
    if args.lines:
        print(f"行数：{count_lines(text)}")
    if args.words:
        print(f"词数：{count_words(text)}")
    if args.histogram:
        frequencies = word_frequencies(
            text, case_sensitive=args.case_sensitive, top_n=args.top
        )
        print(f"\n词频直方图（Top {args.top}）：")
        print(render_histogram(frequencies))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
