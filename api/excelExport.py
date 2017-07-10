import xlrd
import xlwt
from xlutils.copy import copy
import os

def create_new_file(excel_file):
    #creating new excel file and new sheet
    new_workbook = xlwt.Workbook()
    new_sheet = new_workbook.add_sheet('Data')

    #setting columns width
    new_sheet.col(0).width = 7000
    new_sheet.col(1).width = 5000
    new_sheet.col(2).width = 4500
    new_sheet.col(3).width = 5000
    new_sheet.col(4).width = 2300
    new_sheet.col(5).width = 8000
    new_sheet.col(6).width = 1000
    new_sheet.col(7).width = 5000

    #creating title cells style
    style_title = xlwt.easyxf(
        'font: bold on, color black; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color white;')
    alignTitle = xlwt.Alignment()
    alignTitle.horz = xlwt.Alignment.HORZ_CENTER
    alignTitle.vert = xlwt.Alignment.VERT_CENTER
    style_title.alignment = alignTitle

    #merging title cells
    new_sheet.merge(0, 1, 0, 0, style=style_title)
    new_sheet.merge(0, 1, 1, 1, style=style_title)
    new_sheet.merge(0, 1, 2, 2, style=style_title)
    new_sheet.merge(0, 1, 3, 3, style=style_title)
    new_sheet.merge(0, 1, 4, 4, style=style_title)
    new_sheet.merge(0, 1, 5, 5, style=style_title)

    #writing title cells with title style
    new_sheet.write(0, 0, 'Prénom(s)', style=style_title)
    new_sheet.write(0, 1, "Nom", style=style_title)
    new_sheet.write(0, 2, "Date de naissance", style=style_title)
    new_sheet.write(0, 3, "Lieu de naissance", style=style_title)
    new_sheet.write(0, 4, "Erreur ?", style=style_title)
    new_sheet.write(0, 5, "Message d'erreur", style=style_title)
    new_sheet.write(0, 7, "Nombre d'erreurs", style=style_title)
    new_sheet.write(1, 7, "Pourcentage d'erreur", style=style_title)

    #saving new file
    new_workbook.save(excel_file)


def fill_new_line(excel_file, first_name, last_name, birth_date, birth_place, error, error_message):
    #checking if a previous excel data file already exists
    if not os.path.isfile(excel_file):
        create_new_file(excel_file)

    #opening existing file
    main_workbook = xlrd.open_workbook(excel_file)
    main_sheet = main_workbook.sheets()[0]
    row_to_write = main_sheet.nrows

    #copying existing file to be able to write into it
    workbook_copy = copy(main_workbook)
    sheet_copy = workbook_copy.get_sheet(0)

    #rewriting cells style since it is not copied by xlutils.copy function
    sheet_copy.col(0).width = 7000
    sheet_copy.col(1).width = 5000
    sheet_copy.col(2).width = 4500
    sheet_copy.col(3).width = 5000
    sheet_copy.col(4).width = 2300
    sheet_copy.col(5).width = 8000
    sheet_copy.col(6).width = 1000
    sheet_copy.col(7).width = 5000

    style_title = xlwt.easyxf(
        'font: bold on, color black; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color white;')
    alignTitle = xlwt.Alignment()
    alignTitle.horz = xlwt.Alignment.HORZ_CENTER
    alignTitle.vert = xlwt.Alignment.VERT_CENTER
    style_title.alignment = alignTitle

    #creating other cells styles
    style_data = xlwt.easyxf(
        'font: bold off, color black; borders: left dashed, right dashed, top dashed, bottom dashed; pattern: pattern solid, fore_color white;')

    style_error = xlwt.easyxf(
        'font: bold off, color black; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color white;')

    style_percent = xlwt.easyxf(
        'font: bold off, color black; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color white;')
    style_percent.num_format_str='0.00%'

    #re-merging title cells since it is not copied by xlutils.copy function
    sheet_copy.merge(0, 1, 0, 0, style=style_title)
    sheet_copy.merge(0, 1, 1, 1, style=style_title)
    sheet_copy.merge(0, 1, 2, 2, style=style_title)
    sheet_copy.merge(0, 1, 3, 3, style=style_title)
    sheet_copy.merge(0, 1, 4, 4, style=style_title)
    sheet_copy.merge(0, 1, 5, 5, style=style_title)

    #re-writing title cells to re-apply title cells style
    sheet_copy.write(0, 0, 'Prénom(s)', style=style_title)
    sheet_copy.write(0, 1, "Nom", style=style_title)
    sheet_copy.write(0, 2, "Date de naissance", style=style_title)
    sheet_copy.write(0, 3, "Lieu de naissance", style=style_title)
    sheet_copy.write(0, 4, "Erreur ?", style=style_title)
    sheet_copy.write(0, 5, "Message d'erreur", style=style_title)
    sheet_copy.write(0, 7, "Nombre d'erreurs", style=style_title)
    sheet_copy.write(1, 7, "Pourcentage d'erreur", style=style_title)

    #injecting fresh data into the new file with the apropriate style
    sheet_copy.write(row_to_write, 0, first_name, style=style_data)
    sheet_copy.write(row_to_write, 1, last_name, style=style_data)
    sheet_copy.write(row_to_write, 2, birth_date, style=style_data)
    sheet_copy.write(row_to_write, 3, birth_place, style=style_data)
    sheet_copy.write(row_to_write, 4, error, style=style_data)
    sheet_copy.write(row_to_write, 5, error_message, style=style_data)

    #re-writing formulas since they are not copied by xlutils.copy function
    sheet_copy.write(0, 8, xlwt.Formula(
        'COUNTIF(E1:E10;"Oui")'
    ), style=style_error)
    sheet_copy.write(1, 8, xlwt.Formula(
        '(I1/COUNTA(E1:E10))'
    ), style=style_percent)

    #saving the new file (and erasing the old one)
    workbook_copy.save(excel_file)




