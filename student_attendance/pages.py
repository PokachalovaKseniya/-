"""
Страницы веб-приложения для учёта посещаемости студентов.

Каждая функция (*_page) описывает экран: группы, студенты, дисциплины,
занятия, посещаемость, статистика. Скриншоты страниц и фрагментов кода
из этого файла можно вставлять в отчёт.
"""

import reflex as rx

from student_attendance.components import page_shell, section_card
from student_attendance.state import AppState
from student_attendance.styles import COLORS, button_outline, button_primary

# Варианты статуса посещаемости для выпадающего списка на странице «Посещаемость»
STATUS_OPTIONS = [
    {"value": "present", "label": "Присутствовал"},
    {"value": "absent", "label": "Отсутствовал"},
    {"value": "excused", "label": "Уважительная причина"},
    {"value": "late", "label": "Опоздал"},
]


def _group_options():
    return rx.foreach(
        AppState.groups,
        lambda g: rx.select.item(g["name"], value=g["id"]),
    )


def _discipline_options():
    return rx.foreach(
        AppState.disciplines,
        lambda d: rx.select.item(d["name"], value=d["id"]),
    )


def _lesson_options():
    return rx.foreach(
        AppState.lessons,
        lambda les: rx.select.item(les["label"], value=les["id"]),
    )


# ---------------------------------------------------------------------------
# Главная
# ---------------------------------------------------------------------------
def index() -> rx.Component:
    return page_shell(
        "Учёт посещаемости студентов",
        rx.grid(
            _home_card("Группы", "Создание групп и просмотр списка студентов", "/groups", "users"),
            _home_card("Студенты", "Добавление, поиск и импорт из Excel", "/students", "graduation-cap"),
            _home_card("Дисциплины", "Предметы и преподаватели", "/disciplines", "book-open"),
            _home_card("Занятия", "Назначение даты, группы и дисциплины", "/lessons", "calendar"),
            _home_card("Посещаемость", "Отметки: присутствовал / отсутствовал / опоздал", "/attendance", "clipboard-check"),
            _home_card("Статистика", "Процент посещаемости и диаграмма по группе", "/stats", "bar-chart-3"),
            columns=rx.breakpoints(initial="1", sm="2", md="3"),
            spacing="4",
            width="100%",
        ),
        rx.box(
            rx.text(
                "Импорт списка группы: на странице «Студенты» загрузите Excel (.xlsx) "
                "с колонками ФИО, Номер зачётной книжки, Курс.",
                color=COLORS["muted"],
            ),
            margin_top="1.5rem",
            padding="1rem",
            background="#E8F0FE",
            border_radius="8px",
            border=f"1px solid {COLORS['border']}",
        ),
        on_mount=AppState.load_all,
    )


def _home_card(title: str, desc: str, href: str, icon: str) -> rx.Component:
    return rx.link(
        rx.box(
            rx.hstack(
                rx.icon(icon, color=COLORS["primary"], size=28),
                rx.heading(title, size="4", color=COLORS["primary"]),
                spacing="3",
                align="center",
            ),
            rx.text(desc, color=COLORS["muted"], margin_top="0.75rem", font_size="0.95rem"),
            background=COLORS["white"],
            border=f"1px solid {COLORS['border']}",
            border_radius="12px",
            padding="1.25rem",
            height="100%",
            _hover={"border_color": COLORS["accent"], "box_shadow": "0 4px 12px rgba(11,61,145,0.12)"},
            transition="all 0.2s ease",
        ),
        href=href,
        text_decoration="none",
        height="100%",
    )


