from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)


def generate_report(
    student_name,
    report_text
):

    filename = (
        student_name
        .replace(" ", "_")
        + "_Report.pdf"
    )

    doc = SimpleDocTemplate(
        filename
    )

    styles = getSampleStyleSheet()

    content = []

    title = Paragraph(
        "SchoolMind AI Student Report",
        styles["Title"]
    )

    content.append(title)

    content.append(
        Spacer(1, 12)
    )

    body = Paragraph(
        report_text.replace(
            "\n",
            "<br/>"
        ),
        styles["BodyText"]
    )

    content.append(body)

    doc.build(content)

    return filename