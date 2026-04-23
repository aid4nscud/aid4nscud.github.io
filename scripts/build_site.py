from __future__ import annotations

import html
import shutil
from pathlib import Path
from urllib.parse import urlparse

import requests

ROOT = Path(__file__).resolve().parents[1]
SITE_SRC = ROOT / "site_src"
ASSET_DIR = ROOT / "assets" / "site"

import sys
sys.path.insert(0, str(SITE_SRC))
from site_data import SITE, NAV, FOOTER, ASSETS, HOME, COMMUNITY, ABOUT, CONTACT, PAGES  # noqa: E402

session = requests.Session()
session.headers["User-Agent"] = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
)

ASSET_OUTPUTS = {
    "logo": "branding/logo.png",
    "hero_video": "media/hero-video.mp4",
    "hero_poster": "media/hero-poster.jpg",
    "overview_video": "media/overview-video.mp4",
    "overview_poster": "media/overview-poster.jpg",
    "mockup_main": "media/mockup-main.png",
    "mockup_left": "media/mockup-left.png",
    "mockup_right": "media/mockup-right.png",
    "mockup_secondary": "media/mockup-secondary.png",
    "store_badge_a": "branding/store-badge-a.png",
    "store_badge_b": "branding/store-badge-b.png",
}


def e(value: str) -> str:
    return html.escape(value, quote=True)


def asset_url(key: str) -> str:
    return "/assets/site/" + ASSET_OUTPUTS[key].replace("\\", "/")


def clean_outputs() -> None:
    for path in [
        ROOT / "assets" / "mirror",
        ROOT / "assets" / "site",
        ROOT / "_partials",
        ROOT / "home",
        ROOT / "community",
        ROOT / "about-us",
        ROOT / "contact",
        ROOT / "blank-1",
    ]:
        if path.exists():
            shutil.rmtree(path)

    for path in [
        ROOT / "index.html",
        ROOT / "404.html",
        ROOT / "styles.css",
        ROOT / "app.js",
        ROOT / "robots.txt",
        ROOT / "sitemap.xml",
    ]:
        if path.exists():
            path.unlink()


def download_assets() -> None:
    for key, source in ASSETS.items():
        rel = ASSET_OUTPUTS[key]
        target = ASSET_DIR / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        response = session.get(source, timeout=120)
        response.raise_for_status()
        target.write_bytes(response.content)


def copy_static_sources() -> None:
    shutil.copyfile(SITE_SRC / "styles.css", ROOT / "styles.css")
    shutil.copyfile(SITE_SRC / "app.js", ROOT / "app.js")


def render_nav(current_slug: str) -> str:
    items = []
    normalized = current_slug.strip("/")
    for item in NAV:
        item_slug = item["href"].strip("/")
        current = " aria-current=\"page\"" if normalized == item_slug else ""
        items.append(f'<a href="{e(item["href"])}"{current}>{e(item["label"])}</a>')
    return "".join(items)


def render_header(current_slug: str) -> str:
    return f"""
    <header class=\"site-header\">
      <div class=\"container site-header-inner\">
        <a class=\"brand\" href=\"/\" aria-label=\"WorldSchool home\">
          <img class=\"brand-mark\" src=\"{asset_url('logo')}\" alt=\"WorldSchool logo\" />
          <span class=\"brand-tagline\">{e(SITE['brand_tagline'])}</span>
        </a>
        <button class=\"nav-toggle\" type=\"button\" aria-expanded=\"false\" aria-controls=\"site-nav\" data-nav-toggle>
          <span aria-hidden=\"true\">☰</span>
          <span class=\"sr-only\">Toggle navigation</span>
        </button>
        <nav id=\"site-nav\" class=\"site-nav\" data-site-nav>
          {render_nav(current_slug)}
        </nav>
        <div class=\"header-actions\">
          <a class=\"button button-secondary desktop-only\" href=\"/contact/\">Contact</a>
          <a class=\"button button-primary desktop-only\" href=\"/contact/?role=parent\">Join now</a>
        </div>
      </div>
    </header>
    """


