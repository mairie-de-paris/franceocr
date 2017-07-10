import xlrd
import xlwt
from xlutils.copy import copy
import os

def create_new_file(excel_file):
    new_workbook = xlwt.Workbook()
    new_sheet = new_workbook.add_sheet('Data')

    style = xlwt.XFStyle()
    # font
    font = xlwt.Font()
    font.bold = True
    style.font = font
    # borders
    borders = xlwt.Borders()
    borders.bottom = xlwt.Borders.DASHED
    style.borders = borders

    new_sheet.write(0, 0, "Prénoms", style=style)
    new_sheet.write(0, 1, "Nom", style=style)
    new_sheet.write(0, 2, "Date de naissance", style=style)
    new_sheet.write(0, 3, "Lieu de naissance", style=style)
    new_sheet.write(0, 4, "Erreur ?", style=style)
    new_sheet.write(0, 5, "Message d'erreur", style=style)

    new_sheet.col(0).width = 10000
    new_sheet.col(1).width = 10000
    new_sheet.col(2).width = 10000
    new_sheet.col(3).width = 10000
    new_sheet.col(4).width = 100
    new_sheet.col(5).width = 50000

    new_workbook.save(excel_file)


def fill_new_line(excel_file, first_name, last_name, birth_date, birth_place, error, error_message):
    if not os.path.isfile(excel_file):
        create_new_file(excel_file)

    main_workbook = xlrd.open_workbook(excel_file)
    main_sheet = main_workbook.sheets()[0]
    row_to_write = main_sheet.nrows

    workbook_copy = copy(main_workbook)
    sheet_copy = workbook_copy.get_sheet(0)



    sheet_copy.write(row_to_write, 0, first_name)
    sheet_copy.write(row_to_write, 1, last_name)
    sheet_copy.write(row_to_write, 2, birth_date)
    sheet_copy.write(row_to_write, 3, birth_place)
    sheet_copy.write(row_to_write, 4, error)
    sheet_copy.write(row_to_write, 5, error_message)

    workbook_copy.save(excel_file)



#create_new_file("test.xls")
#testworkbook = xlrd.open_workbook("test.xls")
#testsheet = testworkbook.sheets()[0]
#print(testsheet.nrows)
#testworkbook = copy(testworkbook)
#testsheet = testworkbook.get_sheet(0)
#testsheet.write(1,0, None)
#testworkbook.save("test.xls")




