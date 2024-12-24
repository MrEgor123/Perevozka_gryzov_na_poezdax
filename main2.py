import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import simpledialog
import os
from tkcalendar import DateEntry

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
def generate_report(departure_point=None, destination_point=None, cargo_type=None):
    conn = sqlite3.connect('cargo_tracking.db')
    cursor = conn.cursor()

    query = '''
        SELECT departure_point, destination_point, COUNT(*) as train_count, SUM(weight) as total_weight
        FROM shipments
        WHERE 1=1
    '''
    params = []

    # Добавляем фильтры в запрос
    if departure_point:
        query += " AND TRIM(LOWER(departure_point)) = TRIM(LOWER(?))"
        params.append(departure_point.strip())
    if destination_point:
        query += " AND TRIM(LOWER(destination_point)) = TRIM(LOWER(?))"
        params.append(destination_point.strip())
    if cargo_type:
        query += " AND TRIM(LOWER(cargo_type)) = TRIM(LOWER(?))"
        params.append(cargo_type.strip())

    query += " GROUP BY departure_point, destination_point"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return rows



def get_senders_by_type(sender_type):
    conn = sqlite3.connect('cargo_tracking.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT name FROM senders WHERE sender_type = ?', (sender_type,))
    rows = cursor.fetchall()
    
    conn.close()
    return [row[0] for row in rows]

# Получение всех получателей по типу
def get_receivers_by_type(receiver_type):
    conn = sqlite3.connect('cargo_tracking.db')
    cursor = conn.cursor()

    cursor.execute('SELECT name FROM receivers WHERE receiver_type = ?', (receiver_type,))
    rows = cursor.fetchall()

    conn.close()
    return [row[0] for row in rows]

