# 文件：src/__init__.py
# 作用：将 src 目录标记为 Python 包的入口。
# 为什么存在：其他模块可以使用 from src.common.io import ... 这种导入方式。
# 是否运行：不直接运行；执行各阶段脚本时由 Python 导入系统自动使用。
# 当前状态：仅提供包结构，没有建模逻辑。

"""2023 APMCM C project package."""
