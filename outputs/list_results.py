# 文件：outputs/list_results.py
# 所属目录：outputs/（计算结果归档）
# 作用：列出第一问 tables/、figures/、validation/ 下已有的结果文件。
# 输入：默认输出目录 outputs/question1/；也可通过 --root 指定。
# 输出：在终端显示实际存在的结果文件和数量，不生成虚构的结果。
# 运行：python -m outputs.list_results
# 提醒：结果文件必须由建模脚本产生并通过核验；.gitkeep 不计入成果。

"""列出数学建模已经生成的结果文件。"""

import argparse
from pathlib import Path

CATEGORIES = ("tables", "figures", "validation")


def list_results(root: Path) -> dict[str, list[Path]]:
    """只列实际文件，跳过目录占位和隐藏文件。"""
    output: dict[str, list[Path]] = {}
    for category in CATEGORIES:
        folder = root / category
        output[category] = sorted(
            (p for p in folder.rglob("*") if p.is_file() and not p.name.startswith(".")),
            key=lambda item: str(item),
        ) if folder.is_dir() else []
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="查看当前已有的建模结果文件")
    parser.add_argument("--root", type=Path, default=Path("outputs/question1"))
    args = parser.parse_args()
    records = list_results(args.root)
    for category, paths in records.items():
        print(f"{category}: {len(paths)} 个文件")
        for path in paths:
            print(f"  - {path}")
    print("备注：空目录不代表建模失败，可能尚未推进到该阶段。")


if __name__ == "__main__":
    main()