# Функция для отображения формы добавления новой перевозки
def show_add_form():
    form_window = tk.Toplevel()
    form_window.title("Добавить новую перевозку")

    # Увеличенный размер окна по умолчанию
    form_window.geometry("800x400")
    form_window.resizable(True, True)

    left_frame = ttk.Frame(form_window)
    left_frame.grid(row=0, column=0, padx=20, pady=20, sticky='n')

    right_frame = ttk.Frame(form_window)
    right_frame.grid(row=0, column=1, padx=20, pady=20, sticky='n')

    # Левые поля формы
    left_fields = [
        ("Номер поезда", tk.Entry(left_frame)),
        ("Тип локомотива", ttk.Combobox(left_frame, values=["Электровоз", "Тепловоз", "Паровоз"])),
        ("Тип груза", ttk.Combobox(left_frame, values=["Твердый", "Жидкий", "Газовый", "Сыпучий"])),
        ("Тип вагона", ttk.Combobox(left_frame, values=["Полувагон", "Цистерна", "Крытый вагон"])),
        ("Вес груза", tk.Entry(left_frame)),
        ("Тип отправителя", ttk.Combobox(left_frame, values=["Физическое лицо", "Юридическое лицо"])),
        ("Отправитель", ttk.Combobox(left_frame, values=[])),
    ]

    # Правые поля формы
    right_fields = [
        ("Дата отправления", DateEntry(right_frame, date_pattern='yyyy-mm-dd')),  # Используем DateEntry для календаря
        ("Дата прибытия", DateEntry(right_frame, date_pattern='yyyy-mm-dd')),  # Используем DateEntry для календаря
        ("Пункт отправления", tk.Entry(right_frame)),
        ("Пункт прибытия", tk.Entry(right_frame)),
        ("Тип получателя", ttk.Combobox(right_frame, values=["Физическое лицо", "Юридическое лицо"])),
        ("Получатель", ttk.Combobox(right_frame, values=[])),
        ("Доп. информация", tk.Entry(right_frame)),
    ]

    for idx, (label_text, widget) in enumerate(left_fields):
        label = tk.Label(left_frame, text=label_text, font=("Arial", 12, "bold"), foreground="#003366")
        label.grid(row=idx, column=0, padx=10, pady=5, sticky='e')
        widget.grid(row=idx, column=1, padx=10, pady=5, sticky='w', ipadx=5)

    for idx, (label_text, widget) in enumerate(right_fields):
        label = tk.Label(right_frame, text=label_text, font=("Arial", 12, "bold"), foreground="#003366")
        label.grid(row=idx, column=0, padx=10, pady=5, sticky='e')
        widget.grid(row=idx, column=1, padx=10, pady=5, sticky='w')

    # Функция для обновления списка отправителей в зависимости от типа
    def update_sender_list():
        selected_type = left_fields[5][1].get()  # Тип отправителя
        if selected_type:
            senders = get_senders_by_type(selected_type)
            left_fields[6][1]['values'] = senders
        else:
            left_fields[6][1]['values'] = []

    # Функция для обновления списка получателей в зависимости от типа
    def update_receiver_list():
        selected_type = right_fields[4][1].get()  # Тип получателя
        if selected_type:
            receivers = get_receivers_by_type(selected_type)
            right_fields[5][1]['values'] = receivers
        else:
            right_fields[5][1]['values'] = []

    # Привязка события изменения типа отправителя/получателя
    left_fields[5][1].bind("<<ComboboxSelected>>", lambda e: update_sender_list())
    right_fields[4][1].bind("<<ComboboxSelected>>", lambda e: update_receiver_list())

    # Кнопки управления
    def save_data():
        try:
            train_number = left_fields[0][1].get()
            locomotive_type = left_fields[1][1].get()
            cargo_type = left_fields[2][1].get()
            wagon_type = left_fields[3][1].get()
            weight = float(left_fields[4][1].get())
            sender_type = left_fields[5][1].get()
            sender_info = left_fields[6][1].get()
            departure_date = right_fields[0][1].get_date()  # Получаем дату из виджета DateEntry
            arrival_date = right_fields[1][1].get_date()  # Получаем дату из виджета DateEntry
            departure_point = right_fields[2][1].get()
            destination_point = right_fields[3][1].get()
            receiver_type = right_fields[4][1].get()
            receiver_info = right_fields[5][1].get()
            status = "запланирована"

            add_shipment(train_number, locomotive_type, cargo_type, wagon_type, weight,
                         departure_date, arrival_date, departure_point, destination_point,
                         sender_type, sender_info, receiver_type, receiver_info, status)

            messagebox.showinfo("Успех", "Запись успешно сохранена")
            form_window.destroy()
            update_main_table()
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные данные, проверьте поля")

    button_frame = ttk.Frame(form_window)
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
    sender_type.grid(row=1, column=1, padx=10, pady=5, sticky='w')

    label_sender_type = tk.Label(sender_window, text="Тип отправителя", font=("Arial", 12, "bold"))
    label_sender_type.grid(row=1, column=0, padx=10, pady=5, sticky='e')

    # Поля для физического лица
    individual_fields = [
        ("Фамилия", tk.Entry(sender_window)),
        ("Имя", tk.Entry(sender_window)),
        ("Отчество", tk.Entry(sender_window)),
        ("Номер телефона", tk.Entry(sender_window)),
        ("Паспорт", tk.Entry(sender_window)),
        ("Прочая информация", tk.Entry(sender_window)),
    ]

    # Поля для юридического лица
    legal_fields = [
        ("Название организации", tk.Entry(sender_window)),
        ("Адрес регистрации", tk.Entry(sender_window)),
        ("ИНН", tk.Entry(sender_window)),
        ("ФИО Представителя", tk.Entry(sender_window)),
        ("Контактный номер", tk.Entry(sender_window)),
        ("Прочая информация", tk.Entry(sender_window)),
    ]

    # Функция для обновления видимости полей
    def update_sender_form():
        if sender_type.get() == "Физическое лицо":
            fields = individual_fields
        else:
            fields = legal_fields

        # Скрываем все поля
        for widget in sender_window.grid_slaves():
            if int(widget.grid_info()["row"]) > 1:
                widget.grid_forget()

        # Отображаем обновленные поля
        for idx, (label_text, widget) in enumerate(fields, start=2):
            label = tk.Label(sender_window, text=label_text, font=("Arial", 12, "bold"))
            label.grid(row=idx, column=0, padx=10, pady=5, sticky='e')
            widget.grid(row=idx, column=1, padx=10, pady=5, sticky='w')

        # Кнопки управления
        button_frame = ttk.Frame(sender_window)
        button_frame.grid(row=len(fields) + 2, column=0, columnspan=2, pady=20)

        cancel_button = ttk.Button(button_frame, text="Отменить", command=sender_window.destroy)
        cancel_button.grid(row=0, column=0, padx=10)

        save_button = ttk.Button(button_frame, text="Сохранить", command=lambda: save_sender(sender_window, sender_type))
        save_button.grid(row=0, column=1, padx=10)

    sender_type.bind("<<ComboboxSelected>>", lambda e: update_sender_form())
    update_sender_form()  # Инициализация полей при открытии окна

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
    receiver_type.grid(row=1, column=1, padx=10, pady=5, sticky='w')

    label_receiver_type = tk.Label(receiver_window, text="Тип получателя", font=("Arial", 12, "bold"))
    label_receiver_type.grid(row=1, column=0, padx=10, pady=5, sticky='e')

    # Поля для физического лица
    individual_fields = [
        ("Фамилия", tk.Entry(receiver_window)),
        ("Имя", tk.Entry(receiver_window)),
        ("Отчество", tk.Entry(receiver_window)),
        ("Номер телефона", tk.Entry(receiver_window)),
        ("Паспорт", tk.Entry(receiver_window)),
        ("Прочая информация", tk.Entry(receiver_window)),
    ]

    # Поля для юридического лица
    legal_fields = [
        ("Название организации", tk.Entry(receiver_window)),
        ("Адрес регистрации", tk.Entry(receiver_window)),
        ("ИНН", tk.Entry(receiver_window)),
        ("ФИО Представителя", tk.Entry(receiver_window)),
        ("Контактный номер", tk.Entry(receiver_window)),
        ("Прочая информация", tk.Entry(receiver_window)),
    ]

    # Функция для обновления видимости полей
    def update_receiver_form():
        if receiver_type.get() == "Физическое лицо":
            fields = individual_fields
        else:
            fields = legal_fields

        # Скрываем все поля
        for widget in receiver_window.grid_slaves():
            if int(widget.grid_info()["row"]) > 1:
                widget.grid_forget()

        # Отображаем обновленные поля
        for idx, (label_text, widget) in enumerate(fields, start=2):
            label = tk.Label(receiver_window, text=label_text, font=("Arial", 12, "bold"))
            label.grid(row=idx, column=0, padx=10, pady=5, sticky='e')
            widget.grid(row=idx, column=1, padx=10, pady=5, sticky='w')

        # Кнопки управления
        button_frame = ttk.Frame(receiver_window)
        button_frame.grid(row=len(fields) + 2, column=0, columnspan=2, pady=20)

        cancel_button = ttk.Button(button_frame, text="Отменить", command=receiver_window.destroy)
        cancel_button.grid(row=0, column=0, padx=10)

        save_button = ttk.Button(button_frame, text="Сохранить", command=lambda: save_receiver(receiver_window, receiver_type))
        save_button.grid(row=0, column=1, padx=10)

    receiver_type.bind("<<ComboboxSelected>>", lambda e: update_receiver_form())
    update_receiver_form()  # Инициализация полей при открытии окна

