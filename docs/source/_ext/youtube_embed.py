# docs/source/_ext/youtube_embed.py
import json
import re
from functools import lru_cache
from html import escape
from pathlib import Path

from docutils import nodes
from docutils.parsers.rst import Directive, directives


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "video"


def _watch_key(title: str, explicit_key: str | None) -> str:
    return explicit_key.strip() if explicit_key else _slugify(title)


@lru_cache(maxsize=1)
def _load_video_catalog() -> dict:
    catalog_path = Path(__file__).resolve().parent.parent / "_data" / "video_catalog.json"
    return json.loads(catalog_path.read_text())


def _normalize_description(description: str) -> str:
    cleaned = description.strip()
    if cleaned.lower().startswith("learn "):
        cleaned = cleaned[6:].strip()
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]
    return cleaned


def _resolve_catalog_video(identifier: str) -> tuple[str, dict] | None:
    catalog = _load_video_catalog().get("videos", {})
    direct_match = catalog.get(identifier)
    if direct_match is not None:
        return identifier, direct_match

    slug_match = catalog.get(_slugify(identifier))
    if slug_match is not None:
        return _slugify(identifier), slug_match

    normalized_identifier = identifier.strip().lower()
    for key, video in catalog.items():
        if video.get("title", "").strip().lower() == normalized_identifier:
            return key, video

    return None


def _render_video_card(
    *,
    title: str,
    description: str,
    watch_key: str,
    video_id: str | None = None,
    intro_text: str | None = None,
) -> str:
    escaped_title = escape(title)
    escaped_description = escape(_normalize_description(description))
    escaped_key = escape(watch_key)
    iframe_html = ""
    footer_html = """
  <p class="fc-video-unavailable">
    This video slot is planned for the series. Once a YouTube video is linked,
    it will expand and play directly on this page.
  </p>
"""

    if video_id:
        escaped_video_id = escape(video_id)
        player_id = f"fc-video-{escaped_key}"
        fallback_url = f"https://youtu.be/{escaped_video_id}"
        iframe_html = f"""
  <div class="fc-video-frame-wrap">
    <div
      id="{player_id}"
      class="fc-youtube-player"
      data-video-key="{escaped_key}"
      data-video-id="{escaped_video_id}"
      title="{escaped_title}"
    ></div>
  </div>
"""
        footer_html = f"""
  <p class="fc-video-fallback">
    If the embed does not load, watch on YouTube:
    <a href="{fallback_url}">{escaped_title}</a>.
  </p>
"""

    intro_html = ""
    if intro_text:
        intro_html = f"""
<p class="fc-video-intro">{escape(intro_text)}</p>
"""

    return f"""
{intro_html}<details class="fc-video-card" data-video-key="{escaped_key}">
  <summary class="fc-video-summary">
    <span class="fc-video-checkbox-wrap" aria-hidden="true">
      <span class="fc-video-checkbox-ui" aria-hidden="true"></span>
    </span>
    <span class="fc-video-summary-text">
      <span class="fc-video-title">{escaped_title}</span>
      <span class="fc-video-state">Unwatched</span>
    </span>
  </summary>
  <button
    class="fc-video-checkbox"
    data-video-key="{escaped_key}"
    type="button"
    role="checkbox"
    aria-checked="false"
    aria-label="Mark {escaped_title} as watched"
  ></button>
  <div class="fc-video-body">
    <p class="fc-video-description">{escaped_description}</p>
{iframe_html}{footer_html}
  </div>
</details>
"""


class YouTubeEmbed(Directive):
    required_arguments = 1
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        "description": directives.unchanged,
        "key": directives.unchanged,
        "intro": directives.unchanged,
    }
    has_content = False

    def run(self):
        resolved = None
        if len(self.arguments) == 1:
            resolved = _resolve_catalog_video(self.arguments[0].strip())
            if resolved is None:
                error = self.state_machine.reporter.error(
                    f"Unknown video catalog key or title '{self.arguments[0].strip()}'.",
                    line=self.lineno,
                )
                return [error]

            resolved_key, resolved_video = resolved
            video_id = resolved_video.get("video_id")
            title = resolved_video["title"]
            description = self.options.get("description", resolved_video.get("description", ""))
            watch_key = self.options.get("key", resolved_key)
        else:
            video_id = self.arguments[0].strip()
            title = self.arguments[1].strip()
            resolved = _resolve_catalog_video(self.options.get("key", title))
            description = self.options.get("description", "")
            if not description and resolved is not None:
                _, resolved_video = resolved
                description = resolved_video.get("description", "")
            watch_key = _watch_key(title, self.options.get("key"))

        intro_text = self.options.get("intro")
        html = _render_video_card(
            title=title,
            description=description,
            watch_key=watch_key,
            video_id=video_id,
            intro_text=intro_text,
        )
        return [nodes.raw("", html, format="html")]


class VideoCard(Directive):
    required_arguments = 1  # title
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        "description": directives.unchanged_required,
        "key": directives.unchanged,
    }
    has_content = False

    def run(self):
        title = self.arguments[0].strip()
        description = self.options.get("description", "").strip()
        watch_key = _watch_key(title, self.options.get("key"))
        html = _render_video_card(
            title=title,
            description=description,
            watch_key=watch_key,
        )
        return [nodes.raw("", html, format="html")]


class VideoCatalogPage(Directive):
    required_arguments = 1  # page key
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}
    has_content = False

    def run(self):
        page_key = self.arguments[0].strip()
        catalog = _load_video_catalog()
        page = catalog.get("pages", {}).get(page_key)
        videos = catalog.get("videos", {})

        if page is None:
            error = self.state_machine.reporter.error(
                f"Unknown video catalog page '{page_key}'.",
                line=self.lineno,
            )
            return [error]

        nodes_out = []
        for group in page.get("groups", []):
            heading = group["heading"]
            section = nodes.section(ids=[nodes.make_id(heading)])
            section += nodes.title(text=heading)

            for video_key in group.get("video_keys", []):
                video = videos.get(video_key)
                if video is None:
                    error = self.state_machine.reporter.error(
                        f"Unknown video key '{video_key}' in page '{page_key}'.",
                        line=self.lineno,
                    )
                    nodes_out.append(error)
                    continue

                html = _render_video_card(
                    title=video["title"],
                    description=video.get("description", ""),
                    watch_key=video_key,
                    video_id=video.get("video_id"),
                    intro_text=None,
                )
                section += nodes.raw("", html, format="html")

            nodes_out.append(section)

        return nodes_out


def setup(app):
    app.add_directive("youtube_embed", YouTubeEmbed)
    app.add_directive("video_card", VideoCard)
    app.add_directive("video_catalog_page", VideoCatalogPage)
    return {"version": "1.0", "parallel_read_safe": True}