def render_footer() -> str:
    columns = []
    for column in FOOTER["columns"]:
        items = "".join(f"<li>{e(item)}</li>" for item in column["items"])
        columns.append(
            f"<div class=\"footer-column\"><h4>{e(column['title'])}</h4><ul>{items}</ul></div>"
        )
    return f"""
    <footer class=\"site-footer\">
      <div class=\"container site-footer-inner\">
        <div class=\"footer-grid\">
          <div class=\"footer-brand\">
            <img class=\"brand-mark\" src=\"{asset_url('logo')}\" alt=\"WorldSchool logo\" />
            <p>{e(SITE['meta_description'])}</p>
          </div>
          {''.join(columns)}
        </div>
        <div class=\"footer-bottom\">
          <span>TM WorldSchool 2025</span>
          <a href=\"mailto:{e(FOOTER['email'])}\">{e(FOOTER['email'])}</a>
        </div>
      </div>
    </footer>
    """


def card(title: str, body: str, level: str = "h3", accent: bool = False, href: str | None = None) -> str:
    class_name = "card accent-card" if accent else "card"
    inner = f"<{level}>{e(title)}</{level}><p>{e(body)}</p>"
    if href:
        inner += f'<div><a class="text-link" href="{e(href)}" target="_blank" rel="noreferrer">Read more</a></div>'
    return f'<article class="{class_name}">{inner}</article>'