# Функция для сохранения отправителя в базу данных
# Функция для сохранения отправителя в базу данных
# Функция для сохранения отправителя в базу данных
def save_sender(window, sender_type_combobox):
    conn = sqlite3.connect('cargo_tracking.db')
    cursor = conn.cursor()

    sender_type = sender_type_combobox.get()
    if sender_type == "Физическое лицо":
        # Сохраняем только Фамилию и Имя
        last_name = window.grid_slaves(row=3, column=1)[0].get()
        first_name = window.grid_slaves(row=2, column=1)[0].get()
        name = f"{last_name} {first_name}"
        additional_info = window.grid_slaves(row=5, column=1)[0].get()  # Паспорт
    else:
        # Для юридического лица сохраняем только название
        name = window.grid_slaves(row=2, column=1)[0].get()  # Название организации
        additional_info = window.grid_slaves(row=4, column=1)[0].get()  # ИНН

    cursor.execute('''INSERT INTO senders (sender_type, name, additional_info) VALUES (?, ?, ?)''',
                   (sender_type, name, additional_info))

    conn.commit()
    conn.close()
    messagebox.showinfo("Успех", "Данные отправителя успешно сохранены")
    window.destroy()



# Функция для сохранения получателя в базу данных
# Функция для сохранения получателя в базу данных
# Функция для сохранения получателя в базу данных
def save_receiver(window, receiver_type_combobox):
    conn = sqlite3.connect('cargo_tracking.db')
    cursor = conn.cursor()

    receiver_type = receiver_type_combobox.get()
    if receiver_type == "Физическое лицо":
        # Сохраняем только Фамилию и Имя
        last_name = window.grid_slaves(row=3, column=1)[0].get()
        first_name = window.grid_slaves(row=2, column=1)[0].get()
        name = f"{last_name} {first_name}"
        additional_info = window.grid_slaves(row=5, column=1)[0].get()  # Паспорт
    else:
        # Для юридического лица сохраняем только название
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
# Создание главного окна приложения
# Создание главного окна приложения
# Создание главного окна приложения
def create_main_window():
    global root, table_frame, canvas, scrollbar, table_inner_frame
    root = tk.Tk()
    root.title("Система учета перевозки грузов")
    root.state('zoomed')
    root.configure(bg="#f5f5f5")

    # Настройка стиля
    style = ttk.Style()
    style.theme_use("clam")

    # Настройка стиля кнопок
    style.configure("Rounded.TButton",
                    font=("Arial", 14, "bold"),
                    padding=10,
                    foreground="#333333",
                    background="#e0e0e0",
                    relief="flat")
    style.map("Rounded.TButton",
              foreground=[("pressed", "#333333"), ("active", "#333333")],
              background=[("pressed", "!disabled", "#c0c0c0"), ("active", "#d0d0d0")])

    # Функция для создания кнопок с закругленными углами
    def create_rounded_button(parent, text, command):
        button = tk.Button(parent, text=text, command=command, font=("Arial", 14, "bold"), fg="#333333", bg="#e0e0e0",
                           relief="flat", borderwidth=1)
        button.config(highlightbackground="#e0e0e0", highlightcolor="#e0e0e0", padx=15, pady=5)
        button.config(overrelief="flat", activebackground="#d0d0d0", activeforeground="#333333")
        button.pack_propagate(False)
        return button

    # Верхняя панель управления
    top_frame = ttk.Frame(root)
    top_frame.pack(side=tk.TOP, fill=tk.BOTH, pady=15)

    # Добавление логотипа
    logo_image = tk.PhotoImage(file='assets/logo.png').subsample(8, 8)
    logo_label = tk.Label(top_frame, image=logo_image, background="#f5f5f5")
    logo_label.image = logo_image
    logo_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky='nw')

    # Кнопки верхней панели
    orders_button = create_rounded_button(top_frame, "Заказы", command=update_main_table)
    orders_button.grid(row=0, column=1, padx=15, pady=10, sticky='w')

    # Кнопка сортировки по номеру поезда
    sort_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'sort.png')
    sort_icon = tk.PhotoImage(file=sort_icon_path).subsample(50, 50)
    train_sort_button = tk.Button(top_frame, image=sort_icon, command=lambda: update_main_table(order_by='train_number'),
                                  bg="#e0e0e0", relief="flat", borderwidth=0)
    train_sort_button.image = sort_icon
    train_sort_button.grid(row=1, column=1, padx=15, pady=5, sticky='w')

    # Кнопки "Отправители" и "Получатели"
    sender_button = create_rounded_button(top_frame, "Отправители", command=show_sender_form)
    sender_button.grid(row=0, column=2, padx=15, pady=10, sticky='w')

    receiver_button = create_rounded_button(top_frame, "Получатели", command=show_receiver_form)
    receiver_button.grid(row=0, column=3, padx=15, pady=10, sticky='w')

    # Кнопка "Записать" и кнопка сортировки по статусу под ней
    save_button = create_rounded_button(top_frame, "Записать", command=show_add_form)
    save_button.grid(row=0, column=4, padx=15, pady=10, sticky='e')

    status_sort_button = tk.Button(top_frame, image=sort_icon, command=lambda: update_main_table(order_by='status'),
                                   bg="#e0e0e0", relief="flat", borderwidth=0)
    status_sort_button.image = sort_icon
    status_sort_button.grid(row=1, column=4, padx=15, pady=5, sticky='e')

    top_frame.columnconfigure(4, weight=1)

    # Таблица перевозок с полосой прокрутки
    table_frame = ttk.Frame(root)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    canvas = tk.Canvas(table_frame, bg="#ffffff")
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    table_inner_frame = scrollable_frame

    # Нижняя панель управления
    bottom_frame = ttk.Frame(root)
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

    help_button = create_rounded_button(bottom_frame, "Помощь", command=show_help)
    help_button.pack(side=tk.LEFT, padx=15)

    report_button = create_rounded_button(bottom_frame, "Отчеты", command=lambda: show_reports())
    report_button.pack(side=tk.RIGHT, padx=15)

    # Обновляем таблицу
    update_main_table()
    root.mainloop()

