# 文件：paper/check_materials.py
# 所属目录：paper/（论文材料整理）
# 作用：检查论文分节、参考资料、第一问图表是否已经有文件。
# 输入：paper/sections、paper/references、outputs/question1 下的实际文件。
# 输出：终端中的材料清单数量；--strict 要求各项齐全才返回成功状态。
# 运行：python -m paper.check_materials
# 说明：仅统计文件的存在性，不代表论文质量、引用规范或结果准确。

"""检查论文撰写所需材料是否齐备（不生成论文）。"""

import argparse
from pathlib import Path


def count_materials(project_root: Path) -> dict[str, int]:
    """计算各类材料的数量；过滤 README.md 与 .gitkeep。"""
    groups = {
        "论文分节": project_root / "paper" / "sections",
        "参考文献": project_root / "paper" / "references",
        "第一问图表": project_root / "outputs" / "question1" / "figures",
        "第一问结果表": project_root / "outputs" / "question1" / "tables",
    }
    return {
        name: sum(
            1 for item in folder.rglob("*")
            if item.is_file() and item.name != ".gitkeep" and item.name != "README.md"
        ) if folder.is_dir() else 0
        for name, folder in groups.items()
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="检查论文阶段材料是否存在")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--strict", action="store_true", help="任意类别为空则返回非零状态")
    args = parser.parse_args()
    counts = count_materials(args.root)
    for label, count in counts.items():
        print(f"{label}：{count} 个文件")
    if args.strict and any(count == 0 for count in counts.values()):
        raise SystemExit("材料尚不完整，请先完成对应建模阶段。")


if __name__ == "__main__":
    main()
