"""Publie les versions FINALES des TL HTML dans docs/ pour GitHub Pages.

- docs/{ID}/index.html   : dernière version validée du TL pour chaque planche
- docs/assets/...        : assets réellement référencés, copiés depuis assets/
- docs/index.html        : page d'accueil listant les planches publiées

Les chemins file:///... absolus présents dans les TL HTML sont réécrits en
chemins relatifs ../assets/... pour fonctionner sous GitHub Pages.
GitHub Pages source = branch main, path /docs.
"""
from __future__ import annotations

import json
import re
import shutil
import urllib.parse
from datetime import date
from pathlib import Path

import click

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "questionnaires"
TL_DIR = ROOT / "output" / "tl"
PUBLIC_DIR = ROOT / "docs"
PUBLIC_ASSETS_DIR = PUBLIC_DIR / "assets"

ROOT_URI_PREFIX = ROOT.as_uri() + "/"
FILE_URI_RX = re.compile(r'(["\'])(file://[^"\']+)(["\'])')


def detect_questionnaires() -> list[str]:
    rx = re.compile(r"(?P<id>[A-Za-z0-9]+)_tl_v(?P<n>\d+)\.html$")
    ids: set[str] = set()
    for p in TL_DIR.glob("*_tl_v*.html"):
        m = rx.match(p.name)
        if m:
            ids.add(m.group("id"))
    return sorted(ids)


def latest_tl(qid: str) -> tuple[Path, int] | None:
    rx = re.compile(rf"^{re.escape(qid)}_tl_v(\d+)\.html$")
    candidates: list[tuple[int, Path]] = []
    for p in TL_DIR.glob(f"{qid}_tl_v*.html"):
        m = rx.match(p.name)
        if m:
            candidates.append((int(m.group(1)), p))
    if not candidates:
        return None
    n, path = max(candidates, key=lambda t: t[0])
    return path, n


def load_meta(qid: str) -> dict:
    p = DATA_DIR / f"{qid}.json"
    if not p.exists():
        return {"id": qid, "titre": qid, "sous_titre": "", "numero_planche": "", "total_planches": ""}
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def rewrite_html(html: str, copied_assets: set[Path]) -> str:
    """Réécrit chaque file:///.../assets/... en ../assets/... et collecte les assets à copier."""

    def repl(m: re.Match) -> str:
        quote_open, uri, quote_close = m.group(1), m.group(2), m.group(3)
        if not uri.startswith(ROOT_URI_PREFIX):
            return m.group(0)
        rel_quoted = uri[len(ROOT_URI_PREFIX):]
        rel = urllib.parse.unquote(rel_quoted)
        src = (ROOT / rel).resolve()
        try:
            src.relative_to(ROOT)
        except ValueError:
            return m.group(0)
        if not rel.startswith("assets/") or not src.exists():
            return m.group(0)
        copied_assets.add(src)
        new_uri = "../" + urllib.parse.quote(rel, safe="/")
        return f"{quote_open}{new_uri}{quote_close}"

    return FILE_URI_RX.sub(repl, html)


def copy_asset(src: Path) -> Path:
    rel = src.relative_to(ROOT)
    dst = PUBLIC_DIR / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
        shutil.copy2(src, dst)
    return dst


def publish_one(qid: str) -> dict:
    found = latest_tl(qid)
    if found is None:
        click.secho(f"  [skip] {qid} : aucun TL HTML dans output/tl/", fg="yellow")
        return {"id": qid, "skipped": True}
    src, version = found
    meta = load_meta(qid)

    html = src.read_text(encoding="utf-8")
    copied: set[Path] = set()
    new_html = rewrite_html(html, copied)

    target_dir = PUBLIC_DIR / qid
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "index.html"
    target.write_text(new_html, encoding="utf-8")

    for a in copied:
        copy_asset(a)

    click.echo(f"  [ok] {qid} v{version} → docs/{qid}/index.html  ({len(copied)} assets)")
    return {
        "id": qid,
        "version": version,
        "titre": meta.get("titre", qid),
        "sous_titre": meta.get("sous_titre", ""),
        "numero": meta.get("numero_planche", ""),
        "total": meta.get("total_planches", ""),
        "skipped": False,
    }