# ---------------------------------------------------------------------------
# Группы
# ---------------------------------------------------------------------------
def groups_page() -> rx.Component:
    return page_shell(
        "Группы",
        rx.vstack(
            section_card(
                "Создать группу",
                rx.text(
                    "Можно ввести любое обозначение группы вашего вуза — без шаблонов и форматов.",
                    color=COLORS["muted"],
                    margin_bottom="0.75rem",
                    font_size="0.9rem",
                ),
                rx.hstack(
                    rx.input(
                        placeholder="Любое название: ПИ-21, ИС-22, 101б, БИВТ-23-1…",
                        value=AppState.group_name,
                        on_change=AppState.set_group_name,
                        width="100%",
                    ),
                    rx.button("Создать", on_click=AppState.add_group, style=button_primary),
                    width="100%",
                    spacing="3",
                ),
            ),
            rx.grid(
                section_card(
                    "Список групп",
                    rx.foreach(
                        AppState.groups,
                        lambda g: rx.hstack(
                            rx.button(
                                g["name"],
                                variant="soft",
                                on_click=lambda: AppState.select_group(g["id"]),
                                flex="1",
                                justify_content="flex-start",
                            ),
                            rx.icon_button(
                                rx.icon("trash-2", size=16),
                                color_scheme="red",
                                variant="soft",
                                on_click=lambda: AppState.delete_group(g["id"]),
                            ),
                            width="100%",
                            spacing="2",
                            margin_bottom="0.5rem",
                        ),
                    ),
                ),
                section_card(
                    "Студенты выбранной группы",
                    rx.cond(
                        AppState.selected_group_id != "",
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("ФИО"),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(
                                    AppState.group_students,
                                    lambda s: rx.table.row(
                                        rx.table.cell(s["full_name"]),
                                    ),
                                )
                            ),
                            width="100%",
                        ),
                        rx.text("Выберите группу слева", color=COLORS["muted"]),
                    ),
                ),
                columns=rx.breakpoints(initial="1", md="2"),
                spacing="4",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        on_mount=AppState.load_groups,
    )


# ---------------------------------------------------------------------------
# Студенты
# ---------------------------------------------------------------------------
def students_page() -> rx.Component:
    return page_shell(
        "Студенты",
        rx.vstack(
            section_card(
                "Импорт списка группы из Excel",
                rx.text(
                    "Выберите группу, загрузите файл .xlsx с колонками: "
                    "ФИО | Номер зачётной книжки | Курс",
                    color=COLORS["muted"],
                    margin_bottom="0.75rem",
                ),
                rx.hstack(
                    rx.select.root(
                        rx.select.trigger(placeholder="Группа для импорта", width="220px"),
                        rx.select.content(_group_options()),
                        value=AppState.import_group_id,
                        on_change=AppState.set_import_group_id,
                    ),
                    rx.upload(
                        rx.vstack(
                            rx.icon("file-spreadsheet", color=COLORS["primary"]),
                            rx.text("Перетащите .xlsx или нажмите", font_size="0.85rem"),
                            rx.text(rx.selected_files("student_excel"), font_size="0.8rem", color=COLORS["muted"]),
                            align="center",
                            spacing="1",
                        ),
                        id="student_excel",
                        accept={
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
                        },
                        max_files=1,
                        border=f"2px dashed {COLORS['accent']}",
                        padding="1rem",
                        border_radius="8px",
                        background="#F8FBFF",
                    ),
                    rx.button(
                        "Импортировать",
                        on_click=AppState.import_students_excel(
                            rx.upload_files(upload_id="student_excel")
                        ),
                        style=button_primary,
                    ),
                    spacing="3",
                    align="center",
                    flex_wrap="wrap",
                    width="100%",
                ),
                rx.cond(
                    AppState.import_status != "",
                    rx.text(AppState.import_status, color=COLORS["primary"], margin_top="0.75rem"),
                ),
            ),
            section_card(
                rx.cond(AppState.editing_student_id != "", "Редактировать студента", "Добавить студента"),
                rx.hstack(
                    rx.input(
                        placeholder="ФИО",
                        value=AppState.student_full_name,
                        on_change=AppState.set_student_full_name,
                        width="100%",
                    ),
                    rx.select.root(
                        rx.select.trigger(placeholder="Группа", width="220px"),
                        rx.select.content(_group_options()),
                        value=AppState.student_group_id,
                        on_change=AppState.set_student_group_id,
                    ),
                    spacing="3",
                    width="100%",
                    margin_bottom="0.75rem",
                    align="center",
                ),
                rx.hstack(
                    rx.button("Сохранить", on_click=AppState.save_student, style=button_primary),
                    rx.button("Очистить", on_click=AppState.clear_student_form, style=button_outline),
                    spacing="3",
                ),
            ),
            section_card(
                "Список студентов",
                rx.input(
                    placeholder="Поиск по ФИО или группе...",
                    value=AppState.student_search,
                    on_change=AppState.set_student_search,
                    margin_bottom="1rem",
                    width="100%",
                ),
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("ФИО"),
                            rx.table.column_header_cell("Группа"),
                            rx.table.column_header_cell("Действия"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            AppState.students,
                            lambda s: rx.table.row(
                                rx.table.cell(s["full_name"]),
                                rx.table.cell(s["group_name"]),
                                rx.table.cell(
                                    rx.hstack(
                                        rx.icon_button(
                                            rx.icon("pencil", size=16),
                                            variant="soft",
                                            on_click=lambda: AppState.start_edit_student(s["id"]),
                                        ),
                                        rx.icon_button(
                                            rx.icon("trash-2", size=16),
                                            color_scheme="red",
                                            variant="soft",
                                            on_click=lambda: AppState.delete_student(s["id"]),
                                        ),
                                        spacing="2",
                                    )
                                ),
                            ),
                        )
                    ),
                    width="100%",
                ),
            ),
            spacing="4",
            width="100%",
        ),
        on_mount=AppState.load_all,
    )


