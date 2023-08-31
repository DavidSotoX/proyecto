import xlwt
import datetime

#style_grey_header = xlwt.easyxf('pattern: pattern solid, fore_colour gray25; font: bold on; align: wrap on, vert centre, horiz center')

    


class ExcelDocument:
    def __init__(self):
        self.workbook = xlwt.Workbook(encoding='utf-8')

    def add_sheet(self, sheet_name):
        return self.workbook.add_sheet(sheet_name)

    def save(self, file_path):
        self.workbook.save(file_path)

styles = {
    'title':lambda height: xlwt.easyxf(f"font: bold on, name Verdana, height {height}; align: horiz center;"),
    'header':lambda color=22: xlwt.easyxf(f"font: bold on, name Verdana; align: horiz center, vert center, wrap on; pattern: pattern solid, fore_colour {color}; borders: left thin, right thin, top thin, bottom thin;"),
    'header_rotation':lambda rotation=90,color='yellow':  xlwt.easyxf(f"font: bold on; align: rotation {rotation}, horiz center, vert center, wrap on; pattern: pattern solid, fore_colour {color}; borders: left thin, right thin, top thin, bottom thin;"),
    'info': xlwt.easyxf("font: bold on, name Verdana; align: horiz center;"),
    'data': xlwt.easyxf("font: name Verdana;"),
    'data_with_borders': xlwt.easyxf("font: name Verdana; borders: left thin, right thin, top thin, bottom thin;"),
    }

class ExcelSheet:
    def __init__(self, sheet):
        self.sheet = sheet
        self.current_row = 0
        self.current_col = 0
        self.start_group_col = 0
        self.end_group_col = 0

    def add_current_col(self):
        self.current_col+=1
        return self.current_col
    
    def add_return_start_group_col(self,add=False):
        # col=-1
        if add:
            self.start_group_col+=1
            col=self.start_group_col
        else:
            col=self.start_group_col+1
        return col
    
    
    def write_row(self, row_data):
        for col, value in enumerate(row_data):
            self.sheet.write(self.current_row, col, value)
        self.current_row += 1

    def insert_title_subtitle(self, title, subtitle, institution_title):
        self.sheet.write_merge(1, 1, 4, 11, title, styles['title'](14 * 20))
        self.sheet.write_merge(2, 2, 4, 11, subtitle, styles['title'](14 * 20))
        self.sheet.write_merge(3, 3, 3, 13, institution_title, styles['title'](14 * 20))

    def insert_print_date(self):
        self.sheet.row(6).height_mismatch = True
        self.sheet.row(6).height = 19*20
        self.sheet.write_merge(6, 6, 1, 2, "Fecha de impresión", styles['info'])
        self.sheet.write_merge(6, 6, 3, 4, datetime.datetime.now().strftime("%Y-%m-%d"), styles['data'])

    def insert_total_records(self, total):
        self.sheet.row(7).height_mismatch = True
        self.sheet.row(7).height = 19*20
        self.sheet.write_merge(7, 7, 0, 1, "Total de registros", styles['info'])
        self.sheet.write_merge(7, 7, 3, 4, total)

    def insert_table_headers(self, headers):
        for header in headers:
            start_col = header.get('start_col')
            end_col = header.get('end_col')
            start_row = header.get('start_row')
            end_row = header.get('end_row')
            text = header.get('text', '')
            color = header.get('color', 22)
            rotation = header.get('rotation')
            width = header.get('width')
            if width:
                self.set_column_dimensions(col=start_col,width=width)

            self.current_col=end_col
            self.current_row=end_row

            self.sheet.write_merge(
                start_row, end_row, start_col, end_col, text, styles['header_rotation'](rotation,color) if rotation else  styles['header'](color))
            
    def insert_table_headers_group(self, headers_group):

        for header_group in headers_group:
            title_group = header_group.get('title_group')
            start_row_group =header_group.get('start_row_group')
            end_row_group = header_group.get('end_row_group')
            start_col_group = header_group.get('start_col_group')
            end_col_group = header_group.get('end_col_group')
            color = header_group.get('color', 22)
            childrens = header_group.get('childrens')

            # Insertar el título del grupo
            self.sheet.write_merge(start_row_group, end_row_group, start_col_group, end_col_group, title_group, styles['header'](color))
            self.start_group_col =start_col_group
            self.end_group_col =end_col_group

            for children in childrens:
                children['color'] = color

            self.insert_table_headers(childrens)

    def set_row_dimensions(self, row=None, height=None):
        self.sheet.row(row).height_mismatch = True
        self.sheet.row(row).height = int(height) * 20

    def set_column_dimensions(self, col=None, width=None):
        self.sheet.col(col).width = int(width) * 256

    def write_column_data(self, row, column, data):
        style = styles['data_with_borders']
        style.alignment.horz = xlwt.Alignment.HORZ_CENTER
        style.alignment.vert = xlwt.Alignment.VERT_CENTER
        self.sheet.write(row, column, data, styles['data_with_borders'])
 
    def get_next_col(self):
        return self.current_col+1