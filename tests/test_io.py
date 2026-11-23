# 文件：tests/test_io.py
# 作用：自动测试数据读取函数 src/common/io.py 是否符合预期。
# 检查内容：CSV 列名标准化、年份排序、重复年份拦截、缺失值拦截、
#           缺少必要字段时报错、XLSX 文件能否正常读取。
# 使用数据：测试函数自己构造的模拟数据，不是真实新能源汽车观测值。
# 运行：在项目根目录执行 python -m pytest -q。
# 重要说明：测试通过只代表这些代码行为正确，不代表数据来源或模型科学性已核实。

"""仅用合成的示例数据测试数据读取契约，不构成真实建模结果。"""

import pandas as pd
import pytest

from src.common.io import read_annual_data, REQUIRED_COLUMNS


def sample(years=(2020, 2021)):
    return pd.DataFrame({
        "年份": list(years),
        **{name.lower(): [float(i + 1), float(i + 2)] for i, name in enumerate(REQUIRED_COLUMNS[1:])},
    })


def test_csv_schema_normalization_and_sorting(tmp_path):
    df = sample(years=(2021, 2020))
    input_file = tmp_path / "input.csv"
    df.to_csv(input_file, index=False, encoding="utf-8-sig")
    actual = read_annual_data(input_file)
    assert actual.columns.tolist() == REQUIRED_COLUMNS
    assert actual["year"].tolist() == [2020, 2021]
    assert len(actual) == 2


def test_duplicate_year_fails(tmp_path):
    input_file = tmp_path / "dup.csv"
    sample(years=(2020, 2020)).to_csv(input_file, index=False)
    with pytest.raises(ValueError, match="重复年份"):
        read_annual_data(input_file)


def test_missing_value_not_filled(tmp_path):
    input_file = tmp_path / "missing.csv"
    df = sample()
    df.loc[0, "x1"] = None
    df.to_csv(input_file, index=False)
    with pytest.raises(ValueError, match="X1"):
        read_annual_data(input_file)


def test_missing_column_fails(tmp_path):
    input_file = tmp_path / "columns.csv"
    sample().drop(columns=["y2"]).to_csv(input_file, index=False)
    with pytest.raises(ValueError, match="缺少必要字段"):
        read_annual_data(input_file)


def test_excel_input(tmp_path):
    input_file = tmp_path / "input.xlsx"
    sample().to_excel(input_file, index=False)
    assert read_annual_data(input_file)["year"].tolist() == [2020, 2021]


def test_excel_descriptive_headers_and_opt_in_missing(tmp_path):
    input_file = tmp_path / "input.xlsx"
    df = sample().rename(columns={"y1": "Y1 新能源汽车销量（万辆）", "x2": "X2 公共充电桩保有量（个）"})
    df.loc[0, "X2 公共充电桩保有量（个）"] = None
    df.to_excel(input_file, index=False)

    with pytest.raises(ValueError, match="X2"):
        read_annual_data(input_file)

    actual = read_annual_data(input_file, allow_missing=True)
    assert actual.columns.tolist() == REQUIRED_COLUMNS
    assert pd.isna(actual.loc[0, "X2"])
    assert actual.loc[1, "X2"] == df.loc[1, "X2 公共充电桩保有量（个）"]


def test_allow_missing_still_rejects_text(tmp_path):
    input_file = tmp_path / "input.csv"
    df = sample().astype({"x5": str})
    df.loc[0, "x5"] = "NA"
    df.to_csv(input_file, index=False)

    with pytest.raises(ValueError, match="X5"):
        read_annual_data(input_file, allow_missing=True)
