"""第一问 · 第 02 步：分析 X1～X6 与 Y1/Y2，以及 X 指标之间的相关性。

输入为第 01 步生成的年度 CSV。分别计算年度原值与相邻年份变化量的
Pearson 相关系数（线性关系）和 Spearman 秩相关系数（单调关系），并输出
每对指标实际使用的样本数。年度变化量用于初步检查共同时间趋势的影响。

从项目根目录运行：
    python -m src.question1.step02_correlation --allow-missing
"""

import argparse
from pathlib import Path

import matplotlib
import pandas as pd

from src.common.io import INDICATOR_COLUMNS, read_annual_data

Y_COLUMNS = ["Y1", "Y2"]
X_COLUMNS = [name for name in INDICATOR_COLUMNS if name.startswith("X")]
METHODS = ("pearson", "spearman")
MIN_PAIRS = 3


def annual_changes(annual_data: pd.DataFrame) -> pd.DataFrame:
    """对按年份升序排列的宽表计算相邻自然年的变化量（当年减上年）。"""
    indicators = annual_data.loc[:, INDICATOR_COLUMNS]
    # 差分两端任一值为空时，变化量自然为空。若年份断档，也留空以免跨年相减。
    consecutive = annual_data["year"].diff().eq(1)
    return indicators.diff().where(consecutive, axis=0)


def calculate_correlations(indicators: pd.DataFrame) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    """返回两种系数矩阵及对应的成对有效样本数矩阵。"""
    # 0/1 矩阵的列点积统计两列同时有效的行数。不同指标对可能使用不同年份。
    observed = indicators.notna().astype("int64")
    pair_counts = observed.T @ observed

    # pandas 在每对指标的共同样本上计算系数，Spearman 也在该子样本内计算秩。
    # 排除只有两个观测点时必然得到的完美相关。共同样本里若一列为常量，系数同样留空。
    matrices = {method: indicators.corr(method=method, min_periods=MIN_PAIRS) for method in METHODS}
    return matrices, pair_counts


def save_heatmaps(matrices: dict[str, pd.DataFrame], destination: Path, title: str) -> None:
    """将两种方法的 X–Y 与 X–X 子矩阵绘制在同一张图中。"""
    # 使用非交互式后端，使脚本可以在终端或没有图形界面的环境中运行。
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    figure, axes = plt.subplots(2, 2, figsize=(7.4, 8), width_ratios=(2, 6), layout="constrained")
    try:
        for row, (method, matrix) in enumerate(matrices.items()):
            for axis, columns, scope in zip(axes[row], (Y_COLUMNS, X_COLUMNS), ("X–Y", "X–X")):
                # 两种方法和两套数据共用 [-1, 1] 色标，灰格代表系数缺失。
                axis.set_facecolor("#e7eaee")
                sns.heatmap(
                    matrix.loc[X_COLUMNS, columns],
                    ax=axis,
                    annot=True,
                    fmt=".2f",
                    cmap="RdBu_r",
                    vmin=-1,
                    vmax=1,
                    square=True,
                    cbar=False,
                    linewidths=0.5,
                )
                axis.set_title(f"{method.title()}  {scope}")
                axis.tick_params(axis="both", length=0, labelrotation=0)
        figure.colorbar(axes[0, 0].collections[0], ax=axes, label="Correlation coefficient", shrink=0.85)
        figure.suptitle(f"{title}\nGray cells indicate undefined coefficients", fontsize=13)
        figure.savefig(destination, dpi=180)
    finally:
        plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description="第一问：年度指标的 Pearson 和 Spearman 相关性分析")
    parser.add_argument(
        "--input", type=Path, default=Path("data/processed/q1_annual_clean.csv"), help="第 01 步输出的 CSV"
    )
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/question1"), help="结果目录")
    parser.add_argument("--allow-missing", action="store_true", help="保留空白，每对指标仅使用共同有效样本")
    args = parser.parse_args()

    try:
        annual_data = read_annual_data(args.input, allow_missing=args.allow_missing)
    except (FileNotFoundError, ValueError) as error:
        parser.error(str(error))
    if len(annual_data) < MIN_PAIRS:
        parser.error(f"至少需要 {MIN_PAIRS} 个年度样本")

    tables = args.output_dir / "tables"
    figures = args.output_dir / "figures"
    tables.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)

    datasets = (
        ("levels", "Annual levels", annual_data.loc[:, INDICATOR_COLUMNS]),
        ("changes", "Year-over-year changes", annual_changes(annual_data)),
    )
    for label, title, indicators in datasets:
        matrices, pair_counts = calculate_correlations(indicators)
        prefix = f"q1_correlation_{label}"
        pair_counts.to_csv(tables / f"{prefix}_n.csv", encoding="utf-8-sig", index_label="indicator")
        for method, matrix in matrices.items():
            matrix.to_csv(
                tables / f"{prefix}_{method}.csv",
                encoding="utf-8-sig",
                index_label="indicator",
                float_format="%.8f",
            )
        save_heatmaps(matrices, figures / f"{prefix}.png", title)

    print(f"已分析 {len(annual_data)} 个年度，范围为 {annual_data['year'].min()}–{annual_data['year'].max()} 年。")
    print(f"相关系数和成对样本数已保存到 {tables}，热力图已保存到 {figures}。")


if __name__ == "__main__":
    main()
