#!/usr/bin/env python3
"""
_patch_tg_notify.py
===================
Auto-patcher: adds RunLogger + tg_notify block to all test scripts.

Run ONCE from the project root:
    python _patch_tg_notify.py

What it does:
  - Finds every .py script with `if __name__ == "__main__":`
  - Adds sys.path insert + imports at the top (after docstring)
  - Wraps the __main__ block with RunLogger context manager
  - Appends tg_notify call at the end of __main__

After patching, every test run will:
  1. Log to docs/runs_log.csv automatically
  2. Send a Telegram notification on completion

Skips files that are already patched or are infrastructure files.
"""
import os
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
CORE = ROOT / "core"

SKIP_FILES = {
    "__init__.py",
    "run_logger.py",
    "output_manager.py",
    "tg_notify.py",
    "run_pipeline.py",
    "_patch_tg_notify.py",
}

SKIP_DIRS = {".git", "__pycache__", "core", "old", "archived_buggy", "fixed_output", ".venv"}

# ── import block to inject at top of each script ─────────────────────────────
_IMPORT_BLOCK = '''\
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "core"))
from run_logger import RunLogger as _RunLogger
from tg_notify  import notify    as _tg_notify
'''

# ── RunLogger wrapper for __main__ ───────────────────────────────────────────
def _make_main_wrapper(script_name: str, test_label: str) -> tuple[str, str]:
    """Return (prefix_to_inject_before_main_body, suffix_to_inject_at_end)."""
    prefix = (
        f'    with _RunLogger("{script_name}", test="{test_label}") as _rl:\n'
        f'        pass  # RunLogger active — call _rl.set_key_result("...") anywhere\n'
    )
    suffix = (
        f'    _tg_notify("✅ {script_name} done | " + (_rl._key_result or ""), silent=True)\n'
    )
    return prefix, suffix


def infer_test_label(fname: str) -> str:
    """Infer a human-readable test label from the filename."""
    name = pathlib.Path(fname).stem
    # map known names
    mapping = {
        "sigma_radiative_stability":  "Test 1 - Radiative Stability",
        "dark_axion_full":            "Test 2 - V_eff Analysis",
        "fifth_force_constraints":    "Test 3 - Fifth Force",
        "freeze_out_analysis_corrected": "Test 4 - Freeze-out Trapping",
        "theta_topological":          "Test 5 - Topological θ",
        "consistency_check_sidm":     "Test 6 - SIDM Consistency",
        "free_theta_scan":            "Test 8 - Free θ Scan",
        "a4_dark_sector_model":       "Test 9b - A4 Model",
        "verify_a4_cg":               "Verify 1 - A4 CG",
        "boltzmann_17bp":             "Verify 2 - Boltzmann 17BPs",
        "sigma_trapping_ode":         "Verify 3 - σ Trapping ODE",
        "fornax_gc_check":            "Test 11 - Fornax GC",
        "test_alpha_convention":      "Test 12 - α Convention",
        "dark_force_accumulation":    "Test 13A - Force Accumulation",
        "sigma_mass_protection":      "Test 13D - σ Mass Protection",
        "dark_qcd_consistency":       "Test 14 - Dark QCD",
        "born_full_amplitude":        "Test 15 - Born Amplitude",
        "neutrino_dark_resonance":    "Test 16 - Neutrino Resonance",
        "vev_alignment_stability":    "Test 17 - VEV Stability",
        "sidm_velocity_cross_section": "Test 18 - SIDM Velocity σ",
        "qcd_scale_coincidence":      "Test 19 - QCD Coincidence",
    }
    return mapping.get(name, name.replace("_", " ").title())


def patch_file(fpath: pathlib.Path) -> str:
    """Patch a single file. Returns 'patched', 'already_patched', or 'no_main'."""
    content = fpath.read_text(encoding="utf-8", errors="replace")

    if "run_logger" in content or "_RunLogger" in content or "_tg_notify" in content:
        return "already_patched"

    # must have __main__ block
    if 'if __name__ == "__main__":' not in content and "if __name__ == '__main__':" not in content:
        return "no_main"

    test_label = infer_test_label(fpath.name)

    # ── 1. inject import block ─────────────────────────────────────────────
    # insert after module docstring (if any) else at very top
    lines = content.splitlines(keepends=True)
    insert_at = 0

    # skip shebang
    if lines and lines[0].startswith("#!"):
        insert_at = 1

    # skip module docstring (triple-quoted)
    i = insert_at
    if i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            quote = stripped[:3]
            # find closing quote
            if stripped.count(quote) >= 2 and len(stripped) > 6:
                # single-line docstring
                insert_at = i + 1
            else:
                i += 1
                while i < len(lines):
                    if quote in lines[i]:
                        insert_at = i + 1
                        break
                    i += 1

    # skip leading blank lines / comments
    while insert_at < len(lines) and lines[insert_at].strip() == "":
        insert_at += 1

    lines.insert(insert_at, _IMPORT_BLOCK + "\n")
    content = "".join(lines)

    # ── 2. wrap __main__ body ─────────────────────────────────────────────
    # Find the main call pattern — we'll wrap the entire __main__ body
    # with a RunLogger context manager, but to keep it simple we inject
    # the RunLogger open/close around the existing code by indenting it.
    #
    # Strategy: replace `if __name__ == "__main__":\n` with
    #           `if __name__ == "__main__":\n    with _RunLogger(...) as _rl:\n`
    # and add 4 spaces to every subsequent non-empty line until end of file.

    main_match = re.search(
        r'^if __name__ == ["\']__main__["\']\s*:\s*\n',
        content, re.MULTILINE
    )
    if not main_match:
        return "no_main"

    main_end = main_match.end()
    before_main = content[:main_end]
    after_main  = content[main_end:]

    # Indent the __main__ body by 4 extra spaces
    indented_body = re.sub(r'^(    )', r'        ', after_main, flags=re.MULTILINE)
    # Lines that are already at root level (no leading space) stay at 4 spaces
    indented_body = re.sub(r'^([^\s\n])', r'    \1', indented_body, flags=re.MULTILINE)

    tg_suffix = (
        f'\n    _tg_notify("✅ {fpath.name} done | " + (_rl._key_result or ""), silent=True)\n'
    )

    new_content = (
        before_main
        + f'    with _RunLogger("{fpath.name}", test="{test_label}") as _rl:\n'
        + indented_body.rstrip()
        + tg_suffix
    )

    fpath.write_text(new_content, encoding="utf-8")
    return "patched"


def main():
    patched       = []
    already       = []
    no_main       = []
    errors        = []

    for fpath in sorted(ROOT.glob("*.py")):
        if fpath.name in SKIP_FILES:
            continue
        try:
            result = patch_file(fpath)
        except Exception as e:
            errors.append((fpath.name, str(e)))
            continue

        if result == "patched":
            patched.append(fpath.name)
        elif result == "already_patched":
            already.append(fpath.name)
        else:
            no_main.append(fpath.name)

    print(f"\n{'='*55}")
    print(f"  _patch_tg_notify.py — results")
    print(f"{'='*55}")
    print(f"\n✅ Patched ({len(patched)}):")
    for f in patched:
        print(f"   {f}")
    print(f"\n⏭  Already patched ({len(already)}):")
    for f in already:
        print(f"   {f}")
    print(f"\n—  No __main__ ({len(no_main)}):")
    for f in no_main:
        print(f"   {f}")
    if errors:
        print(f"\n❌ Errors ({len(errors)}):")
        for f, e in errors:
            print(f"   {f}: {e}")
    print()


if __name__ == "__main__":
    main()
