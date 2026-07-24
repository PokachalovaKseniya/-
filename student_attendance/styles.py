"""Сине-белая университетская тема оформления."""

COLORS = {
    "primary": "#0B3D91",
    "primary_dark": "#072A66",
    "primary_light": "#1E5BB8",
    "accent": "#4A90D9",
    "bg": "#F4F7FB",
    "white": "#FFFFFF",
    "text": "#1A2B4A",
    "muted": "#5A6F8C",
    "border": "#D0DCE8",
    "success": "#1B7A4E",
    "warning": "#C47F00",
    "danger": "#B42318",
    "late": "#8B5CF6",
}

STATUS_COLORS = {
    "present": COLORS["success"],
    "absent": COLORS["danger"],
    "excused": COLORS["warning"],
    "late": COLORS["late"],
}

card_style = {
    "background": COLORS["white"],
    "border": f"1px solid {COLORS['border']}",
    "border_radius": "12px",
    "padding": "1.25rem",
    "box_shadow": "0 1px 3px rgba(11, 61, 145, 0.08)",
    "width": "100%",
}

input_style = {
    "width": "100%",
    "border_color": COLORS["border"],
}

button_primary = {
    "background": COLORS["primary"],
    "color": "white",
    "_hover": {"background": COLORS["primary_light"]},
}

button_outline = {
    "background": "transparent",
    "color": COLORS["primary"],
    "border": f"1px solid {COLORS['primary']}",
    "_hover": {"background": "#E8F0FE"},
}
