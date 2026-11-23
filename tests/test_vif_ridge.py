"""核对 VIF、带截距岭回归和入模变量筛选。"""

import sys

import numpy as np
import pandas as pd
import pytest

from src.question1.step03_vif_ridge import calculate_vif, fit_ridge, main


@pytest.mark.parametrize("second, expected", [([-2, 0, 0, 2], 2.0), ([-3, -3, 3, 3], np.inf)])
def test_vif_for_correlated_or_collinear_predictors(second, expected):
    predictors = pd.DataFrame({"X1": [-1, -1, 1, 1], "X2": second})

    vif = calculate_vif(predictors).set_index("indicator")["vif"]

    assert vif.to_dict() == pytest.approx({"X1": expected, "X2": expected})


def test_ridge_penalizes_the_slope_but_not_the_intercept():
    predictors = np.array([[10.0], [20.0], [30.0]])
    target = np.array([2.0, 4.0, 6.0])

    coefficients, intercept = fit_ridge(predictors, target, alpha=3.0)

    # X 标准化后平方和为 3。alpha=3 使 OLS 斜率减半，拟合线仍经过样本均值。
    assert coefficients == pytest.approx([0.1])
    assert intercept == pytest.approx(2.0)


def test_results_use_only_retained_predictors(tmp_path, monkeypatch):
    years = list(range(2018, 2024))
    sample = pd.DataFrame({
        "year": years,
        "Y1": [1, 2, 4, 5, 7, 10],
        "Y2": [1, 3, 5, 7, 10, 15],
        "X1": [None] * len(years),
        "X2": [1, 2, 4, 3, 5, 7],
        "X3": [2, 1, 3, 4, 7, 5],
        "X4": [None] * len(years),
        "X5": [8, 6, 5, 7, 4, 2],
        "X6": [1, 3, 2, 4, 6, 5],
    })
    input_path = tmp_path / "annual.csv"
    output_dir = tmp_path / "tables"
    sample.to_csv(input_path, index=False)
    monkeypatch.setattr(sys, "argv", ["step03_vif_ridge", "--input", str(input_path), "--output-dir", str(output_dir)])

    main()

    expected = {"X2", "X3", "X5", "X6"}
    vif = pd.read_csv(output_dir / "q1_vif.csv")
    coefficients = pd.read_csv(output_dir / "q1_ridge_coefficients.csv")
    assert set(vif["indicator"]) == expected
    assert vif["n"].eq(len(years)).all()
    assert coefficients.groupby("target")["indicator"].agg(set).to_dict() == {"Y1": expected, "Y2": expected}
