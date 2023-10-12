rename_drawings на вход получает папку, в которой лежат отсканированные чертежи.
Программа автоматически читает со скана обозначение и наименование чертежа и вместо SCAN0001.pdf переименовывает в "Обозначение чертежа" - "Наименование чертежа".pdf

Используемые библиотеки: Pandas, os, pytesseract, pdf2image, PIL, регулярные выражения

![Пример](https://github.com/glebzadorozhnyi/rename_drawings/blob/master/%D0%9F%D1%80%D0%B8%D0%BC%D0%B5%D1%80.jpg?raw=true)