# ---------------------------------------------------------------------------
# Дисциплины
# ---------------------------------------------------------------------------
def disciplines_page() -> rx.Component:
    return page_shell(
        "Дисциплины",
        rx.vstack(
            section_card(
                rx.cond(
                    AppState.editing_discipline_id != "",
                    "Редактировать дисциплину",
                    "Добавить дисциплину",
                ),
                rx.hstack(
                    rx.input(
                        placeholder="Название предмета",
                        value=AppState.discipline_name,
                        on_change=AppState.set_discipline_name,
                        width="100%",
                    ),
                    rx.input(
                        placeholder="Преподаватель",
                        value=AppState.discipline_teacher,
                        on_change=AppState.set_discipline_teacher,
                        width="100%",
                    ),
                    rx.button("Сохранить", on_click=AppState.save_discipline, style=button_primary),
                    rx.button("Очистить", on_click=AppState.clear_discipline_form, style=button_outline),
                    width="100%",
                    spacing="3",
                    flex_wrap="wrap",
                ),
            ),
            section_card(
                "Список дисциплин",
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Предмет"),
                            rx.table.column_header_cell("Преподаватель"),
                            rx.table.column_header_cell("Действия"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            AppState.disciplines,
                            lambda d: rx.table.row(
                                rx.table.cell(d["name"]),
                                rx.table.cell(d["teacher"]),
                                rx.table.cell(
                                    rx.hstack(
                                        rx.icon_button(
                                            rx.icon("pencil", size=16),
                                            variant="soft",
                                            on_click=lambda: AppState.start_edit_discipline(d["id"]),
                                        ),
                                        rx.icon_button(
                                            rx.icon("trash-2", size=16),
                                            color_scheme="red",
                                            variant="soft",
                                            on_click=lambda: AppState.delete_discipline(d["id"]),
                                        ),
                                        spacing="2",
                                    )
                                ),
                            ),
                        )
                    ),
                    width="100%",
                ),
            ),
            spacing="4",
            width="100%",
        ),
        on_mount=AppState.load_disciplines,
    )


# ---------------------------------------------------------------------------
# Занятия
# ---------------------------------------------------------------------------
def lessons_page() -> rx.Component:
    return page_shell(
        "Занятия",
        rx.vstack(
            section_card(
                "Создать занятие",
                rx.text(
                    "Укажите дату, группу и дисциплину. Для студентов группы автоматически "
                    "создадутся отметки посещаемости.",
                    color=COLORS["muted"],
                    margin_bottom="0.75rem",
                ),
                rx.hstack(
                    rx.input(
                        type="date",
                        value=AppState.lesson_date,
                        on_change=AppState.set_lesson_date,
                    ),
                    rx.select.root(
                        rx.select.trigger(placeholder="Группа", width="180px"),
                        rx.select.content(_group_options()),
                        value=AppState.lesson_group_id,
                        on_change=AppState.set_lesson_group_id,
                    ),
                    rx.select.root(
                        rx.select.trigger(placeholder="Дисциплина", width="220px"),
                        rx.select.content(_discipline_options()),
                        value=AppState.lesson_discipline_id,
                        on_change=AppState.set_lesson_discipline_id,
                    ),
                    rx.button("Создать", on_click=AppState.add_lesson, style=button_primary),
                    spacing="3",
                    flex_wrap="wrap",
                    width="100%",
                ),
            ),
            section_card(
                "Список занятий",
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Дата"),
                            rx.table.column_header_cell("Группа"),
                            rx.table.column_header_cell("Дисциплина"),
                            rx.table.column_header_cell(""),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            AppState.lessons,
                            lambda les: rx.table.row(
                                rx.table.cell(les["lesson_date"]),
                                rx.table.cell(les["group_name"]),
                                rx.table.cell(les["discipline_name"]),
                                rx.table.cell(
                                    rx.icon_button(
                                        rx.icon("trash-2", size=16),
                                        color_scheme="red",
                                        variant="soft",
                                        on_click=lambda: AppState.delete_lesson(les["id"]),
                                    )
                                ),
                            ),
                        )
                    ),
                    width="100%",
                ),
            ),
            spacing="4",
            width="100%",
        ),
        on_mount=AppState.load_all,
    )