def render_home() -> str:
    capabilities = "".join(card(item["title"], item["body"], level="h3") for item in HOME["capabilities"])
    pillars = "".join(card(item["title"], item["body"], level="h3") for item in HOME["pillars"])
    principles = "".join(card(item["title"], item["body"], level="h3", accent=True) for item in HOME["principles"])
    alive = "".join(card(item["title"], item["body"], level="h3") for item in HOME["alive"]["items"])
    benefits = "".join(card(item["title"], item["body"], level="h3") for item in HOME["benefits"])
    prodigies = "".join(card(item["title"], item["body"], level="h3", accent=True, href=item["href"]) for item in HOME["prodigies"]["items"])
    metric_html = "".join(
        f'<div class="metric"><span class="metric-value">{e(item["value"])}</span><span class="metric-label">{e(item["label"])}</span></div>'
        for item in HOME["timeline"]["stats"]
    )
    pills = "".join(f'<span class="pill">{e(word.strip())}</span>' for word in HOME["hero"]["eyebrow"].split("•"))

    return f"""
    <section class=\"hero\">
      <div class=\"hero-media\">
        <video class=\"hero-video\" autoplay muted loop playsinline poster=\"{asset_url('hero_poster')}\">
          <source src=\"{asset_url('hero_video')}\" type=\"video/mp4\" />
        </video>
      </div>
      <div class=\"container hero-grid\">
        <div>
          <p class=\"eyebrow\">{e(HOME['hero']['eyebrow'])}</p>
          <h1 class=\"hero-title\">{e(HOME['hero']['title'])}</h1>
          <p class=\"hero-copy\">{e(HOME['hero']['subtitle'])}</p>
          <div class=\"hero-actions\">
            <a class=\"button button-primary\" href=\"{e(HOME['hero']['cta_primary']['href'])}\">{e(HOME['hero']['cta_primary']['label'])}</a>
            <a class=\"button button-secondary\" href=\"{e(HOME['hero']['cta_secondary']['href'])}\">{e(HOME['hero']['cta_secondary']['label'])}</a>
            <a class=\"button button-tertiary\" href=\"#about\">Discover more</a>
          </div>
          <div class=\"hero-pills\">{pills}</div>
        </div>
        <div class=\"device-cluster\" aria-hidden=\"true\">
          <img class=\"device device-left\" src=\"{asset_url('mockup_left')}\" alt=\"\" />
          <img class=\"device device-secondary\" src=\"{asset_url('mockup_secondary')}\" alt=\"\" />
          <img class=\"device device-main\" src=\"{asset_url('mockup_main')}\" alt=\"WorldSchool app screen\" />
          <img class=\"device device-right\" src=\"{asset_url('mockup_right')}\" alt=\"\" />
        </div>
      </div>
    </section>

    <section id=\"about\" class=\"section\">
      <div class=\"container split\">
        <div class=\"section-header\">
          <p class=\"section-kicker\">Global MOOC Access</p>
          <h2 class=\"section-heading\">{e(HOME['about']['title'])}</h2>
          <p class=\"lead\">{e(HOME['about']['kicker'])}</p>
          <p class=\"section-copy\">{e(HOME['about']['body'][0])}</p>
          <p class=\"section-copy\">{e(HOME['about']['body'][1])}</p>
        </div>
        <div class=\"media-frame\">
          <video autoplay muted loop playsinline poster=\"{asset_url('overview_poster')}\">
            <source src=\"{asset_url('overview_video')}\" type=\"video/mp4\" />
          </video>
        </div>
      </div>
    </section>

    <section class=\"section\">
      <div class=\"container\">
        <div class=\"section-header\">
          <p class=\"section-kicker\">Platform capabilities</p>
          <h2 class=\"section-heading\">Simple. Flexible. Human.</h2>
          <p class=\"section-copy\">WorldSchool gives families, educators, schools, and businesses the tools to organize learning, connect in real life, and collaborate privately on their own terms.</p>
        </div>
        <div class=\"grid grid-3\">{capabilities}</div>
      </div>
    </section>

    <section class=\"section\">
      <div class=\"container\">
        <div class=\"section-header\">
          <p class=\"section-kicker\">Education re-imagined</p>
          <h2 class=\"section-heading\">{e(HOME['pillars_intro']['title'])}</h2>
          <p class=\"section-copy\">{e(HOME['pillars_intro']['body'])}</p>
        </div>
        <div class=\"grid grid-3\">{pillars}</div>
      </div>
    </section>

    <section class=\"section\">
      <div class=\"container\">
        <div class=\"section-header\">
          <p class=\"section-kicker\">Principles</p>
          <h2 class=\"section-heading\">Built for real families</h2>
        </div>
        <div class=\"grid grid-2\">{principles}</div>
      </div>
    </section>

    <section class=\"section\">
      <div class=\"container split\">
        <div>
          <div class=\"section-header\">
            <p class=\"section-kicker\">Iteration, innovation, impact</p>
            <h2 class=\"section-heading\">{e(HOME['timeline']['title'])}</h2>
            <p class=\"section-copy\">{e(HOME['timeline']['body'])}</p>
          </div>
          <div class=\"metric-grid\">{metric_html}</div>
        </div>
        <div class=\"panel\">
          <h3>App experience</h3>
          <p class=\"section-copy\">WorldSchool helps families coordinate learning, community, and real-world experiences in one place.</p>
          <div class=\"grid grid-2\" style=\"margin-top:18px;\">
            <img class=\"device\" style=\"position:relative;width:100%;transform:none;border-radius:24px;\" src=\"{asset_url('mockup_main')}\" alt=\"WorldSchool mobile view\" />
            <img class=\"device\" style=\"position:relative;width:100%;transform:none;border-radius:24px;\" src=\"{asset_url('mockup_secondary')}\" alt=\"WorldSchool app details\" />
          </div>
          <div class=\"badge-row\">
            <img class=\"store-badge\" src=\"{asset_url('store_badge_a')}\" alt=\"WorldSchool store badge\" />
            <img class=\"store-badge\" src=\"{asset_url('store_badge_b')}\" alt=\"WorldSchool store badge\" />
          </div>
        </div>
      </div>
    </section>

    <section class=\"section\">
      <div class=\"container\">
        <div class=\"section-header\">
          <p class=\"section-kicker\">Learning that feels alive</p>
          <h2 class=\"section-heading\">{e(HOME['alive']['title'])}</h2>
          <p class=\"section-copy\">{e(HOME['alive']['body'])}</p>
        </div>
        <div class=\"grid grid-3\">{alive}</div>
      </div>
    </section>

    <section class=\"section\">
      <div class=\"container\">
        <div class=\"section-header\">
          <p class=\"section-kicker\">Why families choose it</p>
          <h2 class=\"section-heading\">{e(HOME['benefits_title'])}</h2>
        </div>
        <div class=\"grid grid-2\">{benefits}</div>
      </div>
    </section>

    <section class=\"section\">
      <div class=\"container\">
        <div class=\"section-header\">
          <p class=\"section-kicker\">What becomes possible</p>
          <h2 class=\"section-heading\">{e(HOME['prodigies']['title'])}</h2>
          <p class=\"section-copy\">{e(HOME['prodigies']['intro'])}</p>
        </div>
        <div class=\"grid grid-2 prodigy-grid\">{prodigies}</div>
      </div>
    </section>

    <section class=\"section cta-section\">
      <div class=\"container\">
        <div class=\"cta-shell\">
          <p class=\"section-kicker\">Join the movement</p>
          <h2 class=\"section-heading\">{e(HOME['cta']['title'])}</h2>
          <p class=\"section-copy\">{e(HOME['cta']['body'])}</p>
          <div class=\"hero-actions\">
            <a class=\"button button-primary\" href=\"/contact/?role=parent\">Join as a Parent</a>
            <a class=\"button button-secondary\" href=\"/contact/?role=host\">Join as a Host</a>
          </div>
        </div>
      </div>
    </section>
    """


