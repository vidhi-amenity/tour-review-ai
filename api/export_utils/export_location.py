from api.models import Review, SOURCE_STREAM
from datetime import timedelta, date
from api import utils
import io
from xlsxwriter import Workbook
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import letter
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import tempfile
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def export_xlsx_location(data, start_date, end_date):
    extension = 'xlsx'
    days_difference = end_date - start_date + timedelta(days=1)

    start_date_before = start_date - days_difference
    end_date_before = start_date - timedelta(days=1)

    start_date_f = start_date.strftime("%d %b, %Y")
    end_date_f = end_date.strftime("%d %b, %Y")

    header = ''
    title = f'Last {days_difference.days} Days'

    # Create a new Excel workbook and add a worksheet
    output = io.BytesIO()
    workbook = Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    center = workbook.add_format({'align': 'center'})
    worksheet.set_column('A:A', 50, center)
    worksheet.set_column('B:B', 12, center)
    worksheet.set_column('C:C', 12, center)

    format_header = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'bold': True
    })
    # worksheet.merge_range('A1:A2', header, format_header)
    # worksheet.write(0, 1, start_date_f)
    # worksheet.write(1, 1, end_date_f)

    worksheet.write(0, 0, 'State')
    worksheet.write(0, 1, 'Positive')
    worksheet.write(0, 2, 'Passive')
    worksheet.write(0, 3, 'Negative')
    worksheet.write(0, 4, 'Total')

    # Write the review data to the worksheet
    for row, review in enumerate(data, start=3):
        worksheet.write(row, 0, review['name'])
        worksheet.write(row, 1, review['positive'])
        worksheet.write(row, 2, review['passive'])
        worksheet.write(row, 3, review['negative'])
        worksheet.write(row, 4, review['value'])

    # Create a new chart object and add data to it
    chart = workbook.add_chart({'type': 'column'})
    chart.add_series({
        'name': 'Current period',
        'categories': '=Sheet1!$A$4:$A$' + str(len(data) + 3),
        'values': '=Sheet1!$E$4:$E$' + str(len(data) + 3),
    })

    # Add the chart to the worksheet and set its properties
    worksheet.insert_chart('F2', chart)
    chart.set_title({'name': title})
    chart.set_x_axis({'name': header})
    chart.set_y_axis({'name': 'Number of Reviews'})
    chart.set_legend({'position': 'top'})

    workbook.close()

    # Imposta il puntatore dell'oggetto BytesIO all'inizio del buffer
    output.seek(0)

    # if xls:
    #     extension = 'xls'
    #     xls_output = io.BytesIO()
    #     workbook = openpyxl.load_workbook(output)
    #
    #     # Prepares the data for Pyexcelerate
    #     data = []
    #     for sheet_name in workbook.sheetnames:
    #         sheet = workbook[sheet_name]
    #         for row in sheet.iter_rows(values_only=True):
    #             data.append(row)
    #
    #     # Creates a new Workbook using Pyexcelerate
    #     wb = pyexcelerate.Workbook()
    #     wb.new_sheet("sheet name", data=data)
    #
    #     # Saves the workbook to a .xls file
    #     wb.save(xls_output)
    #
    #     xls_output.seek(0)
    #     output = xls_output

    return output, title, extension

def pdf_first_page(p, title, logo):
    p.setFont('NotoSans-Bold', 14)
    x = letter[0] / 2
    y = letter[1] / 2
    p.drawImage(logo, x-210, y+100, width=3080 /8, height=662 /8,
                mask='auto')
    p.drawCentredString(x, y+20, 'Report')  # Draw the centered text
    p.drawCentredString(x, y, title)  # Draw the centered text
    p.showPage()


def draw_standard_logo(p, logo):
    logo_width = 100  # Adjust the width of the logo as needed
    logo_height = 22  # Adjust the height of the logo as needed
    p.drawImage(logo, 490, 812, width=logo_width, height=logo_height,
                mask='auto')  # Adjust the coordinates as needed


