import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import simpledialog
import os

# Создание базы данных
def init_db():
    conn = sqlite3.connect('cargo_tracking.db')
    cursor = conn.cursor()
    
    # Создание таблицы для учета перевозок
    # Создание таблицы для учета отправителей
    cursor.execute('''CREATE TABLE IF NOT EXISTS senders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sender_type TEXT,
                        name TEXT,
                        additional_info TEXT
                      )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS shipments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        train_number TEXT,
                        locomotive_type TEXT,
                        cargo_type TEXT,
                        wagon_type TEXT,
                        weight REAL,
                        departure_date TEXT,
                        arrival_date TEXT,
                        departure_point TEXT,
                        destination_point TEXT,
                        sender_type TEXT,
                        sender_info TEXT,
                        receiver_type TEXT,
                        receiver_info TEXT,
                        status TEXT
                      )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS receivers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        receiver_type TEXT,
                        name TEXT,
                        additional_info TEXT
                      )''')
    
    conn.commit()
    conn.close()

# Добавление новой перевозки
def add_shipment(train_number, locomotive_type, cargo_type, wagon_type, weight, departure_date, arrival_date, departure_point, destination_point, sender_type, sender_info, receiver_type, receiver_info, status):
    conn = sqlite3.connect('cargo_tracking.db')
    cursor = conn.cursor()
    
    cursor.execute('''INSERT INTO shipments (train_number, locomotive_type, cargo_type, wagon_type, weight,
                    departure_date, arrival_date, departure_point, destination_point,
                    sender_type, sender_info, receiver_type, receiver_info, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (train_number, locomotive_type, cargo_type, wagon_type, weight,
                    departure_date, arrival_date, departure_point, destination_point,
                    sender_type, sender_info, receiver_type, receiver_info, status))
    
    conn.commit()
    conn.close()

# Получение всех отправителей
def get_all_senders():
    conn = sqlite3.connect('cargo_tracking.db')
    cursor = conn.cursor()

    cursor.execute('SELECT name FROM senders')
    rows = cursor.fetchall()

    conn.close()
    return [row[0] for row in rows]

# Получение всех получателей
def get_all_receivers():
    conn = sqlite3.connect('cargo_tracking.db')
    cursor = conn.cursor()

    cursor.execute('SELECT name FROM receivers')
    rows = cursor.fetchall()

    conn.close()
    return [row[0] for row in rows]

# Получение всех перевозок
def get_all_shipments():
    conn = sqlite3.connect('cargo_tracking.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM shipments')
    rows = cursor.fetchall()
    
    conn.close()
    return rows

# Обновление данных о перевозке
def update_shipment(shipment_id, **kwargs):
    conn = sqlite3.connect('cargo_tracking.db')
    cursor = conn.cursor()
    
    update_query = "UPDATE shipments SET " + ", ".join([f"{key} = ?" for key in kwargs.keys()]) + " WHERE id = ?"
    values = list(kwargs.values()) + [shipment_id]
    
    cursor.execute(update_query, values)
    
    conn.commit()
    conn.close()

# Формирование отчета по выполненным перевозкам
def generate_report():
    conn = sqlite3.connect('cargo_tracking.db')
    cursor = conn.cursor()
    
    cursor.execute('''SELECT departure_point, destination_point, COUNT(*) as train_count, SUM(weight) as total_weight
                      FROM shipments WHERE status = "завершен"
                      GROUP BY departure_point, destination_point''')
    rows = cursor.fetchall()
    
    conn.close()
    return rows

# Функция для отображения формы добавления новой перевозки
def show_add_form():
    form_window = tk.Toplevel()
    form_window.title("Добавить новую перевозку")
    form_window.update_idletasks()
    form_window.geometry(f"{form_window.winfo_reqwidth()}x{form_window.winfo_reqheight()}+{form_window.winfo_screenwidth() // 2 - form_window.winfo_reqwidth() // 2}+{form_window.winfo_screenheight() // 2 - form_window.winfo_reqheight() // 2}")
    form_window.resizable(True, True)  # Делаем окно изменяемым
    form_window.geometry('')  # Убираем фиксированное разрешение

    left_frame = ttk.Frame(form_window, style="Custom.TFrame")
    left_frame.grid(row=0, column=0, padx=20, pady=20, sticky='n')

    right_frame = ttk.Frame(form_window, style="Custom.TFrame")
    right_frame.grid(row=0, column=1, padx=20, pady=20, sticky='n')

    # Левые поля формы
    left_fields = [
        ("Номер поезда", tk.Entry(left_frame)),
        ("Тип локомотива", ttk.Combobox(left_frame, values=["Электровоз", "Тепловоз", "Паровоз"])),
        ("Тип груза", ttk.Combobox(left_frame, values=["Твердый", "Жидкий", "Газовый", "Сыпучий"])),
        ("Тип вагона", ttk.Combobox(left_frame, values=["Полувагон", "Цистерна", "Крытый вагон"])),
        ("Вес груза", tk.Entry(left_frame)),
        ("Отправитель", ttk.Combobox(left_frame, values=get_all_senders())),
    ]
    
    # Правые поля формы
    right_fields = [
        ("Дата отправления", tk.Entry(right_frame, validate='key', validatecommand=(form_window.register(lambda P: len(P) <= 10 and (P == '' or P.replace('.', '').isdigit() or P[-1] == '.')), '%P'))),
        ("Дата прибытия", tk.Entry(right_frame, validate='key', validatecommand=(form_window.register(lambda P: len(P) <= 10 and (P == '' or P.replace('.', '').isdigit() or P[-1] == '.')), '%P'))),
        ("Пункт отправления", tk.Entry(right_frame)),
        ("Пункт прибытия", tk.Entry(right_frame)),
        ("Доп. информация", tk.Entry(right_frame)),
        ("Получатель", ttk.Combobox(right_frame, values=get_all_receivers())),
    ]

    for idx, (label_text, widget) in enumerate(left_fields):
        label = tk.Label(left_frame, text=label_text, font=("Arial", 12, "bold"), foreground="#003366")
        label.grid(row=idx, column=0, padx=10, pady=5, sticky='e')
        widget.grid(row=idx, column=1, padx=10, pady=5, sticky='w', ipadx=5)

    for idx, (label_text, widget) in enumerate(right_fields):
        label = tk.Label(right_frame, text=label_text, font=("Arial", 12, "bold"), foreground="#003366")
        label.grid(row=idx, column=0, padx=10, pady=5, sticky='e')
        widget.grid(row=idx, column=1, padx=10, pady=5, sticky='w')

    # Кнопки управления
    def save_data():
        try:
            train_number = left_fields[0][1].get()
            locomotive_type = left_fields[1][1].get()
            cargo_type = left_fields[2][1].get()
            weight = float(left_fields[4][1].get())
            wagon_type = left_fields[3][1].get()
            sender_combobox = left_fields[5][1]
            sender_combobox['values'] = get_all_senders()
            sender = sender_combobox.get()
            departure_date = right_fields[0][1].get().strip()
            if not departure_date:
                raise ValueError('Дата отправления не может быть пустой')
            arrival_date = right_fields[1][1].get().strip()
            if not arrival_date:
                raise ValueError('Дата прибытия не может быть пустой')
            departure_point = right_fields[2][1].get()
            destination_point = right_fields[3][1].get()
            sender_info = ""
            receiver = right_fields[5][1].get()
            status = "запланирована"

            add_shipment(train_number, locomotive_type, cargo_type, wagon_type, weight,
                         departure_date, arrival_date, departure_point, destination_point,
                         sender, sender_info, receiver, "", status)

            messagebox.showinfo("Успех", "Запись успешно сохранена")
            form_window.destroy()
            update_main_table()
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные данные, проверьте поля")

    button_frame = ttk.Frame(form_window, style="Custom.TFrame")
    button_frame.grid(row=1, column=0, columnspan=2, pady=20)

    cancel_button = ttk.Button(button_frame, text="Отменить", command=form_window.destroy)
    cancel_button.grid(row=0, column=0, padx=10)

    save_button = ttk.Button(button_frame, text="Сохранить", command=save_data)
    save_button.grid(row=0, column=1, padx=10)

# Функция для отображения формы добавления отправителя
def show_sender_form():
    sender_window = tk.Toplevel()
    sender_window.title("Данные об отправителе")
    sender_window.resizable(False, False)
    sender_window.geometry('400x500')  # Устанавливаем начальный размер окна

    label_title = tk.Label(sender_window, text="Данные об отправителе", font=("Arial", 14, "bold"), pady=10)
    label_title.grid(row=0, column=0, columnspan=2, sticky='n')

    sender_type = ttk.Combobox(sender_window, values=["Физическое лицо", "Юридическое лицо"], state='readonly')
    sender_type.current(0)  # По умолчанию выбираем физическое лицо
    sender_type.bind("<<ComboboxSelected>>", lambda e: update_sender_form(sender_window, sender_type))
    sender_type.grid(row=1, column=1, padx=10, pady=5, sticky='w')

    left_fields = [
        ("Тип отправителя", sender_type),
    ]

    for idx, (label_text, widget) in enumerate(left_fields, start=1):
        label = tk.Label(sender_window, text=label_text, font=("Arial", 12, "bold"))
        label.grid(row=idx, column=0, padx=10, pady=5, sticky='e')
        widget.grid(row=idx, column=1, padx=10, pady=5, sticky='w')

    # Функция для обновления формы отправителя при выборе типа
    def update_sender_form(window, sender_type_combobox):
        # Удаляем все виджеты, начиная со второго ряда
        for widget in window.grid_slaves():
            if int(widget.grid_info()["row"]) > 1:
                widget.grid_forget()

        # Определяем, какие поля будут отображаться в зависимости от типа отправителя
        if sender_type_combobox.get() == "Физическое лицо":
            fields = [
                ("Фамилия", tk.Entry(window)),
                ("Имя", tk.Entry(window)),
                ("Отчество", tk.Entry(window)),
                ("Номер телефона", tk.Entry(window)),
                ("Паспорт", tk.Entry(window)),
                ("Прочая информация", tk.Entry(window)),
            ]
        else:
            fields = [
                ("Название организации", tk.Entry(window)),
                ("Адрес регистрации", tk.Entry(window)),
                ("ИНН", tk.Entry(window)),
                ("ФИО Представителя", tk.Entry(window)),
                ("Контактный номер", tk.Entry(window)),
                ("Прочая информация", tk.Entry(window)),
            ]

        # Отображаем обновленные поля
        for idx, (label_text, widget) in enumerate(fields, start=2):
            label = tk.Label(window, text=label_text, font=("Arial", 12, "bold"))
            label.grid(row=idx, column=0, padx=10, pady=5, sticky='e')
            widget.grid(row=idx, column=1, padx=10, pady=5, sticky='w')

        # Кнопки управления
        button_frame = ttk.Frame(window)
        button_frame.grid(row=len(fields) + 2, column=0, columnspan=2, pady=20)

        cancel_button = ttk.Button(button_frame, text="Отменить", command=window.destroy)
        cancel_button.grid(row=0, column=0, padx=10)

        save_button = ttk.Button(button_frame, text="Сохранить", command=lambda: save_sender(window, sender_type))
        save_button.grid(row=0, column=1, padx=10)

# Функция для отображения формы добавления получателя
def show_receiver_form():
    receiver_window = tk.Toplevel()
    receiver_window.title("Данные о получателе")
    receiver_window.resizable(False, False)
    receiver_window.geometry('400x500')  # Устанавливаем начальный размер окна

    label_title = tk.Label(receiver_window, text="Данные о получателе", font=("Arial", 14, "bold"), pady=10)
    label_title.grid(row=0, column=0, columnspan=2, sticky='n')

    receiver_type = ttk.Combobox(receiver_window, values=["Физическое лицо", "Юридическое лицо"], state='readonly')
    receiver_type.current(0)  # По умолчанию выбираем физическое лицо
    receiver_type.bind("<<ComboboxSelected>>", lambda e: update_receiver_form(receiver_window, receiver_type))
    receiver_type.grid(row=1, column=1, padx=10, pady=5, sticky='w')

    left_fields = [
        ("Тип получателя", receiver_type),
    ]

    for idx, (label_text, widget) in enumerate(left_fields, start=1):
        label = tk.Label(receiver_window, text=label_text, font=("Arial", 12, "bold"))
        label.grid(row=idx, column=0, padx=10, pady=5, sticky='e')
        widget.grid(row=idx, column=1, padx=10, pady=5, sticky='w')

    # Функция для обновления формы получателя при выборе типа
    def update_receiver_form(window, receiver_type_combobox):
        # Удаляем все виджеты, начиная со второго ряда
        for widget in window.grid_slaves():
            if int(widget.grid_info()["row"]) > 1:
                widget.grid_forget()

        # Определяем, какие поля будут отображаться в зависимости от типа получателя
        if receiver_type_combobox.get() == "Физическое лицо":
            fields = [
                ("Фамилия", tk.Entry(window)),
                ("Имя", tk.Entry(window)),
                ("Отчество", tk.Entry(window)),
                ("Номер телефона", tk.Entry(window)),
                ("Паспорт", tk.Entry(window)),
                ("Прочая информация", tk.Entry(window)),
            ]
        else:
            fields = [
                ("Название организации", tk.Entry(window)),
                ("Адрес регистрации", tk.Entry(window)),
                ("ИНН", tk.Entry(window)),
                ("ФИО Представителя", tk.Entry(window)),
                ("Контактный номер", tk.Entry(window)),
                ("Прочая информация", tk.Entry(window)),
            ]

        # Отображаем обновленные поля
        for idx, (label_text, widget) in enumerate(fields, start=2):
            label = tk.Label(window, text=label_text, font=("Arial", 12, "bold"))
            label.grid(row=idx, column=0, padx=10, pady=5, sticky='e')
            widget.grid(row=idx, column=1, padx=10, pady=5, sticky='w')

        # Кнопки управления
        button_frame = ttk.Frame(window)
        button_frame.grid(row=len(fields) + 2, column=0, columnspan=2, pady=20)

        cancel_button = ttk.Button(button_frame, text="Отменить", command=window.destroy)
        cancel_button.grid(row=0, column=0, padx=10)

        save_button = ttk.Button(button_frame, text="Сохранить", command=lambda: save_receiver(window, receiver_type))
        save_button.grid(row=0, column=1, padx=10)

# Функция для сохранения отправителя в базу данных
def save_sender(window, sender_type_combobox):
    conn = sqlite3.connect('cargo_tracking.db')
    cursor = conn.cursor()

    sender_type = sender_type_combobox.get()
    if sender_type == "Физическое лицо":
        name = f"{window.grid_slaves(row=3, column=1)[0].get()} {window.grid_slaves(row=2, column=1)[0].get()} {window.grid_slaves(row=1, column=1)[0].get()}"
        additional_info = window.grid_slaves(row=5, column=1)[0].get()  # Паспорт
    else:
        name = window.grid_slaves(row=2, column=1)[0].get()  # Название организации
        additional_info = window.grid_slaves(row=4, column=1)[0].get()  # ИНН

    cursor.execute('''INSERT INTO senders (sender_type, name, additional_info) VALUES (?, ?, ?)''',
                   (sender_type, name, additional_info))

    conn.commit()
    conn.close()
    messagebox.showinfo("Успех", "Данные отправителя успешно сохранены")
    window.destroy()

# Функция для сохранения получателя в базу данных
def save_receiver(window, receiver_type_combobox):
    conn = sqlite3.connect('cargo_tracking.db')
    cursor = conn.cursor()

    receiver_type = receiver_type_combobox.get()
    if receiver_type == "Физическое лицо":
        name = f"{window.grid_slaves(row=3, column=1)[0].get()} {window.grid_slaves(row=2, column=1)[0].get()} {window.grid_slaves(row=1, column=1)[0].get()}"
        additional_info = window.grid_slaves(row=5, column=1)[0].get()  # Паспорт
    else:
        name = window.grid_slaves(row=2, column=1)[0].get()  # Название организации
        additional_info = window.grid_slaves(row=4, column=1)[0].get()  # ИНН

    cursor.execute('''INSERT INTO receivers (receiver_type, name, additional_info) VALUES (?, ?, ?)''',
                   (receiver_type, name, additional_info))

    conn.commit()
    conn.close()
    messagebox.showinfo("Успех", "Данные получателя успешно сохранены")
    window.destroy()

# Функция для отображения помощи
def show_help():
    try:
        with open('assets/answer.txt', 'r', encoding='utf-8') as file:
            help_text = file.read()
        help_window = tk.Toplevel()
        help_window.title("Помощь")
        help_window.geometry("800x600")  # Увеличенный размер окна для удобного чтения
        help_window.resizable(False, False)  # Запрет на изменение размера окна

        text = tk.Text(help_window, wrap='word', font=("Arial", 14), padx=15, pady=15, bg="#f0f0f0")
        text.insert('1.0', help_text)
        text.configure(state='disabled')  # Запрет на редактирование текста
        text.pack(expand=True, fill='both', padx=10, pady=10)

        # Кнопка закрытия
        close_button = ttk.Button(help_window, text="Закрыть", command=help_window.destroy)
        close_button.pack(side=tk.BOTTOM, pady=10)

    except FileNotFoundError:
        messagebox.showerror("Ошибка", "Файл помощи не найден.")

# Создание главного окна приложения
def create_main_window():
    # Добавление тестового отправителя
    conn = sqlite3.connect('cargo_tracking.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO senders (sender_type, name, additional_info) VALUES ('Физическое лицо', 'Иван Иванов', 'Паспорт: 1234567890')")
    cursor.execute("INSERT OR IGNORE INTO receivers (receiver_type, name, additional_info) VALUES ('Физическое лицо', 'Петр Петров', 'Паспорт: 0987654321')")
    conn.commit()
    conn.close()
    global root, table_frame
    root = tk.Tk()
    root.title("Система учета перевозки грузов")
    root.state('zoomed')  # Установлено разрешение 16:9
    root.configure(bg="#f8f9fa")

    style = ttk.Style()
    style.configure("TButton", font=("Arial", 16), padding=15)
    
    style.configure("TFrame", background="#f8f9fa")

    # Верхние кнопки управления
    top_frame = ttk.Frame(root)
    top_frame.pack(side=tk.TOP, fill=tk.BOTH, pady=10)

    button_width = 20  # Оптимизированная ширина кнопок для гармоничного внешнего вида

    logo_image = tk.PhotoImage(file='assets/logo.png').subsample(8, 8)  # Оптимальное уменьшение размера логотипа
    logo_label = tk.Label(top_frame, image=logo_image, background="#f8f9fa")
    logo_label.image = logo_image  # Сохранение ссылки на изображение
    logo_label.pack(side=tk.LEFT, anchor='nw', padx=10, pady=10)

    orders_button = ttk.Button(top_frame, text="Заказы", width=button_width, command=update_main_table)
    orders_button.pack(side=tk.LEFT, padx=10)

    sender_button = ttk.Button(top_frame, text="Отправители", width=button_width, command=show_sender_form)
    sender_button.pack(side=tk.LEFT, padx=10)

    receiver_button = ttk.Button(top_frame, text="Получатели", width=button_width, command=show_receiver_form)
    receiver_button.pack(side=tk.LEFT, padx=10)

    save_button = ttk.Button(top_frame, text="Записать", width=button_width, command=show_add_form)
    save_button.pack(side=tk.RIGHT, padx=10)

    # Таблица перевозок
    table_frame = ttk.Frame(root)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Нижние кнопки управления
    bottom_frame = ttk.Frame(root)
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

    help_button = ttk.Button(bottom_frame, text="Помощь", width=button_width, command=show_help)
    help_button.pack(side=tk.LEFT, padx=10)

    report_button = ttk.Button(bottom_frame, text="Отчеты", width=button_width, command=lambda: messagebox.showinfo("Инфо", "Функция формирования отчета пока не реализована"))
    report_button.pack(side=tk.RIGHT, padx=10)

    update_main_table()
    root.mainloop()

# Обновление главной таблицы с перевозками
def update_main_table():
    for widget in table_frame.winfo_children():
        widget.destroy()

    shipments = get_all_shipments()

    headers = ["ID", "Номер поезда", "Тип локомотива", "Тип груза", "Вес груза", "Тип вагона", "Дата отправления", "Дата прибытия", "Пункт отправления", "Пункт прибытия", "Тип отправителя", "Отправитель", "Тип получателя", "Получатель", "Статус"]
    for col, header in enumerate(headers):
        label = tk.Label(table_frame, text=header, font=("Arial", 12, "bold"), borderwidth=1, relief="solid", padx=5, pady=5, background="#f1f3f5")
        label.grid(row=0, column=col, sticky="nsew", ipadx=5, ipady=5, padx=2)

    for row_idx, shipment in enumerate(shipments, start=1):
        # Исправляем порядок значений в строке таблицы
        corrected_shipment = (
            shipment[0],  # ID
            shipment[1],  # Номер поезда
            shipment[4],  # Тип локомотива
            shipment[2],  # Тип груза
            shipment[5],  # Вес груза
            shipment[3],  # Тип вагона
            shipment[6],  # Дата отправления
            shipment[7],  # Дата прибытия
            shipment[8],  # Пункт отправления
            shipment[9],  # Пункт прибытия
            shipment[10], # Тип отправителя
            shipment[11], # Отправитель
            shipment[12], # Тип получателя
            shipment[13], # Получатель
            shipment[14], # Статус
        )
        for col_idx, value in enumerate(corrected_shipment):
            label = tk.Label(table_frame, text=value, font=("Arial", 10), borderwidth=1, relief="solid", padx=5, pady=5, background="#ffffff")
            label.grid(row=row_idx, column=col_idx, sticky="nsew", ipadx=5, ipady=5, padx=2)

        # Добавление кнопки редактирования для каждой записи
        current_dir = os.path.dirname(os.path.abspath(__file__))
        edit_icon_path = os.path.join(current_dir, 'assets', 'redakt.png')
        edit_icon = tk.PhotoImage(file=edit_icon_path).subsample(25, 25)  # Оптимальное уменьшение размера иконки для гармоничного вида
        edit_button = tk.Button(table_frame, image=edit_icon, borderwidth=0, background="#f8f9fa", command=lambda shipment_id=shipment[0]: show_edit_form(shipment_id))
        edit_button.image = edit_icon  # Сохранение ссылки на изображение
        edit_button.grid(row=row_idx, column=len(corrected_shipment), padx=5, pady=5, sticky='nsew')

# Функция для отображения формы редактирования перевозки
def show_edit_form(shipment_id):
    shipment = next((s for s in get_all_shipments() if s[0] == shipment_id), None)
    if not shipment:
        messagebox.showerror("Ошибка", "Запись не найдена")
        return

    form_window = tk.Toplevel()
    form_window.title("Редактировать перевозку")
    form_window.geometry('800x600')  # Задаем размер окна
    form_window.resizable(False, False)

    left_frame = ttk.Frame(form_window, style="Custom.TFrame")
    left_frame.grid(row=0, column=0, padx=20, pady=20, sticky='n')

    right_frame = ttk.Frame(form_window, style="Custom.TFrame")
    right_frame.grid(row=0, column=1, padx=20, pady=20, sticky='n')

    # Левые поля формы
    left_fields = [
        ("Номер поезда", tk.Entry(left_frame)),
        ("Тип локомотива", ttk.Combobox(left_frame, values=["Электровоз", "Тепловоз", "Паровоз"])),
        ("Тип груза", ttk.Combobox(left_frame, values=["Твердый", "Жидкий", "Газовый", "Сыпучий"])),
        ("Тип вагона", ttk.Combobox(left_frame, values=["Полувагон", "Цистерна", "Крытый вагон"])),
        ("Вес груза", tk.Entry(left_frame)),
        ("Отправитель", ttk.Combobox(left_frame, values=get_all_senders())),
    ]
    
    # Правые поля формы
    right_fields = [
        ("Дата отправления", tk.Entry(right_frame)),
        ("Дата прибытия", tk.Entry(right_frame)),
        ("Пункт отправления", tk.Entry(right_frame)),
        ("Пункт прибытия", tk.Entry(right_frame)),
        ("Доп. информация", tk.Entry(right_frame)),
        ("Получатель", ttk.Combobox(right_frame, values=get_all_receivers())),
        ("Изменение статуса", ttk.Combobox(right_frame, values=["в процессе", "завершен", "отменен"])),
    ]

    # Установка текущих значений
    left_fields[0][1].insert(0, shipment[1])
    left_fields[1][1].set(shipment[4])
    left_fields[2][1].set(shipment[2])
    left_fields[3][1].set(shipment[3])
    left_fields[4][1].insert(0, shipment[5])
    left_fields[5][1].set(shipment[11])

    right_fields[0][1].insert(0, shipment[6])
    right_fields[1][1].insert(0, shipment[7])
    right_fields[2][1].insert(0, shipment[8])
    right_fields[3][1].insert(0, shipment[9])
    right_fields[4][1].insert(0, shipment[13])
    right_fields[5][1].set(shipment[13])
    right_fields[6][1].set(shipment[14])

    for idx, (label_text, widget) in enumerate(left_fields):
        label = tk.Label(left_frame, text=label_text, font=("Arial", 12, "bold"), foreground="#003366")
        label.grid(row=idx, column=0, padx=10, pady=5, sticky='e')
        widget.grid(row=idx, column=1, padx=10, pady=5, sticky='w', ipadx=5)

    for idx, (label_text, widget) in enumerate(right_fields):
        label = tk.Label(right_frame, text=label_text, font=("Arial", 12, "bold"), foreground="#003366")
        label.grid(row=idx, column=0, padx=10, pady=5, sticky='e')
        widget.grid(row=idx, column=1, padx=10, pady=5, sticky='w')

    # Кнопки управления
    def save_data():
        try:
            updated_data = {
                "train_number": left_fields[0][1].get(),
                "locomotive_type": left_fields[1][1].get(),
                "cargo_type": left_fields[2][1].get(),
                "wagon_type": left_fields[3][1].get(),
                "weight": float(left_fields[4][1].get()),
                "departure_date": right_fields[0][1].get(),
                "arrival_date": right_fields[1][1].get(),
                "departure_point": right_fields[2][1].get(),
                "destination_point": right_fields[3][1].get(),
                "receiver_info": right_fields[4][1].get(),
                "receiver_type": right_fields[5][1].get(),
                "status": right_fields[6][1].get(),
            }

            update_shipment(shipment_id, **updated_data)
            messagebox.showinfo("Успех", "Запись успешно обновлена")
            form_window.destroy()
            update_main_table()
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные данные, проверьте поля")

    button_frame = ttk.Frame(form_window, style="Custom.TFrame")
    button_frame.grid(row=1, column=0, columnspan=2, pady=20)

    cancel_button = ttk.Button(button_frame, text="Отменить", command=form_window.destroy)
    cancel_button.grid(row=0, column=0, padx=10)

    save_button = ttk.Button(button_frame, text="Сохранить", command=save_data)
    save_button.grid(row=0, column=1, padx=10)

if __name__ == "__main__":
    init_db()
    create_main_window()
