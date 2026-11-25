"""Check the committed assembly exports without running KiCad or generating files."""
import csv
import math
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class AssemblyExportsTests(unittest.TestCase):
    def test_bom_and_placements_match_the_board(self):
        # v0.3.1 replaced the legacy assembly/ exports with manufacturing/.
        if (ROOT / "manufacturing").is_dir():
            folder, placement_name = ROOT / "manufacturing", "SMD-pos"
        else:
            folder, placement_name = ROOT / "assembly", "all-pos"
        bom = read_csv(folder / "smart_motor_controller-BOM.csv")
        placements = read_csv(folder / f"smart_motor_controller-{placement_name}.csv")
        self.assertTrue(bom, "Empty BOM")
        self.assertTrue(placements, "Empty placement file")

        board = (ROOT / "smart_motor_controller.kicad_pcb").read_text(encoding="utf-8")
        # Both the older fp_text and newer footprint property encode the reference.
        board_refs = set(re.findall(r'(?m)^\s*\((?:fp_text reference|property "Reference")\s+"([^"]+)"', board))
        bom_footprints = {}
        for row in bom:
            self.assertRegex(row["LCSC"], r"^C[0-9]+$")
            footprint = row["Footprint"].rsplit(":", 1)[-1]
            self.assertTrue(footprint)
            for ref in (ref.strip() for ref in row["Designator"].split(",")):
                self.assertIn(ref, board_refs, f"{ref} missing from PCB")
                self.assertNotIn(ref, bom_footprints, f"Duplicate BOM entry for {ref}")
                bom_footprints[ref] = footprint

        placed = set()
        for row in placements:
            ref = row["Designator"]
            self.assertNotIn(ref, placed, f"Duplicate placement for {ref}")
            placed.add(ref)
            self.assertIn(ref, bom_footprints, f"Placement without BOM entry for {ref}")
            self.assertEqual(row["Footprint"].removeprefix(ref + "_"), bom_footprints[ref], ref)
            self.assertIn(row["Layer"].lower(), ("top", "bottom"), ref)
            for field in ("Mid X", "Mid Y", "Rotation"):
                self.assertTrue(math.isfinite(float(row[field])), f"{ref} has invalid {field}")
        self.assertEqual(placed, set(bom_footprints), "BOM and placement references differ")