def write_table_header(p, header,compare):
    page_height = 800  # Maximum y coordinate for the page content
    row_height = 20  # Height of each row
    y = page_height - row_height
    p.setFont('NotoSans-Bold', 12)
    p.drawString(50, y, header)
    p.drawString(270, y, 'Tot. Current Period')
    if compare:
        p.drawString(420, y, 'Tot. Previous Period')
    p.setFont('NotoSans', 12)



def export_pdf_location(data, start_date, end_date):
    header = 'Reviews Location'

    start_date_f = start_date.strftime("%d %b, %Y")
    end_date_f = end_date.strftime("%d %b, %Y")
    title = header
    title_chart = f'Period {start_date_f} - {end_date_f}'

    pdfmetrics.registerFont(TTFont('NotoSans', 'assets/fonts/Noto_Sans/NotoSans-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('NotoSans-Bold', 'assets/fonts/Noto_Sans/NotoSans-Bold.ttf'))

    buffer = BytesIO()

    # Create the PDF canvas
    p = canvas.Canvas(buffer)

    # Load the logo image
    logo_path = 'assets/logos/logo.png'  # Replace 'logo.png' with the actual path to your logo image
    logo = ImageReader(logo_path)

    pdf_first_page(p, title, logo)
    pdf_chart_page_location(p, logo, title_chart, data, header)
    draw_standard_logo(p, logo)
    cols = [
        {'name': 'State', 'param': 'name', 'spacing': 50},
        {'name': 'Positive', 'param': 'positive', 'spacing': 250},
        {'name': 'Passive', 'param': 'passive', 'spacing': 320},
        {'name': 'Negative', 'param': 'negative', 'spacing': 390},
    ]
    write_table_header_location(p, cols)

    page_height = 760  # Maximum y coordinate for the page content
    row_height = 20  # Height of each row
    rows_per_page = page_height / row_height

    for i, review in enumerate(data, start=1):
        row = i % rows_per_page
        if row == 0:
            # Start a new page
            p.showPage()
            draw_standard_logo(p, logo)
            write_table_header_location(p, cols)

        y = page_height - (row * row_height)

        for c in cols:
            if review[c['param']] == None:
                continue
            review[c['param']] = str(review[c['param']])

            text = review[c['param']][:30] + '...' if len(review[c['param']]) > 30 else review[c['param']]
            p.drawString(c['spacing'], y, text)

    # Save the PDF content
    p.save()

    # Retrieve the PDF content from the buffer
    buffer.seek(0)
    pdf_data = buffer.getvalue()

    # Close the buffer
    buffer.close()

    return pdf_data, title


def pdf_chart_page_location(p, logo, title_chart, data, header):
    p.setFont('NotoSans-Bold', 14)
    x = letter[0] / 2
    y = letter[1] / 2
    draw_standard_logo(p, logo)
    p.drawCentredString(x, y+250, title_chart)

    labels = [entry['name'] for entry in data]
    values_total_reviews = [entry['value'] for entry in data]

    # Crea il grafico a due colonne utilizzando matplotlib
    fig = plt.figure(figsize=(12, 6))  # Larghezza: 8 pollici, Altezza: 6 pollici
    bar_width = 0.35
    index = range(len(labels))

    plt.bar(index, values_total_reviews, bar_width, color='blue', label='Total Reviews')

    plt.xlabel(header)
    plt.ylabel('Reviews')
    plt.title('Reviews Comparison')
    plt.xticks([i + bar_width / 2 for i in index], labels)
    plt.xticks(rotation=45, ha='right')
    # plt.gca().set_xticks(range(0, len(labels), 10))  # Mostra una label ogni 10 elementi

    if len(labels) > 30:
        plt.xticks([])

    plt.legend()

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        chart_image_path = temp_file.name + '.png'  # Aggiungi estensione .png al nome del file
        plt.savefig(chart_image_path)

    image_reader = ImageReader(chart_image_path)

    p.drawImage(image_reader, -35, 300, width=680,
                height=340)
    os.remove(chart_image_path)

    p.showPage()


def write_table_header_location(p, cols):
    page_height = 800  # Maximum y coordinate for the page content
    row_height = 20  # Height of each row
    y = page_height - row_height
    p.setFont('NotoSans-Bold', 12)
    for c in cols:
        p.drawString(c['spacing'], y, c['name'])
    p.setFont('NotoSans', 12)