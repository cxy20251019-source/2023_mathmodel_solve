# 2023 APMCM C 题｜新能源汽车发展与影响因素建模

本仓库用于独立开展 2023 年亚太地区大学生数学建模竞赛 C 题的复现与研究。目标是 **数据来源可追溯、建模步骤可核验、图表与结论可复现**，不预设优秀论文中的答案。

> 状态：第一问已完成年度数据校验、探索性相关分析、VIF 共线性诊断，以及 Y1 和 Y2 的岭回归试算。指标来源与统计口径仍待核实。

## 项目目录

```text
2023_mathmodel_solve/
├── data/
│   ├── raw/                  # 原始数据（保留下载原貌）
│   ├── interim/              # 合并后、最终清洗前的年度数据
│   ├── processed/            # 清洗结果
│   ├── README.md             # 数据接口及注意事项
│   └── sources_template.csv  # 来源登记模板
├── src/
│   ├── common/               # 共用读取与校验函数
│   ├── question1/            # 第一问步骤 01—06
│   ├── question2/            # 后续问题预留
│   └── question3/            # 后续问题预留
├── outputs/question1/
│   ├── tables/               # 相关性、VIF 与回归结果
│   ├── figures/              # 论文图
│   └── validation/           # 稳健性和敏感性结果
├── paper/
│   ├── sections/             # 论文各部分
│   └── references/           # 引用资料
├── docs/
│   ├── model_decisions.md    # 方法决策与解释边界
│   └── run_log.md            # 阶段验收与运行日志
├── tests/                   # 基础测试
├── requirements.txt
└── .gitignore
```

## 第一问：依次推进，不一键出结论

| 顺序 | 文件 | 阶段 | 本次状态 |
|---|---|---|---|
| 01 | `step01_prepare_data.py` | 年度数据读取、列名、类型、缺失与年份核查 | **已实现基础校验** |
| 02 | `step02_correlation.py` | X–Y、X–X Pearson / Spearman 相关性 | 已实现年度原值和一阶差分分析 |
| 03 | `step03_vif_ridge.py` | VIF 共线性诊断与岭回归 | 以 X2、X3、X5、X6 诊断共线性并分别拟合 Y1、Y2 |
| 04 | `step04_evaluation.py` | 发展水平综合评价与因素分析 | 方法待数据核验后决定 |
| 05 | `step05_sensitivity.py` | 敏感性和稳健性检验 | 预留 |
| 06 | `step06_visualization.py` | 论文图表汇总 | 预留 |

第 02 步衡量两项指标之间的相关性。第 03 步用 VIF 衡量一个 X 指标能在多大程度上由其余 X 指标线性解释，再用岭回归估计每项 X 与 Y 的调整后线性关联。

## 输入数据的最小接口

建议第一问年度合并宽表中有以下 9 列：

```text
year, Y1, Y2, X1, X2, X3, X4, X5, X6
```

每行是同一统计口径下的一个年份。暂不假设任何指标的具体含义、正负向或单位，须根据原始出处填写 `data/sources_template.csv`。支持输入 CSV 或 XLSX。年度列接受 `year`、`年份`、`年`。指标代码不区分大小写，代码后可用空格附上名称和单位，例如 `Y1 新能源汽车销量（万辆）`。阶段 01 的规范输出只保留 9 个约定列。

年度合并表位于 `data/interim/`。各指标的原始来源文件放在 `data/raw/`。

## 使用方法

在仓库根目录下：

```bash
python -m pip install -r requirements.txt
python -m pytest
python -m src.question1.step01_prepare_data --input "data/interim/新能源汽车_Y1Y2_X1-X6_年度合并 (1).xlsx" --allow-missing
python -m src.question1.step02_correlation --allow-missing
python -m src.question1.step03_vif_ridge
```

第 01 步输出 `data/processed/q1_annual_clean.csv`。可用 `--sheet` 指定工作表，用 `--header-row` 指定从 1 开始计数的标题行。两步默认拒绝指标缺失。这里显式传入 `--allow-missing`，保留单元格空白。重复年份、异常年份和非数值指标仍会报错。

第 02 步将 Pearson、Spearman 和成对样本数矩阵保存到 `outputs/question1/tables/`，热力图保存到 `outputs/question1/figures/`。文件名中的 `levels` 表示年度原值，`changes` 表示相邻自然年的变化量。每个系数使用该指标对共同有效的样本。共同有效样本少于 3 个或配对后有常量列时，系数留空。不同指标对可能覆盖不同的年份，读结果时请同时核对样本数和差分结果。

第 03 步使用 X2、X3、X5、X6、Y1、Y2 均有观测值的年度原值。`q1_vif.csv` 记录共线性诊断，`q1_ridge_coefficients.csv` 记录原单位系数与标准化系数，`q1_ridge_models.csv` 记录正则化参数、截距、样本年份和调参误差。三张表保存在 `outputs/question1/tables/`。具体口径见 `docs/model_decisions.md`。

### 约定

1. 原始数据不修改，只在 `interim`、`processed` 中做整理；每个变量来源、年份和单位必须可追踪。
2. 按“数据 → 相关性 → VIF 与岭回归 → 评价 → 验证 → 论文”的顺序推进。每步有结果后人工核验。
3. `outputs` 用于可复现的分析输出；不允许用手工伪造的表格或图代替运行结果。
4. 后续题目目录仅预留，实际任务拆分以原题要求为准。
