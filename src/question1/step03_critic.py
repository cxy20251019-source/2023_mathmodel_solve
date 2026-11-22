# 文件：src/question1/step03_critic.py
# 第一问 · 第 03 步：CRITIC 客观赋权（尚未实现）。
# 目标：利用指标的变异程度与指标间冲突性，给综合评价指标确定客观权重。
# 计划输入：核验后的年度指标表、需要赋权的指标集合及指标方向。
# 计划输出：outputs/question1/tables/ 中的权重及计算明细。
# 需要先决定：给 Y1/Y2 赋权还是给其他评价指标赋权，以及标准化规则。
# 重要区别：CRITIC 权重 ≠ X 对 Y 的回归系数 ≠ 因果影响程度。
# 当前状态：只定义模型任务；运行会抛出 NotImplementedError。

"""Step 03：CRITIC 客观赋权（待实现）。

CRITIC 的指标权重来自指标变异程度与指标间冲突性；不是 X 对 Y 的回归
系数，更不代表因果影响大小。赋权前需要明确具体评价指标集、指标方向、
无量纲化方式与零方差指标的处理原则。
"""


def main() -> None:
    raise NotImplementedError("CRITIC 阶段尚未实现：须先确定赋权对象与处理原则。")


if __name__ == "__main__":
    main()