INDEX_TEMPLATE = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SRC — Infographies</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,600&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #080A0F;
    --bg2: #0E1117;
    --bg3: #141820;
    --teal: #00D4B4;
    --gold: #F0B429;
    --white: #F0EDE8;
    --muted: #6B7280;
    --font-display: 'Bebas Neue', sans-serif;
    --font-body: 'DM Sans', sans-serif;
    --font-mono: 'Space Mono', monospace;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{
    background: var(--bg);
    color: var(--white);
    font-family: var(--font-body);
    font-size: 17px;
    line-height: 1.5;
    -webkit-text-size-adjust: 100%;
  }}
  body {{
    min-height: 100vh;
    padding: clamp(24px, 6vw, 64px);
    max-width: 920px;
    margin: 0 auto;
  }}
  header {{
    border-bottom: 1px solid rgba(255,255,255,0.08);
    padding-bottom: clamp(20px, 4vh, 36px);
    margin-bottom: clamp(24px, 5vh, 48px);
  }}
  .tag {{
    font-family: var(--font-mono);
    font-size: 12px;
    letter-spacing: 6px;
    color: var(--muted);
    text-transform: uppercase;
  }}
  h1 {{
    font-family: var(--font-display);
    font-size: clamp(48px, 10vw, 96px);
    line-height: 0.95;
    color: var(--teal);
    letter-spacing: 1px;
    margin: 8px 0 14px;
  }}
  .lede {{
    font-size: clamp(15px, 2vw, 19px);
    color: var(--white);
    max-width: 60ch;
  }}
  .lede strong {{ color: var(--gold); font-weight: 600; }}
  section.planches {{
    display: grid;
    gap: clamp(12px, 2vh, 16px);
  }}
  a.card {{
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: center;
    gap: clamp(14px, 3vw, 28px);
    background: var(--bg2);
    border: 1px solid rgba(255,255,255,0.07);
    border-left: 4px solid var(--teal);
    padding: clamp(16px, 2.5vh, 24px) clamp(18px, 3.5vw, 30px);
    text-decoration: none;
    color: var(--white);
    transition: background 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
  }}
  a.card:hover {{
    background: var(--bg3);
    border-left-color: var(--gold);
    transform: translateX(2px);
  }}
  .card-id {{
    font-family: var(--font-display);
    font-size: clamp(40px, 7vw, 64px);
    line-height: 1;
    color: var(--teal);
    letter-spacing: 1px;
    min-width: 1.6em;
  }}
  .card-text .card-titre {{
    font-family: var(--font-display);
    font-size: clamp(22px, 3.6vw, 32px);
    line-height: 1.05;
    color: var(--white);
    letter-spacing: 0.5px;
  }}
  .card-text .card-sub {{
    font-size: clamp(13px, 1.8vw, 16px);
    color: var(--muted);
    margin-top: 4px;
  }}
  .card-meta {{
    font-family: var(--font-mono);
    font-size: 12px;
    letter-spacing: 1.5px;
    color: var(--muted);
    text-align: right;
    white-space: nowrap;
  }}
  .empty {{
    background: var(--bg2);
    border-left: 4px solid var(--muted);
    padding: clamp(16px, 2.5vh, 24px) clamp(18px, 3.5vw, 30px);
    color: var(--muted);
    font-family: var(--font-mono);
    font-size: 14px;
  }}
  footer {{
    margin-top: clamp(32px, 6vh, 64px);
    padding-top: clamp(16px, 3vh, 24px);
    border-top: 1px solid rgba(255,255,255,0.08);
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    font-family: var(--font-mono);
    font-size: 12px;
    letter-spacing: 1.5px;
    color: var(--muted);
  }}
  footer .footer-brand {{
    font-family: var(--font-display);
    font-size: 18px;
    letter-spacing: 1px;
    color: var(--white);
  }}
</style>
</head>
<body>
  <header>
    <div class="tag">Spine Research Community</div>
    <h1>Infographies SRC</h1>
    <p class="lede">Versions <strong>finales validées</strong> des planches Follow.
      12 questionnaires, 50 chirurgiens, une seule logique de remplissage.</p>
  </header>

  <section class="planches">
{cards}
  </section>

  <footer>
    <span class="footer-brand">SRC</span>
    <span>Mise à jour · {today}</span>
  </footer>
</body>
</html>
"""

CARD_TEMPLATE = """    <a class="card" href="./{id}/">
      <div class="card-id">{id}</div>
      <div class="card-text">
        <div class="card-titre">{titre}</div>
        <div class="card-sub">{sub}</div>
      </div>
      <div class="card-meta">{meta}</div>
    </a>"""


def render_index(published: list[dict]) -> str:
    cards_html: list[str] = []
    visible = [p for p in published if not p.get("skipped")]
    visible.sort(key=lambda p: (str(p.get("numero") or ""), p["id"]))
    for p in visible:
        sub = p.get("sous_titre") or ""
        numero = p.get("numero", "")
        total = p.get("total", "")
        meta_bits = []
        if numero and total:
            meta_bits.append(f"#{numero}/{total}")
        meta_bits.append(f"v{p['version']}")
        cards_html.append(
            CARD_TEMPLATE.format(
                id=p["id"],
                titre=p.get("titre", p["id"]),
                sub=sub,
                meta=" · ".join(meta_bits),
            )
        )
    if not cards_html:
        cards_html.append('    <div class="empty">Aucune planche publiée pour l\'instant.</div>')
    return INDEX_TEMPLATE.format(
        cards="\n".join(cards_html),
        today=date.today().isoformat(),
    )


def dir_size(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def fmt_size(n: int) -> str:
    for unit in ("o", "Ko", "Mo", "Go"):
        if n < 1024 or unit == "Go":
            return f"{n:.1f} {unit}" if unit != "o" else f"{n} {unit}"
        n /= 1024
    return f"{n:.1f} Go"


@click.command()
@click.option("--questionnaire", "-q", "questionnaires", multiple=True,
              help="ID(s) à publier. Répétable.")
@click.option("--all", "publish_all", is_flag=True,
              help="Publie toutes les planches détectées dans output/tl/.")
def main(questionnaires: tuple[str, ...], publish_all: bool) -> None:
    if not questionnaires and not publish_all:
        raise click.UsageError("Précise --questionnaire ID ou --all.")

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    ids = list(detect_questionnaires()) if publish_all else list(questionnaires)
    click.echo(f"Publication de {len(ids)} planche(s) : {', '.join(ids) or '—'}")

    published: list[dict] = []
    for qid in ids:
        published.append(publish_one(qid))

    index_path = PUBLIC_DIR / "index.html"
    index_path.write_text(render_index(published), encoding="utf-8")
    click.echo(f"  [ok] index → {index_path.relative_to(ROOT)}")

    total = dir_size(PUBLIC_DIR)
    click.echo(f"docs/ : {fmt_size(total)}")


if __name__ == "__main__":
    main()
