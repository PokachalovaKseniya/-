import reflex as rx

# Импорт models обязателен, чтобы таблицы БД зарегистрировались в Reflex
from student_attendance import models  
from student_attendance.pages import (
    attendance_page,
    disciplines_page,
    groups_page,
    index,
    lessons_page,
    stats_page,
    students_page,
)
from student_attendance.styles import COLORS

# Создание приложения Reflex (веб-интерфейс на Python)
app = rx.App(
    style={
        "font_family": "'Segoe UI', 'Trebuchet MS', sans-serif",
        "background": COLORS["bg"],
        "color": COLORS["text"],
    },
)

# Регистрация страниц приложения
app.add_page(index, route="/", title="Учёт посещаемости")
app.add_page(groups_page, route="/groups", title="Группы")
app.add_page(students_page, route="/students", title="Студенты")
app.add_page(disciplines_page, route="/disciplines", title="Дисциплины")
app.add_page(lessons_page, route="/lessons", title="Занятия")
app.add_page(attendance_page, route="/attendance", title="Посещаемость")
app.add_page(stats_page, route="/stats", title="Статистика")
