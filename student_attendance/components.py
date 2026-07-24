"""Общий каркас страниц: шапка и навигация."""

import reflex as rx

from student_attendance.state import AppState
from student_attendance.styles import COLORS


def nav_link(text: str, href: str) -> rx.Component:
    return rx.link(
        text,
        href=href,
        color="white",
        font_weight="500",
        font_size="0.95rem",
        padding_x="0.75rem",
        padding_y="0.4rem",
        border_radius="6px",
        _hover={"background": "rgba(255,255,255,0.15)", "text_decoration": "none"},
        text_decoration="none",
    )


def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.text(
                "Учёт посещаемости",
                color="white",
                font_weight="700",
                font_size="1.15rem",
            ),
            rx.hstack(
                nav_link("Главная", "/"),
                nav_link("Группы", "/groups"),
                nav_link("Студенты", "/students"),
                nav_link("Дисциплины", "/disciplines"),
                nav_link("Занятия", "/lessons"),
                nav_link("Посещаемость", "/attendance"),
                nav_link("Статистика", "/stats"),
                spacing="1",
                wrap="wrap",
                justify="end",
            ),
            justify="between",
            align="center",
            width="100%",
            flex_wrap="wrap",
            gap="1rem",
        ),
        background=COLORS["primary"],
        padding_x="1.5rem",
        padding_y="1rem",
        width="100%",
        border_bottom=f"4px solid {COLORS['accent']}",
    )


def message_banner() -> rx.Component:
    return rx.cond(
        AppState.message != "",
        rx.box(
            rx.hstack(
                rx.text(AppState.message, flex="1"),
                rx.icon_button(
                    rx.icon("x", size=16),
                    on_click=AppState.clear_message,
                    variant="ghost",
                    size="1",
                ),
                width="100%",
                align="center",
            ),
            background=rx.cond(
                AppState.message_type == "error",
                "#FDECEC",
                rx.cond(AppState.message_type == "success", "#E8F5EE", "#E8F0FE"),
            ),
            color=COLORS["text"],
            border=f"1px solid {COLORS['border']}",
            border_radius="8px",
            padding="0.75rem 1rem",
            margin_bottom="1rem",
            width="100%",
        ),
    )


def page_shell(title, *children, on_mount=None) -> rx.Component:
    return rx.box(
        navbar(),
        rx.box(
            rx.heading(title, size="7", color=COLORS["primary"], margin_bottom="1rem"),
            message_banner(),
            *children,
            max_width="1200px",
            margin="0 auto",
            padding="1.5rem",
            width="100%",
        ),
        background=COLORS["bg"],
        min_height="100vh",
        font_family="'Segoe UI', 'Trebuchet MS', sans-serif",
        on_mount=on_mount,
    )


def section_card(title, *children) -> rx.Component:
    return rx.box(
        rx.heading(title, size="4", color=COLORS["primary"], margin_bottom="0.85rem"),
        *children,
        background=COLORS["white"],
        border=f"1px solid {COLORS['border']}",
        border_radius="12px",
        padding="1.25rem",
        box_shadow="0 1px 3px rgba(11, 61, 145, 0.08)",
        width="100%",
    )
