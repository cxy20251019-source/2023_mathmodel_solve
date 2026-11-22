# 文件：docs/append_run_log.py
# 所属目录：docs/（研究过程记录）
# 作用：将一次建模/核验工作的关键信息追加到 Markdown 实验日志。
# 输入：--stage、--input、--command、--issues、--conclusion、--next 参数。
# 输出：在 docs/run_log.md 的原有表格末尾新增一行（保留历史）。
# 运行示例：python -m docs.append_run_log --stage "数据检查" --conclusion "通过"
# 注意：日志内容应真实填写；本脚本只记录，不检验科研结论。

"""追加建模实验日志；不删除已有记录。"""

import argparse
from datetime import date
from pathlib import Path

DEFAULT_LOG = Path("docs/run_log.md")


def clean_cell(value: str) -> str:
    """在 Markdown 表格中安全显示输入的内容。"""
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\r", " ").replace("\n", " ").strip()


def append_record(path: Path, cells: list[str]) -> None:
    """在已有日志表格最后一行后插入记录，避免追加到表格外。"""
    if len(cells) != 7:
        raise ValueError("实验日志必须提供 7 个字段")
    if not path.is_file():
        raise FileNotFoundError(f"找不到实验日志文件：{path}")
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    table_start = next(
        (i for i, line in enumerate(lines) if line.startswith("| 日期 | 阶段 |")),
        None,
    )
    if table_start is None:
        raise ValueError("没有找到预期的实验日志 Markdown 表格")
    insert_at = table_start + 1
    while insert_at < len(lines) and lines[insert_at].startswith("|"):
        insert_at += 1
    row = "| " + " | ".join(clean_cell(value) for value in cells) + " |\n"
    lines.insert(insert_at, row)
    path.write_text("".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="向 docs/run_log.md 追加真实实验记录")
    parser.add_argument("--file", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--stage", required=True, help="阶段，例如数据核验")
    parser.add_argument("--input", default="未记录", help="本次使用的数据文件")
    parser.add_argument("--command", default="未记录", help="命令或代码版本")
    parser.add_argument("--issues", default="无/未记录", help="发现的问题")
    parser.add_argument("--conclusion", required=True, help="本次核验结论")
    parser.add_argument("--next", default="待确定", help="下一步")
    parser.add_argument("--date", default=date.today().isoformat(), help="YYYY-MM-DD")
    args = parser.parse_args()
    date.fromisoformat(args.date)
    append_record(
        args.file,
        [args.date, args.stage, args.input, args.command, args.issues, args.conclusion, args.next],
    )
    print(f"已追加记录到：{args.file}")


if __name__ == "__main__":
    main()
