"""Step 03：CRITIC 客观赋权（待实现）。

CRITIC 的指标权重来自指标变异程度与指标间冲突性；不是 X 对 Y 的回归
系数，更不代表因果影响大小。赋权前需要明确具体评价指标集、指标方向、
无量纲化方式与零方差指标的处理原则。
"""


def main() -> None:
    raise NotImplementedError("CRITIC 阶段尚未实现：须先确定赋权对象与处理原则。")


if __name__ == "__main__":
    main()