def render_community() -> str:
    cards = "".join(card(item["title"], item["body"], level="h3", accent=i == 0) for i, item in enumerate(COMMUNITY["cards"]))
    pillars = "".join(card(item["title"], item["body"], level="h3") for item in HOME["pillars"][:6])
    return f"""
    <section class=\"page-hero\">
      <div class=\"container\">
        <div class=\"page-hero-shell\">
          <p class=\"eyebrow\">Community</p>
          <h1>{e(COMMUNITY['title'])}</h1>
          <p>{e(COMMUNITY['subtitle'])}</p>
          <p class=\"section-copy\">{e(COMMUNITY['intro'])}</p>
        </div>
      </div>
    </section>
    <section class=\"section\">
      <div class=\"container\"><div class=\"grid grid-2\">{cards}</div></div>
    </section>
    <section class=\"section\">
      <div class=\"container\">
        <div class=\"section-header\">
          <p class=\"section-kicker\">How community works</p>
          <h2 class=\"section-heading\">Education Re-Imagined</h2>
          <p class=\"section-copy\">Community at WorldSchool is about more than access — it is about building healthy ecosystems where children, parents, and educators can genuinely grow together.</p>
        </div>
        <div class=\"grid grid-3\">{pillars}</div>
      </div>
    </section>
    <section class=\"section cta-section\">
      <div class=\"container\"><div class=\"cta-shell\"><h2 class=\"section-heading\">Join the Global Learning Movement</h2><p class=\"section-copy\">Find the people, places, and experiences that make learning feel real, social, and alive.</p><div class=\"hero-actions\"><a class=\"button button-primary\" href=\"/contact/?role=parent\">Join as a Parent</a><a class=\"button button-secondary\" href=\"/contact/?role=host\">Become a Host</a></div></div></div>
    </section>
    """


def render_about() -> str:
    values = "".join(card(value, "", level="h3", accent=True) for value in ABOUT["values"])
    principles = "".join(card(item["title"], item["body"], level="h3") for item in HOME["principles"])
    metric_html = "".join(
        f'<div class="metric"><span class="metric-value">{e(item["value"])}</span><span class="metric-label">{e(item["label"])}</span></div>'
        for item in HOME["timeline"]["stats"]
    )
    return f"""
    <section class=\"page-hero\">
      <div class=\"container\">
        <div class=\"page-hero-shell\">
          <p class=\"eyebrow\">About WorldSchool</p>
          <h1>{e(ABOUT['title'])}</h1>
          <p>{e(ABOUT['subtitle'])}</p>
        </div>
      </div>
    </section>
    <section class=\"section\">
      <div class=\"container split\">
        <div class=\"panel\"><p class=\"section-copy\">{e(ABOUT['intro'][0])}</p><p class=\"section-copy\">{e(ABOUT['intro'][1])}</p></div>
        <div class=\"media-frame\"><img src=\"{asset_url('hero_poster')}\" alt=\"WorldSchool\" /></div>
      </div>
    </section>
    <section class=\"section\"><div class=\"container\"><div class=\"section-header\"><p class=\"section-kicker\">What guides the platform</p><h2 class=\"section-heading\">Principle-first education</h2></div><div class=\"grid grid-2\">{values}</div></div></section>
    <section class=\"section\"><div class=\"container\"><div class=\"section-header\"><p class=\"section-kicker\">Track record</p><h2 class=\"section-heading\">{e(HOME['timeline']['title'])}</h2><p class=\"section-copy\">{e(HOME['timeline']['body'])}</p></div><div class=\"metric-grid\">{metric_html}</div></div></section>
    <section class=\"section\"><div class=\"container\"><div class=\"section-header\"><p class=\"section-kicker\">Core principles</p><h2 class=\"section-heading\">How WorldSchool is built</h2></div><div class=\"grid grid-2\">{principles}</div></div></section>
    <section class=\"section cta-section\"><div class=\"container\"><div class=\"cta-shell\"><h2 class=\"section-heading\">Want to learn more?</h2><p class=\"section-copy\">Reach out as a parent, host, educator, or supporter and start a conversation about what learning can look like outside conventional systems.</p><div class=\"hero-actions\"><a class=\"button button-primary\" href=\"/contact/\">Contact WorldSchool</a></div></div></div></section>
    """


