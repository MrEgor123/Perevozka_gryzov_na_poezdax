import tkinter as tk
from tkinter import ttk

# Создание главного окна
root = tk.Tk()
root.title("Система учета перевозки грузов")
root.geometry("1200x600")

# Функции сортировки
def sort_by_order_number():
    items = tree.get_children()
    sorted_items = sorted(items, key=lambda i: int(tree.item(i)['values'][0]))
    for i, item in enumerate(sorted_items):
        tree.move(item, '', i)

def sort_by_status():
    items = tree.get_children()
    sorted_items = sorted(items, key=lambda i: tree.item(i)['values'][-1])
    for i, item in enumerate(sorted_items):
        tree.move(item, '', i)

# Верхняя панель с кнопками сортировки
sort_frame = tk.Frame(root)
sort_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

sort_order_button = tk.Button(sort_frame, text="Сортировка по номеру заказа", command=sort_by_order_number)
sort_order_button.pack(side=tk.LEFT, padx=5)

sort_status_button = tk.Button(sort_frame, text="Сортировка по статусу", command=sort_by_status)
sort_status_button.pack(side=tk.RIGHT, padx=5)

# Дерево для отображения данных о перевозках
tree = ttk.Treeview(root, columns=("ID", "Номер поезда", "Тип локомотива", "Тип груза", "Вес груза", "Тип вагона", "Дата отправления", "Дата прибытия", "Пункт отправления", "Пункт прибытия", "Тип отправителя", "Отправитель", "Тип получателя", "Получатель", "Статус"), show="headings")

for col in tree['columns']:
    tree.heading(col, text=col)

# Пример данных для отображения
example_data = [
    (1, "12345", "Электровоз", "Уголь", 6000, "Полувагон", "2024-09-20", "2024-09-25", "Москва", "Санкт-Петербург", "Юридическое лицо", "ООО Логистик", "Физическое лицо", "Иван Иванов", "в процессе"),
    (2, "1", "Электровоз", "Твердый", 1200, "Полувагон", "09.11.2024", "11.11.2024", "Киров", "Кирово-Чепецк", "Компания Б", "Груз очень важный!", "Компания Г", "Иван Иванов", "запланирована"),
    (3, "234872", "Электровоз", "Сыпучий", 50000, "Полувагон", "12.12.2024", "13.01.2025", "Киров", "Кирово-Чепецк", "Компания А", "Очень круто!", "Компания Г", "Иван Иванов", "в процессе"),
    (4, "263784", "Электровоз", "Твердый", 2230, "Полувагон", "16.11.2024", "18.11.2024", "Москва", "Киров", "Егор Чарушин Физическое лицо", "ООО АТП", "АО АТП", "Петр Петров", "завершен"),
    (5, "55555", "Тепловоз", "Твердый", 5500, "Полувагон", "12.12.2023", "17.12.2023", "г Махачкала", "г Киров", "Иван Иванов", "Петр Петров", "Физическое лицо", "Петр Петров", "запланирована")
]

for row in example_data:
    tree.insert("", tk.END, values=row)

tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

# Кнопка закрытия приложения
close_button = tk.Button(root, text="Закрыть", command=root.quit)
close_button.pack(side=tk.BOTTOM, pady=10)

root.mainloop()