# ---------------------------------------------------------------------------
# Посещаемость
# ---------------------------------------------------------------------------
def attendance_page() -> rx.Component:
    return page_shell(
        "Посещаемость",
        rx.vstack(
            section_card(
                "Выбор занятия",
                rx.select.root(
                    rx.select.trigger(placeholder="Дата · Группа · Дисциплина", width="100%"),
                    rx.select.content(_lesson_options()),
                    value=AppState.attendance_lesson_id,
                    on_change=AppState.select_attendance_lesson,
                    width="100%",
                ),
            ),
            section_card(
                "Отметки студентов",
                rx.cond(
                    AppState.attendance_lesson_id != "",
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("ФИО"),
                                rx.table.column_header_cell("Статус"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                AppState.attendance_rows,
                                lambda row: rx.table.row(
                                    rx.table.cell(row["full_name"]),
                                    rx.table.cell(
                                        rx.select.root(
                                            rx.select.trigger(width="240px"),
                                            rx.select.content(
                                                rx.foreach(
                                                    STATUS_OPTIONS,
                                                    lambda item: rx.select.item(
                                                        item["label"], value=item["value"]
                                                    ),
                                                )
                                            ),
                                            value=row["status"],
                                            on_change=lambda status: AppState.set_attendance_status(
                                                row["attendance_id"], status
                                            ),
                                        )
                                    ),
                                ),
                            )
                        ),
                        width="100%",
                    ),
                    rx.text("Выберите занятие", color=COLORS["muted"]),
                ),
            ),
            spacing="4",
            width="100%",
        ),
        on_mount=AppState.load_lessons,
    )


# ---------------------------------------------------------------------------
# Статистика
# ---------------------------------------------------------------------------
def stats_page() -> rx.Component:
    return page_shell(
        "Статистика посещаемости",
        rx.vstack(
            section_card(
                "Выбор группы",
                rx.hstack(
                    rx.select.root(
                        rx.select.trigger(placeholder="Группа", width="220px"),
                        rx.select.content(_group_options()),
                        value=AppState.stats_group_id,
                        on_change=AppState.set_stats_group_id,
                    ),
                    rx.button("Рассчитать", on_click=AppState.load_stats, style=button_primary),
                    spacing="3",
                ),
                rx.cond(
                    AppState.stats_group_id != "",
                    rx.box(
                        rx.text(
                            "Средняя посещаемость группы: ",
                            AppState.group_avg_percent,
                            "%",
                            font_weight="700",
                            color=COLORS["primary"],
                            font_size="1.15rem",
                            margin_top="1rem",
                        ),
                    ),
                ),
            ),
            section_card(
                "Диаграмма посещаемости студентов (%)",
                rx.cond(
                    AppState.chart_data.length() > 0,
                    rx.recharts.bar_chart(
                        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                        rx.recharts.graphing_tooltip(),
                        rx.recharts.bar(
                            data_key="percent",
                            fill=COLORS["primary"],
                            radius=[4, 4, 0, 0],
                        ),
                        rx.recharts.x_axis(data_key="name"),
                        rx.recharts.y_axis(domain=[0, 100]),
                        data=AppState.chart_data,
                        width="100%",
                        height=320,
                    ),
                    rx.text("Нет данных для диаграммы", color=COLORS["muted"]),
                ),
            ),
            section_card(
                "По каждому студенту",
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("ФИО"),
                            rx.table.column_header_cell("Посещения"),
                            rx.table.column_header_cell("Пропуски"),
                            rx.table.column_header_cell("Уваж."),
                            rx.table.column_header_cell("Опоздания"),
                            rx.table.column_header_cell("Всего"),
                            rx.table.column_header_cell("%"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            AppState.student_stats,
                            lambda s: rx.table.row(
                                rx.table.cell(s["full_name"]),
                                rx.table.cell(s["present"]),
                                rx.table.cell(s["absent"]),
                                rx.table.cell(s["excused"]),
                                rx.table.cell(s["late"]),
                                rx.table.cell(s["total"]),
                                rx.table.cell(s["percent"]),
                            ),
                        )
                    ),
                    width="100%",
                ),
            ),
            spacing="4",
            width="100%",
        ),
        on_mount=AppState.load_groups,
    )
