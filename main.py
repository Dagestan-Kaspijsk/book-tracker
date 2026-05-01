import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class BookTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker")
        self.root.geometry("900x600")
        self.root.resizable(False, False)
        
        # Имя файла для сохранения данных
        self.data_file = "books.json"
        
        # --- 1. СОЗДАЕМ ГЛАВНЫЙ ФРЕЙМ (КОНТЕЙНЕР) ---
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 2. ЛЕВЫЙ БЛОК: ПОЛЯ ВВОДА ---
        input_frame = ttk.LabelFrame(main_frame, text="Добавить новую книгу", padding="10")
        input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Название
        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.title_entry = ttk.Entry(input_frame, width=30)
        self.title_entry.grid(row=1, column=0, columnspan=2, pady=2)

        # Автор
        ttk.Label(input_frame, text="Автор:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.author_entry = ttk.Entry(input_frame, width=30)
        self.author_entry.grid(row=3, column=0, columnspan=2, pady=2)

        # Жанр
        ttk.Label(input_frame, text="Жанр:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.genre_entry = ttk.Entry(input_frame, width=30)
        self.genre_entry.grid(row=5, column=0, columnspan=2, pady=2)

        # Страницы
        ttk.Label(input_frame, text="Страниц:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.pages_entry = ttk.Entry(input_frame, width=15)
        self.pages_entry.grid(row=7, column=0, pady=2)

        # Кнопка "Добавить"
        self.add_button = ttk.Button(input_frame, text="Добавить книгу", command=self.add_book)
        self.add_button.grid(row=7, column=1, pady=2)

        # --- 3. ПРАВЫЙ БЛОК: СПИСОК КНИГ И ФИЛЬТРЫ ---
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Блок для кнопок управления (Сохранить/Загрузить/Фильтр)
        control_frame = ttk.Frame(right_frame)
        control_frame.pack(fill=tk.X, pady=5)

        self.save_button = ttk.Button(control_frame, text="💾 Сохранить в JSON", command=self.save_to_json)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.load_button = ttk.Button(control_frame, text="📂 Загрузить из JSON", command=self.load_from_json)
        self.load_button.pack(side=tk.LEFT, padx=5)

        # Фильтр по жанру
        self.genre_filter_var = tk.StringVar()
        self.genre_combo = ttk.Combobox(control_frame, textvariable=self.genre_filter_var, state='readonly', width=15)
        self.genre_combo['values'] = ('Все', 'Фантастика', 'Детектив', 'Роман', 'Наука')
        self.genre_combo.current(0) # Устанавливаем значение по умолчанию
        self.genre_combo.pack(side=tk.RIGHT, padx=5)
        
        # Фильтр по страницам (больше чем...)
        filter_pages_frame = ttk.Frame(control_frame)
        filter_pages_frame.pack(side=tk.RIGHT, padx=(20, 0))
        
        ttk.Label(filter_pages_frame, text="Страниц >").pack(side=tk.LEFT)
        self.pages_filter_entry = ttk.Entry(filter_pages_frame, width=8)
        self.pages_filter_entry.pack(side=tk.LEFT, padx=5)
        
        self.filter_button = ttk.Button(filter_pages_frame, text="Фильтровать", command=self.filter_books)
        self.filter_button.pack(side=tk.LEFT)


        # Таблица для книг (Treeview)
        self.columns = ("title", "author", "genre", "pages")
        self.tree = ttk.Treeview(right_frame, columns=self.columns, show="headings")
        
         # Задаем заголовки колонок и их ширину
        for col in self.columns:
            self.tree.heading(col, text=col.capitalize())
            if col == "pages":
                self.tree.column(col, width=60, anchor='center')
            else:
                self.tree.column(col, width=200, anchor='w')
        
         # Добавляем полосу прокрутки
         # Создаем Scrollbar
         scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.tree.yview)
         scrollbar.pack(side="right", fill="y")
         
         # Прикрепляем Scrollbar к Treeview
         self.tree.configure(yscrollcommand=scrollbar.set)
         
         self.tree.pack(fill="both", expand=True)

    # --- ЛОГИКА ПРИЛОЖЕНИЯ ---

    def add_book(self):
         """Добавляет книгу из полей ввода в таблицу."""
         title = self.title_entry.get()
         author = self.author_entry.get()
         genre = self.genre_entry.get()
         pages = self.pages_entry.get()

         # Валидация: проверка на пустые поля
         if not title or not author or not genre or not pages:
             messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
             return

         # Валидация: проверка на число страниц
         if not pages.isdigit():
             messagebox.showerror("Ошибка", "Количество страниц должно быть целым числом!")
             return

         # Добавляем строку в таблицу
         self.tree.insert("", "end", values=(title, author, genre, pages))
         
         # Очищаем поля ввода
         self.title_entry.delete(0, tk.END)
         self.author_entry.delete(0, tk.END)
         self.genre_entry.delete(0, tk.END)
         self.pages_entry.delete(0, tk.END)
         
         # Ставим фокус на первое поле
         self.title_entry.focus()

    def save_to_json(self):
         """Сохраняет все книги из таблицы в файл JSON."""
         books = []
         for child in self.tree.get_children():
             values = self.tree.item(child)["values"]
             book = {
                 "title": values[0],
                 "author": values[1],
                 "genre": values[2],
                 "pages": int(values[3])
             }
             books.append(book)
         
         try:
             with open(self.data_file, 'w', encoding='utf-8') as f:
                 json.dump(books, f, ensure_ascii=False, indent=4)
             messagebox.showinfo("Успех", f"Данные сохранены в {self.data_file}")
         except Exception as e:
             messagebox.showerror("Ошибка сохранения", str(e))

    def load_from_json(self):
         """Загружает книги из файла JSON и отображает их в таблице."""
         # Очищаем текущую таблицу
         for item in self.tree.get_children():
             self.tree.delete(item)

         if not os.path.exists(self.data_file):
             messagebox.showwarning("Файл не найден", f"Файл {self.data_file} не существует. Сохраните данные сначала.")
             return

         try:
             with open(self.data_file, 'r', encoding='utf-8') as f:
                 books = json.load(f)
             
             for book in books:
                 self.tree.insert("", "end", values=(book['title'], book['author'], book['genre'], book['pages']))
             
             messagebox.showinfo("Успех", f"Данные загружены из {self.data_file}")
             
         except json.JSONDecodeError:
             messagebox.showerror("Ошибка файла", "Файл JSON поврежден или имеет неверный формат.")
         except Exception as e:
             messagebox.showerror("Ошибка загрузки", str(e))

    def filter_books(self):
         """Фильтрует книги в таблице по выбранным критериям."""
         selected_genre = self.genre_filter_var.get()
         pages_filter_text = self.pages_filter_entry.get()
         
         # Скрываем все записи
         for child in self.tree.get_children():
             self.tree.item(child, tags='hidden')
             self.tree.tag_configure('hidden', tags=['hidden'])

         # Показываем только те, что проходят фильтр
         for child in self.tree.get_children():
             values = self.tree.item(child)['values']
             genre_match = (selected_genre == 'Все') or (values[2] == selected_genre)
             
             pages_match = True
             if pages_filter_text.isdigit():
                 filter_pages = int(pages_filter_text)
                 book_pages = int(values[3])
                 pages_match = book_pages > filter_pages

             if genre_match and pages_match:
                 self.tree.item(child, tags='')


# --- ЗАПУСК ПРИЛОЖЕНИЯ ---
if __name__ == "__main__":
     root = tk.Tk()
     app = BookTrackerApp(root)
     root.mainloop()