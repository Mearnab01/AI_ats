
# ── SVG icon library ───────────────────────────────────────────────────────────
_ICONS: dict[str, str] = {
    "check":    '<polyline points="20 6 9 17 4 12"/>',
    "x":        '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
    "alert":    '<path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
    "info":     '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>',
    "arrow":    '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>',
    "trending": '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
    "file":     '<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/>',
    "cpu":      '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/>',

    "chart":    '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
    "star":     '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    "shield":   '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    "target":   '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "layers":   '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
    "clock":    '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "award":    '<circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/>',
    "download": '<path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
    "pdf":      '<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><path d="M9 15v-4"/><path d="M12 15v-6"/><path d="M15 15v-2"/>',
    "eye":      '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>',
    "trash":    '<polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>',
    "upload":   '<polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0018 9h-1.26A8 8 0 103 16.3"/>',
}

def svg_icon(name: str, size: int = 16, stroke: str = "currentColor") -> str:
    paths = _ICONS.get(name, "")
    if not paths:
        # Fail loud in dev instead of silently rendering an empty box.
        paths = _ICONS["alert"]
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{stroke}" stroke-width="1.8" stroke-linecap="round" '
        f'stroke-linejoin="round" style="display:inline-block;vertical-align:middle;">'
        f"{paths}</svg>"
    )


# ── Severity style mapping ─────────────────────────────────────────────────────
_SEVERITY_MAP = {
    "critical": ("#F0503A", "rgba(240,80,58,.08)",  "rgba(240,80,58,.2)",  "danger"),
    "high":     ("#F0503A", "rgba(240,80,58,.06)",  "rgba(240,80,58,.15)", "danger"),
    "medium":   ("#F5A623", "rgba(245,166,35,.06)", "rgba(245,166,35,.15)","warning"),
    "moderate": ("#F5A623", "rgba(245,166,35,.06)", "rgba(245,166,35,.15)","warning"),
    "low":      ("#4A9EF5", "rgba(74,158,245,.06)", "rgba(74,158,245,.15)","info"),
}
_DEFAULT_SEVERITY = ("#8C92A0", "rgba(255,255,255,.04)", "rgba(255,255,255,.1)", "neutral")


def get_severity_style(severity: str | None) -> tuple[str, str, str]:
    level = (severity or "low").lower()
    c, bg, border, _ = _SEVERITY_MAP.get(level, _DEFAULT_SEVERITY)
    return c, bg, border


def severity_badge(severity: str) -> str:
    level = (severity or "low").lower()
    color, bg, border, _ = _SEVERITY_MAP.get(level, _DEFAULT_SEVERITY)
    return (
        f'<span style="display:inline-flex;align-items:center;padding:2px 9px;'
        f'border-radius:9999px;font-size:11px;font-weight:700;letter-spacing:.04em;'
        f'text-transform:uppercase;background:{bg};color:{color};border:1px solid {border};">'
        f"{level}</span>"
    )


# ── Card wrapper ───────────────────────────────────────────────────────────────
def card(content: str, extra_style: str = "") -> str:
    return (
        f'<div style="background:#111318;border:1px solid rgba(255,255,255,.08);'
        f'border-radius:16px;padding:20px 24px;position:relative;overflow:hidden;{extra_style}">'
        f'<div style="position:absolute;inset:0;background:linear-gradient(145deg,rgba(255,255,255,.025) 0%,transparent 100%);pointer-events:none;"></div>'
        f"{content}</div>"
    )


# ── Section header ─────────────────────────────────────────────────────────────
def section_header(icon: str, title: str, subtitle: str = "") -> str:
    sub = f'<p style="margin:0;font-size:12px;color:#555C6B;margin-top:1px;">{subtitle}</p>' if subtitle else ""
    return (
        f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;'
        f'padding-bottom:16px;border-bottom:1px solid rgba(255,255,255,.08);">'
        f'<div style="width:32px;height:32px;background:rgba(232,164,74,.08);'
        f'border:1px solid rgba(232,164,74,.35);border-radius:8px;display:flex;'
        f'align-items:center;justify-content:center;flex-shrink:0;">'
        f'{svg_icon(icon, 16, "#E8A44A")}</div>'
        f'<div><h3 style="margin:0;font-size:15px;font-family:Fraunces,serif;font-weight:600;'
        f'color:#F0F2F5;">{title}</h3>{sub}</div></div>'
    )


