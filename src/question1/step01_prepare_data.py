"""Step 01：检查并导出年度宽表，不擅自填补缺失值。"""

import argparse
from pathlib import Path

from src.common.io import read_annual_data


def main() -> None:
    parser = argparse.ArgumentParser(description="第一问：验证年度合并表的基本质量")
    parser.add_argument("--input", required=True, help="CSV / XLSX 输入路径")
    parser.add_argument("--output", default="data/processed/q1_annual_clean.csv", help="输出 CSV 路径")
    parser.add_argument("--sheet", default="0", help="Excel 工作表名或从 0 开始的序号")
    parser.add_argument("--header-row", type=int, default=1, help="从 1 开始计数的标题行（默认 1）")
    args = parser.parse_args()
    if args.header_row < 1:
        parser.error("--header-row 必须大于等于 1")

    sheet: str | int = int(args.sheet) if args.sheet.isdecimal() else args.sheet
    df = read_annual_data(args.input, sheet_name=sheet, header=args.header_row - 1)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destination, index=False, encoding="utf-8-sig")
    print(f"校验通过：{len(df)} 个年度样本，年份 {df['year'].min()}—{df['year'].max()}")
    print(f"输出文件：{destination}")
    print("提醒：此步骤仅检查格式和基本数据质量，不等于来源/口径已经核实。")


if __name__ == "__main__":
    main()
