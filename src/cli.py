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

from stats import count_chars, count_lines, count_words  # noqa: E402


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
    return parser


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
    if not (args.chars or args.lines or args.words):
        args.chars = args.lines = args.words = True

    if args.chars:
        print(f"字符数（含空白）：{count_chars(text)}")
        print(f"字符数（不含空白）：{count_chars(text, ignore_whitespace=True)}")
    if args.lines:
        print(f"行数：{count_lines(text)}")
    if args.words:
        print(f"词数：{count_words(text)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
