"""
BSD 3-Clause License

Copyright (c) 2017, Mairie de Paris
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


import xlrd
import xlwt
import xlutils.copy
import os


TITLE_ALIGNMENT = xlwt.Alignment()
TITLE_ALIGNMENT.horz = xlwt.Alignment.HORZ_CENTER
TITLE_ALIGNMENT.vert = xlwt.Alignment.VERT_CENTER

TITLE_STYLE = xlwt.easyxf(
    "font: bold on, color black;"
    "borders: left thin, right thin, top thin, bottom thin;"
    "pattern: pattern solid, fore_color white;"
)
TITLE_STYLE.alignment = TITLE_ALIGNMENT

DATA_STYLE = xlwt.easyxf(
    "font: bold off, color black;"
    "borders: left dashed, right dashed, top dashed, bottom dashed;"
    "pattern: pattern solid, fore_color white;"
)

ERROR_STYLE = xlwt.easyxf(
    "font: bold off, color black;"
    "borders: left thin, right thin, top thin, bottom thin;"
    "pattern: pattern solid, fore_color white;"
)

PERCENT_STYLE = xlwt.easyxf(
    "font: bold off, color black;"
    "borders: left thin, right thin, top thin, bottom thin;"
    "pattern: pattern solid, fore_color white;"
)
PERCENT_STYLE.num_format_str = '0.00%'


def apply_layout(sheet):
    # setting columns width
    sheet.col(0).width = 7000
    sheet.col(1).width = 5000
    sheet.col(2).width = 4500
    sheet.col(3).width = 5000
    sheet.col(4).width = 2300
    sheet.col(5).width = 8000
    sheet.col(6).width = 1000
    sheet.col(7).width = 5000

    # merging title cells
    sheet.merge(0, 1, 0, 0, style=TITLE_STYLE)
    sheet.merge(0, 1, 1, 1, style=TITLE_STYLE)
    sheet.merge(0, 1, 2, 2, style=TITLE_STYLE)
    sheet.merge(0, 1, 3, 3, style=TITLE_STYLE)
    sheet.merge(0, 1, 4, 4, style=TITLE_STYLE)
    sheet.merge(0, 1, 5, 5, style=TITLE_STYLE)

    # writing title cells with title style
    sheet.write(0, 0, 'Prénom(s)', style=TITLE_STYLE)
    sheet.write(0, 1, "Nom", style=TITLE_STYLE)
    sheet.write(0, 2, "Date de naissance", style=TITLE_STYLE)
    sheet.write(0, 3, "Lieu de naissance", style=TITLE_STYLE)
    sheet.write(0, 4, "Erreur ?", style=TITLE_STYLE)
    sheet.write(0, 5, "Message d'erreur", style=TITLE_STYLE)
    sheet.write(0, 7, "Nombre d'erreurs", style=TITLE_STYLE)
    sheet.write(1, 7, "Pourcentage d'erreur", style=TITLE_STYLE)

    return sheet


def create_new_file(excel_file):
    # creating new excel file and new sheet
    new_workbook = xlwt.Workbook()
    new_sheet = new_workbook.add_sheet('Data')

    new_sheet = apply_layout(new_sheet)

    # saving new file
    new_workbook.save(excel_file)


def fill_new_line(excel_file, first_name, last_name, birth_date, birth_place, error, error_message):
    # checking if a previous excel data file already exists
    if not os.path.isfile(excel_file):
        create_new_file(excel_file)

    # opening existing file
    main_workbook = xlrd.open_workbook(excel_file)
    main_sheet = main_workbook.sheets()[0]
    row_to_write = main_sheet.nrows

    # copying existing file to be able to write into it
    workbook_copy = xlutils.copy.copy(main_workbook)
    sheet_copy = workbook_copy.get_sheet(0)

    sheet_copy = apply_layout(sheet_copy)

    # injecting fresh data into the new file with the appropriate style
    sheet_copy.write(row_to_write, 0, first_name, style=DATA_STYLE)
    sheet_copy.write(row_to_write, 1, last_name, style=DATA_STYLE)
    sheet_copy.write(row_to_write, 2, birth_date, style=DATA_STYLE)
    sheet_copy.write(row_to_write, 3, birth_place, style=DATA_STYLE)
    sheet_copy.write(row_to_write, 4, error, style=DATA_STYLE)
    sheet_copy.write(row_to_write, 5, error_message, style=DATA_STYLE)

    # re-writing formulas since they are not copied by xlutils.copy function
    sheet_copy.write(0, 8, xlwt.Formula(
        'COUNTIF(E3:E10003;"Oui")'  # limit of 10 000 data entries
    ), style=ERROR_STYLE)
    sheet_copy.write(1, 8, xlwt.Formula(
        '(I1/(COUNTA(E3:E10003)))'  # limit of 10 000 data entries
    ), style=PERCENT_STYLE)

    # saving the new file (and erasing the old one)
    workbook_copy.save(excel_file)
