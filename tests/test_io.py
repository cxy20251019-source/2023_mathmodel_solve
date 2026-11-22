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
