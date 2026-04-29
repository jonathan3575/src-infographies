"""Export rendered HTML to PDF (print) or MP4 (TL vertical) via Playwright.

Consumes the latest *_v{N}.html in output/{pdf,tl} produced by render.py.
"""
from __future__ import annotations

import asyncio
import re
import shutil
import subprocess
from pathlib import Path

import click

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PDF_DIR = ROOT / "output" / "pdf"
OUTPUT_TL_DIR = ROOT / "output" / "tl"

TL_WIDTH = 1080
TL_HEIGHT = 1920
TL_SCROLL_DURATION_MS = 15_000


def latest_html(directory: Path, qid: str, suffix: str) -> Path:
    rx = re.compile(rf"{re.escape(qid)}_{suffix}_v(\d+)\.html$")
    candidates = []
    for p in directory.glob(f"{qid}_{suffix}_v*.html"):
        m = rx.match(p.name)
        if m:
            candidates.append((int(m.group(1)), p))
    if not candidates:
        raise FileNotFoundError(f"Aucun HTML {suffix} pour {qid} dans {directory}. Lance render d'abord.")
    candidates.sort()
    return candidates[-1][1]


async def export_print(qid: str) -> Path:
    from playwright.async_api import async_playwright

    html_path = latest_html(OUTPUT_PDF_DIR, qid, "print")
    pdf_path = html_path.with_suffix(".pdf")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(html_path.as_uri(), wait_until="networkidle")
        await page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            margin={"top": "12mm", "right": "12mm", "bottom": "12mm", "left": "12mm"},
        )
        await context.close()
        await browser.close()
    return pdf_path


async def export_tl(qid: str) -> Path:
    from playwright.async_api import async_playwright

    html_path = latest_html(OUTPUT_TL_DIR, qid, "tl")
    out_mp4 = html_path.with_suffix(".mp4")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(
            viewport={"width": TL_WIDTH, "height": TL_HEIGHT},
            record_video_dir=str(OUTPUT_TL_DIR),
            record_video_size={"width": TL_WIDTH, "height": TL_HEIGHT},
        )
        page = await context.new_page()
        await page.goto(html_path.as_uri(), wait_until="networkidle")

        await page.evaluate(
            """
            async (durationMs) => {
              const total = document.body.scrollHeight - window.innerHeight;
              const start = performance.now();
              return new Promise(resolve => {
                function step(now) {
                  const t = Math.min(1, (now - start) / durationMs);
                  const eased = t < 0.5 ? 2*t*t : 1 - Math.pow(-2*t+2, 2)/2;
                  window.scrollTo(0, total * eased);
                  if (t < 1) requestAnimationFrame(step);
                  else resolve(true);
                }
                requestAnimationFrame(step);
              });
            }
            """,
            TL_SCROLL_DURATION_MS,
        )

        video = page.video
        await context.close()
        await browser.close()

        if video is None:
            raise RuntimeError("Playwright n'a pas enregistré de vidéo (video=None).")
        webm_path = Path(await video.path())

    if shutil.which("ffmpeg"):
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(webm_path), "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out_mp4)],
            check=True,
        )
        webm_path.unlink(missing_ok=True)
        return out_mp4
    fallback = html_path.with_suffix(".webm")
    shutil.move(str(webm_path), str(fallback))
    return fallback


@click.command()
@click.option("--questionnaire", "-q", required=True, help="ID du questionnaire (ex : 2L)")
@click.option("--format", "fmt", type=click.Choice(["print", "tl"]), required=True)
def main(questionnaire: str, fmt: str) -> None:
    if fmt == "print":
        out = asyncio.run(export_print(questionnaire))
    else:
        out = asyncio.run(export_tl(questionnaire))
    click.echo(f"Export {fmt} : {out}")


if __name__ == "__main__":
    main()