sort_order_train_number_desc = False  # По умолчанию сортировка по возрастанию
sort_order_status_desc = False  # По умолчанию сортировка по возрастанию

# Обновление главной таблицы с перевозками
# Обновление главной таблицы с перевозками
def update_main_table(order_by=None):
    global sort_order_train_number_desc, sort_order_status_desc

    # Очистка таблицы перед обновлением данных
    for widget in table_inner_frame.winfo_children():
        widget.destroy()

    shipments = get_all_shipments()

    # Сортировка данных
    if order_by == 'train_number':
        sort_order_train_number_desc = not sort_order_train_number_desc
        shipments.sort(key=lambda x: int(x[1]) if x[1].isdigit() else 0, reverse=sort_order_train_number_desc)
    elif order_by == 'status':
        sort_order_status_desc = not sort_order_status_desc
        shipments.sort(key=lambda x: x[14], reverse=sort_order_status_desc)

    # Обновленный порядок заголовков и данных
    headers = ["ID", "Номер поезда", "Тип локомотива", "Тип вагона", "Тип груза", "Вес груза",
               "Дата отправления", "Дата прибытия", "Пункт отправления", "Пункт прибытия",
               "Тип отправителя", "Отправитель", "Тип получателя", "Получатель", "Статус"]
    
    for col, header in enumerate(headers):
        label = tk.Label(table_inner_frame, text=header, font=("Arial", 12, "bold"), borderwidth=1, relief="solid", 
                         padx=5, pady=5, background="#e0e0e0")
        label.grid(row=0, column=col, sticky="nsew", ipadx=5, ipady=5, padx=2)

    for row_idx, shipment in enumerate(shipments, start=1):
        corrected_shipment = (
            shipment[0],  # ID
            shipment[1],  # Номер поезда
            shipment[4],  # Тип локомотива
            shipment[3],  # Тип вагона
            shipment[2],  # Тип груза
            shipment[5],  # Вес груза
            shipment[6],  # Дата отправления
            shipment[7],  # Дата прибытия
            shipment[8],  # Пункт отправления
            shipment[9],  # Пункт прибытия
            shipment[10], # Тип отправителя
            shipment[11], # Отправитель
            shipment[12], # Тип получателя
            shipment[13], # Получатель
            shipment[14]  # Статус
        )
        for col_idx, value in enumerate(corrected_shipment):
            label = tk.Label(table_inner_frame, text=value, font=("Arial", 10), borderwidth=1, relief="solid", 
                             padx=5, pady=5, background="#ffffff")
            label.grid(row=row_idx, column=col_idx, sticky="nsew", ipadx=5, ipady=5, padx=2)

        # Кнопка редактирования
        edit_icon = tk.PhotoImage(file='assets/redakt.png').subsample(25, 25)
        edit_button = tk.Button(table_inner_frame, image=edit_icon, borderwidth=0, background="#f8f9fa", 
                                command=lambda shipment_id=shipment[0]: show_edit_form(shipment_id))
        edit_button.image = edit_icon
        edit_button.grid(row=row_idx, column=len(corrected_shipment), padx=5, pady=5, sticky='nsew')




