from docx.shared import Mm
from docxtpl import DocxTemplate, InlineImage
import glob


def create_docx_file(filepath, filename, content):
    content["COUNT_OF_VIOLATIONS"] = correct_form(content["COUNT_OF_VIOLATIONS"],
                                                  'эпизод', 'эпизода', 'эпизодов')
    content["TIME_SOUND"] = correct_form(content["TIME_SOUND"], 'минута', 'минуты', 'минут')
    content["TIME_PROCESSING"] = correct_form(content["TIME_PROCESSING"], 'секунда', 'секунды', 'секунд')
    content["AGE"] = correct_form(content["AGE"], 'год', 'года', 'лет')

    doc = DocxTemplate("templates/template_report.docx")
    imageObjs = []
    for fPath in glob.glob('uploads/images/*.png'):
        print(fPath)
        imgObj = InlineImage(doc, fPath, width=Mm(180))
        imageObjs.append(imgObj)
    content["images"] = imageObjs
    doc.render(content)
    doc.save(f"./{filepath}/{filename}.docx")


def correct_form(number, one, few, many):
    number = int(number)
    if number % 100 in (11, 12, 13, 14):
        return f"{number} {many}"
    elif number % 10 == 1:
        return f"{number} {one}"
    elif number % 10 in (2, 3, 4):
        return f"{number} {few}"
    else:
        return f"{number} {many}"
