# 2023 APMCM C 题｜新能源汽车发展与影响因素建模

本仓库用于独立开展 2023 年亚太地区大学生数学建模竞赛 C 题的复现与研究。目标是 **数据来源可追溯、建模步骤可核验、图表与结论可复现**，不预设优秀论文中的答案。

> 状态：第一问的数据核验与模型准备阶段。此工程包仅包含结构、基础数据校验代码和后续步骤的待办脚本；**不包含原始数据与建模结论**。

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
│   ├── tables/               # 数据表与权重结果
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
| 02 | `step02_correlation.py` | X–Y、X–X Pearson / Spearman 相关性 | 待实现，先核查 01 |
| 03 | `step03_critic.py` | CRITIC 客观权重 | 待实现，先确定指标集与方向 |
| 04 | `step04_evaluation.py` | 发展水平综合评价与因素分析 | 方法待数据核验后决定 |
| 05 | `step05_sensitivity.py` | 敏感性和稳健性检验 | 预留 |
| 06 | `step06_visualization.py` | 论文图表汇总 | 预留 |

**关键区别**：CRITIC 根据指标变异性和指标间冲突性计算客观权重，不能直接用作 X 对 Y 的影响系数，更不代表因果关系。相关性大小也不能单独证明因果影响。Y1、Y2 的组合方式、X1～X6 的分析模型，需核对实际数据与题目后确定。

## 输入数据的最小接口

建议第一问年度合并宽表中有以下 9 列：

```text
year, Y1, Y2, X1, X2, X3, X4, X5, X6
```

每行是同一统计口径下的一个年份。暂不假设任何指标的具体含义、正负向或单位，须根据原始出处填写 `data/sources_template.csv`。支持输入 CSV 或 XLSX；年度列接受 `year`、`年份`、`年`，指标列接受大小写形式。多余列会被保留在原始输入中，但阶段 01 的规范输出只保留 9 个约定列。

现有《新能源汽车_Y1Y2_X1-X6_年度合并》可以放进 `data/interim/`，原始下载文件放进 `data/raw/`，不直接覆盖来源文件。

## 使用方法

在仓库根目录下：

```bash
python -m pip install -r requirements.txt
python -m pytest
python -m src.question1.step01_prepare_data --input "data/interim/年度合并.xlsx"
```

输入 Excel 若不在第一个工作表：`--sheet 工作表名`；若标题行不在第一行：`--header-row 2`（从 1 计数）。通过校验后输出 `data/processed/q1_annual_clean.csv`。如果指标缺失、年份重复、年份格式异常或指标不是纯数值，脚本将报错并阻止输出，**不会默认插值或填 0**。有缺失值时，请先制定处理决策并记录在 `docs/run_log.md`，再修改处理脚本。

### 约定

1. 原始数据不修改，只在 `interim`、`processed` 中做整理；每个变量来源、年份和单位必须可追踪。
2. 按“数据 → 相关性 → CRITIC → 建模 → 验证 → 论文”的顺序推进；每步有结果后人工核验。
3. `outputs` 用于可复现的分析输出；不允许用手工伪造的表格或图代替运行结果。
4. 后续题目目录仅预留，实际任务拆分以原题要求为准。