# Функция для отображения формы редактирования перевозки
def show_edit_form(shipment_id):
    shipment = next((s for s in get_all_shipments() if s[0] == shipment_id), None)
    if not shipment:
        messagebox.showerror("Ошибка", "Запись не найдена")
        return

    form_window = tk.Toplevel()
    form_window.title("Редактировать перевозку")
    form_window.geometry('800x400')  # Задаем размер окна
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
        ("Тип отправителя", ttk.Combobox(left_frame, values=["Физическое лицо", "Юридическое лицо"])),
        ("Отправитель", ttk.Combobox(left_frame, values=get_senders_by_type(shipment[10]))),
    ]

    # Правые поля формы
    right_fields = [
        ("Дата отправления", tk.Entry(right_frame)),
        ("Дата прибытия", tk.Entry(right_frame)),
        ("Пункт отправления", tk.Entry(right_frame)),
        ("Пункт прибытия", tk.Entry(right_frame)),
        ("Тип получателя", ttk.Combobox(right_frame, values=["Физическое лицо", "Юридическое лицо"])),
        ("Получатель", ttk.Combobox(right_frame, values=get_receivers_by_type(shipment[12]))),
        ("Изменение статуса", ttk.Combobox(right_frame, values=["в процессе", "завершен", "отменен"])),
    ]

    # Установка текущих значений
    left_fields[0][1].insert(0, shipment[1])
    left_fields[1][1].set(shipment[2])
    left_fields[2][1].set(shipment[3])
    left_fields[3][1].set(shipment[4])
    left_fields[4][1].insert(0, shipment[5])
    left_fields[5][1].set(shipment[10])
    left_fields[6][1].set(shipment[11])

    right_fields[0][1].insert(0, shipment[6])
    right_fields[1][1].insert(0, shipment[7])
    right_fields[2][1].insert(0, shipment[8])
    right_fields[3][1].insert(0, shipment[9])
    right_fields[4][1].set(shipment[12])
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

    # Функция для обновления списка отправителей в зависимости от типа
    def update_sender_list():
        selected_type = left_fields[5][1].get()  # Тип отправителя
        if selected_type:
            senders = get_senders_by_type(selected_type)
            left_fields[6][1]['values'] = senders
        else:
            left_fields[6][1]['values'] = []

    # Функция для обновления списка получателей в зависимости от типа
    def update_receiver_list():
        selected_type = right_fields[4][1].get()  # Тип получателя
        if selected_type:
            receivers = get_receivers_by_type(selected_type)
            right_fields[5][1]['values'] = receivers
        else:
            right_fields[5][1]['values'] = []

    # Привязка события изменения типа отправителя/получателя
    left_fields[5][1].bind("<<ComboboxSelected>>", lambda e: update_sender_list())
    right_fields[4][1].bind("<<ComboboxSelected>>", lambda e: update_receiver_list())

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
                "sender_type": left_fields[5][1].get(),
                "sender_info": left_fields[6][1].get(),
                "receiver_type": right_fields[4][1].get(),
                "receiver_info": right_fields[5][1].get(),
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


