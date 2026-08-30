from django import template
from django.utils.safestring import mark_safe

register = template.Library()

_STROKE = 'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"'

_ICONS = {
    'users': '<circle cx="8" cy="7" r="3"/><path d="M2.5 17c0-3 2.5-5 5.5-5s5.5 2 5.5 5"/><path d="M14 5.2a3 3 0 0 1 0 5.8"/><path d="M17.5 17c0-2.5-1.6-4.3-3.8-4.9"/>',
    'box': '<path d="M3 6.5 10 3l7 3.5-7 3.5-7-3.5Z"/><path d="M3 6.5V14l7 3.5 7-3.5V6.5"/><path d="M10 10v7.5"/>',
    'file-text': '<path d="M5 2.5h7l3 3v12H5v-15Z"/><path d="M12 2.5v3h3"/><path d="M7.3 10h5.4M7.3 12.6h5.4M7.3 14.9h3.6"/>',
    'upload': '<path d="M10 13V4"/><path d="M6.3 7.5 10 3.8l3.7 3.7"/><path d="M3.5 13v2.7a1.3 1.3 0 0 0 1.3 1.3h10.4a1.3 1.3 0 0 0 1.3-1.3V13"/>',
    'settings': '<circle cx="10" cy="10" r="2.6"/><path d="M10 2.7v2M10 15.3v2M17.3 10h-2M4.7 10h-2M15.2 4.8l-1.4 1.4M6.2 13.8l-1.4 1.4M15.2 15.2l-1.4-1.4M6.2 6.2 4.8 4.8"/>',
    'search': '<circle cx="8.5" cy="8.5" r="5.5"/><path d="M16.5 16.5 13 13"/>',
    'mail': '<rect x="2.5" y="4.5" width="15" height="11" rx="1.5"/><path d="M3.2 5.5 10 11l6.8-5.5"/>',
    'chat': '<path d="M3 9.8c0-3.7 3.1-6.6 7-6.6s7 3 7 6.6-3.1 6.6-7 6.6c-1 0-2-.2-2.9-.6L3.5 17l1-3.4A6.3 6.3 0 0 1 3 9.8Z"/>',
    'check': '<path d="M4 10.5 8 14.5 16 5.5"/>',
    'check-circle': '<circle cx="10" cy="10" r="7.3"/><path d="M6.5 10.2 8.8 12.6 13.6 7.3"/>',
    'globe': '<circle cx="10" cy="10" r="7.3"/><path d="M2.7 10h14.6"/><path d="M10 2.7c2 2.1 3.1 4.6 3.1 7.3s-1.1 5.2-3.1 7.3c-2-2.1-3.1-4.6-3.1-7.3s1.1-5.2 3.1-7.3Z"/>',
    'inbox': '<path d="M3 11.5 5.3 3.8h9.4L17 11.5"/><path d="M3 11.5v4.2a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-4.2h-4.2a2.8 2.8 0 0 1-5.6 0H3Z"/>',
    'chevron-left': '<path d="M12.5 4.5 7 10l5.5 5.5"/>',
    'chevron-right': '<path d="M7.5 4.5 13 10l-5.5 5.5"/>',
    'logout': '<path d="M8 17.3H4.7a1.2 1.2 0 0 1-1.2-1.2V3.9a1.2 1.2 0 0 1 1.2-1.2H8"/><path d="M13 13.7 17 10l-4-3.7"/><path d="M17 10H8"/>',
    'x': '<path d="M5 5l10 10M15 5 5 15"/>',
    'menu': '<path d="M3 5.5h14M3 10h14M3 14.5h14"/>',
    'sparkle': (
        '<path d="M10 2.2c.5 2.9 1.1 4.6 2.1 5.7 1.1 1 2.8 1.6 5.7 2.1-2.9.5-4.6 1.1-5.7 2.1'
        '-1 1.1-1.6 2.8-2.1 5.7-.5-2.9-1.1-4.6-2.1-5.7-1.1-1-2.8-1.6-5.7-2.1 2.9-.5 4.6-1.1 '
        '5.7-2.1 1-1.1 1.6-2.8 2.1-5.7Z" fill="currentColor" stroke="none"/>'
    ),
    'lock': '<rect x="4.5" y="9" width="11" height="8" rx="1.5"/><path d="M6.5 9V6.3a3.5 3.5 0 0 1 7 0V9"/>',
    'alert': (
        '<path d="M10 3 2.5 16h15L10 3Z"/><path d="M10 8.3v3.4"/>'
        '<circle cx="10" cy="14.1" r="1" fill="currentColor" stroke="none"/>'
    ),
    'linkedin': (
        '<rect x="2.5" y="2.5" width="15" height="15" rx="3.5"/>'
        '<circle cx="7.2" cy="7.2" r="1" fill="currentColor" stroke="none"/>'
        '<path d="M7.2 9.8v4.2"/>'
        '<path d="M10.5 14v-2.6a1.9 1.9 0 0 1 3.8 0V14"/>'
        '<path d="M10.5 9.8v4.2"/>'
    ),
    'facebook': (
        '<rect x="2.5" y="2.5" width="15" height="15" rx="3.5"/>'
        '<path d="M11.8 15v-4.6h1.6M9.6 10.4h4M11.8 10.4V8.3a1.4 1.4 0 0 1 1.4-1.4h1"/>'
    ),
    'instagram': (
        '<rect x="2.5" y="2.5" width="15" height="15" rx="4.5"/>'
        '<circle cx="10" cy="10" r="3.4"/>'
        '<circle cx="14.2" cy="5.8" r="0.6" fill="currentColor" stroke="none"/>'
    ),
    'link': (
        '<path d="M8.3 11.7a2.9 2.9 0 0 0 4.2.2l2-2a2.9 2.9 0 1 0-4.1-4.1l-1.1 1.1"/>'
        '<path d="M11.7 8.3a2.9 2.9 0 0 0-4.2-.2l-2 2a2.9 2.9 0 1 0 4.1 4.1l1.1-1.1"/>'
    ),
}


@register.simple_tag
def icon(name, size=18, css_class=''):
    body = _ICONS.get(name, '')
    cls = f' class="{css_class}"' if css_class else ''
    svg = (
        f'<svg{cls} width="{size}" height="{size}" viewBox="0 0 20 20" '
        f'{_STROKE} aria-hidden="true" focusable="false">{body}</svg>'
    )
    return mark_safe(svg)
