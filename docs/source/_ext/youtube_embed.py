# docs/source/_ext/youtube_embed.py
from docutils import nodes
from docutils.parsers.rst import Directive, directives


class YouTubeEmbed(Directive):
    required_arguments = 2  # video_id, title
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {}
    has_content = False

    def run(self):
        video_id = self.arguments[0].strip()
        title = self.arguments[1].strip()

        html = f"""
<details>
  <summary><strong>{title}</strong></summary>
  <div style="position: relative; padding-bottom: 56.25%; height: 0; margin-top: 0.75rem; border-radius: 16px; overflow: hidden;">
    <iframe
      src="https://www.youtube-nocookie.com/embed/{video_id}?rel=0"
      title="{title}"
      style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      referrerpolicy="strict-origin-when-cross-origin"
      allowfullscreen
      loading="lazy"
    ></iframe>
  </div>
</details>
"""
        nodes_out = []

        # Auto-insert intro line
        nodes_out.append(
            nodes.paragraph("", "Prefer a walkthrough? Expand to watch the YouTube tutorial.")
        )

        # Raw HTML embed
        nodes_out.append(nodes.raw("", html, format="html"))

        # Auto-insert fallback link (no fallback values; uses required args)
        fallback = nodes.paragraph()
        fallback += nodes.Text("If the embed does not load, watch on YouTube: ")
        fallback += nodes.reference("", title, refuri=f"https://youtu.be/{video_id}")
        fallback += nodes.Text(".")
        nodes_out.append(fallback)

        return nodes_out


def setup(app):
    app.add_directive("youtube_embed", YouTubeEmbed)
    return {"version": "1.0", "parallel_read_safe": True}