# Функция для отображения формы отчетов
def show_reports():
    report_window = tk.Toplevel()
    report_window.title("Отчеты по перевозкам")
    report_window.geometry('700x500')
    report_window.resizable(False, False)

    # Основной фрейм для отчета
    report_frame = ttk.Frame(report_window, padding=20)
    report_frame.pack(fill=tk.BOTH, expand=True)

    # Кнопки фильтра и сброса
    filter_button = ttk.Button(report_frame, text="Фильтр", command=lambda: show_filter_options(report_text))
    filter_button.grid(row=0, column=0, padx=10, pady=10, sticky='w')

    reset_button = ttk.Button(report_frame, text="Сброс", command=lambda: update_report(report_text, reset=True))
    reset_button.grid(row=0, column=1, padx=10, pady=10, sticky='w')

    # Заголовок
    summary_label = tk.Label(report_frame, text="Сводные данные по перевозкам", font=("Arial", 16, "bold"))
    summary_label.grid(row=1, column=0, columnspan=2, pady=10)

    # Текстовая область для отчета
    report_text = tk.Text(report_frame, height=20, width=80, wrap='word', font=("Arial", 12))
    report_text.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
    report_text.configure(state='disabled')

    # Кнопка для закрытия окна
    close_button = ttk.Button(report_frame, text="Закрыть", command=report_window.destroy)
    close_button.grid(row=3, column=0, columnspan=2, pady=20)

    # Отображение данных отчета при открытии окна
    update_report(report_text)

