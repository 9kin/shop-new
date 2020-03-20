import data.db_session as db
from data.__all_models import *
import xlrd


db.global_init('db/items.sqlite')
session = db.create_session()


#item = items.Item()
#item.name = 'qq'
#item.cost = 54
#item.manufacturer = 'OOOO'

# session.add(item)


book = xlrd.open_workbook("PList.xls", encoding_override="cp1252")

sheet = book.sheet_by_index(0)

# sheet.nrows 2
manufacturer = ''
for rownum in range(2, sheet.nrows):
    row = sheet.row_values(rownum)
    if row[1] != '':
        manufacturer = row[0]
    else:
        try:
            session.add(items.Item(
                name=row[0],
                count=row[10],
                cost=row[13],
                manufacturer=manufacturer
            ))
        except:
            print('qqq')
            print(row)
            session.commit()
            exit(0)
session.commit()
