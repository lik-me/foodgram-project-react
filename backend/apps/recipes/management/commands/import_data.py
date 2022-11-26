import csv
import os
import re

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

TABLE_PREFIX = "recipes"
FILES_TBLS_LIST = {
    "ingredients.csv": [f"{TABLE_PREFIX}_ingredients", 0],
}

PATH_TO_CSV = os.path.join(settings.BASE_DIR, "data")


class Command(BaseCommand):
    help = "Import data from csv files to DB"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        # Временно отключаем внешние ключи.
        # should comment if PosgreSQL used
        # cursor.execute("PRAGMA foreign_keys = OFF;")
        files_csv_list = os.listdir(PATH_TO_CSV)
        for file_name in files_csv_list:
            if file_name in FILES_TBLS_LIST.keys():
                tbl_t = FILES_TBLS_LIST[file_name][0]
                header_in_query = FILES_TBLS_LIST[file_name][1]
                file = os.path.join(PATH_TO_CSV, file_name)
                with open(file, newline="", encoding="utf-8") as csvfile:
                    csv_reader = csv.reader(csvfile, delimiter=",")
                    row_num = 0
                    for row in csv_reader:
                        if row_num == 0:
                            sql_hdr = self.header_handler(
                                row, header_in_query, tbl_t, file_name
                            )
                        else:
                            sql_fld_values = self.data_handler(
                                row, file_name, row_num)
                            sql_body_final = (
                                f"{sql_hdr} VALUES ({sql_fld_values})"
                            )
                            cursor.execute(sql_body_final)
                        row_num += 1
        # Включаем внешние ключи.
        # should comment if PosgreSQL used
        # cursor.execute("PRAGMA foreign_keys = ON;")
        self.stdout.write(self.style.SUCCESS("Импорт данных завершен!"))

    def header_handler(self, row, header_in_query, tbl_t, file_name):
        """
        Создание заголовочной части тела запроса.
        """
        # sql_hdr = f"INSERT INTO `{tbl_t}`"
        # Remove quotes if PosgreSQL used
        sql_hdr = f"INSERT INTO {tbl_t}"
        return sql_hdr

    def data_handler(self, row, file_name, counter):
        """
        Создание основной части тела запроса.
        """

        vals = ""
        if len(row) == 1:
            # Разделитель в данных
            if row[0][0] == '"' and row[0][-1] == '"':
                row[0] = row[0][1:-1]
            row = re.split(
                """,
                (?=(?:[^'"]|'[^']*'|"[^"]*")*$)""",
                row[0],
            )
        for w in row:
            if w.isnumeric():
                vals += f"{w}, "
            else:
                w = w.replace("'", "%27")
                vals += f"'{w}', "
        vals = f"{counter}, {vals}"
        sql_fld_values = vals[0:-2]
        return sql_fld_values