def render_contact() -> str:
    points = "".join(
        f'<li><strong>{e(item["label"])}:</strong> {e(item["value"])}</li>' for item in CONTACT["contact_points"]
    )
    role_buttons = "".join(
        f'<button class="role-chip{" is-active" if i == 0 else ""}" type="button" data-role-target="{"host" if item["value"].lower() == "host" else "parent"}" aria-pressed="{"true" if i == 0 else "false"}"><strong>{e(item["value"])}</strong><span>{e(item["description"])}</span></button>'
        for i, item in enumerate(CONTACT["roles"])
    )
    return f"""
    <section class=\"page-hero\">
      <div class=\"container\">
        <div class=\"page-hero-shell\">
          <p class=\"eyebrow\">Contact</p>
          <h1>{e(CONTACT['title'])}</h1>
          <p>{e(CONTACT['subtitle'])}</p>
        </div>
      </div>
    </section>
    <section class=\"section cta-section\">
      <div class=\"container contact-layout\">
        <aside class=\"contact-card\">
          <p class=\"section-kicker\">Direct contact</p>
          <h3>Built for families, hosts, and educators</h3>
          <p>Use the form to draft an inquiry in your own email client. That keeps the site completely static and independent while still making outreach easy.</p>
          <ul class=\"contact-points\">{points}</ul>
        </aside>
        <div class=\"contact-card\">
          <form class=\"contact-form\" data-contact-form>
            <input type=\"hidden\" name=\"role\" value=\"Parent\" data-role-input />
            <div>
              <div class=\"fieldset-title\">I’m reaching out as</div>
              <div class=\"role-switch\">{role_buttons}</div>
            </div>
            <div class=\"field-grid\">
              <div class=\"field\"><label for=\"first_name\">First name</label><input class=\"input\" id=\"first_name\" name=\"first_name\" required /></div>
              <div class=\"field\"><label for=\"last_name\">Last name</label><input class=\"input\" id=\"last_name\" name=\"last_name\" required /></div>
              <div class=\"field\"><label for=\"email\">Email</label><input class=\"input\" id=\"email\" name=\"email\" type=\"email\" required /></div>
              <div class=\"field\"><label for=\"phone\">Phone</label><input class=\"input\" id=\"phone\" name=\"phone\" /></div>
              <div class=\"field\"><label for=\"zip\">Zip code</label><input class=\"input\" id=\"zip\" name=\"zip\" /></div>
              <div class=\"field\"><label for=\"city\">City</label><input class=\"input\" id=\"city\" name=\"city\" /></div>
              <div class=\"field\"><label for=\"state\">State</label><input class=\"input\" id=\"state\" name=\"state\" /></div>
              <div class=\"field\"><label for=\"country\">Country</label><input class=\"input\" id=\"country\" name=\"country\" /></div>
            </div>
            <div class=\"field\"><label for=\"message\">Message</label><textarea class=\"textarea\" id=\"message\" name=\"message\" placeholder=\"Have a message for us?\"></textarea></div>
            <button class=\"button button-primary button-block\" type=\"submit\">Open email draft</button>
            <p class=\"form-note\">Submitting opens your mail app with the completed inquiry addressed to Hello@WorldSchool.com.</p>
            <p class=\"form-status\" data-form-status></p>
          </form>
        </div>
      </div>
    </section>
    """


