# 文件：data/check_sources.py
# 所属目录：data/（数据管理）
# 作用：检查 Y1、Y2、X1～X6 的来源登记表是否缺列、重复或缺少说明。
# 输入：默认 data/sources_template.csv，也可以使用 --file 指定登记表。
# 输出：终端中的错误与待补充项；不会修改来源表或伪造数据。
# 运行：python -m data.check_sources
# 注意：这里检查的是“来源记录完整性”，不是来源网站数据的真实性。

"""核查新能源汽车第一问的指标来源登记情况。"""

import argparse
import csv
from pathlib import Path

EXPECTED_VARIABLES = ["Y1", "Y2", "X1", "X2", "X3", "X4", "X5", "X6"]
REQUIRED_COLUMNS = [
    "variable", "meaning", "unit", "region", "year_range",
    "original_filename", "source_organization", "source_url",
    "download_date", "processing_notes", "status",
]
IMPORTANT_DETAILS = [
    "meaning", "unit", "region", "year_range",
    "original_filename", "source_organization", "source_url",
]


def audit_sources(path: Path) -> tuple[list[str], list[str]]:
    """返回 (格式错误, 有待补充的来源信息)，不修改原始文件。"""
    errors: list[str] = []
    warnings: list[str] = []

    if not path.is_file():
        return [f"找不到来源登记文件：{path}"], []

    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        columns = reader.fieldnames or []
        missing_cols = [column for column in REQUIRED_COLUMNS if column not in columns]
        if missing_cols:
            return [f"来源表缺少字段：{', '.join(missing_cols)}"], []
        rows = list(reader)

    seen: set[str] = set()
    for number, row in enumerate(rows, start=2):
        name = (row.get("variable") or "").strip().upper()
        if not name:
            errors.append(f"第 {number} 行没有填写指标名称")
            continue
        if name in seen:
            errors.append(f"第 {number} 行重复出现指标 {name}")
        seen.add(name)
        if name not in EXPECTED_VARIABLES:
            warnings.append(f"第 {number} 行存在未预设的指标 {name}，请确认用途")
            continue
        pending = [field for field in IMPORTANT_DETAILS if not (row.get(field) or "").strip()]
        if pending:
            warnings.append(f"{name} 的来源信息待补：{', '.join(pending)}")
        if (row.get("status") or "").strip().lower() in {"", "pending"}:
            warnings.append(f"{name} 尚未标记为已核验")

    for name in EXPECTED_VARIABLES:
        if name not in seen:
            errors.append(f"缺少指标登记行：{name}")

    return errors, warnings


def main() -> None:
    parser = argparse.ArgumentParser(description="检查第一问指标来源的登记完整性")
    parser.add_argument("--file", type=Path, default=Path("data/sources_template.csv"))
    args = parser.parse_args()
    errors, warnings = audit_sources(args.file)
    for item in errors:
        print(f"[错误] {item}")
    for item in warnings:
        print(f"[待补充] {item}")
    print(f"检查完成：{len(errors)} 个格式错误，{len(warnings)} 个待补充项。")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