def update_report(report_text, filters=None, reset=False):
    if reset:
        report_text.configure(state='normal')  # Делаем текстовую область редактируемой для очистки
        report_text.delete(1.0, tk.END)       # Полностью очищаем текстовую область
        report_text.insert(tk.END, "Нет данных для отображения.")  # Добавляем сообщение
        report_text.configure(state='disabled')  # Возвращаем текстовую область в состояние только для чтения
        return

    rows = generate_report(**filters) if filters else generate_report()
    report_data = ""

    if rows:
        for row in rows:
            report_data += (
                f"Пункт отправления: {row[0]}, "
                f"Пункт прибытия: {row[1]}, "
                f"Количество поездов: {row[2]}, "
                f"Общий вес: {row[3]} тонн\n"
            )
    else:
        report_data = "Нет данных для отображения."

    report_text.configure(state='normal')  # Делаем текстовую область редактируемой для обновления
    report_text.delete(1.0, tk.END)       # Очищаем текстовую область
    report_text.insert(tk.END, report_data)
    report_text.configure(state='disabled')  # Возвращаем текстовую область в состояние только для чтения



# Функция для отображения фильтрации в отчетах
def show_filter_options(report_text):
    filter_window = tk.Toplevel()
    filter_window.title("Фильтр данных")
    filter_window.geometry('400x300')
    filter_window.resizable(False, False)

    # Основной фрейм
    filter_frame = ttk.Frame(filter_window, padding=10)
    filter_frame.pack(fill=tk.BOTH, expand=True)

    # Поля для фильтров
    departure_label = tk.Label(filter_frame, text="Пункт отправления:")
    departure_label.grid(row=0, column=0, padx=10, pady=5, sticky='e')
    departure_entry = ttk.Entry(filter_frame)
    departure_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w')

    destination_label = tk.Label(filter_frame, text="Пункт прибытия:")
    destination_label.grid(row=1, column=0, padx=10, pady=5, sticky='e')
    destination_entry = ttk.Entry(filter_frame)
    destination_entry.grid(row=1, column=1, padx=10, pady=5, sticky='w')

    cargo_label = tk.Label(filter_frame, text="Тип груза:")
    cargo_label.grid(row=2, column=0, padx=10, pady=5, sticky='e')
    cargo_combobox = ttk.Combobox(filter_frame, values=["Твердый", "Жидкий", "Газовый", "Сыпучий"])
    cargo_combobox.grid(row=2, column=1, padx=10, pady=5, sticky='w')

    # Применение фильтров
    def apply_filters():
        filters = {
            "departure_point": departure_entry.get().strip() if departure_entry.get() else None,
            "destination_point": destination_entry.get().strip() if destination_entry.get() else None,
            "cargo_type": cargo_combobox.get().strip() if cargo_combobox.get() else None,
        }
        update_report(report_text, filters)
        filter_window.destroy()

    # Кнопки управления
    apply_button = ttk.Button(filter_frame, text="Применить", command=apply_filters)
    apply_button.grid(row=3, column=0, columnspan=2, pady=10)

    cancel_button = ttk.Button(filter_frame, text="Отмена", command=filter_window.destroy)
    cancel_button.grid(row=4, column=0, columnspan=2, pady=5)


if __name__ == "__main__":
    init_db()
    create_main_window()
