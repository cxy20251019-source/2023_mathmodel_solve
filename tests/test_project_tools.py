# 文件：tests/test_project_tools.py
# 所属目录：tests/（代码测试）
# 作用：验证新加入的来源检查、日志追加、成果清单和论文材料检查函数。
# 输入：pytest 创建的临时文件夹与模拟内容，不读取/篡改真实研究数据。
# 输出：pytest 的测试结果；不会产生新能源汽车模型结论。
# 运行：python -m pytest -q

"""对项目辅助工具进行基础单元测试。"""

from pathlib import Path

from data.check_sources import audit_sources
from docs.append_run_log import append_record, clean_cell
from outputs.list_results import list_results
from paper.check_materials import count_materials


def test_check_sources_template(tmp_path: Path):
    path = tmp_path / "sources.csv"
    path.write_text(
        "variable,meaning,unit,region,year_range,original_filename,source_organization,"
        "source_url,download_date,processing_notes,status\n"
        + "".join(f"{name},,,,,,,,,,pending\n" for name in ["Y1", "Y2", *[f"X{i}" for i in range(1, 7)]]),
        encoding="utf-8",
    )
    errors, warnings = audit_sources(path)
    assert not errors
    assert warnings


def test_source_missing_column_fails(tmp_path: Path):
    path = tmp_path / "bad.csv"
    path.write_text("variable,meaning\nY1,test\n", encoding="utf-8")
    errors, _ = audit_sources(path)
    assert errors


def test_log_inserts_inside_table(tmp_path: Path):
    path = tmp_path / "run_log.md"
    path.write_text(
        "# 记录\n\n| 日期 | 阶段 | 输入数据与来源 | 运行指令/代码版本 | 发现的问题 | 核验结论 | 下一步 |\n"
        "|---|---|---|---|---|---|---|\n"
        "| 2026-01-01 | 初始化 | 无 | 无 | 无 | 完成 | 下一步 |\n"
        "\n附注。\n",
        encoding="utf-8",
    )
    append_record(path, ["2026-11-22", "核验", "data.csv", "command", "无", "通过", "继续"])
    written = path.read_text(encoding="utf-8")
    assert written.index("| 2026-11-22") < written.index("附注。")
    assert clean_cell("a|b") == "a\\|b"


def test_outputs_skip_placeholders(tmp_path: Path):
    folder = tmp_path / "figures"
    folder.mkdir()
    (folder / ".gitkeep").touch()
    (folder / "heatmap.png").write_bytes(b"fake image")
    records = list_results(tmp_path)
    assert len(records["figures"]) == 1
    assert records["tables"] == []


def test_paper_counts_only_actual_files(tmp_path: Path):
    sections = tmp_path / "paper" / "sections"
    sections.mkdir(parents=True)
    (sections / ".gitkeep").touch()
    assert count_materials(tmp_path)["论文分节"] == 0
    (sections / "question1.md").write_text("# 第一问", encoding="utf-8")
    assert count_materials(tmp_path)["论文分节"] == 1