# ── Progress bar (HTML) ────────────────────────────────────────────────────────
def progress_bar(pct: float, color: str = "brand") -> str:
    grads = {
        "success": "linear-gradient(90deg,#1a9e63,#2ECC8A)",
        "warning": "linear-gradient(90deg,#c47a0a,#F5A623)",
        "danger":  "linear-gradient(90deg,#c03020,#F0503A)",
        "brand":   "linear-gradient(90deg,#C4852E,#E8A44A)",
    }
    bg = grads.get(color, grads["brand"])
    return (
        f'<div style="background:#0C0E12;border-radius:9999px;height:6px;overflow:hidden;">'
        f'<div class="progress-bar" data-width="{pct:.0f}" '
        f'style="height:100%;width:{pct:.0f}%;background:{bg};border-radius:9999px;'
        f'transition:width 620ms cubic-bezier(.22,.68,0,1.2);"></div></div>'
    )


def bar_color(pct: float) -> str:
    return "success" if pct >= 0.8 else "warning" if pct >= 0.6 else "danger"


# ── Score color ────────────────────────────────────────────────────────────────
def score_color(score: float) -> str:
    return "#2ECC8A" if score >= 80 else "#F5A623" if score >= 60 else "#F0503A"


# ── Badge ─────────────────────────────────────────────────────────────────────
def badge(text: str, variant: str = "neutral") -> str:
    styles = {
        "success": ("rgba(46,204,138,.10)",  "#2ECC8A", "rgba(46,204,138,.25)"),
        "warning": ("rgba(245,166,35,.10)",  "#F5A623", "rgba(245,166,35,.25)"),
        "danger":  ("rgba(240,80,58,.10)",   "#F0503A", "rgba(240,80,58,.25)"),
        "info":    ("rgba(74,158,245,.10)",  "#4A9EF5", "rgba(74,158,245,.25)"),
        "brand":   ("rgba(232,164,74,.08)",  "#E8A44A", "rgba(232,164,74,.35)"),
        "neutral": ("#1E2129",               "#8C92A0", "rgba(255,255,255,.08)"),
    }
    bg, color, border = styles.get(variant, styles["neutral"])
    return (
        f'<span style="display:inline-flex;align-items:center;padding:2px 9px;'
        f'border-radius:9999px;font-size:11px;font-weight:700;letter-spacing:.04em;'
        f'text-transform:uppercase;background:{bg};color:{color};border:1px solid {border};">'
        f"{text}</span>"
    )


# ── Pill ──────────────────────────────────────────────────────────────────────
def pill(text: str, variant: str = "neutral") -> str:
    styles = {
        "success": ("rgba(46,204,138,.08)",  "#2ECC8A", "rgba(46,204,138,.2)"),
        "danger":  ("rgba(240,80,58,.08)",   "#F0503A", "rgba(240,80,58,.2)"),
        "warning": ("rgba(245,166,35,.08)",  "#F5A623", "rgba(245,166,35,.2)"),
        "neutral": ("rgba(255,255,255,.04)", "#8C92A0", "rgba(255,255,255,.08)"),
    }
    bg, color, border = styles.get(variant, styles["neutral"])
    return (
        f'<span style="display:inline-block;background:{bg};color:{color};'
        f'border:1px solid {border};border-radius:9999px;padding:3px 11px;'
        f'font-size:12px;font-weight:600;margin:2px 3px;">{text}</span>'
    )


# ── Alert ─────────────────────────────────────────────────────────────────────
def alert(message: str, variant: str = "info") -> str:
    icon_map = {"success":"check","warning":"alert","danger":"x","info":"info"}
    color_map = {
        "success": ("#2ECC8A","rgba(46,204,138,.08)","rgba(46,204,138,.2)"),
        "warning": ("#F5A623","rgba(245,166,35,.08)","rgba(245,166,35,.2)"),
        "danger":  ("#F0503A","rgba(240,80,58,.08)", "rgba(240,80,58,.2)"),
        "info":    ("#4A9EF5","rgba(74,158,245,.08)","rgba(74,158,245,.2)"),
    }
    color, bg, border = color_map.get(variant, color_map["info"])
    icon = svg_icon(icon_map.get(variant,"info"), 18, color)
    return (
        f'<div style="display:flex;align-items:flex-start;gap:12px;padding:14px 18px;'
        f'border-radius:10px;border:1px solid {border};background:{bg};'
        f'font-size:13px;color:{color};margin-bottom:12px;">'
        f'<span style="flex-shrink:0;margin-top:1px;">{icon}</span>'
        f'<span style="line-height:1.6;">{message}</span></div>'
    )