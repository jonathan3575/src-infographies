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
<title>SRC — Le système</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,600&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
  :root {
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
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body {
    background: var(--bg);
    color: var(--white);
    font-family: var(--font-body);
    font-size: clamp(15px, 2vw, 18px);
    line-height: 1.5;
    -webkit-text-size-adjust: 100%;
  }

  /* === HERO === */
  header.hero {
    min-height: clamp(420px, 70vh, 720px);
    padding: clamp(40px, 8vw, 96px) clamp(20px, 5vw, 56px);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    background: radial-gradient(ellipse at top, rgba(0, 212, 180, 0.10), transparent 60%);
  }
  .hero-logo {
    width: clamp(96px, 18vw, 160px);
    height: auto;
    object-fit: contain;
    mix-blend-mode: screen;
    opacity: 0.92;
    margin-bottom: clamp(24px, 5vh, 40px);
  }
  .hero-tag {
    font-family: var(--font-mono);
    font-size: clamp(11px, 2vw, 16px);
    letter-spacing: clamp(3px, 1vw, 8px);
    color: var(--teal);
    text-transform: uppercase;
    margin-bottom: clamp(8px, 1.5vh, 16px);
  }
  .hero-title {
    font-family: var(--font-display);
    font-size: clamp(56px, 12vw, 120px);
    line-height: 0.92;
    color: var(--white);
    letter-spacing: 1px;
    margin-bottom: clamp(12px, 2vh, 20px);
  }
  .hero-sub {
    font-size: clamp(16px, 2.5vw, 22px);
    color: var(--muted);
    font-weight: 300;
    letter-spacing: 0.5px;
    margin-bottom: clamp(20px, 3vh, 32px);
  }
  .hero-lede {
    font-size: clamp(18px, 2.6vw, 26px);
    color: var(--white);
    max-width: 36ch;
    line-height: 1.4;
  }
  .hero-lede strong { color: var(--gold); font-weight: 600; }

  /* === MAIN === */
  main {
    max-width: 1280px;
    margin: 0 auto;
    padding: clamp(40px, 8vh, 80px) clamp(20px, 5vw, 56px);
  }
  .section-tag {
    font-family: var(--font-mono);
    font-size: clamp(11px, 2vw, 16px);
    letter-spacing: clamp(3px, 1vw, 8px);
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: clamp(8px, 1.5vh, 12px);
  }
  .section-title {
    font-family: var(--font-display);
    font-size: clamp(40px, 8vw, 80px);
    line-height: 1;
    color: var(--teal);
    letter-spacing: 1px;
    margin-bottom: clamp(28px, 5vh, 48px);
  }

  /* === GRILLE PLANCHES === */
  .planches {
    display: grid;
    grid-template-columns: 1fr;
    gap: clamp(14px, 2vh, 20px);
  }
  @media (min-width: 720px) {
    .planches { grid-template-columns: repeat(2, 1fr); }
  }
  @media (min-width: 1080px) {
    .planches { grid-template-columns: repeat(3, 1fr); }
  }
  a.card {
    background: var(--bg2);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 4px;
    padding: clamp(20px, 3vh, 28px) clamp(20px, 3.5vw, 32px);
    text-decoration: none;
    color: var(--white);
    display: flex;
    flex-direction: column;
    gap: clamp(8px, 1.2vh, 12px);
    min-height: 200px;
    position: relative;
    transition: border-color 0.2s ease, transform 0.2s ease, background 0.2s ease;
  }
  a.card:hover {
    background: var(--bg3);
    border-color: var(--teal);
    transform: translateY(-2px);
  }
  a.card.intro {
    border-left: 4px solid var(--gold);
    background: linear-gradient(180deg, rgba(240,180,41,0.06), var(--bg2));
  }
  a.card.intro:hover { border-color: var(--gold); }
  .card-tag {
    font-family: var(--font-mono);
    font-size: 10px;
    letter-spacing: 2.5px;
    color: var(--muted);
    text-transform: uppercase;
  }
  a.card.intro .card-tag { color: var(--gold); }
  .card-id {
    font-family: var(--font-display);
    font-size: clamp(64px, 8vw, 96px);
    line-height: 0.85;
    color: var(--teal);
    letter-spacing: 1px;
  }
  a.card.intro .card-id { color: var(--gold); }
  .card-titre {
    font-family: var(--font-display);
    font-size: clamp(20px, 2.6vw, 28px);
    line-height: 1.05;
    color: var(--white);
    letter-spacing: 0.3px;
    margin-top: auto;
  }
  .card-sub {
    font-size: clamp(13px, 1.6vw, 15px);
    color: var(--muted);
    line-height: 1.4;
  }
  .card-meta {
    font-family: var(--font-mono);
    font-size: 11px;
    letter-spacing: 1.5px;
    color: var(--muted);
    margin-top: 4px;
  }
  .empty {
    background: var(--bg2);
    border-left: 4px solid var(--muted);
    padding: clamp(20px, 3vh, 28px);
    color: var(--muted);
    font-family: var(--font-mono);
  }

  /* === À PROPOS === */
  section.about {
    margin-top: clamp(48px, 8vh, 96px);
    background: var(--bg2);
    border-radius: 4px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.08);
  }
  .about-photo {
    position: relative;
    height: clamp(200px, 30vh, 320px);
    background-image: url('./assets/brand/bureau_src_rooftop.jpg');
    background-size: cover;
    background-position: center;
  }
  .about-photo::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(180deg, rgba(8,10,15,0.2) 0%, rgba(8,10,15,0.85) 100%);
  }
  .about-text {
    padding: clamp(24px, 4vh, 40px) clamp(20px, 4vw, 48px);
    display: flex;
    flex-direction: column;
    gap: clamp(10px, 1.6vh, 16px);
  }
  .about-text p {
    font-size: clamp(15px, 2vw, 19px);
    color: var(--white);
    line-height: 1.55;
    max-width: 60ch;
  }
  .about-text p strong { color: var(--gold); font-weight: 600; }
  .about-signature {
    align-self: flex-end;
    margin-top: clamp(8px, 1.5vh, 14px);
    font-family: var(--font-display);
    font-size: clamp(20px, 2.8vw, 28px);
    color: var(--gold);
    letter-spacing: 1px;
  }

  /* === FOOTER === */
  footer {
    max-width: 1280px;
    margin: 0 auto;
    padding: clamp(28px, 5vh, 48px) clamp(20px, 5vw, 56px);
    border-top: 1px solid rgba(255,255,255,0.08);
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 16px;
    font-family: var(--font-mono);
    font-size: 12px;
    letter-spacing: 1.5px;
    color: var(--muted);
  }
  .footer-left {
    display: flex;
    align-items: center;
    gap: 14px;
  }
  .footer-logo {
    width: 40px;
    height: 40px;
    object-fit: contain;
    mix-blend-mode: screen;
    opacity: 0.85;
  }
  .footer-link {
    color: var(--muted);
    text-decoration: none;
    transition: color 0.2s ease;
  }
  .footer-link:hover { color: var(--teal); }
