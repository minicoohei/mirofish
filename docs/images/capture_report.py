"""Capture report HTML sections as screenshots using Playwright."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

REPORT = Path(__file__).parent.parent.parent / "cc_layer" / "state" / "session_kou" / "report.html"
OUT_DIR = Path(__file__).parent

SECTIONS = [
    ("01_profile", "#profile", 1000),
    ("02_core_skills", "#core", 800),
    ("03_overview_radar", "#overview", 1000),
    ("04_income_chart", "#salary", 700),
    ("05_career_paths", "#paths", 1200),
    ("06_reskill", "#reskill", 700),
    ("07_mirror", "#mirror", 900),
    ("08_swarm_voices", "#voices", 1200),
    ("09_macro_trends", "#macro", 900),
    ("10_knowledge_graph", "#graph", 1000),
]


def main():
    report_path = sys.argv[1] if len(sys.argv) > 1 else str(REPORT)
    report_url = f"file://{Path(report_path).resolve()}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.goto(report_url, wait_until="networkidle")
        page.wait_for_timeout(3000)  # Wait for charts to render

        for name, selector, clip_h in SECTIONS:
            try:
                el = page.query_selector(selector)
                if el:
                    # Scroll element into view
                    el.scroll_into_view_if_needed()
                    page.wait_for_timeout(800)

                    box = el.bounding_box()
                    if box:
                        # Capture with some padding, clip to desired height
                        y = max(0, box["y"] - 10)
                        h = min(clip_h, box["height"] + 20)
                        page.screenshot(
                            path=str(OUT_DIR / f"report_{name}.png"),
                            clip={"x": 0, "y": y, "width": 1400, "height": h},
                        )
                        print(f"OK: report_{name}.png ({int(box['height'])}px section, clipped to {int(h)}px)")
                    else:
                        print(f"SKIP: {name} - no bounding box")
                else:
                    print(f"SKIP: {name} - selector '{selector}' not found")
            except Exception as e:
                print(f"ERROR: {name} - {e}")

        browser.close()

    # Create GIF from best sections
    try:
        from PIL import Image

        gif_sections = [
            "01_profile",
            "03_overview_radar",
            "04_income_chart",
            "05_career_paths",
            "08_swarm_voices",
            "10_knowledge_graph",
        ]
        frames = []
        for name in gif_sections:
            img_path = OUT_DIR / f"report_{name}.png"
            if img_path.exists():
                img = Image.open(img_path)
                w, h = img.size
                new_w = 800
                new_h = int(h * new_w / w)
                img = img.resize((new_w, new_h), Image.LANCZOS)
                frames.append(img)

        if frames:
            frames[0].save(
                OUT_DIR / "report_demo.gif",
                save_all=True,
                append_images=frames[1:],
                duration=3000,  # 3 seconds per frame
                loop=0,
            )
            print(f"\nGIF saved: report_demo.gif ({len(frames)} frames)")
    except ImportError:
        print("Pillow not installed, skipping GIF. Install: pip install Pillow")


if __name__ == "__main__":
    main()
