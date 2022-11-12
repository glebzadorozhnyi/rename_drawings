import pytesseract
import os
from pdf2image import convert_from_path
import re
from PIL import Image
import pandas as pd

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'


def get_files(directory):
    os.chdir(directory)
    list_files = os.listdir()
    return list_files


def scrap_file(file_name, transform=False):
    image = convert_from_path(file_name, poppler_path=r'C:\Program Files\poppler\Library\bin')
    image = image[0]
    width, height = image.size

    pakb = image.crop((width - 1000, height - 600, width - 100, height * 0.99))
    label = image.crop((width * 0.41, height * 0.84, width * 0.74, height * 0.935))


    if transform:
        width, height = pakb.size
        m = -0.2
        xshift = abs(m) * width
        new_width = width + int(round(xshift))
        pakb = pakb.transform((new_width, height), Image.AFFINE,
                            (1, m, -xshift if m > 0 else 0, 0, 1, 0), Image.BICUBIC)
    #label.save(file_name + str(transform) + '.jpeg')
    fake_label = pytesseract.image_to_string(label, lang='rus').strip()
    fake_label = fake_label.replace('\n', ' ')
    fake_label = re.sub('[^а-яА-Я ]', '', fake_label).strip()
    return pytesseract.image_to_string(pakb, config='digits').strip(), fake_label


def get_pakb(string, fake_label):
    print(string)
    pattern = '[\d]{4}[\.]{0,1}[\d]{2}[\.]{0,1}[\d]{2}[\.]{0,1}[\d]{4}'
    pakb = re.findall(pattern, string)
    if pakb == []:
        return False
    else:
        pakb = pakb[0]
        pakb = re.sub('\.', '' ,pakb)
        pakb = pakb[0:4] + '.' + pakb[4:6] + '.' + pakb[6:8] + '.' + pakb[8:]
    label = add_label(pakb, data)
    pakb2 = 'ЦКБ.' + pakb + ' - '
    if label == '':
        label = add_label(pakb[-4:], data)
        if label == '':
            label = fake_label
        pakb2 = '@' + pakb2
    return pakb2 + label


def rename(filename, pakb, cnt=0):
    try:
        if cnt == 0:
            os.rename(filename, pakb + r'.pdf')
        else:
            os.rename(filename, '!' + pakb+str(cnt) + r'.pdf')
    except FileExistsError:
        rename(filename, pakb, cnt+1)



def rename_catalog(catalog):
    for file in catalog:
        raw_pakb, fake_label = scrap_file(file)
        pakb = get_pakb(raw_pakb, fake_label)
        if pakb:
            rename(file, pakb)
        else:
            raw_pakb, fake_label = scrap_file(file, transform=True)
            pakb = get_pakb(raw_pakb, fake_label)
            if pakb:
                rename(file, pakb)

def read_csv_in(filename):
    data = pd.read_csv(filename, encoding='ANSI', sep=';')
    data = data[['Имя', 'Тип']]
    data = data.query('Имя.str.lower().str.contains("цкб")').reset_index(drop=True)
    data['Имя'] = data['Имя'].str.strip()
    # сплитуем Имя на Наименование и Обозначение
    rows = data.loc[data['Имя'].str.contains(' - ')].index
    data[['Обозначение', 'Наименование']] = data.loc[rows, 'Имя'].str.split(pat=' - ', n=1, expand=True)
    # если Наименование пусто, то Имя идёт в Наименование
    data.loc[data['Наименование'].isna(), 'Наименование'] = data['Имя']
    data = data.fillna('')
    data = data.drop(columns='Имя')


    return data[['Наименование', 'Обозначение']]

def add_label(pakb, df):

    df = df.query('Обозначение.str.contains(@pakb)')
    if len(df) > 0:
        df = df['Наименование'].value_counts()
        anwser = df.index[0]
        anwser = re.sub('[^а-яА-ЯёЁ\d ]', '', anwser)
        return anwser
    else:
        return ''


data = read_csv_in('ckb.csv')
curr_dir = os.getcwd()
A_dir = 'C'
A_files = get_files(A_dir)
os.chdir(curr_dir + '/C')
rename_catalog(A_files)





