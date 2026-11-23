"""核查成对样本计数、未定义系数和跨年断档。"""

import pandas as pd
import pytest

from src.question1.step02_correlation import annual_changes, calculate_correlations


def test_correlations_use_common_observations():
    indicators = pd.DataFrame({
        "Y1": [1.0, 2.0, 3.0, 4.0, 5.0],
        "X1": [2.0, 4.0, None, None, 10.0],
        "X2": [None, 1.0, 2.0, None, None],
        "X3": [3.0, 3.0, 3.0, 3.0, 3.0],
    })
    matrices, counts = calculate_correlations(indicators)

    assert counts.loc["X1", "Y1"] == 3
    assert counts.loc["X2", "Y1"] == 2
    assert counts.loc["X3", "Y1"] == 5
    for matrix in matrices.values():
        assert matrix.loc["X1", "Y1"] == pytest.approx(1.0)
        assert pd.isna(matrix.loc["X2", "Y1"])
        assert pd.isna(matrix.loc["X3", "Y1"])


def test_changes_require_consecutive_years_and_two_valid_endpoints():
    data = pd.DataFrame({
        "year": [2017, 2018, 2020, 2021, 2022],
        "Y1": [1.0, 3.0, 9.0, 10.0, 14.0],
        "Y2": [1.0, 3.0, 9.0, 10.0, 14.0],
        **{f"X{i}": [1.0, None, 9.0, 10.0, 14.0] for i in range(1, 7)},
    })

    changes = annual_changes(data)

    assert changes["Y1"].dropna().to_dict() == {1: 2.0, 3: 1.0, 4: 4.0}
    assert changes["X1"].dropna().to_dict() == {3: 1.0, 4: 4.0}