def render_404() -> str:
    return """
    <section class=\"page-hero\">
      <div class=\"container\">
        <div class=\"page-hero-shell\">
          <p class=\"eyebrow\">404</p>
          <h1>Page not found</h1>
          <p>The page you were looking for is not here, but the main sections of the site are below.</p>
          <div class=\"hero-actions\">
            <a class=\"button button-primary\" href=\"/\">Go home</a>
            <a class=\"button button-secondary\" href=\"/contact/\">Contact</a>
          </div>
        </div>
      </div>
    </section>
    """


def render_body(kind: str) -> str:
    if kind == "home":
        return render_home()
    if kind == "community":
        return render_community()
    if kind == "about":
        return render_about()
    if kind == "contact":
        return render_contact()
    raise ValueError(f"Unknown page kind: {kind}")


def canonical_for(slug: str) -> str:
    if not slug:
        return SITE["domain"] + "/"
    return SITE["domain"] + "/" + slug.strip("/") + "/"


def render_document(page: dict, current_slug: str, body_html: str) -> str:
    canonical = canonical_for(page["slug"])
    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{e(page['title'])}</title>
  <meta name=\"description\" content=\"{e(page['description'])}\" />
  <meta property=\"og:title\" content=\"{e(page['title'])}\" />
  <meta property=\"og:description\" content=\"{e(page['description'])}\" />
  <meta property=\"og:type\" content=\"website\" />
  <meta property=\"og:url\" content=\"{e(canonical)}\" />
  <meta property=\"og:image\" content=\"{e(SITE['domain'] + asset_url('hero_poster'))}\" />
  <meta name=\"twitter:card\" content=\"summary_large_image\" />
  <meta name=\"twitter:title\" content=\"{e(page['title'])}\" />
  <meta name=\"twitter:description\" content=\"{e(page['description'])}\" />
  <link rel=\"canonical\" href=\"{e(canonical)}\" />
  <link rel=\"icon\" href=\"{asset_url('logo')}\" type=\"image/png\" />
  <link rel=\"stylesheet\" href=\"/styles.css\" />
</head>
<body class=\"page page-{e(page['kind'])}\">
  {render_header(current_slug)}
  <main>
    {body_html}
  </main>
  {render_footer()}
  <script src=\"/app.js\" defer></script>
</body>
</html>
"""


def write_page(slug: str, title: str, description: str, kind: str) -> None:
    page = {"slug": slug, "title": title, "description": description, "kind": kind}
    body = render_body(kind)
    output = ROOT / slug / "index.html" if slug else ROOT / "index.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_document(page, slug, body), encoding="utf-8")


def write_404() -> None:
    page = {"slug": "404", "title": "404 | WorldSchool App", "description": SITE["meta_description"], "kind": "home"}
    body = render_404()
    (ROOT / "404.html").write_text(render_document(page, "", body), encoding="utf-8")


def write_robots() -> None:
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: https://aid4nscud.github.io/sitemap.xml\n",
        encoding="utf-8",
    )


def write_sitemap() -> None:
    urls = [canonical_for(page["slug"]) for page in PAGES]
    body = "\n".join(f"  <url><loc>{url}</loc></url>" for url in urls)
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n',
        encoding="utf-8",
    )


def write_readme() -> None:
    (ROOT / "README.md").write_text(
        "# WorldSchool static site\n\n"
        "Independent static rebuild of the WorldSchool marketing site for GitHub Pages.\n\n"
        "## Structure\n\n"
        "- `site_src/site_data.py` — shared page content and asset sources\n"
        "- `site_src/styles.css` — site styles\n"
        "- `site_src/app.js` — small client-side interactions\n"
        "- `scripts/build_site.py` — downloads selected public assets and regenerates the published pages\n\n"
        "## Rebuild\n\n"
        "Run:\n\n"
        "`python3 scripts/build_site.py`\n",
        encoding="utf-8",
    )


def main() -> None:
    clean_outputs()
    download_assets()
    copy_static_sources()
    for page in PAGES:
        write_page(page["slug"], page["title"], page["description"], page["kind"])
    write_404()
    write_robots()
    write_sitemap()
    write_readme()
    print("built site")


if __name__ == "__main__":
    main()
