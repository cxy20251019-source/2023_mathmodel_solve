# 文件：data/inspect_annual.py
# 所属目录：data/（数据管理）
# 作用：快速查看原始/合并数据的行列数、字段名称及缺失值数量。
# 输入：CSV 或 XLSX 文件，由 --input 指定；Excel 可指定 --sheet。
# 输出：仅在终端打印概况，不生成清洗表，也不修改原始数据。
# 运行：python -m data.inspect_annual --input "data/interim/年度合并.xlsx"
# 与 src 的区别：这是导入前的“预览”；src/question1/step01_* 是严格质量校验。
# 注意：本程序不会判断统计口径是否正确。

"""预览数据表结构，帮助人工确认年度合并表。"""

import argparse
from pathlib import Path

import pandas as pd


def inspect_table(path: Path, *, sheet: str | int = 0) -> pd.DataFrame:
    """读取待核查文件，保留原列名以便发现不一致的地方。"""
    if not path.is_file():
        raise FileNotFoundError(f"找不到文件：{path}")
    if path.suffix.lower() == ".xlsx":
        return pd.read_excel(path, sheet_name=sheet)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path, encoding="utf-8-sig")
    raise ValueError("请提供 .csv 或 .xlsx 文件")


def main() -> None:
    parser = argparse.ArgumentParser(description="预览数据列名、数据量和缺失情况")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--sheet", default="0", help="工作表名或从 0 开始的序号")
    args = parser.parse_args()
    sheet: str | int = int(args.sheet) if args.sheet.isdecimal() else args.sheet
    df = inspect_table(args.input, sheet=sheet)
    print(f"数据文件：{args.input}")
    print(f"行数：{df.shape[0]}，列数：{df.shape[1]}")
    print("列名：" + "、".join(str(column) for column in df.columns))
    print("缺失值数量：")
    print(df.isna().sum().to_string())
    print("提示：这只是数据预览，不能替代严格校验和数据来源核实。")


if __name__ == "__main__":
    main()
