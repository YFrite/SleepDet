from docxtpl import DocxTemplate


def create_docx_file(filename, args):
    doc = DocxTemplate("templates/template_report.docx")
    context = args
    doc.render(context)
    doc.save(f"${filename}.docx")
