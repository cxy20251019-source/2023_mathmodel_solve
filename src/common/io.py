# 文件：src/common/io.py
# 所属：公共工具层（被第一问的数据准备脚本调用）。
# 作用：读取年度 CSV/XLSX，将列名统一成 year、Y1、Y2、X1～X6，
#       验证年份唯一、指标为数值且无缺失，并按年份排序后返回 DataFrame。
# 输入：本地 CSV 或 XLSX；Excel 可指定工作表和标题行。
# 输出：内存中的 Pandas DataFrame；这个文件本身不负责保存 CSV。
# 调用者：src/question1/step01_prepare_data.py。
# 注意：只做格式和基础质量检查，不会填补缺失、推断指标正负向、
#       核实统计来源，也不代表数据已满足论文研究的全部要求。
# 当前状态：已实现基础读取和校验，不需要单独运行。

"""年度宽表的读取及最小质量校验：只检查数据，不擅自改口径或补缺失。"""

from pathlib import Path

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = ["year", "Y1", "Y2", "X1", "X2", "X3", "X4", "X5", "X6"]
INDICATOR_COLUMNS = REQUIRED_COLUMNS[1:]
YEAR_ALIASES = {"year", "年份", "年"}


def read_annual_data(path: str | Path, *, sheet_name: str | int = 0, header: int = 0) -> pd.DataFrame:
    """读取一张年度宽表并返回规范 9 列；发现异常就抛错，不做插值。

    参数：
      path: CSV / XLSX 路径
      sheet_name: Excel 工作表名或从 0 开始的序号
      header: 标题行的零基序号
    """
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"找不到输入文件：{source}")
    if header < 0:
        raise ValueError("header 必须是从 0 开始的非负整数")

    extension = source.suffix.lower()
    if extension == ".csv":
        df = pd.read_csv(source, header=header, encoding="utf-8-sig")
    elif extension == ".xlsx":
        df = pd.read_excel(source, sheet_name=sheet_name, header=header)
    else:
        raise ValueError(f"仅支持 CSV 或 XLSX，得到：{source.suffix}")

    if df.empty:
        raise ValueError("输入表没有可用记录")

    rename_map: dict[object, str] = {}
    for column in df.columns:
        key = str(column).strip()
        upper = key.upper()
        if key.lower() in YEAR_ALIASES:
            rename_map[column] = "year"
        elif upper in INDICATOR_COLUMNS:
            rename_map[column] = upper
        else:
            rename_map[column] = key

    df = df.rename(columns=rename_map)
    if df.columns.duplicated().any():
        duplicated = df.columns[df.columns.duplicated()].tolist()
        raise ValueError(f"规范化后出现重复列：{duplicated}")

    missing_cols = [name for name in REQUIRED_COLUMNS if name not in df.columns]
    if missing_cols:
        raise ValueError(f"缺少必要字段：{missing_cols}；现有列：{list(df.columns)}")

    out = df.loc[:, REQUIRED_COLUMNS].copy()
    numeric_year = pd.to_numeric(out["year"], errors="coerce")
    if numeric_year.isna().any() or not np.isfinite(numeric_year.to_numpy(dtype=float)).all():
        raise ValueError("year 列存在空白或无法转换为年份的值")
    if not (numeric_year % 1 == 0).all():
        raise ValueError("year 列应为整数年份")
    out["year"] = numeric_year.astype("int64")
    if out["year"].duplicated().any():
        years = out.loc[out["year"].duplicated(), "year"].tolist()
        raise ValueError(f"存在重复年份：{years}")

    for col in INDICATOR_COLUMNS:
        raw = out[col]
        # 千分位分隔符可以直接去除；其他文本值不会被猜测或替换。
        cleaned = raw.astype("string").str.strip().str.replace(",", "", regex=False)
        numeric = pd.to_numeric(cleaned, errors="coerce")
        bad = numeric.isna() | ~np.isfinite(numeric.to_numpy(dtype=float))
        if bad.any():
            years = out.loc[bad, "year"].tolist()
            raise ValueError(f"{col} 存在缺失或非数值记录，年份：{years}；请人工核查来源")
        out[col] = numeric.astype(float)

    return out.sort_values("year").reset_index(drop=True)
