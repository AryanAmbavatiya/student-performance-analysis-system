from flask import Flask, render_template, request, redirect, url_for
import student_performance_analysis as project

app = Flask(__name__)

project.load_data()


@app.route("/")
def home():
    averages = []
    for student_marks in project.marks:
        averages.append(project.calculate_average(student_marks))

    class_average = 0
    if len(averages) > 0:
        class_average = sum(averages) / len(averages)

    highest = None
    lowest = None

    if len(project.students) > 0:
        highest_index = averages.index(max(averages))
        lowest_index = averages.index(min(averages))
        highest = project.students[highest_index]
        lowest = project.students[lowest_index]

    subject_averages = []
    if len(project.students) > 0:
        for i in range(len(project.SUBJECTS)):
            total = 0
            for student_marks in project.marks:
                total = total + student_marks[i]
            subject_averages.append(total / len(project.students))

    return render_template(
        "index.html",
        subjects=project.SUBJECTS,
        students=project.students,
        marks=project.marks,
        averages=averages,
        get_grade=project.get_grade,
        class_average=class_average,
        highest=highest,
        lowest=lowest,
        subject_averages=subject_averages
    )


@app.route("/add", methods=["POST"])
def add_student():
    name = request.form["name"].strip()

    student_marks = []
    for subject in project.SUBJECTS:
        mark = float(request.form[subject])
        if mark < 0 or mark > 100:
            return "Marks must be between 0 and 100. Go back and try again."
        student_marks.append(mark)

    if name != "":
        project.students.append(name)
        project.marks.append(student_marks)
        project.save_data()

    return redirect(url_for("home"))


@app.route("/search", methods=["POST"])
def search_student():
    query = request.form["search_name"].strip().lower()
    found_student = None

    for i, name in enumerate(project.students):
        if name.lower() == query:
            average = project.calculate_average(project.marks[i])
            found_student = {
                "name": name,
                "marks": project.marks[i],
                "average": average,
                "grade": project.get_grade(average)
            }
            break

    averages = [project.calculate_average(m) for m in project.marks]
    class_average = sum(averages) / len(averages) if averages else 0

    highest = None
    lowest = None
    subject_averages = []

    if project.students:
        highest = project.students[averages.index(max(averages))]
        lowest = project.students[averages.index(min(averages))]
        for i in range(len(project.SUBJECTS)):
            total = 0
            for student_marks in project.marks:
                total += student_marks[i]
            subject_averages.append(total / len(project.students))

    return render_template(
        "index.html",
        subjects=project.SUBJECTS,
        students=project.students,
        marks=project.marks,
        averages=averages,
        get_grade=project.get_grade,
        class_average=class_average,
        highest=highest,
        lowest=lowest,
        subject_averages=subject_averages,
        found_student=found_student,
        searched=True
    )


@app.route("/delete/<int:student_index>")
def delete_student(student_index):
    if 0 <= student_index < len(project.students):
        project.students.pop(student_index)
        project.marks.pop(student_index)
        project.save_data()

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
