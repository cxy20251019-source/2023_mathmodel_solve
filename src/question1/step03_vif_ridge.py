"""第一问 · 第 03 步：计算 X2、X3、X5、X6 的 VIF，并分别拟合 Y1、Y2 的岭回归。

使用年度原值和共同有效年份。VIF 衡量解释变量之间的多重共线性。
岭回归系数描述在其余 X 指标取值固定时，某项 X 与目标 Y 的线性关联。

从项目根目录运行：
    python -m src.question1.step03_vif_ridge
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.common.io import INDICATOR_COLUMNS, read_annual_data

X_COLUMNS = ["X2", "X3", "X5", "X6"]
Y_COLUMNS = [name for name in INDICATOR_COLUMNS if name.startswith("Y")]
RIDGE_ALPHAS = np.logspace(-3, 3, 25)
INITIAL_TRAIN_YEARS = 5


def calculate_vif(predictors: pd.DataFrame) -> pd.DataFrame:
    """逐列用其余 X 指标做辅助回归，返回每个 X 的 R² 和 VIF。"""
    n, p = predictors.shape
    if n <= p:
        raise ValueError(f"VIF 辅助回归需要多于 {p} 个完整年度，目前只有 {n} 个")

    values = predictors.to_numpy(dtype=float)
    scale = values.std(axis=0)
    constant = predictors.columns[np.ptp(values, axis=0) == 0].tolist()
    if constant:
        raise ValueError(f"这些指标在共同样本中为常量，VIF 无法定义：{constant}")

    # 各列中心化后，含截距回归等价于对中心化数据做无截距回归。
    # 再按各列标准差缩放，以减少不同指标量级造成的数值误差。
    standardized = (values - values.mean(axis=0)) / scale
    rows = []
    for index, name in enumerate(predictors.columns):
        target = standardized[:, index]
        others = np.delete(standardized, index, axis=1)
        coefficients, *_ = np.linalg.lstsq(others, target, rcond=None)
        residual = target - others @ coefficients

        # 1 − R² = 残差平方和 / 总平方和。直接计算该比值可避免 R² 接近 1 时的消减误差。
        tolerance = float(np.clip((residual @ residual) / (target @ target), 0, 1))
        # 几乎为零的残差对应数值精度下的完全共线，以无穷大表示。
        vif = np.inf if tolerance <= 1e-24 else 1 / tolerance
        rows.append({"indicator": name, "auxiliary_r_squared": 1 - tolerance, "vif": vif, "n": n})
    return pd.DataFrame(rows).sort_values("vif", ascending=False, kind="stable")


def fit_ridge(predictors: np.ndarray, target: np.ndarray, alpha: float) -> tuple[np.ndarray, float]:
    """在训练集内标准化 X，拟合后返回原单位下的系数和截距。"""
    mean_x = predictors.mean(axis=0)
    mean_y = target.mean()
    scale_x = predictors.std(axis=0)
    # 某个早期训练窗口里的常量列中心化后全为 0，用比例 1 避免除以 0。
    scale_x = np.where(np.ptp(predictors, axis=0) == 0, 1, scale_x)
    standardized = (predictors - mean_x) / scale_x

    # 最小化残差平方和 + alpha × 系数平方和。先中心化 Y，截距自然不受惩罚。
    gram = standardized.T @ standardized
    penalty = alpha * np.eye(predictors.shape[1])
    scaled_coefficients = np.linalg.solve(gram + penalty, standardized.T @ (target - mean_y))
    coefficients = scaled_coefficients / scale_x
    intercept = float(mean_y - mean_x @ coefficients)
    return coefficients, intercept


def select_alpha(predictors: np.ndarray, target: np.ndarray) -> tuple[float, float]:
    """用扩张窗口选取 RMSE 最小的正则化参数，输入须按年份升序排列。"""
    if len(target) <= INITIAL_TRAIN_YEARS:
        raise ValueError(f"岭回归选参至少需要 {INITIAL_TRAIN_YEARS + 1} 个完整年度")

    rmses = []
    for alpha in RIDGE_ALPHAS:
        errors = []
        for next_row in range(INITIAL_TRAIN_YEARS, len(target)):
            # 每折用该行之前的所有可用年份训练，且均值和标准差只来自当折训练集。
            coefficients, intercept = fit_ridge(predictors[:next_row], target[:next_row], alpha)
            prediction = intercept + predictors[next_row] @ coefficients
            errors.append(target[next_row] - prediction)
        rmses.append(float(np.sqrt(np.mean(np.square(errors)))))
    best = int(np.argmin(rmses))
    return float(RIDGE_ALPHAS[best]), rmses[best]


def analyze_ridge(sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """为两个目标分别选参和拟合，返回系数表以及模型摘要。"""
    predictors = sample.loc[:, X_COLUMNS].to_numpy(dtype=float)
    coefficient_tables = []
    models = []
    for name in Y_COLUMNS:
        target = sample[name].to_numpy(dtype=float)
        scale_y = target.std()
        if np.ptp(target) == 0:
            raise ValueError(f"{name} 在共同样本中为常量，标准化岭回归系数无法定义")

        alpha, tuning_rmse = select_alpha(predictors, target)
        coefficients, intercept = fit_ridge(predictors, target, alpha)
        # 原单位系数乘以 X 的标准差，再除以 Y 的标准差，得到可比较的标准化系数。
        coefficient_tables.append(pd.DataFrame({
            "target": name,
            "indicator": X_COLUMNS,
            "coefficient": coefficients,
            "standardized_coefficient": coefficients * predictors.std(axis=0) / scale_y,
        }))
        models.append({
            "target": name,
            "alpha": alpha,
            "intercept": intercept,
            "n": len(sample),
            "tuning_rmse": tuning_rmse,
            "tuning_years": ",".join(map(str, sample.index[INITIAL_TRAIN_YEARS:])),
            "sample_years": ",".join(map(str, sample.index)),
        })
    return pd.concat(coefficient_tables, ignore_index=True), pd.DataFrame(models)


def main() -> None:
    parser = argparse.ArgumentParser(description="第一问：VIF 共线性诊断和岭回归")
    parser.add_argument(
        "--input", type=Path, default=Path("data/processed/q1_annual_clean.csv"), help="第 01 步输出的 CSV"
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path("outputs/question1/tables"), help="结果表目录"
    )
    args = parser.parse_args()

    try:
        annual_data = read_annual_data(args.input, allow_missing=True).set_index("year")
        # 只根据入模的四项 X 和两个 Y 筛选完整年份，供 VIF 和两个岭模型共同使用。
        sample = annual_data.dropna(subset=X_COLUMNS + Y_COLUMNS)
        vif = calculate_vif(sample.loc[:, X_COLUMNS])
        coefficients, models = analyze_ridge(sample)
    except (FileNotFoundError, ValueError) as error:
        parser.error(str(error))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for filename, table in (
        ("q1_vif.csv", vif),
        ("q1_ridge_coefficients.csv", coefficients),
        ("q1_ridge_models.csv", models),
    ):
        table.to_csv(args.output_dir / filename, index=False, encoding="utf-8-sig", float_format="%.12g")

    print(f"参与分析的 {len(sample)} 个年份：{sample.index.tolist()}")
    print(f"入模变量含缺失值的年份：{annual_data.index.difference(sample.index).tolist()}")
    print(vif.loc[:, ["indicator", "vif"]].to_string(index=False))
    print(models.loc[:, ["target", "alpha", "tuning_rmse"]].to_string(index=False))
    print(f"结果表目录：{args.output_dir}")


if __name__ == "__main__":
    main()
