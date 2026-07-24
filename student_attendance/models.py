import reflex as rx
from sqlmodel import Field


# Справочник статусов посещаемости (ключ в БД -> подпись в интерфейсе)
ATTENDANCE_STATUSES = {
    "present": "Присутствовал",
    "absent": "Отсутствовал",
    "excused": "Уважительная причина",
    "late": "Опоздал",
}


class StudyGroup(rx.Model, table=True):
    name: str = Field(unique=True, index=True)


class Student(rx.Model, table=True):
    full_name: str  # ФИО студента
    student_card: str = Field(index=True)  # служебный идентификатор / зачётка
    course: int = 1  # курс (по умолчанию 1)
    # Связь с таблицей групп (внешний ключ)
    group_id: int = Field(foreign_key="studygroup.id", index=True)


class Discipline(rx.Model, table=True):
    name: str  # название дисциплины
    teacher: str = ""  # ФИО преподавателя


class Lesson(rx.Model, table=True):
    lesson_date: str  # дата в формате ГГГГ-ММ-ДД
    group_id: int = Field(foreign_key="studygroup.id", index=True)
    discipline_id: int = Field(foreign_key="discipline.id", index=True)


class Attendance(rx.Model, table=True):
    """
    Отметка посещаемости конкретного студента на конкретном занятии.
    status: present | absent | excused | late
    """

    lesson_id: int = Field(foreign_key="lesson.id", index=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    status: str = "present"  # статус посещаемости
