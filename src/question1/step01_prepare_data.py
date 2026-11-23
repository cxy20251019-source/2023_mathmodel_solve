# 文件：src/question1/step01_prepare_data.py
# 第一问 · 第 01 步：数据准备与基础质量核验（已实现）。
# 作用：调用 src/common/io.py 读取合并后的年度数据，检查格式后导出建模宽表。
# 输入：data/interim/ 中的年度合并 CSV 或 XLSX（实际路径由 --input 指定）。
# 输出：默认 data/processed/q1_annual_clean.csv。
# 运行：在项目根目录执行
#       python -m src.question1.step01_prepare_data --input "data/interim/年度合并.xlsx"
# 参数：--sheet 可指定 Excel 工作表；--header-row 指定标题行（从 1 起）。
# 注意：默认拒绝缺失值。--allow-missing 保留指标空白，供探索性相关分析使用。
#       重复年份或非数值记录仍会报错，不填 0 或插值。
# 下一步：人工核对来源与统计口径，再运行 step02_correlation.py。

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
    parser.add_argument("--allow-missing", action="store_true", help="保留指标空白，供成对分析使用")
    args = parser.parse_args()
    if args.header_row < 1:
        parser.error("--header-row 必须大于等于 1")

    sheet: str | int = int(args.sheet) if args.sheet.isdecimal() else args.sheet
    df = read_annual_data(
        args.input, sheet_name=sheet, header=args.header_row - 1, allow_missing=args.allow_missing
    )
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destination, index=False, encoding="utf-8-sig")
    print(f"校验通过：{len(df)} 个年度样本，年份 {df['year'].min()}—{df['year'].max()}")
    for indicator, count in df.isna().sum().items():
        if count:
            years = df.loc[df[indicator].isna(), "year"].tolist()
            print(f"{indicator} 保留 {count} 个空白，年份：{years}")
    print(f"输出文件：{destination}")
    print("提醒：此步骤仅检查格式和基本数据质量，不等于来源/口径已经核实。")


if __name__ == "__main__":
    main()
