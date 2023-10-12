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
    if width > height:
        scope = 'A3'
    else:
        scope = 'A4'

    if scope == 'A3':
        pakb = image.crop((width * 0.73, height * 0.78, width * 0.94, height * 0.86))
        label = image.crop((width * 0.71, height * 0.85, width * 0.85, height * 0.94))
        #pakb = image.crop((width - 1000, height - 600, width - 100, height * 0.99))
        #label = image.crop((width - 1000, height - 500, width - 450, height - 150)) #Параметры для А1 и А2
    if scope == 'A4':
        #pakb = image.crop((width * 0.4, height * 0.77, width * 0.85, height * 0.85))
        pakb = image.crop((width * 0.4, height * 0.8, width * 0.85, height * 0.9))
        label = image.crop((width * 0.41, height * 0.84, width * 0.74, height * 0.935))
    #pakb = pakb.rotate(1.5)
    if transform:
        width, height = pakb.size
        m = -0.2
        xshift = abs(m) * width
        new_width = width + int(round(xshift))
        pakb = pakb.transform((new_width, height), Image.AFFINE,
                            (1, m, -xshift if m > 0 else 0, 0, 1, 0), Image.BICUBIC)
    pakb.save(file_name + '.jpeg')
    label.save(file_name + '0.jpeg')
    fake_label = pytesseract.image_to_string(label, lang='rus').strip()
    fake_label = fake_label.replace('\n', ' ')
    fake_label = re.sub('[^а-яА-Я ]', '', fake_label).strip()
    return pytesseract.image_to_string(pakb, config='digits').strip(), fake_label


def get_pakb(string, fake_label):
    pattern = '[\d]{6}[\.]{0,1}[\d]{3}'
    pakb = re.findall(pattern, string)
    if pakb == []:
        return False
    else:
        pakb = pakb[0]
    if len(pakb) == 9:
        pakb = pakb[0:6] + '.' + pakb[6:]
    label = add_label(pakb, data)
    pakb = 'ПАКБ.' + pakb + ' - '
    if label == '':
        label = fake_label
        pakb = '@' + pakb
    return pakb + label


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
    data = data.query('Имя.str.lower().str.contains("пакб")').reset_index(drop=True)
    data['Имя'] = data['Имя'].str.strip()
    # сплитуем Имя на Наименование и Обозначение
    rows = data.loc[data['Имя'].str.contains(' - ')].index
    data[['Обозначение', 'Наименование']] = data.loc[rows, 'Имя'].str.split(pat=' - ', n=1, expand=True)
    # если Наименование пусто, то Имя идёт в Наименование
    data.loc[data['Наименование'].isna(), 'Наименование'] = data['Имя']
    data = data.fillna('')
    data = data.drop(columns='Имя')
    # помечаем элементы, которые начинаются не на ПАКБ или имеют слишком длинное имя.
    data.loc[data.eval(
        '~Обозначение.str.lower().str.contains("^пакб[\. ]{0,2}\d{6}[\. ]{0,2}\d{3}.{0,4}$")'), 'bez_pakb'] = True
    data['bez_pakb'] = data['bez_pakb'].fillna(False)
    data = data[data['bez_pakb'] == False]

    return data[['Наименование', 'Обозначение']]

def add_label(pakb, df):
    pakb = 'ПАКБ.' + pakb
    df = df[df['Обозначение'] == pakb]
    if len(df) > 0:
        df = df['Наименование'].value_counts()
        anwser = df.index[0]
        anwser = re.sub('[^а-яА-ЯёЁ\d ]', '', anwser)
        return anwser
    else:
        return ''


data = read_csv_in('all.csv')
curr_dir = os.getcwd()
A_dir = 'а3'
A_files = get_files(A_dir)
os.chdir(curr_dir + '/а3')
rename_catalog(A_files)





