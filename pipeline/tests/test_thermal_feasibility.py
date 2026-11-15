from pathlib import Path

from pipeline.experiments.thermal.run_feasibility import ROOT, _display_report_path


def test_report_path_display_supports_outputs_inside_and_outside_repository() -> None:
    inside = ROOT / "reports" / "thermal-feasibility.md"
    outside = ROOT.parent / "thermal-feasibility.md"

    assert _display_report_path(inside) == "reports/thermal-feasibility.md"
    assert _display_report_path(outside) == str(outside)