</style>
</head>
<body>
  <header class="hero">
    <img src="./assets/brand/logo_src.jpeg" alt="Logo SRC" class="hero-logo">
    <div class="hero-tag">Spine Research Community</div>
    <h1 class="hero-title">Le système SRC</h1>
    <p class="hero-sub">50 Spine Surgeons · une base · 12 questionnaires</p>
    <p class="hero-lede">12 planches pour t'aider à remplir Follow <strong>vite et bien</strong>.</p>
  </header>

  <main>
    <div class="section-tag">Les planches</div>
    <h2 class="section-title">12 questionnaires, 1 série</h2>
    <section class="planches">
__CARDS__
    </section>

    <section class="about">
      <div class="about-photo" role="img" aria-label="Bureau SRC"></div>
      <div class="about-text">
        <p><strong>Nous sommes plus de 50 Spine Surgeons</strong> à utiliser Follow chaque jour.</p>
        <p>Une seule base, une seule logique de remplissage. C'est ça qui rend la SRC unique en France.</p>
        <div class="about-signature">— Le bureau SRC</div>
      </div>
    </section>
  </main>

  <footer>
    <div class="footer-left">
      <img src="./assets/brand/logo_src.jpeg" alt="Logo SRC" class="footer-logo">
      <span>© SRC · __TODAY__</span>
    </div>
    <a class="footer-link" href="https://github.com/jonathan3575/src-infographies" target="_blank" rel="noopener">github.com/jonathan3575/src-infographies</a>
  </footer>
</body>
</html>
"""

CARD_TEMPLATE = """    <a class="card__CLASS_EXTRA__" href="./__ID__/">
      <div class="card-tag">__CARD_TAG__</div>
      <div class="card-id">__ID__</div>
      <div class="card-titre">__TITRE__</div>
      <div class="card-meta">__META__</div>
    </a>"""

# Brand assets toujours copiés dans docs/assets/brand/, indépendamment des planches.
# - logo_src.jpeg : header + footer page d'accueil + planches
# - bureau_src.jpg : photo institutionnelle, utilisée par le mot du bureau de la planche 00
# - bureau_src_rooftop.jpg : ambiance communauté (rooftop), utilisée par l'encart "À propos" de la page d'accueil
BRAND_ASSETS = (
    "assets/brand/logo_src.jpeg",
    "assets/brand/bureau_src.jpg",
    "assets/brand/bureau_src_rooftop.jpg",
)


def render_index(published: list[dict]) -> str:
    cards_html: list[str] = []
    visible = [p for p in published if not p.get("skipped")]
    visible.sort(key=lambda p: (str(p.get("numero") or ""), p["id"]))
    for p in visible:
        is_intro = p["id"] == "00"
        class_extra = " intro" if is_intro else ""
        card_tag = "Intro · vue d'ensemble" if is_intro else "Questionnaire"
        numero = p.get("numero", "")
        total = p.get("total", "")
        meta_bits: list[str] = []
        if numero and total:
            meta_bits.append(f"#{numero}/{total}")
        meta_bits.append(f"v{p['version']}")

        replacements = {
            "__ID__": p["id"],
            "__TITRE__": p.get("titre", p["id"]),
            "__META__": " · ".join(meta_bits),
            "__CLASS_EXTRA__": class_extra,
            "__CARD_TAG__": card_tag,
        }
        card = CARD_TEMPLATE
        for k, v in replacements.items():
            card = card.replace(k, v)
        cards_html.append(card)

    if not cards_html:
        cards_html.append('    <div class="empty">Aucune planche publiée pour l\'instant.</div>')

    return (
        INDEX_TEMPLATE
        .replace("__CARDS__", "\n".join(cards_html))
        .replace("__TODAY__", date.today().isoformat())
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

    # Brand assets toujours copiés (pour que docs/index.html fonctionne même
    # si aucune planche ne les référence directement).
    for rel in BRAND_ASSETS:
        src = ROOT / rel
        if src.exists():
            copy_asset(src)

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
