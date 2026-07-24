from __future__ import annotations

from collections import defaultdict
from datetime import date

import reflex as rx
from sqlmodel import select

from student_attendance.excel_import import parse_students_xlsx
from student_attendance.models import (
    ATTENDANCE_STATUSES,
    Attendance,
    Discipline,
    Lesson,
    Student,
    StudyGroup,
)


class AppState(rx.State):
    """Состояние веб-приложения учёта посещаемости (Reflex State)."""

    # --- сообщения ---
    message: str = ""
    message_type: str = "info"  # info | success | error

    # --- группы ---
    groups: list[dict] = []
    group_name: str = ""
    selected_group_id: str = ""
    group_students: list[dict] = []

    # --- студенты ---
    students: list[dict] = []
    student_search: str = ""
    student_full_name: str = ""
    student_card: str = ""
    student_course: str = "1"
    student_group_id: str = ""
    editing_student_id: str = ""
    import_group_id: str = ""
    import_status: str = ""

    # --- дисциплины ---
    disciplines: list[dict] = []
    discipline_name: str = ""
    discipline_teacher: str = ""
    editing_discipline_id: str = ""

    # --- занятия ---
    lessons: list[dict] = []
    lesson_date: str = date.today().isoformat()
    lesson_group_id: str = ""
    lesson_discipline_id: str = ""

    # --- посещаемость ---
    attendance_lesson_id: str = ""
    attendance_rows: list[dict] = []

    # --- статистика ---
    stats_group_id: str = ""
    student_stats: list[dict] = []
    group_avg_percent: float = 0.0
    chart_data: list[dict] = []

    def _set_msg(self, text: str, kind: str = "info"):
        self.message = text
        self.message_type = kind

    @rx.event
    def clear_message(self):
        self.message = ""
        self.message_type = "info"

    # Явные сеттеры (в Reflex 0.9 автосеттеры не регистрируются)
    @rx.event
    def set_group_name(self, value: str):
        self.group_name = value

    @rx.event
    def set_import_group_id(self, value: str):
        self.import_group_id = value

    @rx.event
    def set_student_full_name(self, value: str):
        self.student_full_name = value

    @rx.event
    def set_student_card(self, value: str):
        self.student_card = value

    @rx.event
    def set_student_course(self, value: str):
        self.student_course = value

    @rx.event
    def set_student_group_id(self, value: str):
        self.student_group_id = value

    @rx.event
    def set_discipline_name(self, value: str):
        self.discipline_name = value

    @rx.event
    def set_discipline_teacher(self, value: str):
        self.discipline_teacher = value

    @rx.event
    def set_lesson_date(self, value: str):
        self.lesson_date = value

    @rx.event
    def set_lesson_group_id(self, value: str):
        self.lesson_group_id = value

    @rx.event
    def set_lesson_discipline_id(self, value: str):
        self.lesson_discipline_id = value

    @rx.event
    def set_stats_group_id(self, value: str):
        self.stats_group_id = value

    # ------------------------------------------------------------------
    # Загрузка справочников
    # ------------------------------------------------------------------
    @rx.event
    def load_all(self):
        self.load_groups()
        self.load_students()
        self.load_disciplines()
        self.load_lessons()

    @rx.event
    def load_groups(self):
        with rx.session() as session:
            rows = session.exec(select(StudyGroup).order_by(StudyGroup.name)).all()
            self.groups = [{"id": str(g.id), "name": g.name} for g in rows]

    @rx.event
    def load_students(self):
        query = self.student_search.strip().lower()
        with rx.session() as session:
            students = session.exec(select(Student).order_by(Student.full_name)).all()
            groups = {g.id: g.name for g in session.exec(select(StudyGroup)).all()}
            result = []
            for s in students:
                group_name = groups.get(s.group_id, "—")
                if query and query not in s.full_name.lower() and query not in group_name.lower():
                    continue
                result.append(
                    {
                        "id": str(s.id),
                        "full_name": s.full_name,
                        "group_id": str(s.group_id),
                        "group_name": group_name,
                    }
                )
            self.students = result

    @rx.event
    def load_disciplines(self):
        with rx.session() as session:
            rows = session.exec(select(Discipline).order_by(Discipline.name)).all()
            self.disciplines = [
                {"id": str(d.id), "name": d.name, "teacher": d.teacher}
                for d in rows
            ]

    @rx.event
    def load_lessons(self):
        with rx.session() as session:
            lessons = session.exec(select(Lesson).order_by(Lesson.lesson_date.desc())).all()
            groups = {g.id: g.name for g in session.exec(select(StudyGroup)).all()}
            discs = {d.id: d.name for d in session.exec(select(Discipline)).all()}
            self.lessons = [
                {
                    "id": str(les.id),
                    "lesson_date": les.lesson_date,
                    "group_id": str(les.group_id),
                    "group_name": groups.get(les.group_id, "—"),
                    "discipline_id": str(les.discipline_id),
                    "discipline_name": discs.get(les.discipline_id, "—"),
                    "label": f"{les.lesson_date} · {groups.get(les.group_id, '—')} · {discs.get(les.discipline_id, '—')}",
                }
                for les in lessons
            ]

    # ------------------------------------------------------------------
    # Группы
    # ------------------------------------------------------------------
    @rx.event
    def add_group(self):
        """Создаёт учебную группу с произвольным названием (без шаблона формата)."""
        # Любая строка допускается: у каждого вуза своё обозначение групп.
        name = self.group_name.strip()
        if not name:
            self._set_msg("Введите название группы", "error")
            return
        with rx.session() as session:
            exists = session.exec(select(StudyGroup).where(StudyGroup.name == name)).first()
            if exists:
                self._set_msg(f"Группа «{name}» уже есть в списке", "error")
                return
            session.add(StudyGroup(name=name))
            session.commit()
        self.group_name = ""
        self.load_groups()
        self._set_msg(f"Группа «{name}» создана", "success")

    @rx.event
    def delete_group(self, group_id: str):
        gid = int(group_id)
        with rx.session() as session:
            students = session.exec(select(Student).where(Student.group_id == gid)).all()
            if students:
                self._set_msg("Нельзя удалить группу: в ней есть студенты", "error")
                return
            group = session.get(StudyGroup, gid)
            if group:
                session.delete(group)
                session.commit()
        self.load_groups()
        if self.selected_group_id == group_id:
            self.selected_group_id = ""
            self.group_students = []
        self._set_msg("Группа удалена", "success")

    @rx.event
    def select_group(self, group_id: str):
        self.selected_group_id = group_id
        self.load_group_students()

    @rx.event
    def load_group_students(self):
        if not self.selected_group_id:
            self.group_students = []
            return
        gid = int(self.selected_group_id)
        with rx.session() as session:
            rows = session.exec(
                select(Student).where(Student.group_id == gid).order_by(Student.full_name)
            ).all()
            self.group_students = [
                {
                    "id": str(s.id),
                    "full_name": s.full_name
                }
                for s in rows
            ]

    # ------------------------------------------------------------------
    # Студенты
    # ------------------------------------------------------------------
    @rx.event
    def set_student_search(self, value: str):
        self.student_search = value
        self.load_students()

    @rx.event
    def clear_student_form(self):
        self.student_full_name = ""
        self.student_card = ""
        self.student_course = "1"
        self.student_group_id = ""
        self.editing_student_id = ""

    @rx.event
    def start_edit_student(self, student_id: str):
        with rx.session() as session:
            s = session.get(Student, int(student_id))
            if not s:
                return
            self.editing_student_id = student_id
            self.student_full_name = s.full_name
            self.student_group_id = str(s.group_id)

    @rx.event
    def save_student(self):
        """Добавляет или обновляет студента (в форме: только ФИО и группа)."""
        full_name = self.student_full_name.strip()
        if not full_name or not self.student_group_id:
            self._set_msg("Заполните ФИО и группу", "error")
            return

        with rx.session() as session:
            if self.editing_student_id:
                s = session.get(Student, int(self.editing_student_id))
                if not s:
                    self._set_msg("Студент не найден", "error")
                    return
                s.full_name = full_name
                s.group_id = int(self.student_group_id)
                session.add(s)
                msg = "Данные студента обновлены"
            else:
                # Служебные поля для БД (в интерфейсе не показываются)
                card = f"auto-{int(date.today().strftime('%Y%m%d'))}-{full_name[:20]}"
                session.add(
                    Student(
                        full_name=full_name,
                        group_id=int(self.student_group_id),
                    )
                )
                msg = "Студент добавлен"
            session.commit()

        self.clear_student_form()
        self.load_students()
        self.load_group_students()
        self._set_msg(msg, "success")

    @rx.event
    def delete_student(self, student_id: str):
        sid = int(student_id)
        with rx.session() as session:
            marks = session.exec(select(Attendance).where(Attendance.student_id == sid)).all()
            for m in marks:
                session.delete(m)
            s = session.get(Student, sid)
            if s:
                session.delete(s)
                session.commit()
        self.load_students()
        self.load_group_students()
        self._set_msg("Студент удалён", "success")

    @rx.event
    async def import_students_excel(self, files: list[rx.UploadFile]):
        """
        Импортирует список студентов из .xlsx в выбранную группу.
        Использует openpyxl через parse_students_xlsx().
        """
        if not self.import_group_id:
            self.import_status = "Сначала выберите группу для импорта"
            self._set_msg(self.import_status, "error")
            return
        if not files:
            self.import_status = "Выберите Excel-файл (.xlsx)"
            self._set_msg(self.import_status, "error")
            return

        file = files[0]
        data = await file.read()
        students, error = parse_students_xlsx(data)
        if error:
            self.import_status = error
            self._set_msg(error, "error")
            return

        gid = int(self.import_group_id)
        added = 0
        skipped = 0
        with rx.session() as session:
            existing_cards = {
                s.student_card
                for s in session.exec(select(Student).where(Student.group_id == gid)).all()
            }
            for item in students:
                if item["student_card"] in existing_cards:
                    skipped += 1
                    continue
                session.add(
                    Student(
                        full_name=item["full_name"],
                        student_card=item["student_card"],
                        course=item["course"],
                        group_id=gid,
                    )
                )
                existing_cards.add(item["student_card"])
                added += 1
            session.commit()

        self.import_status = f"Импортировано: {added}. Пропущено (дубликаты): {skipped}."
        self.load_students()
        if self.selected_group_id == self.import_group_id:
            self.load_group_students()
        self._set_msg(self.import_status, "success")
        yield rx.clear_selected_files("student_excel")

    # ------------------------------------------------------------------
    # Дисциплины
    # ------------------------------------------------------------------
    @rx.event
    def clear_discipline_form(self):
        self.discipline_name = ""
        self.discipline_teacher = ""
        self.editing_discipline_id = ""

    @rx.event
    def start_edit_discipline(self, discipline_id: str):
        with rx.session() as session:
            d = session.get(Discipline, int(discipline_id))
            if not d:
                return
            self.editing_discipline_id = discipline_id
            self.discipline_name = d.name
            self.discipline_teacher = d.teacher

    @rx.event
    def save_discipline(self):
        name = self.discipline_name.strip()
        teacher = self.discipline_teacher.strip()
        if not name:
            self._set_msg("Введите название дисциплины", "error")
            return
        with rx.session() as session:
            if self.editing_discipline_id:
                d = session.get(Discipline, int(self.editing_discipline_id))
                if not d:
                    self._set_msg("Дисциплина не найдена", "error")
                    return
                d.name = name
                d.teacher = teacher
                session.add(d)
                msg = "Дисциплина обновлена"
            else:
                session.add(Discipline(name=name, teacher=teacher))
                msg = "Дисциплина добавлена"
            session.commit()
        self.clear_discipline_form()
        self.load_disciplines()
        self._set_msg(msg, "success")

    @rx.event
    def delete_discipline(self, discipline_id: str):
        did = int(discipline_id)
        with rx.session() as session:
            used = session.exec(select(Lesson).where(Lesson.discipline_id == did)).first()
            if used:
                self._set_msg("Нельзя удалить: дисциплина используется в занятиях", "error")
                return
            d = session.get(Discipline, did)
            if d:
                session.delete(d)
                session.commit()
        self.load_disciplines()
        self._set_msg("Дисциплина удалена", "success")

    # ------------------------------------------------------------------
    # Занятия
    # ------------------------------------------------------------------
    @rx.event
    def add_lesson(self):
        """
        Создаёт занятие (дата + группа + дисциплина)
        и сразу формирует отметки посещаемости для всех студентов группы.
        """
        if not self.lesson_date or not self.lesson_group_id or not self.lesson_discipline_id:
            self._set_msg("Укажите дату, группу и дисциплину", "error")
            return
        with rx.session() as session:
            lesson = Lesson(
                lesson_date=self.lesson_date,
                group_id=int(self.lesson_group_id),
                discipline_id=int(self.lesson_discipline_id),
            )
            session.add(lesson)
            session.commit()
            session.refresh(lesson)
            # Создаём отметки по умолчанию «присутствовал» для всех студентов группы
            students = session.exec(
                select(Student).where(Student.group_id == lesson.group_id)
            ).all()
            for s in students:
                session.add(
                    Attendance(lesson_id=lesson.id, student_id=s.id, status="present")
                )
            session.commit()
        self.load_lessons()
        self._set_msg("Занятие создано", "success")

    @rx.event
    def delete_lesson(self, lesson_id: str):
        lid = int(lesson_id)
        with rx.session() as session:
            marks = session.exec(select(Attendance).where(Attendance.lesson_id == lid)).all()
            for m in marks:
                session.delete(m)
            les = session.get(Lesson, lid)
            if les:
                session.delete(les)
                session.commit()
        if self.attendance_lesson_id == lesson_id:
            self.attendance_lesson_id = ""
            self.attendance_rows = []
        self.load_lessons()
        self._set_msg("Занятие удалено", "success")

    # ------------------------------------------------------------------
    # Посещаемость
    # ------------------------------------------------------------------
    @rx.event
    def select_attendance_lesson(self, lesson_id: str):
        self.attendance_lesson_id = lesson_id
        self.load_attendance()

    @rx.event
    def load_attendance(self):
        if not self.attendance_lesson_id:
            self.attendance_rows = []
            return
        lid = int(self.attendance_lesson_id)
        with rx.session() as session:
            lesson = session.get(Lesson, lid)
            if not lesson:
                self.attendance_rows = []
                return
            students = session.exec(
                select(Student)
                .where(Student.group_id == lesson.group_id)
                .order_by(Student.full_name)
            ).all()
            marks = {
                a.student_id: a
                for a in session.exec(
                    select(Attendance).where(Attendance.lesson_id == lid)
                ).all()
            }
            rows = []
            for s in students:
                mark = marks.get(s.id)
                if mark is None:
                    mark = Attendance(lesson_id=lid, student_id=s.id, status="absent")
                    session.add(mark)
                    session.commit()
                    session.refresh(mark)
                rows.append(
                    {
                        "attendance_id": str(mark.id),
                        "student_id": str(s.id),
                        "full_name": s.full_name,
                        "student_card": s.student_card,
                        "status": mark.status,
                        "status_label": ATTENDANCE_STATUSES.get(mark.status, mark.status),
                    }
                )
            self.attendance_rows = rows

    @rx.event
    def set_attendance_status(self, attendance_id: str, status: str):
        """Меняет статус посещаемости: present / absent / excused / late."""
        with rx.session() as session:
            mark = session.get(Attendance, int(attendance_id))
            if mark:
                mark.status = status
                session.add(mark)
                session.commit()
        self.load_attendance()

    # ------------------------------------------------------------------
    # Статистика
    # ------------------------------------------------------------------
    @rx.event
    def load_stats(self):
        """
        Считает статистику по группе:
        посещения, пропуски, % по студенту и средний % по группе + данные для диаграммы.
        Посещением считаются статусы «присутствовал» и «опоздал».
        """
        if not self.stats_group_id:
            self.student_stats = []
            self.group_avg_percent = 0.0
            self.chart_data = []
            return

        gid = int(self.stats_group_id)
        with rx.session() as session:
            students = session.exec(
                select(Student).where(Student.group_id == gid).order_by(Student.full_name)
            ).all()
            lessons = session.exec(select(Lesson).where(Lesson.group_id == gid)).all()
            lesson_ids = [les.id for les in lessons]
            marks_by_student: dict[int, list[str]] = defaultdict(list)
            if lesson_ids:
                marks = session.exec(
                    select(Attendance).where(Attendance.lesson_id.in_(lesson_ids))
                ).all()
                for m in marks:
                    marks_by_student[m.student_id].append(m.status)

            stats = []
            percents = []
            chart = []
            for s in students:
                statuses = marks_by_student.get(s.id, [])
                total = len(statuses)
                present = sum(1 for st in statuses if st in ("present", "late"))
                absent = sum(1 for st in statuses if st == "absent")
                excused = sum(1 for st in statuses if st == "excused")
                late = sum(1 for st in statuses if st == "late")
                percent = round((present / total) * 100, 1) if total else 0.0
                percents.append(percent)
                short_name = s.full_name.split()[0] if s.full_name else s.full_name
                stats.append(
                    {
                        "id": str(s.id),
                        "full_name": s.full_name,
                        "present": str(present),
                        "absent": str(absent),
                        "excused": str(excused),
                        "late": str(late),
                        "total": str(total),
                        "percent": f"{percent}%",
                    }
                )
                chart.append({"name": short_name, "percent": percent})

            self.student_stats = stats
            self.group_avg_percent = round(sum(percents) / len(percents), 1) if percents else 0.0
            self.chart_data = chart
