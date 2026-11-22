# 文件：run_project.py
# 位置：项目根目录（便于初次打开 PyCharm 时找到统一运行入口）。
# 作用：把分散在 data、docs、outputs、paper、src 的工具统一到一个命令下。
# 运行示例：
#   python run_project.py check-sources
#   python run_project.py inspect-data --input "data/interim/年度合并.xlsx"
#   python run_project.py prepare-data --input "data/interim/年度合并.xlsx"
#   python run_project.py list-results
#   python run_project.py check-paper
#   python run_project.py log-run --stage "数据核验" --conclusion "待进一步检查"
# 注意：这里只负责启动相应脚本，不会一键执行尚未核验的建模步骤。

"""用于在 PyCharm 或终端中统一启动项目的辅助工具。"""

import argparse
from pathlib import Path
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parent
MODULES = {
    "check-sources": "data.check_sources",
    "inspect-data": "data.inspect_annual",
    "prepare-data": "src.question1.step01_prepare_data",
    "log-run": "docs.append_run_log",
    "list-results": "outputs.list_results",
    "check-paper": "paper.check_materials",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="2023 APMCM C 题工程工具入口")
    parser.add_argument("command", choices=list(MODULES), help="要运行的阶段或工具")
    args, forwarded = parser.parse_known_args()
    result = subprocess.run(
        [sys.executable, "-m", MODULES[args.command], *forwarded],
        cwd=PROJECT_ROOT,
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
