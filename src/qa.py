"""QA scorer : runs the 20 checks defined in .claude/agents/qa-scorer.md.

Reads the latest rendered HTML (print + TL) and produces a JSON report in
output/qa-reports/. Returns score on 100; threshold for delivery is 95.

Each check is worth 5 points. Some checks (PDF dimensions, MP4 duration,
WCAG ratio) are stubbed when the underlying artifact is not yet produced —
they return passed=False with details so the operator knows what's missing.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

import click

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PDF_DIR = ROOT / "output" / "pdf"
OUTPUT_TL_DIR = ROOT / "output" / "tl"
QA_DIR = ROOT / "output" / "qa-reports"

PALETTE_PRINT = {"#1E2D3D", "#00A890", "#C48F1A", "#B8BEC7", "#F8F6F1", "#0E1117", "#5B6470", "#E5E2DB"}
PALETTE_TL = {"#080A0F", "#0E1117", "#141820", "#00D4B4", "#00A890", "#F0B429", "#C48F1A", "#F0EDE8", "#6B7280"}
ALLOWED_FONTS = {"Bebas Neue", "DM Sans", "Space Mono"}
EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F600-\U0001F64F]",
    flags=re.UNICODE,
)
HEX_COLOR_RE = re.compile(r"#[0-9A-Fa-f]{6}\b")


@dataclass
class Check:
    id: int
    name: str
    passed: bool
    details: str = ""


def latest(directory: Path, qid: str, suffix: str, ext: str) -> Path | None:
    rx = re.compile(rf"{re.escape(qid)}_{suffix}_v(\d+)\.{ext}$")
    matches = []
    for p in directory.glob(f"{qid}_{suffix}_v*.{ext}"):
        m = rx.match(p.name)
        if m:
            matches.append((int(m.group(1)), p))
    matches.sort()
    return matches[-1][1] if matches else None


def read(path: Path | None) -> str:
    return path.read_text(encoding="utf-8") if path and path.exists() else ""


def run_checks(qid: str) -> tuple[list[Check], int]:
    print_html = latest(OUTPUT_PDF_DIR, qid, "print", "html")
    tl_html = latest(OUTPUT_TL_DIR, qid, "tl", "html")
    pdf_file = latest(OUTPUT_PDF_DIR, qid, "print", "pdf")
    mp4_file = latest(OUTPUT_TL_DIR, qid, "tl", "mp4") or latest(OUTPUT_TL_DIR, qid, "tl", "webm")

    p_html = read(print_html)
    t_html = read(tl_html)
    combined = p_html + "\n" + t_html

    checks: list[Check] = []

    def add(cid: int, name: str, ok: bool, details: str = "") -> None:
        checks.append(Check(cid, name, ok, details))

    # 1. Palette respectée
    used = set(c.upper() for c in HEX_COLOR_RE.findall(combined))
    allowed = {c.upper() for c in PALETTE_PRINT | PALETTE_TL}
    rogue = used - allowed
    add(1, "Palette respectée", not rogue, f"Couleurs hors palette : {sorted(rogue)}" if rogue else "")

    # 2. Fonts respectées
    font_decls = re.findall(r"font-family\s*:\s*([^;]+);", combined, flags=re.I)
    fonts_used = set()
    for decl in font_decls:
        for token in re.findall(r"'([^']+)'|\"([^\"]+)\"", decl):
            fonts_used.add((token[0] or token[1]).strip())
    rogue_fonts = {f for f in fonts_used if f not in ALLOWED_FONTS and f.lower() not in {"sans-serif", "monospace", "serif"}}
    add(2, "Fonts respectées", not rogue_fonts, f"Fonts hors charte : {sorted(rogue_fonts)}" if rogue_fonts else "")

    # 3. Logo SRC dans header ET footer
    has_logo_print = 'data-zone="header"' in p_html and 'data-zone="footer"' in p_html and "logo_src" in p_html
    has_logo_tl = 'data-zone="header"' in t_html and 'data-zone="footer"' in t_html and "logo_src" in t_html
    add(3, "Logo SRC header+footer", has_logo_print and has_logo_tl,
        "" if (has_logo_print and has_logo_tl) else "Logo absent du header ou footer (print ou TL).")

    # 4. Pas d'emoji dans la version print
    emojis = EMOJI_RE.findall(p_html)
    add(4, "Pas d'emoji (print)", not emojis, f"Emojis trouvés : {emojis[:5]}" if emojis else "")

    # 5. Légende couleur visible
    has_legend = 'data-zone="legend"' in combined or "légende" in combined.lower()
    add(5, "Légende couleur visible", has_legend, "" if has_legend else "Aucun bloc data-zone=\"legend\" trouvé.")

    # 6. Les 7 zones obligatoires
    zones = ["header", "identity", "hero", "disrupteur", "valeur", "frise", "footer"]
    missing_print = [z for z in zones if f'data-zone="{z}"' not in p_html]
    missing_tl = [z for z in zones if f'data-zone="{z}"' not in t_html]
    add(6, "7 zones présentes", not missing_print and not missing_tl,
        f"Print manque : {missing_print} | TL manque : {missing_tl}" if (missing_print or missing_tl) else "")

    # 7. Numéro de planche affiché (#XX/YY)
    has_num = bool(re.search(r"#\s*\d{2}\s*/\s*\d{1,2}", combined))
    add(7, "Numéro de planche", has_num, "" if has_num else "Pattern #XX/YY introuvable.")

    # 8. Code questionnaire affiché
    has_code = qid in combined
    add(8, "Code questionnaire affiché", has_code, "" if has_code else f"Code {qid} introuvable.")

    # 9. Étape parcours indiquée
    has_etape = 'data-field="etape"' in combined or "étape" in combined.lower()
    add(9, "Étape parcours indiquée", has_etape, "")

    # 10. Encart "à quoi ça sert" non vide
    has_valeur = 'data-zone="valeur"' in combined and len(re.findall(r"<li", combined)) >= 3
    add(10, "Encart valeur clinique non vide", has_valeur, "" if has_valeur else "Encart valeur absent ou < 3 puces.")

    # 11. Texte corps ≥ 10pt
    small = re.findall(r"font-size\s*:\s*(\d+(?:\.\d+)?)\s*pt", p_html)
    too_small = [s for s in small if float(s) < 10]
    add(11, "Corps ≥ 10pt (print)", not too_small, f"Tailles < 10pt : {too_small}" if too_small else "")

    # 12. Titre principal ≥ 56pt Bebas Neue
    title_pt = re.search(r"--title-size\s*:\s*(\d+(?:\.\d+)?)\s*pt", p_html)
    ok_title = bool(title_pt) and float(title_pt.group(1)) >= 56
    add(12, "Titre ≥ 56pt", ok_title,
        "" if ok_title else "Variable --title-size absente ou < 56pt dans print_a4.")

    # 13. Format A4 portrait + marges 12mm
    has_a4 = "@page" in p_html and "A4" in p_html and "12mm" in p_html
    add(13, "Format A4 + marges 12mm", has_a4, "" if has_a4 else "@page A4 12mm absent du print HTML.")

    # 14. Screenshot Follow ≥ 35% surface (heuristique : flag CSS dans template)
    flag = "data-screenshot-area-min=\"35\"" in p_html
    add(14, "Screenshot ≥ 35% surface", flag,
        "" if flag else "Le template doit poser data-screenshot-area-min=\"35\" sur le hero.")

    # 15. Contraste WCAG AA (TODO : nécessite parsing CSS + calcul ratio)
    add(15, "Contraste WCAG AA", False, "TODO : check de contraste non implémenté (manuel pour l'instant).")

    # 16. Format 1080×1920 respecté (TL)
    has_1080 = "1080" in t_html and "1920" in t_html
    add(16, "TL 1080×1920", has_1080, "" if has_1080 else "Dimensions 1080×1920 absentes du TL.")

    # 17. 5 à 7 sections scroll-snap
    sections = re.findall(r'<section[^>]*data-snap="true"', t_html)
    n = len(sections)
    add(17, "5 à 7 sections scroll-snap", 5 <= n <= 7, f"Sections trouvées : {n}")

    # 18. MP4 entre 25 et 35 secondes
    if mp4_file and shutil.which("ffprobe"):
        try:
            r = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(mp4_file)],
                capture_output=True, text=True, check=True,
            )
            dur = float(r.stdout.strip())
            ok_dur = 25 <= dur <= 35
            add(18, "Durée MP4 25-35s", ok_dur, f"Durée mesurée : {dur:.1f}s")
        except Exception as e:
            add(18, "Durée MP4 25-35s", False, f"ffprobe a échoué : {e}")
    else:
        add(18, "Durée MP4 25-35s", False, "MP4 absent ou ffprobe indisponible.")

    # 19. Animation à l'entrée de chaque section
    has_io = "IntersectionObserver" in t_html
    add(19, "IntersectionObserver présent", has_io, "" if has_io else "IntersectionObserver absent du TL.")

    # 20. Tutoiement (aucun "vous")
    vous = re.findall(r"\b[Vv]ous\b", combined)
    add(20, "Tutoiement (pas de 'vous')", not vous, f"{len(vous)} occurrence(s) de 'vous'." if vous else "")

    score = sum(5 for c in checks if c.passed)
    return checks, score


@click.command()
@click.option("--questionnaire", "-q", required=True)
def main(questionnaire: str) -> None:
    checks, score = run_checks(questionnaire)
    failed = [c for c in checks if not c.passed]

    print_html = latest(OUTPUT_PDF_DIR, questionnaire, "print", "html")
    version = 1
    if print_html:
        m = re.search(r"_v(\d+)\.html$", print_html.name)
        if m:
            version = int(m.group(1))

    report = {
        "id": questionnaire,
        "version": version,
        "score": score,
        "passed": score >= 95,
        "checks": [asdict(c) for c in checks],
        "summary": f"{len(failed)} check(s) échoué(s) sur {len(checks)}. Score {score}/100. "
                   + ("Livré." if score >= 95 else "À corriger."),
    }
    out = QA_DIR / f"{questionnaire}_v{version}.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    click.echo(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
