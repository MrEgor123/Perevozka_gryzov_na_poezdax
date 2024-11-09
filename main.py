import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import simpledialog

# Создание базы данных
def init_db():
    conn = sqlite3.connect('cargo_tracking.db')
    cursor = conn.cursor()
    
    # Создание таблицы для учета перевозок
    cursor.execute('''CREATE TABLE IF NOT EXISTS shipments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        train_number TEXT,
                        cargo_type TEXT,
                        wagon_type TEXT,
                        locomotive_type TEXT,
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
    
    conn.commit()
    conn.close()

# Добавление новой перевозки
def add_shipment(train_number, cargo_type, wagon_type, locomotive_type, weight,
                 departure_date, arrival_date, departure_point, destination_point,
                 sender_type, sender_info, receiver_type, receiver_info, status):
    conn = sqlite3.connect('cargo_tracking.db')
    cursor = conn.cursor()
    
    cursor.execute('''INSERT INTO shipments (train_number, cargo_type, wagon_type, locomotive_type, weight,
                    departure_date, arrival_date, departure_point, destination_point,
                    sender_type, sender_info, receiver_type, receiver_info, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (train_number, cargo_type, wagon_type, locomotive_type, weight,
                    departure_date, arrival_date, departure_point, destination_point,
                    sender_type, sender_info, receiver_type, receiver_info, status))
    
    conn.commit()
    conn.close()

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
        ("Тип груза", ttk.Combobox(left_frame, values=["Сыпучий", "Жидкий", "Твердый"])),
        ("Вес груза", tk.Entry(left_frame)),
        ("Тип вагона", ttk.Combobox(left_frame, values=["Платформа", "Полувагон", "Цистерна"])),
        ("Отправитель", ttk.Combobox(left_frame, values=["Компания А", "Компания Б"])),
    ]

    # Правые поля формы
    right_fields = [
    ("Дата отправления", tk.Entry(right_frame, validate='key', validatecommand=(form_window.register(lambda P: len(P) <= 10 and (P == '' or P.replace('.', '').isdigit() or P[-1] == '.')), '%P'))),
    ("Дата прибытия", tk.Entry(right_frame, validate='key', validatecommand=(form_window.register(lambda P: len(P) <= 10 and (P == '' or P.replace('.', '').isdigit() or P[-1] == '.')), '%P'))),
    ("Пункт отправления", tk.Entry(right_frame)),
    ("Пункт прибытия", tk.Entry(right_frame)),
    ("Доп. информация", tk.Entry(right_frame)),
    ("Получатель", ttk.Combobox(right_frame, values=["Компания В", "Компания Г"])),
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
            weight = float(left_fields[3][1].get())
            wagon_type = left_fields[4][1].get()
            sender = left_fields[5][1].get()
            departure_date = right_fields[0][1].get().strip().strip()
            if not departure_date:
                raise ValueError('Дата отправления не может быть пустой')
            arrival_date = right_fields[1][1].get().strip().strip()
            if not arrival_date:
                raise ValueError('Дата прибытия не может быть пустой')
            departure_point = right_fields[2][1].get()
            destination_point = right_fields[3][1].get()
            sender_info = right_fields[4][1].get()
            receiver = right_fields[5][1].get()
            status = "запланирована"

            add_shipment(train_number, cargo_type, wagon_type, locomotive_type, weight,
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
    global root, table_frame
    root = tk.Tk()
    root.title("Система учета перевозки грузов")
    root.state('zoomed')  # Установлено разрешение 16:9
    root.configure(bg="#f0f0f0")

    style = ttk.Style()
    style.configure("TButton", font=("Arial", 16), padding=15)
    
    
    
    style.configure("TFrame", background="#f0f0f0")

    # Верхние кнопки управления
    top_frame = ttk.Frame(root)
    top_frame.pack(side=tk.TOP, fill=tk.BOTH, pady=10)

    button_width = 25  # Оптимизированная ширина кнопок для 16:9

    logo_image = tk.PhotoImage(file='assets/logo.png').subsample(10, 10)  # Уменьшение размера логотипа
    logo_label = tk.Label(top_frame, image=logo_image, background="#f0f0f0")
    logo_label.image = logo_image  # Сохранение ссылки на изображение
    logo_label.pack(side=tk.LEFT, anchor='nw', padx=10, pady=10)

    orders_button = ttk.Button(top_frame, text="Заказы", width=button_width, command=update_main_table)
    orders_button.pack(side=tk.LEFT, padx=5)

    sender_button = ttk.Button(top_frame, text="Отправители", width=button_width, command=lambda: messagebox.showinfo("Инфо", "Функция отправителей пока не реализована"))
    sender_button.pack(side=tk.LEFT, padx=5)

    receiver_button = ttk.Button(top_frame, text="Получатели", width=button_width, command=lambda: messagebox.showinfo("Инфо", "Функция получателей пока не реализована"))
    receiver_button.pack(side=tk.LEFT, padx=5)

    save_button = ttk.Button(top_frame, text="Записать", width=button_width, command=show_add_form)
    save_button.pack(side=tk.RIGHT, padx=5)

    # Таблица перевозок
    table_frame = ttk.Frame(root)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Нижние кнопки управления
    bottom_frame = ttk.Frame(root)
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

    help_button = ttk.Button(bottom_frame, text="Помощь", width=button_width, command=show_help)
    help_button.pack(side=tk.LEFT, padx=5)

    report_button = ttk.Button(bottom_frame, text="Отчеты", width=button_width, command=lambda: messagebox.showinfo("Инфо", "Функция формирования отчета пока не реализована"))
    report_button.pack(side=tk.RIGHT, padx=5)

    update_main_table()
    root.mainloop()

# Обновление главной таблицы с перевозками
def update_main_table():
    for widget in table_frame.winfo_children():
        widget.destroy()

    shipments = get_all_shipments()

    headers = ["ID", "Поезд", "Груз", "Тип вагона", "Локомотив", "Вес", "Отправление", "Прибытие", "Пункт отправления", "Пункт прибытия", "Отправитель", "Получатель", "Статус"]
    for col, header in enumerate(headers):
        label = tk.Label(table_frame, text=header, font=("Arial", 12, "bold"), borderwidth=1, relief="solid", padx=5, pady=5)
        label.grid(row=0, column=col, sticky="nsew", ipadx=5, ipady=5, padx=2)

    for row_idx, shipment in enumerate(shipments, start=1):
        for col_idx, value in enumerate(shipment):
            label = tk.Label(table_frame, text=value, font=("Arial", 10), borderwidth=1, relief="solid", padx=5, pady=5)
            label.grid(row=row_idx, column=col_idx, sticky="nsew", ipadx=5, ipady=5, padx=2)

if __name__ == "__main__":
    init_db()
    create_main_window()
