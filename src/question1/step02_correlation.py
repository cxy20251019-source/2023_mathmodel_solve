# 文件：src/question1/step02_correlation.py
# 第一问 · 第 02 步：相关性分析（尚未实现，仅保留阶段接口）。
# 目标：分析 X1～X6 与 Y1/Y2 的相关关系，并检查 X 指标之间的相关性。
# 计划输入：data/processed/q1_annual_clean.csv（第一步确认的数据）。
# 计划输出：outputs/question1/tables/ 中的相关矩阵及 figures/ 中的热力图。
# 候选方法：Pearson（线性相关）、Spearman（单调关系）。
# 注意：必须同时检查样本量、年份趋势造成的伪相关及指标口径。
# 当前状态：运行会抛出 NotImplementedError，表示尚未计算结果。
# 下一步：数据通过验收后，才实现此模块。

"""Step 02：相关性矩阵（待实现）。

预定输入：data/processed/q1_annual_clean.csv。
待核验项目：样本量、趋势性伪相关、X–Y Pearson/Spearman 关系、X–X 共线性。
预定输出：outputs/question1/tables/ 以及 figures/。

当前仅保留职责边界。第一步数据验收前不擅自运行。
"""


def main() -> None:
    raise NotImplementedError("相关性阶段尚未实现：请先核验第一步的数据。")


if __name__ == "__main__":
    main()
