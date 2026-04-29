"""Render JSON questionnaire data through Jinja2 templates to HTML.

Produces two HTML files per questionnaire:
- output/pdf/{ID}_print_v{N}.html  (intermediate, consumed by export.py)
- output/tl/{ID}_tl_v{N}.html      (final TL deliverable, also consumed by export.py)
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

import click
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.schema import Questionnaire

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "questionnaires"
TEMPLATES_DIR = ROOT / "templates"
OUTPUT_PDF_DIR = ROOT / "output" / "pdf"
OUTPUT_TL_DIR = ROOT / "output" / "tl"


def load_questionnaire(qid: str) -> Questionnaire:
    path = DATA_DIR / f"{qid}.json"
    if not path.exists():
        raise FileNotFoundError(f"JSON introuvable : {path}")
    with path.open(encoding="utf-8") as f:
        raw = json.load(f)
    return Questionnaire(**raw)


def load_parcours() -> dict:
    path = ROOT / "data" / "parcours.json"
    if not path.exists():
        return {"ordre": [], "parcours": []}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def next_version(directory: Path, pattern: str) -> int:
    """Return next vN integer for files matching pattern with {n} placeholder."""
    rx = re.compile(pattern.replace("{n}", r"(\d+)"))
    existing = [int(m.group(1)) for p in directory.glob("*") if (m := rx.match(p.name))]
    return max(existing, default=0) + 1


def make_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def check_screenshots(qid: str, paths: list[str]) -> list[Path]:
    """Garde-fou : vérifie que chaque screenshot listé existe avant rendu."""
    missing: list[str] = []
    resolved: list[Path] = []
    for rel in paths:
        p = (ROOT / rel).resolve()
        if not p.exists():
            missing.append(rel)
        resolved.append(p)
    if missing:
        details = "\n".join(f"  - {m}" for m in missing)
        raise FileNotFoundError(
            f"[{qid}] {len(missing)} screenshot(s) manquant(s) :\n{details}\n"
            f"Dépose les fichiers dans assets/screenshots/follow/ avant de relancer."
        )
    return resolved


def render_html(qid: str) -> tuple[Path, Path, int]:
    q = load_questionnaire(qid)
    parcours = load_parcours()
    env = make_env()

    print_version = next_version(OUTPUT_PDF_DIR, rf"{qid}_print_v{{n}}\.html")
    tl_version = next_version(OUTPUT_TL_DIR, rf"{qid}_tl_v{{n}}\.html")
    version = max(print_version, tl_version)

    screenshot_paths = check_screenshots(qid, q.screenshot_follow)
    abs_screenshots = [p.as_uri() for p in screenshot_paths]

    ctx = {
        "q": q.model_dump(),
        "parcours": parcours,
        "version": version,
        "today": date.today().isoformat(),
        "logo_path": (ROOT / "assets" / "brand" / "logo_src.jpeg").as_uri(),
        "abs_screenshots": abs_screenshots,
    }

    if q.id == "00":
        print_template_name = "print_a4_manifeste.html.j2"
        tl_template_name = "tl_vertical_manifeste.html.j2"
    else:
        print_template_name = "print_a4.html.j2"
        tl_template_name = "tl_vertical.html.j2"

    print_html = env.get_template(print_template_name).render(**ctx)
    tl_html = env.get_template(tl_template_name).render(**ctx)

    print_path = OUTPUT_PDF_DIR / f"{qid}_print_v{version}.html"
    tl_path = OUTPUT_TL_DIR / f"{qid}_tl_v{version}.html"
    print_path.write_text(print_html, encoding="utf-8")
    tl_path.write_text(tl_html, encoding="utf-8")

    return print_path, tl_path, version


@click.command()
@click.option("--questionnaire", "-q", required=True, help="ID du questionnaire (ex : 2L)")
def main(questionnaire: str) -> None:
    print_path, tl_path, version = render_html(questionnaire)
    click.echo(f"v{version} | print HTML : {print_path}")
    click.echo(f"v{version} | tl    HTML : {tl_path}")


if __name__ == "__main__":
    main()
