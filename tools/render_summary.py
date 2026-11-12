#!/usr/bin/env python3
"""Render portrait or landscape summary graphics from the hosted Atlas data.

Run: python tools/render_summary.py --layout landscape
Portrait: 720x1280 MP4 / 540x960 GIF. Landscape: 1280x720 / 960x540.
MP4 is 30 fps; GIF is 25 fps. Both last 41 seconds.
The radar uses annual means. Proof/logic/data-flow drawings are illustrations.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import hashlib
import json
import math
from pathlib import Path
import subprocess

import matplotlib
matplotlib.use("Agg")
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle
import numpy as np
from PIL import Image
from scipy.interpolate import PchipInterpolator

class AtlasDataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_data = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "script" and dict(attrs).get("id") == "atlasData":
            self.in_data = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self.in_data = False

    def handle_data(self, data: str) -> None:
        if self.in_data:
            self.parts.append(data)


def read_payload(source: Path) -> dict:
    parser = AtlasDataParser()
    parser.feed(source.read_text(encoding="utf-8"))
    if not parser.parts:
        raise ValueError("Source atlas has no embedded atlasData JSON")
    return json.loads("".join(parser.parts))


ROOT = Path(__file__).resolve().parents[1]
W, H, FPS, GIF_FPS, DURATION = 720, 1280, 30, 25, 41
BG, PANEL, INK, MUTED, GRID = "#10151f", "#18222f", "#f3f3ef", "#9baec0", "#344656"
THEORY, BLUE, CYAN, GREEN, VIOLET = "#f3be75", "#58c4dd", "#68d5ce", "#83c167", "#b39be6"
RADIAL_MIN, RADIAL_MAX = -.6, .6
LABELS = ["Resources &\nbenchmarks", "Formal\ntheory", "Empirical\nperformance", "Scale &\ncapability", "Artifact\nrelease"]
COLORS = [CYAN, THEORY, BLUE, VIOLET, GREEN]
STORY_HEADLINES = [
    "This NeurIPS paper used formal theory to prove how fast an algorithm converges.",
    "Back then, accepted NeurIPS papers emphasized formal theory more than in any other year studied.",
    "But as time went on, accepted papers placed more emphasis on other contributions.",
    "By contrast, in 2024, accepted papers emphasized formal theory less than in any other year studied.",
    "In 2024, resource-and-benchmark framing was 0.76 standard deviations higher than in 2015.",
    "NeurIPS framing shifted away from formal theory and toward resources and benchmarks.",
]
HEADLINE_LINES = [
    ["This NeurIPS paper used", "formal theory to prove how", "fast an algorithm converges."],
    ["Back then, accepted NeurIPS", "papers emphasized formal theory", "more than in any other", "year studied."],
    ["But as time went on, accepted", "papers placed more emphasis", "on other contributions."],
    ["By contrast, in 2024,", "accepted papers emphasized", "formal theory less than in", "any other year studied."],
    ["In 2024,", "resource-and-benchmark framing", "was 0.76 standard deviations", "higher than in 2015."],
    ["NeurIPS framing shifted away", "from formal theory and toward", "resources and benchmarks."],
]
# Preserve the approved closing design while fading the current resource-framing headline.
APPROVED_HEADLINE_LINES = [HEADLINE_LINES[0], [], HEADLINE_LINES[4], HEADLINE_LINES[5]]
SCROLL_PAPER_IDS = [
    "main_2015_6512bd43d9caa6e02c990b0a82652dca_default",
    "main_2015_404dcc91b2aeaa7caa47487d1483e48a_default",
    "main_2015_0ebcc77dc72360d0eb8e9504c78d38bd_default",
    "main_2015_c0f168ce8900fa56e57789e2a2f2c9d0_default",
    "main_2015_7fec306d1e665bc9c748b5d2b99a6e97_default",
    "main_2015_309fee4e541e51de2e41f21bebb342aa_default",
]
PAPER_IDS = [
    "main_2015_c058f544c737782deacefa532d9add4c_default",
    "main_2024_370df50ccfdf8bde18f8f9c2d9151bda_datasets_and_benchmarks_track",
]
FINEWEB_URL = "https://proceedings.neurips.cc/paper_files/paper/2024/hash/370df50ccfdf8bde18f8f9c2d9151bda-Abstract-Datasets_and_Benchmarks_Track.html"


def clamp(x):
    return max(0., min(1., x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def enter(t, start, duration=.6):
    return ease((t - start) / duration)


def source_record(data):
    examples = []
    for paper_id in PAPER_IDS:
        paper = next(p for p in data["paper_axis_index"] if p["paper_id"] == paper_id)
        examples.append({key: paper[key] for key in ("paper_id", "title", "year", "proceedings_url", "scores")})
    examples[0]["citation_snapshot"] = {
        "provider": "Semantic Scholar", "count": 473, "accessed": "2026-10-23",
        "record_url": "https://www.semanticscholar.org/paper/8b56449fa9aeadcf86181697e9ec2269419d8817",
        "api_url": "https://api.semanticscholar.org/graph/v1/paper/ARXIV:1511.05932?fields=title,year,citationCount,influentialCitationCount,url,externalIds,venue",
        "displayed_in_animation": False,
        "note": "Used only when selecting an influential example; not a quality score or cross-year citation comparison.",
    }
    examples[0]["contribution"] = "Global linear convergence results for four Frank-Wolfe variants under relaxed assumptions."
    examples[0]["selection"] = "One influential theory-focused example, not an average or representative 2015 paper."
    examples[1]["dataset_snapshot"] = {
        "label": "2024 paper release", "tokens": 15_000_000_000_000,
        "common_crawl_snapshots": 96, "source_url": FINEWEB_URL, "accessed": "2026-10-23",
        "note": "These are the original paper's figures, not the subsequently expanded live dataset.",
    }
    examples[1]["selection"] = "An illustrative resource-building paper in the Datasets and Benchmarks track."
    return {
        "status": "Hosted summary animation; presentation update based on Kaggle v4 scientific data",
        "duration_seconds": DURATION, "video_fps": FPS, "gif_fps": GIF_FPS,
        "video_size": [W, H], "gif_size": [540, 960],
        "plot": "Radar polygons show annual mean framing scores, not individual-paper profiles.",
        "radial_scale": {"minimum": RADIAL_MIN, "maximum": RADIAL_MAX, "units": "full-corpus standard deviations", "shared_across_all_axes_and_frames": True},
        "interpolation": "C1 shape-preserving PCHIP interpolation through all ten observed annual means, with a continuously and linearly moving year cursor during the six-second middle section. No within-year measurements are asserted.",
        "illustrations": "The proof/error-bound curve, assumptions-to-proof-to-guarantee sequence and web-to-dataset flow are conceptual animations, not empirical figures.",
        "yearly": [{"year": r["year"], "n_papers": r["n_papers"], "means": {a: r[a + "_z_mean"] for a in data["focus_axes"]}} for r in data["yearly"]],
        "examples": examples,
        "scrolling_examples": [
            {key: p[key] for key in ("paper_id", "title", "year", "proceedings_url")}
            for paper_id in SCROLL_PAPER_IDS
            for p in data["paper_axis_index"] if p["paper_id"] == paper_id
        ],
        "scrolling_selection": "Six selected 2015 theory-focused papers illustrate the contribution style. Their number is not a sample proportion; no scores or author rankings are shown.",
        "theory_extrema": {
            "maximum_year": max(data["yearly"], key=lambda r: r["formal_theory_genre_z_mean"])["year"],
            "minimum_year": min(data["yearly"], key=lambda r: r["formal_theory_genre_z_mean"])["year"],
            "scope": "Annual mean formal-theory framing, not counts of paper types or popularity. Overlapping axes are separately standardized and cannot establish which paper type is most or least common.",
        },
        "storyboard": [
            {"seconds": [0, 7.5], "scene": "2015 theory paper: a drawn convergence bound and assumptions leading through proof to a mathematical guarantee"},
            {"seconds": [7.5, 13.5], "scene": "Six real 2015 theory-paper titles scroll beneath the decade-high theory-framing headline"},
            {"seconds": [13.5, 15], "scene": "The examples recede and the view widens to the conference"},
            {"seconds": [15, 21], "scene": "The radar and timeline move continuously from 2015 through 2024 as contribution emphases change"},
            {"seconds": [21, 25], "scene": "The 2024 profile holds as the headline identifies the decade-low theory-framing mean"},
            {"seconds": [25, 27], "scene": "Radar recedes into the background as the 2024 paper enters"},
            {"seconds": [27, 35], "scene": "The aggregate 2024 resource-framing shift, with FineWeb as an illustrative resource and its 2024 dataset scale"},
            {"seconds": [35, 41], "scene": "The current resource-framing headline fades into the unchanged approved final slide"},
        ],
        "resource_framing_comparison": {
            "axis": "resource_benchmark_genre",
            "baseline_year": 2015, "comparison_year": 2024,
            "change_sd": next(r["resource_benchmark_genre_z_mean"] for r in data["yearly"] if r["year"] == 2024)
                         - next(r["resource_benchmark_genre_z_mean"] for r in data["yearly"] if r["year"] == 2015),
            "display": "0.76 standard deviations higher than in 2015",
            "interpretation": "Unadjusted difference in annual mean framing scores; not a percentage of papers or a fitted decade slope.",
        },
        "headlines": STORY_HEADLINES,
        "headline_layout": "Each scene has one complete sentence in a fixed top-third reading area. Temporal and contrastive transitions connect the sentences into a continuous account of the paper's central finding. A separate large current-year label updates from 2015 to 2024 while the chart and timeline cursor move continuously. The year stays fully legible between updates.",
        "closing_sentence": STORY_HEADLINES[-1],
        "interpretation": "Accepted papers' titles and abstracts, 2015–2024. Examples illustrate framing, not typicality or research quality. Annual averages are unadjusted and partly reflect topic and track composition. Formal-theory framing declined; it did not disappear.",
    }


class Renderer:
    def __init__(self, data, layout="portrait"):
        self.landscape = layout == "landscape"
        self.width, self.height = (1280, 720) if self.landscape else (W, H)
        self.text_scale = .76 if self.landscape else 1.
        self.data = data
        self.axes = data["focus_axes"]
        self.rows = {int(r["year"]): r for r in data["yearly"]}
        self.papers = [next(p for p in data["paper_axis_index"] if p["paper_id"] == p_id) for p_id in PAPER_IDS]
        self.scroll_papers = [next(p for p in data["paper_axis_index"] if p["paper_id"] == p_id) for p_id in SCROLL_PAPER_IDS]
        self.fig = Figure(figsize=(self.width / 100, self.height / 100), dpi=100, facecolor=BG)
        self.canvas = FigureCanvasAgg(self.fig)
        # Keep equal x/y scaling in the illustrations, including every radar.
        self.ax = self.fig.add_axes([650 / 1280, 28 / 720, W * .76 / 1280, 850 * .76 / 720]
                                    if self.landscape else [0, 0, 1, 1])
        self.header_ax = self.fig.add_axes([0, 0, 1, 1], frameon=False) if self.landscape else None
        angles = np.array([-math.pi / 2 + i * math.tau / 5 for i in range(5)])
        self.directions = np.column_stack((np.cos(angles), np.sin(angles)))
        self.interpolator = PchipInterpolator(list(self.rows), [self.means(y) for y in self.rows], axis=0)
        self.opacity = 1.
        # Confirm that the display passes through every measured annual value.
        for year in self.rows:
            np.testing.assert_allclose(self.interpolator(year), self.means(year), atol=1e-12)
        values = self.interpolator(np.linspace(2015, 2024, 1001))
        assert values.min() >= RADIAL_MIN and values.max() <= RADIAL_MAX
        assert [" ".join(lines) for lines in HEADLINE_LINES] == STORY_HEADLINES
        for lines in HEADLINE_LINES:
            headline_font = FontProperties(family="DejaVu Sans", weight="bold", size=(34 if len(lines) > 3 else 37) * .72)
            for line in lines:
                width, _, _ = self.canvas.get_renderer().get_text_width_height_descent(line, headline_font, False)
                assert width <= W - 64, f"Headline exceeds side margins: {line}"

    def text(self, x, y, content, size=28, color=INK, weight="normal", ha="left", va="top", alpha=1, spacing=1.2, rotation=0):
        return self.ax.text(x, y, content, fontsize=size * .72 * self.text_scale, color=color,
                            fontfamily="DejaVu Sans", fontweight=weight, ha=ha, va=va,
                            alpha=clamp(alpha * self.opacity), linespacing=spacing, zorder=10, rotation=rotation)

    def box(self, x, y, width, height, color=PANEL, edge=GRID, alpha=1, radius=18, lw=1.4):
        self.ax.add_patch(FancyBboxPatch((x, y), width, height,
            boxstyle=f"round,pad=0,rounding_size={radius}", facecolor=color, edgecolor=edge,
            linewidth=lw, alpha=clamp(alpha * self.opacity), zorder=2))

    def line(self, x, y, color=GRID, width=2, alpha=1, dash="solid", zorder=3):
        self.ax.plot(x, y, color=color, linewidth=width, alpha=clamp(alpha * self.opacity),
                     linestyle=dash, solid_capstyle="round", zorder=zorder)

    def wrap(self, content, width, size=28, weight="bold"):
        font = FontProperties(family="DejaVu Sans", weight=weight, size=size * .72)
        renderer = self.canvas.get_renderer()
        lines, line = [], ""
        for word in content.split():
            candidate = f"{line} {word}".strip()
            measured, _, _ = renderer.get_text_width_height_descent(candidate, font, False)
            if line and measured > width:
                lines.append(line)
                line = word
            else:
                line = candidate
        return "\n".join(lines + [line])

    def means(self, year):
        return np.array([self.rows[year][a + "_z_mean"] for a in self.axes])

    def approved_header(self, t):
        """Keep the entire narrative and its year within the top third."""
        self.opacity = 1
        year = 2015 + 9 * clamp((t - 10) / 6)
        if t < 26.7:
            a = 1 - enter(t, 26, .5)
            base = min(2024, math.floor(year + 1e-9))
            color = THEORY if year < 2015.01 else BLUE
            self.text(360, 98, str(base), size=92, color=color, weight="bold",
                      ha="center", va="center", alpha=a)
        else:
            a = enter(t, 26.7, .6)
            self.text(185, 51, "2015", size=74, color=THEORY, weight="bold", ha="center", alpha=a)
            self.text(360, 68, "→", size=48, color=MUTED, ha="center", alpha=a)
            self.text(535, 51, "2024", size=74, color=BLUE, weight="bold", ha="center", alpha=a)
        if t < 9:
            scene, a = 0, enter(t, .2, .6) * (1 - enter(t, 8.5, .5))
        elif t < 16.6:
            scene, a = 1, enter(t, 9.1, .65) * (1 - enter(t, 16, .55))
        elif t < 26.6:
            scene, a = 2, enter(t, 16.65, .65) * (1 - enter(t, 26, .55))
        else:
            scene, a = 3, enter(t, 26.7, .65)
        lines = APPROVED_HEADLINE_LINES[scene]
        size, top, step = (34, 160, 44) if len(lines) > 3 else (37, 178, 49)
        for i, line in enumerate(lines):
            color = THEORY if scene == 0 and i == 1 else BLUE if scene == 3 and i == 2 else INK
            self.text(360, top + i * step, line, size=size, color=color, weight="bold", ha="center", alpha=a)
        if t < 26.6:
            a = enter(t, .7) * (1 - enter(t, 26, .55))
            x0, x1, y = 88, 632, 365
            progress = (year - 2015) / 9
            self.line([x0, x1], [y, y], GRID, 3, a)
            self.line([x0, x0 + progress * (x1 - x0)], [y, y], BLUE, 3, a)
            for tick in range(10):
                x = x0 + tick / 9 * (x1 - x0)
                self.line([x, x], [y - 5, y + 5], MUTED, 1, .5 * a)
            self.ax.scatter([x0 + progress * (x1 - x0)], [y], s=90, c=THEORY if progress == 0 else BLUE, alpha=a, zorder=6)
            self.text(x0, y + 13, "2015", size=22, color=THEORY, weight="bold", alpha=a)
            self.text(x1, y + 13, "2024", size=22, color=BLUE, weight="bold", ha="right", alpha=a)
        else:
            self.text(360, 366, "19,361 accepted papers · titles and abstracts", size=22,
                      color=MUTED, ha="center", alpha=enter(t, 26.7, .65))

    def story_header(self, t):
        """New story beats retain the approved fixed reading area and year rail."""
        self.opacity = 1
        year = 2015 + 9 * clamp((t - 15) / 6)
        base = min(2024, math.floor(year + 1e-9))
        self.text(360, 98, str(base), size=92, color=THEORY if year < 2015.01 else BLUE,
                  weight="bold", ha="center", va="center")
        if t < 7.9:
            scene, a = 0, enter(t, .2, .6) * (1 - enter(t, 7.4, .5))
        elif t < 13.9:
            scene, a = 1, enter(t, 7.95, .6) * (1 - enter(t, 13.4, .5))
        elif t < 21.3:
            scene, a = 2, enter(t, 14, .65) * (1 - enter(t, 20.8, .5))
        elif t < 25.6:
            scene, a = 3, enter(t, 21.4, .6) * (1 - enter(t, 25, .55))
        else:
            scene, a = 4, enter(t, 25.65, .65)
        lines = HEADLINE_LINES[scene]
        size, top, step = (34, 160, 44) if len(lines) > 3 else (37, 178, 49)
        for i, line in enumerate(lines):
            color = THEORY if (scene == 0 and i == 1) or (scene in (1, 3) and i == 0) else INK
            self.text(360, top + i * step, line, size=size, color=color, weight="bold", ha="center", alpha=a)
        x0, x1, y = 88, 632, 365
        progress, a = (year - 2015) / 9, enter(t, .7)
        self.line([x0, x1], [y, y], GRID, 3, a)
        self.line([x0, x0 + progress * (x1 - x0)], [y, y], BLUE, 3, a)
        for tick in range(10):
            x = x0 + tick / 9 * (x1 - x0)
            self.line([x, x], [y - 5, y + 5], MUTED, 1, .5 * a)
        self.ax.scatter([x0 + progress * (x1 - x0)], [y], s=90, c=THEORY if progress == 0 else BLUE, alpha=a, zorder=6)
        self.text(x0, y + 13, "2015", size=22, color=THEORY, weight="bold", alpha=a)
        self.text(x1, y + 13, "2024", size=22, color=BLUE, weight="bold", ha="right", alpha=a)

    def landscape_header(self, t):
        """Reflow the same six sentences beside the original scene geometry."""
        body_ax, body_scale = self.ax, self.text_scale
        self.ax, self.text_scale = self.header_ax, 1.
        self.ax.clear()
        self.ax.set(xlim=(0, self.width), ylim=(self.height, 0))
        self.ax.set_axis_off()
        self.opacity = 1
        for x in range(0, self.width + 1, 60):
            self.line([x, x], [0, self.height], GRID, .45, .08, zorder=0)
        for y in range(0, self.height + 1, 60):
            self.line([0, self.width], [y, y], GRID, .45, .08, zorder=0)
        self.line([605, 605], [68, 650], GRID, 1, .55)
        self.text(64, 48, "NEURIPS · EVIDENCE FRAMING", size=18, color=MUTED, weight="bold")
        year = 2015 + 9 * clamp((t - 15) / 6)
        label = "2015 → 2024" if t >= 35.7 else str(min(2024, math.floor(year + 1e-9)))
        self.text(60, 100, label, size=70 if t >= 35.7 else 96,
                  color=THEORY if year < 2015.01 else BLUE, weight="bold")
        if t < 7.9:
            scene, a = 0, enter(t, .2, .6) * (1 - enter(t, 7.4, .5))
        elif t < 13.9:
            scene, a = 1, enter(t, 7.95, .6) * (1 - enter(t, 13.4, .5))
        elif t < 21.3:
            scene, a = 2, enter(t, 14, .65) * (1 - enter(t, 20.8, .5))
        elif t < 25.6:
            scene, a = 3, enter(t, 21.4, .6) * (1 - enter(t, 25, .55))
        elif t < 35.6:
            scene, a = 4, enter(t, 25.65, .65) * (1 - enter(t, 35, .55))
        else:
            scene, a = 5, enter(t, 35.7, .65)
        headline_size = 34 if scene == 4 else 40
        headline = self.wrap(STORY_HEADLINES[scene], 485, size=headline_size)
        self.text(64, 232, headline, size=headline_size, weight="bold", spacing=1.24, alpha=a)
        x0, x1, y = 66, 550, 553
        progress = (year - 2015) / 9
        self.line([x0, x1], [y, y], GRID, 3)
        self.line([x0, x0 + progress * (x1 - x0)], [y, y], BLUE, 3)
        for tick in range(10):
            x = x0 + tick / 9 * (x1 - x0)
            self.line([x, x], [y - 5, y + 5], MUTED, 1, .5)
        self.ax.scatter([x0 + progress * (x1 - x0)], [y], s=90,
                        c=THEORY if progress == 0 else BLUE, zorder=6)
        self.text(x0, y + 15, "2015", size=21, color=THEORY, weight="bold")
        self.text(x1, y + 15, "2024", size=21, color=BLUE, weight="bold", ha="right")
        self.text(64, 632, "19,361 accepted papers · titles and abstracts", size=18, color=MUTED)
        self.ax, self.text_scale = body_ax, body_scale

    def scene_theory_papers(self, t, alpha=1):
        self.opacity = alpha
        before = set(self.ax.get_children())
        scroll = max(0, t - 7.9) * 142
        for i, paper in enumerate(self.scroll_papers):
            py = 464 + i * 190 - scroll
            if py > 1165 or py + 170 < 436:
                continue
            self.box(60, py, 600, 170, edge="#735d44", radius=14)
            self.text(90, py + 20, "NEURIPS 2015 · FORMAL THEORY", size=17, color=THEORY, weight="bold")
            self.text(90, py + 56, self.wrap(paper["title"], 540, size=26), size=26, weight="bold", spacing=1.17)
        clip = Rectangle((0, 436), W, 712, transform=self.ax.transData)
        for artist in set(self.ax.get_children()) - before:
            artist.set_clip_path(clip)
            artist.set_clip_on(True)
            artist._story_scroll_clip = True
        self.text(360, 1183, "Selected theory-focused papers · NeurIPS 2015", size=20,
                  color=MUTED, ha="center")

    def paper_icon(self, x, y, scale=1, color=BLUE, alpha=1):
        self.box(x - 16 * scale, y - 21 * scale, 32 * scale, 42 * scale,
                 color=BG, edge=color, alpha=alpha, radius=3 * scale, lw=1.1)
        for offset in [-7, 1, 9]:
            self.line([x - 9 * scale, x + 9 * scale], [y + offset * scale] * 2, color, 1, alpha)

    def shape(self, values, cx, cy, radius, color=BLUE, alpha=1, reference=False):
        values = np.asarray(values)
        assert np.all(values >= RADIAL_MIN) and np.all(values <= RADIAL_MAX), "Radar would clip data"
        xy = np.array([cx, cy]) + self.directions * ((values - RADIAL_MIN) / (RADIAL_MAX - RADIAL_MIN))[:, None] * radius
        a = clamp(alpha * self.opacity)
        if not reference:
            self.ax.add_patch(Polygon(xy, closed=True, facecolor=color, edgecolor="none", alpha=.16 * a, zorder=4))
        self.ax.add_patch(Polygon(xy, closed=True, fill=False, edgecolor=color, linewidth=3 if not reference else 1.5,
                                 alpha=a, linestyle="solid" if not reference else (0, (4, 5)), joinstyle="round", zorder=5))
        if not reference:
            self.ax.scatter(xy[:, 0], xy[:, 1], s=27, c=color, alpha=a, zorder=6)

    def radar(self, values, cx=360, cy=640, radius=205, color=BLUE, alpha=1, labels=1, ghost=False, compact=False, background=False):
        previous_artists = set(self.ax.get_children())
        a = clamp(alpha * self.opacity)
        for value in [-.4, -.2, 0, .2, .4, .6]:
            r = (value - RADIAL_MIN) / (RADIAL_MAX - RADIAL_MIN) * radius
            self.ax.add_patch(Circle((cx, cy), r, fill=False, edgecolor="#6c8292" if value == 0 else GRID,
                linewidth=.9, linestyle=(0, (3, 5)) if value == 0 else "solid", alpha=.8 * a, zorder=1))
        for i, direction in enumerate(self.directions):
            point = np.array([cx, cy]) + direction * radius
            self.line([cx, point[0]], [cy, point[1]], GRID, 1, alpha=alpha)
            if labels > 0:
                p = np.array([cx, cy]) + direction * (radius + (47 if compact else 65))
                self.text(*p, LABELS[i], size=17 if compact else 23, color=COLORS[i], weight="bold",
                          ha="center", va="center", alpha=alpha * labels, spacing=1.12)
        if ghost:
            self.shape(self.means(2015), cx, cy, radius, THEORY, alpha=alpha * .4, reference=True)
        self.shape(values, cx, cy, radius, color, alpha=alpha)
        if background:
            for artist in set(self.ax.get_children()) - previous_artists:
                artist.set_zorder(.5)

    def proof(self, t, py, alpha=1):
        """A conceptual geometric error-bound illustration, not paper results."""
        x0, x1, y0, y1 = 128, 592, py + 365, py + 230
        self.line([x0, x0, x1], [y1, y0, y0], MUTED, 1.4, alpha)
        self.text(x0, y1 - 27, "Error bound", size=19, color=MUTED, alpha=alpha)
        self.text(x1, y0 + 12, "Iterations", size=18, color=MUTED, ha="right", alpha=alpha)
        progress = enter(t, 1.8, 2.8)
        u = np.linspace(0, max(.002, progress), 100)
        curve = y0 - 125 * np.exp(-4.8 * u)
        self.line(x0 + (x1 - x0) * u, curve, THEORY, 3.3, alpha)
        self.ax.scatter([x0 + (x1 - x0) * progress], [y0 - 125 * np.exp(-4.8 * progress)], s=70, c=THEORY, alpha=self.opacity * alpha, zorder=6)
        self.text(575, py + 253, r"$C\,\rho^k$", size=34, color=THEORY, ha="right", alpha=alpha * enter(t, 2.3))
        p = enter(t, 4.5)
        self.line([545, 557, 582], [py + 415, py + 428, py + 401], GREEN, 4, alpha * p)
        self.text(128, py + 406, "Linear convergence proved", size=23, color=GREEN, alpha=alpha * p)

    def scene_2015(self, t, alpha=1, shift=0):
        self.opacity = alpha
        paper_in = enter(t, .45, .8)
        py = 436 + shift + 80 * (1 - paper_in)
        self.box(60, py, 600, 450, edge="#735d44", alpha=paper_in)
        self.text(92, py + 22, "FORMAL THEORY", size=18, color=THEORY, weight="bold", alpha=paper_in)
        title = self.wrap(self.papers[0]["title"], 536, size=29)
        self.text(92, py + 62, title, size=29, weight="bold", alpha=paper_in)
        self.proof(t, py=py, alpha=enter(t, 1.5))
        self.theory_flow(t, shift)
        self.text(360, 1183 + shift, "An illustrative theory paper · NeurIPS 2015", size=21,
                  color=MUTED, ha="center", alpha=enter(t, 5.9))

    def theory_flow(self, t, shift=0):
        """A schematic proof sequence, not a formal derivation from the paper."""
        self.text(360, 932 + shift, "A mathematical guarantee", size=29, color=THEORY,
                  weight="bold", ha="center", alpha=enter(t, 4.4))
        cy = 1032 + shift
        for i, (x, label) in enumerate([(140, "Assumptions"), (360, "Proof"), (580, "Guarantee")]):
            p = enter(t, 4.6 + i * .4, .8)
            theta = np.linspace(-math.pi / 2, -math.pi / 2 + math.tau * p, 100)
            color = GREEN if i == 2 else THEORY
            self.line(x + 43 * np.cos(theta), cy + 43 * np.sin(theta), color, 2, p)
            if i < 2:
                self.text(x, cy, r"$\mathcal{A}$" if i == 0 else r"$\vdash$", size=41,
                          color=THEORY, ha="center", va="center", alpha=p)
            else:
                self.line([x - 18, x - 5, x + 20], [cy, cy + 13, cy - 16], GREEN, 3.5, p)
            self.text(x, cy + 66, label, size=23, ha="center", alpha=p)
            if i < 2:
                q = enter(t, 5.0 + i * .4, .6)
                end = x + 62 + 96 * q
                self.ax.add_patch(FancyArrowPatch((x + 62, cy), (end, cy), arrowstyle="-|>",
                    mutation_scale=15, color=THEORY, alpha=self.opacity * q * .65, linewidth=1.5, zorder=4))
                phase = ((t - 5.0 - i * .4) * .65) % 1
                self.ax.scatter([x + 62 + 96 * phase], [cy], s=24, c=THEORY,
                                alpha=self.opacity * q, zorder=5)

    def scene_morph(self, t, alpha=1, intro=1, backdrop=0):
        self.opacity = alpha
        progress = clamp((t - 10) / 6)
        year = 2015 + 9 * progress
        means = self.interpolator(year)
        if backdrop:
            cy = 745 - 175 * backdrop
            radius = 205 + 55 * backdrop
        else:
            cy = 745 + 110 * (1 - intro)
            radius = 205 * (.65 + .35 * intro)
        text_alpha = 1 - enter(t, 16, .55) if backdrop else 1
        self.radar(means, cy=cy, radius=radius, color=BLUE, alpha=1 - .82 * backdrop, labels=text_alpha, ghost=True, background=backdrop > 0)
        if backdrop < 1:
            self.line([267, 299], [1025, 1025], THEORY, 1.5, .5 * text_alpha, dash=(0, (4, 5)))
            self.text(313, 1015, "2015 reference", size=18, color=MUTED, alpha=text_alpha)
            self.text(360, 1085, "19,361 accepted papers", size=29, ha="center", alpha=text_alpha)
            self.text(360, 1132, "Titles + abstracts · yearly averages", size=22, color=MUTED, ha="center", alpha=text_alpha)
            self.text(360, 1197, "Smooth visual interpolation of annual means", size=18, color=MUTED, ha="center", alpha=text_alpha)

    def dataset_flow(self, t, shift=0, alpha=1):
        # Schematic documents flow into a reusable dataset.
        yy = 764 + shift
        for i in range(6):
            p = (t * .32 + i / 6) % 1
            x = 105 + p * 244
            y = yy - 55 + 68 * math.sin(p * math.pi)
            self.paper_icon(x, y, .72, CYAN, alpha * (.3 + .7 * math.sin(math.pi * p)))
        x, y, width, height = 395, yy - 20, 115, 93
        self.box(x - width / 2, y, width, height, color=PANEL, edge=CYAN, alpha=alpha, radius=0)
        for dy in [0, height]:
            self.ax.add_patch(Ellipse((x, y + dy), width, 30, facecolor=PANEL, edgecolor=CYAN,
                                      alpha=self.opacity * alpha, linewidth=2, zorder=4))
        for dy in [31, 62]:
            self.ax.add_patch(Ellipse((x, y + dy), width, 30, fill=False, edgecolor=CYAN,
                                      alpha=self.opacity * alpha * .65, linewidth=1.2, zorder=4))
        self.ax.add_patch(FancyArrowPatch((475, yy + 23), (562, yy + 23), arrowstyle="-|>", mutation_scale=17,
                                          color=BLUE, alpha=self.opacity * alpha, linewidth=2, zorder=4))
        for layer in range(2):
            for i in range(3):
                nx, ny = 574 + layer * 35, yy - 10 + i * 31
                self.ax.add_patch(Circle((nx, ny), 5, color=BLUE, alpha=self.opacity * alpha, zorder=5))
                if layer == 0:
                    for j in range(3):
                        self.line([nx, nx + 35], [ny, yy - 10 + j * 31], BLUE, .8, alpha * .3)

    def scene_2024(self, t, alpha=1, offset=0):
        self.opacity = alpha
        # The annual radar remains behind this foreground paper during entry.
        py = 436 + 110 * (1 - enter(t, 16.6, 1.4))
        self.box(60 + offset, py, 600, 430, edge="#31606c")
        self.text(92 + offset, py + 22, "RESOURCES + SCALE", size=18, color=CYAN, weight="bold")
        self.text(92 + offset, py + 65, "The FineWeb Datasets", size=37, weight="bold")
        subtitle = self.papers[1]["title"].split(":", 1)[1].strip()
        self.text(92 + offset, py + 122, self.wrap(subtitle, 530, size=26, weight="normal"), size=26, spacing=1.24)
        # Keep the diagram within the moving card; offset only occurs on exit.
        if abs(offset) < .1:
            self.dataset_flow(t, shift=py - 436, alpha=enter(t, 18.1))
        amount = 15 * enter(t, 18.7, 2.2)
        self.text(360 + offset, 905, f"{amount:.0f}T", size=92, color=CYAN, weight="bold", ha="center", alpha=enter(t, 18.5))
        self.text(360 + offset, 1015, "tokens of web text", size=29, ha="center", alpha=enter(t, 18.5))
        self.text(360 + offset, 1070, "96 web snapshots", size=26, color=BLUE, ha="center", alpha=enter(t, 20.5))
        self.text(360 + offset, 1120, "2024 dataset release", size=19, color=MUTED, ha="center", alpha=enter(t, 20.5))

    def scene_final(self, t, alpha=1, progress=1):
        self.opacity = alpha
        for index, year in enumerate([2015, 2024]):
            center = 185 + index * 350 + (-100 if index == 0 else 100) * (1 - progress)
            color = THEORY if index == 0 else BLUE
            self.text(center, 480, str(year), size=44, color=color, weight="bold", ha="center")
            self.radar(self.means(year), cx=center, cy=710, radius=140, labels=0, color=color)
            # Gentle tracing motion highlights the direction of the strongest shift.
            axis = 1 if index == 0 else 0
            radius = (self.means(year)[axis] - RADIAL_MIN) / (RADIAL_MAX - RADIAL_MIN) * 140
            pulse = .5 + .5 * math.sin((t - 26) * math.tau / 2.5)
            pt = np.array([center, 710]) + self.directions[axis] * radius
            self.ax.add_patch(Circle(pt, 7 + pulse * 7, fill=False, edgecolor=color, alpha=self.opacity * .45, linewidth=1.2, zorder=6))
        self.text(360, 883, "Yearly averages · same axes and scale", size=22, color=MUTED, ha="center")
        for index, label in enumerate(["Frank–Wolfe\nconvergence", "FineWeb\ndatasets"]):
            x = 70 + index * 350
            color = THEORY if index == 0 else BLUE
            self.box(x, 955, 230, 144, edge=color)
            self.text(x + 115, 978, "EXAMPLE", size=15, color=MUTED, ha="center")
            self.text(x + 115, 1010, label, size=25, color=color, weight="bold", ha="center")
        self.ax.add_patch(FancyArrowPatch((320, 1026), (399, 1026), arrowstyle="-|>", mutation_scale=22,
                                         color=MUTED, alpha=self.opacity, linewidth=2, zorder=5))
        self.text(360, 1143, "Accepted papers' titles and abstracts\n2015–2024", size=23, color=MUTED, ha="center", spacing=1.45)

    def render(self, t):
        story_time = t
        closing = t >= 35
        if closing:
            # Preserve the exact original frame times, including transition alpha
            # and pulse phase, instead of introducing floating-point time drift.
            t = (round(t * FPS) - 9 * FPS) / FPS
        self.ax.clear()
        self.ax.set(xlim=(0, W), ylim=(H, 430 if self.landscape else 0))
        self.ax.set_axis_off()
        self.opacity = 1
        # A quiet coordinate grid gives the illustrations depth without a title banner.
        for x in range(0, W + 1, 60):
            self.line([x, x], [0, H], GRID, .45, .08, zorder=0)
        for y in range(0, H + 1, 60):
            self.line([0, W], [y, y], GRID, .45, .08, zorder=0)
        background_artists = set(self.ax.get_children())
        if closing:
            if t < 28:
                p = ease((t - 26) / 2)
                self.scene_2024(t, alpha=1 - enter(t, 26, .65), offset=300 * p)
                self.scene_final(t, alpha=enter(t, 26.7, 1.1), progress=p)
            else:
                self.scene_final(t)
        elif t < 7.5:
            self.scene_2015(t)
        elif t < 13.5:
            p = ease((t - 7.5) / 1.2)
            if t < 8.2:
                self.scene_2015(t, alpha=1 - enter(t, 7.5, .65), shift=-260 * p)
            self.scene_theory_papers(t, alpha=enter(t, 7.9, .8))
        elif t < 15:
            p = ease((t - 13.5) / 1.5)
            self.scene_theory_papers(t, alpha=1 - enter(t, 13.5, .65))
            self.scene_morph(t - 5, alpha=enter(t, 14, 1), intro=p)
        elif t < 21:
            self.scene_morph(t - 5)
        elif t < 25:
            self.scene_morph(16)
        elif t < 27:
            p = ease((t - 25) / 2)
            self.scene_morph(t - 9, backdrop=p)
            self.scene_2024(t - 9, alpha=enter(t, 25.65, 1))
        else:
            self.opacity = 1
            self.radar(self.means(2024), cy=570, radius=260, color=BLUE, alpha=.14, labels=0, background=True)
            self.scene_2024(t - 9)
        # Illustrations can move away without crossing the fixed headline area.
        body_clip = Rectangle((0, 430), W, H - 430, transform=self.ax.transData)
        for artist in set(self.ax.get_children()) - background_artists:
            if not getattr(artist, "_story_scroll_clip", False):
                artist.set_clip_path(body_clip)
            artist.set_clip_on(True)
        if self.landscape:
            self.landscape_header(story_time)
        elif closing:
            self.approved_header(t)
        else:
            self.story_header(t)
        self.canvas.draw()
        return Image.fromarray(np.asarray(self.canvas.buffer_rgba())[:, :, :3].copy())


def run(args):
    data = read_payload(args.source)
    wide = args.layout == "landscape"
    prefix = "evidence-framing-shift-wide" if wide else "evidence-framing-shift"
    output = args.output
    frames = args.frames or ROOT / ".render-cache" / args.layout / "frames"
    output.mkdir(parents=True, exist_ok=True)
    frames.mkdir(parents=True, exist_ok=True)
    record = source_record(data)
    renderer = Renderer(data, args.layout)
    if wide:
        record.update(video_size=[1280, 720], gif_size=[960, 540], layout="landscape",
                      headline_layout="The same six sentences reflow in a left reading column; the illustrations retain equal x/y scaling in a right column. Timings, annual means and narrative are shared with the portrait version.")
    record_path = output / ("story-sources-wide.json" if wide else "story-sources.json")
    samples = [("poster", 7), ("2015-papers", 10), ("2024-theory", 23), ("2024", 33), ("comparison", 39), ("morph", 18)]
    for name, t in samples:
        renderer.render(t).save(output / f"{prefix}-{name}.png")
    record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    if args.stills_only:
        print(f"Rendered {args.layout} preview stills to {output}")
        return
    for i in range(FPS * DURATION):
        renderer.render(i / FPS).save(frames / f"frame-{i:04d}.png")
        if i % 180 == 0:
            print(f"Rendered {i}/{FPS * DURATION} frames", flush=True)
    pattern = str(frames / "frame-%04d.png")
    common = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", pattern, "-frames:v", str(FPS * DURATION)]
    mp4 = output / f"{prefix}.mp4"
    subprocess.run(common + ["-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(mp4)], check=True)
    palette = frames.parent / "palette-v2.png"
    filtering = f"fps={GIF_FPS},scale={'960:540' if wide else '540:960'}:flags=lanczos"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(mp4),
                    "-vf", filtering + ",palettegen=max_colors=192:stats_mode=diff", "-frames:v", "1", str(palette)], check=True)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(mp4), "-i", str(palette),
                    "-lavfi", f"[0:v]{filtering}[v];[v][1:v]paletteuse=dither=bayer:bayer_scale=4",
                    "-loop", "0", str(output / f"{prefix}.gif")], check=True)
    record["artifacts"] = {
        p.name: {"bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in sorted(output.glob(f"{prefix}.*"))
    }
    record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"duration_seconds": DURATION, "frames": FPS * DURATION, "artifacts": record["artifacts"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "index.html")
    parser.add_argument("--output", type=Path, default=ROOT / "drafts")
    parser.add_argument("--frames", type=Path)
    parser.add_argument("--layout", choices=["portrait", "landscape"], default="portrait")
    parser.add_argument("--stills-only", action="store_true")
    run(parser.parse_args())
