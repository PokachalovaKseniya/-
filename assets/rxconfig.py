import reflex as rx

config = rx.Config(
    app_name="student_attendance",
    # Локальная база данных SQLite (файл student_attendance.db в корне проекта)
    db_url="sqlite:///student_attendance.db",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(
                appearance="light",
                accent_color="blue",  # сине-белая университетская тема
                radius="medium",
            )
        ),
    ],
)
