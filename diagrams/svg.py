import math
from xml.sax.saxutils import escape

FONT = "Inter, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Cascadia Mono', Consolas, Menlo, monospace"

INK = '#1F2937'
MUTED = '#6B7280'
LINE = '#4B5563'
BORDER = '#E5E7EB'

KINDS = {
    'server': ('#E8F0FE', '#2F6FEB', '#1E3A8A'),
    'client': ('#E6F6EF', '#0E9F6E', '#065F46'),
    'host': ('#F1EAFE', '#7C3AED', '#4C1D95'),
    'neutral': ('#F3F4F6', '#9CA3AF', INK),
    'accent': ('#FEF3C7', '#D97706', '#78350F'),
    'danger': ('#FEE2E2', '#DC2626', '#7F1D1D'),
    'code': ('#F8FAFC', '#64748B', '#0F172A'),
    'plain': ('#FFFFFF', '#D1D5DB', INK),
}

STROKES = {
    'server': '#2F6FEB',
    'client': '#0E9F6E',
    'host': '#7C3AED',
    'accent': '#D97706',
    'danger': '#DC2626',
    'neutral': LINE,
    'muted': '#9CA3AF',
}


def text_width(text, size=13, mono=False):
    if mono:
        return len(text) * size * 0.6
    width = 0.0
    for char in text:
        if char in 'il.,:;|!\'`':
            width += 0.28
        elif char in 'fjrt()[]{} ':
            width += 0.36
        elif char.isupper() or char in 'mw':
            width += 0.68
        else:
            width += 0.55
    return width * size


class Canvas:
    def __init__(self, width, height, title, background=True):
        self.width = width
        self.height = height
        self.title = title
        self.parts = []
        self.background = background
        self.markers = set()

    def add(self, fragment):
        self.parts.append(fragment)

    def text(self, x, y, value, size=13, weight=400, anchor='start', color=INK, mono=False, italic=False):
        family = MONO if mono else FONT
        style = ' font-style="italic"' if italic else ''
        self.add(
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}" text-anchor="{anchor}"{style}>{escape(value)}</text>'
        )

    def lines(self, x, y, values, size=13, weight=400, anchor='start', color=INK, mono=False, gap=None):
        step = gap or size * 1.4
        for index, value in enumerate(values):
            self.text(x, y + index * step, value, size, weight, anchor, color, mono)

    def rect(self, x, y, w, h, fill, stroke, radius=8, dashed=False, stroke_width=1.5):
        dash = ' stroke-dasharray="6 4"' if dashed else ''
        self.add(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{radius}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"{dash}/>'
        )

    def box(self, x, y, w, h, kind, title=None, body=(), mono_body=False, radius=10, dashed=False,
            title_size=14, body_size=12, align='center', title_mono=False):
        fill, stroke, ink = KINDS[kind]
        self.rect(x, y, w, h, fill, stroke, radius, dashed)
        rows = ([title] if title else []) + list(body)
        line_h = body_size * 1.45
        block = (title_size * 1.3 if title else 0) + len(body) * line_h
        top = y + (h - block) / 2
        if align == 'center':
            tx, anchor = x + w / 2, 'middle'
        else:
            tx, anchor = x + 14, 'start'
        cursor = top
        if title:
            cursor += title_size
            self.text(tx, cursor, title, title_size, 600, anchor, ink, title_mono)
            cursor += title_size * 0.3
        for row in body:
            cursor += line_h
            self.text(tx, cursor - body_size * 0.35, row, body_size, 400, anchor, ink if mono_body else MUTED, mono_body)
        return rows

    def pill(self, x, y, label, kind='neutral', size=11, mono=False, anchor='middle'):
        fill, stroke, ink = KINDS[kind]
        w = text_width(label, size, mono) + 16
        h = size + 10
        left = x - w / 2 if anchor == 'middle' else x
        self.rect(left, y - h / 2, w, h, fill, stroke, h / 2, stroke_width=1)
        self.text(left + w / 2, y + size * 0.36, label, size, 600, 'middle', ink, mono)
        return w

    def marker(self, color):
        key = color.lstrip('#')
        if key not in self.markers:
            self.markers.add(key)
        return f'url(#arrow-{key})'

    def arrow(self, points, color=LINE, dashed=False, width=1.6, start=False, end=True, label=None,
              label_at=0.5, label_offset=(0, -7), label_size=11.5, label_color=None, label_anchor='middle',
              label_mono=False, label_bg=True):
        path = 'M ' + ' L '.join(f'{px:.1f} {py:.1f}' for px, py in points)
        dash = ' stroke-dasharray="6 4"' if dashed else ''
        head = f' marker-end="{self.marker(color)}"' if end else ''
        tail = f' marker-start="{self.marker(color)}"' if start else ''
        self.add(
            f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{width}" '
            f'stroke-linejoin="round" stroke-linecap="round"{dash}{head}{tail}/>'
        )
        if label:
            lx, ly = point_along(points, label_at)
            lx += label_offset[0]
            ly += label_offset[1]
            if label_bg:
                w = text_width(label, label_size, label_mono) + 8
                left = lx - w / 2 if label_anchor == 'middle' else (lx - 4 if label_anchor == 'start' else lx - w + 4)
                self.add(
                    f'<rect x="{left:.1f}" y="{ly - label_size:.1f}" width="{w:.1f}" height="{label_size + 5:.1f}" '
                    f'rx="3" fill="#FFFFFF" fill-opacity="0.92"/>'
                )
            self.text(lx, ly, label, label_size, 500, label_anchor, label_color or color, label_mono)

    def line(self, x1, y1, x2, y2, color=BORDER, width=1, dashed=False):
        dash = ' stroke-dasharray="4 4"' if dashed else ''
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}"{dash}/>')

    def circle(self, cx, cy, r, fill, stroke=None, width=1.5):
        outline = f' stroke="{stroke}" stroke-width="{width}"' if stroke else ''
        self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"{outline}/>')

    def svg(self):
        defs = ''.join(
            f'<marker id="arrow-{key}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#{key}"/></marker>'
            for key in sorted(self.markers)
        )
        background = (
            f'<rect x="0.5" y="0.5" width="{self.width - 1}" height="{self.height - 1}" rx="12" fill="#FFFFFF" stroke="{BORDER}"/>'
            if self.background else ''
        )
        body = '\n  '.join(self.parts)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" '
            f'viewBox="0 0 {self.width} {self.height}" role="img" aria-label="{escape(self.title)}">\n'
            f'  <title>{escape(self.title)}</title>\n'
            f'  <defs>{defs}</defs>\n'
            f'  {background}\n'
            f'  {body}\n'
            f'</svg>\n'
        )


def point_along(points, fraction):
    lengths = [math.dist(a, b) for a, b in zip(points, points[1:])]
    total = sum(lengths)
    target = total * fraction
    for (a, b), length in zip(zip(points, points[1:]), lengths):
        if target <= length and length > 0:
            t = target / length
            return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        target -= length
    return points[-1]
