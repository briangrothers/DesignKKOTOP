import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import json
import os
import math
import random

class Wall:
    def __init__(self, x1, y1, x2, y2, thickness=0.2, color="#8B4513"):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.thickness = thickness
        self.color = color
        self.canvas_id = None
        self.doors = []
        self.windows = []

class Door:
    def __init__(self, position, width=0.9, height=2.0):
        self.position = position
        self.width = width
        self.height = height
        self.color = "#7C5B00"

class Window:
    def __init__(self, position, width=1.2, height=1.2):
        self.position = position
        self.width = width
        self.height = height
        self.color = "#87CEEB"

class Furniture:
    def __init__(self, name, width, height, color, icon, category, x=0, y=0):
        self.name = name
        self.width = width
        self.height = height
        self.color = color
        self.icon = icon
        self.category = category
        self.x = x
        self.y = y
        self.rotation = 0
        self.canvas_ids = []

class Floor:
    def __init__(self, floor_type, color, pattern, points=None):
        self.floor_type = floor_type
        self.color = color
        self.pattern = pattern
        self.points = points or []
        self.canvas_id = None
        self.texture_ids = []

class InteriorDesignApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Дизайн интерьера")
        self.root.geometry("1900x1000")
        
        # Настройки
        self.PIXELS_PER_METER = 40
        self.SNAP_THRESHOLD = 0.3
        
        # Прилипание к сетке
        self.grid_snap = True
        self.grid_size = 0.5
        
        # Данные
        self.walls = []
        self.furniture = []
        self.floors = []
        self.furniture_types = self.create_furniture_types()
        self.furniture_categories = self.get_furniture_categories()
        self.floor_types = self.create_floor_types()
        
        # Состояние
        self.mode = "walls"
        self.current_wall_start = None
        self.selected_item = None
        self.selected_furniture_type = None
        self.selected_floor_type = None
        self.drag_data = None
        self.highlighted_item = None
        self.adding_mode = None
        self.furniture_preview = None
        self.floor_mode = False
        self.floor_points = []
        self.current_category = "Все"
        
        # Для перетаскивания мебели
        self.drag_furniture = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        self.wall_colors = {"walls": "#FFFFFF"}        
        self.bg_dark = "#2D2D2D"
        self.bg_medium = "#3D3D3D"
        self.bg_light = "#4D4D4D"
        self.fg_color = "#FFFFFF"
        self.select_color = "#FF0000"
        self.accent_color = "#FF5E00"
        
        self.setup_ui()
        self.bind_events()
        self.draw_grid()
    
    def get_furniture_categories(self):
        """Получить категории мебели"""
        return ["Все", "Для сидения", "Для сна", "Столы", "Хранение", "Кухня", "Ванная", "Декор", "Техника"]
    
    def create_furniture_types(self):
        """Вся мебель с категориями"""
        return [
            # Для сидения
            {"name": "Диван", "w": 2.0, "h": 0.9, "color": "#8B4513", "icon": "🛋️", "category": "Для сидения"},
            {"name": "Кресло", "w": 0.8, "h": 0.8, "color": "#8B4513", "icon": "🪑", "category": "Для сидения"},
            {"name": "Стул", "w": 0.5, "h": 0.5, "color": "#8B4513", "icon": "🪑", "category": "Для сидения"},
            {"name": "Табурет", "w": 0.4, "h": 0.4, "color": "#A0522D", "icon": "🪑", "category": "Для сидения"},
            {"name": "Банкетка", "w": 1.2, "h": 0.5, "color": "#8B4513", "icon": "🪑", "category": "Для сидения"},
            {"name": "Пуфик", "w": 0.5, "h": 0.5, "color": "#CD853F", "icon": "🪑", "category": "Для сидения"},
            {"name": "Кресло-качалка", "w": 0.9, "h": 0.8, "color": "#8B4513", "icon": "🪑", "category": "Для сидения"},
            {"name": "Стул офисный", "w": 0.6, "h": 0.6, "color": "#2F4F4F", "icon": "🪑", "category": "Для сидения"},
            
            # Для сна
            {"name": "Кровать двуспальная", "w": 2.0, "h": 1.8, "color": "#A52A2A", "icon": "🛏️", "category": "Для сна"},
            {"name": "Кровать односпальная", "w": 2.0, "h": 1.2, "color": "#A52A2A", "icon": "🛏️", "category": "Для сна"},
            {"name": "Кровать детская", "w": 1.6, "h": 0.8, "color": "#CD853F", "icon": "🛏️", "category": "Для сна"},
            {"name": "Диван-кровать", "w": 2.0, "h": 1.0, "color": "#8B4513", "icon": "🛋️", "category": "Для сна"},
            {"name": "Кушетка", "w": 1.8, "h": 0.8, "color": "#8B4513", "icon": "🛏️", "category": "Для сна"},
            {"name": "Матрас", "w": 2.0, "h": 1.5, "color": "#D2B48C", "icon": "🛏️", "category": "Для сна"},
            
            # Столы
            {"name": "Стол обеденный", "w": 1.8, "h": 0.8, "color": "#D2691E", "icon": "🍽️", "category": "Столы"},
            {"name": "Стол письменный", "w": 1.2, "h": 0.6, "color": "#CD853F", "icon": "📚", "category": "Столы"},
            {"name": "Стол журнальный", "w": 1.0, "h": 0.5, "color": "#D2691E", "icon": "☕", "category": "Столы"},
            {"name": "Стол компьютерный", "w": 1.4, "h": 0.7, "color": "#2F4F4F", "icon": "💻", "category": "Столы"},
            {"name": "Стол кухонный", "w": 1.5, "h": 0.8, "color": "#D2691E", "icon": "🍳", "category": "Столы"},
            {"name": "Стол раскладной", "w": 1.6, "h": 0.8, "color": "#CD853F", "icon": "🍽️", "category": "Столы"},
            {"name": "Столик для завтрака", "w": 0.8, "h": 0.5, "color": "#D2691E", "icon": "☕", "category": "Столы"},
            {"name": "Консоль", "w": 1.2, "h": 0.4, "color": "#8B4513", "icon": "📦", "category": "Столы"},
            
            # Хранение
            {"name": "Шкаф платяной", "w": 1.8, "h": 0.6, "color": "#8B4513", "icon": "👔", "category": "Хранение"},
            {"name": "Шкаф книжный", "w": 0.8, "h": 0.3, "color": "#D2691E", "icon": "📚", "category": "Хранение"},
            {"name": "Шкаф угловой", "w": 1.2, "h": 1.2, "color": "#8B4513", "icon": "📦", "category": "Хранение"},
            {"name": "Комод", "w": 1.2, "h": 0.5, "color": "#8B4513", "icon": "🗄️", "category": "Хранение"},
            {"name": "Тумба под ТВ", "w": 1.5, "h": 0.5, "color": "#2F4F4F", "icon": "📺", "category": "Хранение"},
            {"name": "Тумба прикроватная", "w": 0.5, "h": 0.5, "color": "#CD853F", "icon": "🔔", "category": "Хранение"},
            {"name": "Стеллаж", "w": 1.5, "h": 0.4, "color": "#A0522D", "icon": "📚", "category": "Хранение"},
            {"name": "Полка навесная", "w": 1.0, "h": 0.3, "color": "#8B4513", "icon": "📚", "category": "Хранение"},
            {"name": "Этажерка", "w": 0.8, "h": 0.8, "color": "#CD853F", "icon": "📦", "category": "Хранение"},
            {"name": "Сундук", "w": 1.0, "h": 0.5, "color": "#8B4513", "icon": "🧰", "category": "Хранение"},
            {"name": "Вешалка напольная", "w": 0.6, "h": 0.6, "color": "#8B4513", "icon": "👕", "category": "Хранение"},
            
            # Кухня
            {"name": "Кухонный гарнитур", "w": 2.5, "h": 0.6, "color": "#A0522D", "icon": "🍳", "category": "Кухня"},
            {"name": "Мойка", "w": 0.8, "h": 0.5, "color": "#C0C0C0", "icon": "🚰", "category": "Кухня"},
            {"name": "Плита", "w": 0.6, "h": 0.6, "color": "#2F4F4F", "icon": "🔥", "category": "Кухня"},
            {"name": "Холодильник", "w": 0.8, "h": 0.8, "color": "#FFFFFF", "icon": "❄️", "category": "Кухня"},
            {"name": "Микроволновка", "w": 0.5, "h": 0.3, "color": "#C0C0C0", "icon": "📡", "category": "Кухня"},
            {"name": "Посудомойка", "w": 0.6, "h": 0.6, "color": "#C0C0C0", "icon": "🍽️", "category": "Кухня"},
            {"name": "Стиральная машина", "w": 0.6, "h": 0.6, "color": "#FFFFFF", "icon": "🧺", "category": "Кухня"},
            {"name": "Остров кухонный", "w": 1.8, "h": 0.8, "color": "#D2691E", "icon": "🍳", "category": "Кухня"},
            {"name": "Барная стойка", "w": 1.5, "h": 0.4, "color": "#8B4513", "icon": "🍷", "category": "Кухня"},
            {"name": "Вытяжка", "w": 0.8, "h": 0.3, "color": "#C0C0C0", "icon": "💨", "category": "Кухня"},
            {"name": "Кофемашина", "w": 0.4, "h": 0.4, "color": "#8B4513", "icon": "☕", "category": "Кухня"},
            {"name": "Тостер", "w": 0.3, "h": 0.2, "color": "#C0C0C0", "icon": "🍞", "category": "Кухня"},
            {"name": "Чайник", "w": 0.3, "h": 0.3, "color": "#C0C0C0", "icon": "🫖", "category": "Кухня"},
            
            # Ванная комната
            {"name": "Ванна", "w": 1.7, "h": 0.7, "color": "#FFFFFF", "icon": "🛁", "category": "Ванная"},
            {"name": "Душевая кабина", "w": 0.9, "h": 0.9, "color": "#C0C0C0", "icon": "🚿", "category": "Ванная"},
            {"name": "Унитаз", "w": 0.5, "h": 0.7, "color": "#FFFFFF", "icon": "🚽", "category": "Ванная"},
            {"name": "Раковина", "w": 0.6, "h": 0.5, "color": "#FFFFFF", "icon": "🚰", "category": "Ванная"},
            {"name": "Раковина двойная", "w": 1.2, "h": 0.5, "color": "#FFFFFF", "icon": "🚰", "category": "Ванная"},
            {"name": "Тумба под раковину", "w": 0.8, "h": 0.5, "color": "#8B4513", "icon": "🗄️", "category": "Ванная"},
            {"name": "Зеркало с подсветкой", "w": 0.8, "h": 0.1, "color": "#C0C0C0", "icon": "🪞", "category": "Ванная"},
            {"name": "Шкафчик навесной", "w": 0.6, "h": 0.3, "color": "#8B4513", "icon": "📦", "category": "Ванная"},
            {"name": "Полка для полотенец", "w": 0.8, "h": 0.2, "color": "#C0C0C0", "icon": "🧻", "category": "Ванная"},
            {"name": "Стиральная машина", "w": 0.6, "h": 0.6, "color": "#FFFFFF", "icon": "🧺", "category": "Ванная"},
            {"name": "Сушилка для белья", "w": 0.8, "h": 0.8, "color": "#C0C0C0", "icon": "👕", "category": "Ванная"},
            {"name": "Биде", "w": 0.4, "h": 0.6, "color": "#FFFFFF", "icon": "🚽", "category": "Ванная"},
            {"name": "Писсуар", "w": 0.4, "h": 0.5, "color": "#FFFFFF", "icon": "🚽", "category": "Ванная"},
            {"name": "Корзина для белья", "w": 0.4, "h": 0.4, "color": "#8B4513", "icon": "🧺", "category": "Ванная"},
            {"name": "Вешалка для полотенец", "w": 0.6, "h": 0.1, "color": "#C0C0C0", "icon": "🧻", "category": "Ванная"},
            {"name": "Держатель для туалетной бумаги", "w": 0.2, "h": 0.1, "color": "#C0C0C0", "icon": "🧻", "category": "Ванная"},
            {"name": "Мыльница", "w": 0.2, "h": 0.2, "color": "#C0C0C0", "icon": "🧼", "category": "Ванная"},
            {"name": "Стакан для зубных щеток", "w": 0.1, "h": 0.1, "color": "#C0C0C0", "icon": "🪥", "category": "Ванная"},
            {"name": "Фен", "w": 0.2, "h": 0.2, "color": "#C0C0C0", "icon": "💨", "category": "Ванная"},
            {"name": "Весы напольные", "w": 0.3, "h": 0.3, "color": "#C0C0C0", "icon": "⚖️", "category": "Ванная"},
            
            # Декор
            {"name": "Ковер", "w": 2.0, "h": 1.5, "color": "#8B4513", "icon": "🧶", "category": "Декор"},
            {"name": "Картина", "w": 0.8, "h": 0.1, "color": "#D2691E", "icon": "🖼️", "category": "Декор"},
            {"name": "Зеркало", "w": 0.8, "h": 0.1, "color": "#C0C0C0", "icon": "🪞", "category": "Декор"},
            {"name": "Цветок", "w": 0.3, "h": 0.3, "color": "#228B22", "icon": "🌿", "category": "Декор"},
            {"name": "Торшер", "w": 0.3, "h": 0.3, "color": "#DAA520", "icon": "💡", "category": "Декор"},
            {"name": "Люстра", "w": 0.5, "h": 0.5, "color": "#DAA520", "icon": "💡", "category": "Декор"},
            {"name": "Ваза", "w": 0.3, "h": 0.3, "color": "#4682B4", "icon": "🏺", "category": "Декор"},
            {"name": "Часы", "w": 0.3, "h": 0.1, "color": "#8B4513", "icon": "⏰", "category": "Декор"},
            {"name": "Камин", "w": 1.5, "h": 0.4, "color": "#8B4513", "icon": "🔥", "category": "Декор"},
            {"name": "Аквариум", "w": 1.0, "h": 0.4, "color": "#87CEEB", "icon": "🐠", "category": "Декор"},
            {"name": "Жалюзи", "w": 1.0, "h": 0.1, "color": "#FFFFFF", "icon": "🪟", "category": "Декор"},
            {"name": "Шторы", "w": 1.0, "h": 0.1, "color": "#8B4513", "icon": "🪟", "category": "Декор"},
            
            # Техника
            {"name": "Телевизор", "w": 1.2, "h": 0.1, "color": "#2F4F4F", "icon": "📺", "category": "Техника"},
            {"name": "Компьютер", "w": 0.5, "h": 0.5, "color": "#2F4F4F", "icon": "💻", "category": "Техника"},
            {"name": "Ноутбук", "w": 0.4, "h": 0.3, "color": "#2F4F4F", "icon": "💻", "category": "Техника"},
            {"name": "Колонки", "w": 0.3, "h": 0.3, "color": "#2F4F4F", "icon": "🔊", "category": "Техника"},
            {"name": "Кондиционер", "w": 0.8, "h": 0.2, "color": "#FFFFFF", "icon": "❄️", "category": "Техника"},
            {"name": "Пылесос", "w": 0.4, "h": 0.4, "color": "#2F4F4F", "icon": "🧹", "category": "Техника"},
            {"name": "Обогреватель", "w": 0.4, "h": 0.4, "color": "#CD853F", "icon": "🔥", "category": "Техника"},
            {"name": "Вентилятор", "w": 0.4, "h": 0.4, "color": "#FFFFFF", "icon": "🌀", "category": "Техника"},
            {"name": "Утюг", "w": 0.3, "h": 0.2, "color": "#C0C0C0", "icon": "👕", "category": "Техника"},
            {"name": "Гладильная доска", "w": 0.4, "h": 0.3, "color": "#8B4513", "icon": "👕", "category": "Техника"},
            {"name": "Робот-пылесос", "w": 0.3, "h": 0.3, "color": "#2F4F4F", "icon": "🤖", "category": "Техника"},
        ]
    
    def create_floor_types(self):
        """Типы полов"""
        return [
            {"name": "Паркет", "color": "#D2B48C", "pattern": "wood_plank", "icon": "🪵"},
            {"name": "Ламинат", "color": "#DEB887", "pattern": "wood_light", "icon": "🔲"},
            {"name": "Плитка белая", "color": "#F5F5F5", "pattern": "tile_grid", "icon": "⬜"},
            {"name": "Плитка серая", "color": "#808080", "pattern": "tile_grid", "icon": "🔳"},
            {"name": "Плитка черная", "color": "#2F4F4F", "pattern": "tile_grid", "icon": "⬛"},
            {"name": "Мрамор", "color": "#E8E8E8", "pattern": "marble", "icon": "◻️"},
            {"name": "Ковролин", "color": "#8B4513", "pattern": "carpet", "icon": "🧶"},
            {"name": "Линолеум", "color": "#C0C0C0", "pattern": "solid", "icon": "⬛"},
            {"name": "Дерево темное", "color": "#8B4513", "pattern": "wood_dark", "icon": "🪵"},
            {"name": "Дерево светлое", "color": "#DEB887", "pattern": "wood_light", "icon": "🪵"},
            {"name": "Плитка мозаика", "color": "#A0522D", "pattern": "mosaic", "icon": "🔶"},
            {"name": "Бетон", "color": "#808080", "pattern": "concrete", "icon": "🧱"},
            {"name": "Камень", "color": "#A9A9A9", "pattern": "stone", "icon": "🪨"},
            {"name": "Плитка ванная", "color": "#87CEEB", "pattern": "tile_grid", "icon": "🚿"},
        ]
    
    def setup_ui(self):
        """Интерфейс"""
        # Настройка стилей
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background=self.bg_dark, foreground=self.fg_color)
        style.configure('TFrame', background=self.bg_dark)
        style.configure('TScrollbar', background=self.bg_medium, troughcolor=self.bg_dark)
        
        # Меню
        menubar = tk.Menu(self.root, bg=self.bg_medium, fg=self.fg_color,
                         activebackground=self.bg_light, activeforeground=self.fg_color)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_medium, fg=self.fg_color,
                           activebackground=self.bg_light, activeforeground=self.fg_color)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новый", command=self.new_project)
        file_menu.add_command(label="Сохранить", command=self.save_project)
        file_menu.add_command(label="Загрузить", command=self.load_project)
        file_menu.add_separator()
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Главная панель
        main = tk.Frame(self.root, bg=self.bg_dark)
        main.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Верхняя панель с мебелью
        top_panel = tk.Frame(main, bg=self.bg_dark, height=150, relief=tk.RAISED, borderwidth=2)
        top_panel.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        top_panel.pack_propagate(False)
        
        # Заголовок
        tk.Label(top_panel, text="Каталог мебели", bg=self.bg_dark, fg=self.accent_color,
                font=("Arial", 12, "bold")).pack(pady=2)
        
        # Категории мебели
        category_frame = tk.Frame(top_panel, bg=self.bg_dark)
        category_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(category_frame, text="Категория:", bg=self.bg_dark, fg=self.fg_color).pack(side=tk.LEFT, padx=5)
        
        self.category_var = tk.StringVar(value="Все")
        category_combo = ttk.Combobox(category_frame, textvariable=self.category_var,
                                      values=self.furniture_categories, state="readonly",
                                      width=20)
        category_combo.pack(side=tk.LEFT, padx=5)
        category_combo.bind('<<ComboboxSelected>>', self.on_category_change)
        
        # Список мебели горизонтальный
        furn_container = tk.Frame(top_panel, bg=self.bg_dark)
        furn_container.pack(fill=tk.BOTH, expand=True, pady=2)
        
        # Кнопки прокрутки
        btn_left = tk.Button(furn_container, text="◀", command=self.scroll_furniture_left,
                            bg=self.bg_light, fg=self.fg_color, relief=tk.RAISED,
                            activebackground=self.bg_medium, activeforeground=self.fg_color)
        btn_left.pack(side=tk.LEFT, padx=2, fill=tk.Y)
        
        # Канвас для горизонтального скролла мебели
        self.furn_canvas = tk.Canvas(furn_container, bg=self.bg_dark, highlightthickness=0, height=80)
        furn_h_scroll = ttk.Scrollbar(furn_container, orient="horizontal", command=self.furn_canvas.xview)
        self.furn_scroll_frame = tk.Frame(self.furn_canvas, bg=self.bg_dark)
        
        self.furn_scroll_frame.bind(
            "<Configure>",
            lambda e: self.furn_canvas.configure(scrollregion=self.furn_canvas.bbox("all"))
        )
        
        self.furn_canvas.create_window((0, 0), window=self.furn_scroll_frame, anchor="nw")
        self.furn_canvas.configure(xscrollcommand=furn_h_scroll.set)
        
        self.furn_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        furn_h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        btn_right = tk.Button(furn_container, text="▶", command=self.scroll_furniture_right,
                             bg=self.bg_light, fg=self.fg_color, relief=tk.RAISED,
                             activebackground=self.bg_medium, activeforeground=self.fg_color)
        btn_right.pack(side=tk.RIGHT, padx=2, fill=tk.Y)
        
        # Заполняем мебель
        self.update_furniture_display()
        
        # Основной контейнер для левой и центральной частей
        middle_container = tk.Frame(main, bg=self.bg_dark)
        middle_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Левая панель с типами пола
        left_panel = tk.Frame(middle_container, bg=self.bg_dark, width=250, relief=tk.RAISED, borderwidth=2)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_panel.pack_propagate(False)
        
        # Внутренний фрейм для скроллинга левой панели
        canvas_left = tk.Canvas(left_panel, bg=self.bg_dark, highlightthickness=0)
        scroll_left = ttk.Scrollbar(left_panel, orient="vertical", command=canvas_left.yview)
        scrollable_left = tk.Frame(canvas_left, bg=self.bg_dark)
        
        scrollable_left.bind(
            "<Configure>",
            lambda e: canvas_left.configure(scrollregion=canvas_left.bbox("all"))
        )
        
        canvas_left.create_window((0, 0), window=scrollable_left, anchor="nw")
        canvas_left.configure(yscrollcommand=scroll_left.set)
        
        canvas_left.pack(side="left", fill="both", expand=True)
        scroll_left.pack(side="right", fill="y")
        
        # Типы пола
        floor_frame = tk.LabelFrame(scrollable_left, text="Типы пола", bg=self.bg_dark, fg=self.fg_color,
                                   padx=5, pady=5, relief=tk.RIDGE, bd=2)
        floor_frame.pack(fill=tk.X, pady=5, padx=5)
        
        tk.Button(floor_frame, text="🔄 Создать пол", command=self.activate_floor_mode,
                 bg=self.bg_light, fg=self.fg_color, relief=tk.RAISED,
                 activebackground=self.bg_medium, activeforeground=self.fg_color).pack(fill=tk.X, pady=2)
        
        tk.Label(floor_frame, text="Выберите тип пола:", bg=self.bg_dark, fg=self.fg_color).pack(pady=2)
        
        for f in self.floor_types:
            btn = tk.Button(floor_frame, 
                          text=f"{f['icon']} {f['name']}",
                          command=lambda x=f: self.select_floor_type(x),
                          bg=self.bg_light, fg=self.fg_color, relief=tk.RAISED, anchor='w',
                          activebackground=self.bg_medium, activeforeground=self.fg_color)
            btn.pack(fill=tk.X, pady=1)
        
        # Холст (рабочая область) - центр, белый фон
        canvas_frame = tk.Frame(middle_container, bg=self.bg_dark)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white', width=1300, height=900,
                               highlightbackground=self.bg_medium, highlightthickness=2)
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Правая панель с инструментами
        right_panel = tk.Frame(middle_container, bg=self.bg_dark, width=350, relief=tk.RAISED, borderwidth=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        right_panel.pack_propagate(False)
        
        # Внутренний фрейм для скроллинга правой панели
        canvas_right = tk.Canvas(right_panel, bg=self.bg_dark, highlightthickness=0)
        scroll_right = ttk.Scrollbar(right_panel, orient="vertical", command=canvas_right.yview)
        scrollable_right = tk.Frame(canvas_right, bg=self.bg_dark)
        
        scrollable_right.bind(
            "<Configure>",
            lambda e: canvas_right.configure(scrollregion=canvas_right.bbox("all"))
        )
        
        canvas_right.create_window((0, 0), window=scrollable_right, anchor="nw")
        canvas_right.configure(yscrollcommand=scroll_right.set)
        
        canvas_right.pack(side="left", fill="both", expand=True)
        scroll_right.pack(side="right", fill="y")
        
        # Режимы
        mode_frame = tk.LabelFrame(scrollable_right, text="Режим", bg=self.bg_dark, fg=self.fg_color,
                                  padx=5, pady=5, relief=tk.RIDGE, bd=2)
        mode_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.mode_var = tk.StringVar(value="walls")
        tk.Radiobutton(mode_frame, text=" Построить стены", variable=self.mode_var,
                      value="walls", command=self.change_mode, bg=self.bg_dark,
                      fg=self.fg_color, selectcolor=self.bg_medium,
                      activebackground=self.bg_light, activeforeground=self.fg_color).pack(anchor=tk.W)
        tk.Radiobutton(mode_frame, text="Расставить мебель", variable=self.mode_var,
                      value="furniture", command=self.change_mode, bg=self.bg_dark,
                      fg=self.fg_color, selectcolor=self.bg_medium,
                      activebackground=self.bg_light, activeforeground=self.fg_color).pack(anchor=tk.W)
        tk.Radiobutton(mode_frame, text="Выбор объекта", variable=self.mode_var,
                      value="select", command=self.change_mode, bg=self.bg_dark,
                      fg=self.fg_color, selectcolor=self.bg_medium,
                      activebackground=self.bg_light, activeforeground=self.fg_color).pack(anchor=tk.W)
        
        # Инструменты для стен
        wall_frame = tk.LabelFrame(scrollable_right, text="Стены", bg=self.bg_dark, fg=self.fg_color,
                                  padx=5, pady=5, relief=tk.RIDGE, bd=2)
        wall_frame.pack(fill=tk.X, pady=5, padx=5)
        
        tk.Label(wall_frame, text="Толщина (м):", bg=self.bg_dark, fg=self.fg_color).pack()
        self.thickness_var = tk.StringVar(value="0.2")
        tk.Spinbox(wall_frame, from_=0.1, to=1.0, increment=0.05,
                   textvariable=self.thickness_var, bg=self.bg_light,
                   fg=self.fg_color, buttonbackground=self.bg_medium).pack(fill=tk.X)
        
        tk.Button(wall_frame, text="Цвет стен", command=self.choose_wall_color,
                 bg=self.bg_light, fg=self.fg_color, relief=tk.RAISED,
                 activebackground=self.bg_medium, activeforeground=self.fg_color).pack(fill=tk.X, pady=2)
        
        # Двери и окна
        openings_frame = tk.LabelFrame(scrollable_right, text="Двери и окна", bg=self.bg_dark, fg=self.fg_color,
                                      padx=5, pady=5, relief=tk.RIDGE, bd=2)
        openings_frame.pack(fill=tk.X, pady=5, padx=5)
        
        tk.Button(openings_frame, text="🚪 Добавить дверь", command=self.activate_door_mode,
                 bg=self.bg_light, fg=self.fg_color, relief=tk.RAISED,
                 activebackground=self.bg_medium, activeforeground=self.fg_color).pack(fill=tk.X, pady=2)
        tk.Button(openings_frame, text="🪟 Добавить окно", command=self.activate_window_mode,
                 bg=self.bg_light, fg=self.fg_color, relief=tk.RAISED,
                 activebackground=self.bg_medium, activeforeground=self.fg_color).pack(fill=tk.X, pady=2)
        
        tk.Label(openings_frame, text="Ширина двери (м):", bg=self.bg_dark, fg=self.fg_color).pack()
        self.door_width_var = tk.StringVar(value="0.5")
        tk.Spinbox(openings_frame, from_=0.5, to=2.0, increment=0.1,
                   textvariable=self.door_width_var, bg=self.bg_light,
                   fg=self.fg_color, buttonbackground=self.bg_medium).pack(fill=tk.X, pady=2)
        
        tk.Label(openings_frame, text="Ширина окна (м):", bg=self.bg_dark, fg=self.fg_color).pack()
        self.window_width_var = tk.StringVar(value="0.5")
        tk.Spinbox(openings_frame, from_=0.5, to=3.0, increment=0.1,
                   textvariable=self.window_width_var, bg=self.bg_light,
                   fg=self.fg_color, buttonbackground=self.bg_medium).pack(fill=tk.X, pady=2)
        
        # Действия
        action_frame = tk.LabelFrame(scrollable_right, text="Действия", bg=self.bg_dark, fg=self.fg_color,
                                    padx=5, pady=5, relief=tk.RIDGE, bd=2)
        action_frame.pack(fill=tk.X, pady=5, padx=5)
        
        tk.Button(action_frame, text="Удалить (Del)", command=self.delete_selected,
                 bg=self.bg_light, fg=self.fg_color, relief=tk.RAISED,
                 activebackground=self.bg_medium, activeforeground=self.fg_color).pack(fill=tk.X)
        tk.Button(action_frame, text="Повернуть (R)", command=self.rotate_selected,
                 bg=self.bg_light, fg=self.fg_color, relief=tk.RAISED,
                 activebackground=self.bg_medium, activeforeground=self.fg_color).pack(fill=tk.X, pady=2)
        tk.Button(action_frame, text="Очистить всё", command=self.clear_all,
                 bg=self.bg_light, fg=self.fg_color, relief=tk.RAISED,
                 activebackground=self.bg_medium, activeforeground=self.fg_color).pack(fill=tk.X)
        
        # Информация
        info_frame = tk.LabelFrame(scrollable_right, text="Инфо", bg=self.bg_dark, fg=self.fg_color,
                                  padx=5, pady=5, relief=tk.RIDGE, bd=2)
        info_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.info_label = tk.Label(info_frame, text="", justify=tk.LEFT, bg=self.bg_dark, fg=self.fg_color)
        self.info_label.pack()
        
        # Статус бар
        self.status = tk.Label(self.root, text="Готов", relief=tk.SUNKEN, anchor=tk.W,
                              bg=self.bg_medium, fg=self.fg_color)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.update_info()
    
    def update_furniture_display(self):
        """Обновить отображение мебели в соответствии с выбранной категорией"""
        # Очищаем текущие кнопки
        for widget in self.furn_scroll_frame.winfo_children():
            widget.destroy()
        
        # Фильтруем мебель по категории
        category = self.category_var.get()
        if category == "Все":
            filtered_furniture = self.furniture_types
        else:
            filtered_furniture = [f for f in self.furniture_types if f["category"] == category]
        
        # Создаем кнопки для каждого предмета мебели
        for f in filtered_furniture:
            btn = tk.Button(self.furn_scroll_frame, 
                          text=f"{f['icon']}\n{f['name']}\n({f['w']}x{f['h']}м)",
                          command=lambda x=f: self.select_furniture(x),
                          bg=self.bg_light, fg=self.fg_color, relief=tk.RAISED,
                          activebackground=self.bg_medium, activeforeground=self.fg_color,
                          width=10, height=3, font=("Arial", 8))
            btn.pack(side=tk.LEFT, padx=2, pady=2)
    
    def on_category_change(self, event):
        """Обработчик изменения категории"""
        self.update_furniture_display()
    
    def scroll_furniture_left(self):
        """Прокрутка списка мебели влево"""
        self.furn_canvas.xview_scroll(-1, "units")
    
    def scroll_furniture_right(self):
        """Прокрутка списка мебели вправо"""
        self.furn_canvas.xview_scroll(1, "units")
    
    def bind_events(self):
        """События"""
        # Основные события
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Leave>", self.on_mouse_leave)
        
        # Клавиатура
        self.root.bind("<BackSpace>", lambda e: self.delete_selected())
        self.root.bind("<Delete>", lambda e: self.delete_selected())
        self.root.bind("<Escape>", lambda e: self.cancel_select())
        self.root.bind("<Return>", lambda e: self.complete_floor())
        self.root.bind("<r>", lambda e: self.rotate_selected())
        self.root.bind("<R>", lambda e: self.rotate_selected())
    
    def activate_door_mode(self):
        """Активировать режим добавления двери"""
        self.adding_mode = "door"
        self.status.config(text="Режим добавления двери - нажмите на стену")
    
    def activate_window_mode(self):
        """Активировать режим добавления окна"""
        self.adding_mode = "window"
        self.status.config(text="Режим добавления окна - нажмите на стену")
    
    def change_mode(self):
        """Смена режима"""
        if self.selected_item:
            self.status.config(text="Сначала отмените выбор (Esc)")
            self.mode_var.set(self.mode)
            return
            
        self.mode = self.mode_var.get()
        self.current_wall_start = None
        self.adding_mode = None
        self.furniture_preview = None
        self.canvas.delete("preview")
        self.canvas.delete("furniture_preview")
        
        if self.mode == "walls":
            self.status.config(text="Клик - начало стены, еще клик - конец")
        elif self.mode == "furniture":
            if self.selected_furniture_type:
                self.status.config(text=f"Разместите {self.selected_furniture_type['name']} кликом")
            else:
                self.status.config(text="Выберите мебель из списка сверху")
        else:
            self.status.config(text="Кликните на объект чтобы выбрать")
    
    def activate_floor_mode(self):
        """Активировать режим создания пола"""
        if len(self.walls) < 3:
            messagebox.showwarning("Предупреждение", "Сначала постройте стены (минимум 3 стены)")
            return
        
        self.floor_mode = True
        self.floor_points = []
        self.mode = "floor"
        self.mode_var.set("walls")
        self.status.config(text="Режим создания пола: кликайте по углам внутри стен (Enter - завершить, Esc - отмена)")
    
    def cancel_floor_mode(self):
        """Отмена режима создания пола"""
        self.floor_mode = False
        self.floor_points = []
        self.canvas.delete("floor_preview")
        self.canvas.delete("floor_preview_line")
        self.status.config(text="Режим создания пола отменен")
    
    def find_polygon_center(self, points):
        """Найти центр полигона"""
        if not points:
            return (0, 0)
        x_sum = sum(p[0] for p in points)
        y_sum = sum(p[1] for p in points)
        return (x_sum / len(points), y_sum / len(points))
    
    def sort_points_clockwise(self, points):
        """Сортировка точек по часовой стрелке"""
        if len(points) < 3:
            return points
        
        # Находим центр
        center_x, center_y = self.find_polygon_center(points)
        
        # Сортируем по углу
        def get_angle(point):
            return math.atan2(point[1] - center_y, point[0] - center_x)
        
        return sorted(points, key=get_angle)
    
    def is_point_inside_polygon(self, x, y, polygon):
        """Проверка, находится ли точка внутри полигона (алгоритм луча)"""
        if len(polygon) < 3:
            return False
        
        inside = False
        n = len(polygon)
        
        for i in range(n):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i + 1) % n]
            
            # Проверка пересечения луча с ребром
            if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
                inside = not inside
        
        return inside
    
    def get_room_polygon(self):
        """Получить полигон комнаты из стен"""
        if len(self.walls) < 3:
            return []
        
        # Собираем все уникальные точки пересечения стен
        points = []
        for wall in self.walls:
            points.append((wall.x1, wall.y1))
            points.append((wall.x2, wall.y2))
        
        # Удаляем дубликаты
        points = list(set(points))
        
        if len(points) < 3:
            return []
        
        # Сортируем точки по часовой стрелке
        return self.sort_points_clockwise(points)
    
    def complete_floor(self):
        """Завершить создание пола"""
        if len(self.floor_points) < 3:
            messagebox.showwarning("Предупреждение", "Нужно минимум 3 точки для создания пола")
            return
        
        if not self.selected_floor_type:
            messagebox.showwarning("Предупреждение", "Выберите тип пола из левой панели")
            return
        
        # Сортируем точки по часовой стрелке для правильного отображения
        sorted_points = self.sort_points_clockwise(self.floor_points)
        
        # Создаем пол
        floor = Floor(
            self.selected_floor_type["name"],
            self.selected_floor_type["color"],
            self.selected_floor_type["pattern"],
            sorted_points
        )
        self.floors.append(floor)
        
        # Очищаем режим создания пола
        self.floor_mode = False
        self.floor_points = []
        self.canvas.delete("floor_preview")
        self.canvas.delete("floor_preview_line")
        
        # Перерисовываем все с правильным порядком слоев
        self.redraw()
        
        self.status.config(text=f"Пол создан: {self.selected_floor_type['name']}")
        self.update_info()
    
    def select_floor_type(self, f):
        """Выбор типа пола"""
        self.selected_floor_type = f
        self.status.config(text=f"Выбран пол: {f['name']}. Нажмите 'Создать пол' и кликайте по углам")
    
    def on_click(self, event):
        """Клик"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        gx = (x - 50) / self.PIXELS_PER_METER
        gy = (y - 50) / self.PIXELS_PER_METER
        
        # Если в режиме создания пола
        if self.floor_mode:
            self.floor_click(gx, gy, x, y)
            return
        
        # Если в режиме добавления двери/окна
        if self.adding_mode in ["door", "window"]:
            self.add_opening(x, y, gx, gy)
            return
        
        # Если есть выбранный объект - ничего не делаем
        if self.selected_item:
            self.status.config(text="Сначала отмените выбор (Esc)")
            return
        
        if self.mode == "walls":
            self.wall_click(gx, gy)
        elif self.mode == "furniture":
            self.furniture_click(gx, gy)
        else:  # select
            self.select_click(x, y, gx, gy)
    
    def floor_click(self, gx, gy, x, y):
        """Клик для создания пола"""
        # Получаем полигон комнаты
        room_polygon = self.get_room_polygon()
        
        if not room_polygon:
            self.status.config(text="Сначала создайте замкнутый контур стен")
            return
        
        # Проверяем, что точка внутри комнаты
        if not self.is_point_inside_polygon(gx, gy, room_polygon):
            # Пробуем найти ближайшую точку на стене
            closest_point = self.find_closest_wall_point(gx, gy)
            if closest_point and self.is_point_inside_polygon(closest_point[0], closest_point[1], room_polygon):
                gx, gy = closest_point
                x = 50 + gx * self.PIXELS_PER_METER
                y = 50 + gy * self.PIXELS_PER_METER
                self.status.config(text="Точка привязана к стене")
            else:
                self.status.config(text="Точка должна быть внутри стен")
                return
        
        if self.grid_snap:
            gx = round(gx / self.grid_size) * self.grid_size
            gy = round(gy / self.grid_size) * self.grid_size
            x = 50 + gx * self.PIXELS_PER_METER
            y = 50 + gy * self.PIXELS_PER_METER
        
        # Проверяем, не слишком ли близко к предыдущим точкам
        for existing_gx, existing_gy in self.floor_points:
            dist = math.sqrt((gx - existing_gx)**2 + (gy - existing_gy)**2)
            if dist < 0.3:
                self.status.config(text="Точка слишком близко к существующей")
                return
        
        self.floor_points.append((gx, gy))
        self.draw_floor_preview()
        self.status.config(text=f"Точка {len(self.floor_points)} добавлена. Нажмите Enter для завершения")
    
    def find_closest_wall_point(self, x, y):
        """Найти ближайшую точку на стене"""
        closest_point = None
        min_dist = float('inf')
        
        for wall in self.walls:
            # Проверяем расстояние до линии стены
            x1, y1 = wall.x1, wall.y1
            x2, y2 = wall.x2, wall.y2
            
            # Вектор стены
            dx = x2 - x1
            dy = y2 - y1
            length = math.sqrt(dx**2 + dy**2)
            
            if length == 0:
                continue
            
            # Находим проекцию точки на линию
            t = ((x - x1) * dx + (y - y1) * dy) / (length ** 2)
            t = max(0, min(1, t))
            
            # Точка проекции
            px = x1 + t * dx
            py = y1 + t * dy
            
            # Расстояние до линии
            dist = math.sqrt((x - px)**2 + (y - py)**2)
            
            if dist < wall.thickness and dist < min_dist:
                min_dist = dist
                closest_point = (px, py)
            
            # Проверяем концы стены
            dist_to_start = math.sqrt((x - x1)**2 + (y - y1)**2)
            if dist_to_start < wall.thickness and dist_to_start < min_dist:
                min_dist = dist_to_start
                closest_point = (x1, y1)
            
            dist_to_end = math.sqrt((x - x2)**2 + (y - y2)**2)
            if dist_to_end < wall.thickness and dist_to_end < min_dist:
                min_dist = dist_to_end
                closest_point = (x2, y2)
        
        return closest_point
    
    def draw_floor_preview(self):
        """Предпросмотр пола"""
        self.canvas.delete("floor_preview")
        self.canvas.delete("floor_preview_line")
        
        if len(self.floor_points) < 1:
            return
        
        # Сортируем точки для предпросмотра
        sorted_points = self.sort_points_clockwise(self.floor_points)
        
        # Рисуем линии между точками
        points_px = []
        for i, (gx, gy) in enumerate(sorted_points):
            x = 50 + gx * self.PIXELS_PER_METER
            y = 50 + gy * self.PIXELS_PER_METER
            points_px.append((x, y))
            
            # Рисуем точку с номером
            color = self.select_color if i == len(sorted_points) - 1 else self.accent_color
            self.canvas.create_oval(x-6, y-6, x+6, y+6, fill=color,
                                   outline='black', width=2, tags="floor_preview")
            self.canvas.create_text(x, y-15, text=str(i+1), fill=color,
                                   font=("Arial", 10, "bold"), tags="floor_preview")
        
        # Рисуем линии между точками
        if len(points_px) >= 2:
            for i in range(len(points_px)):
                x1, y1 = points_px[i]
                x2, y2 = points_px[(i + 1) % len(points_px)]
                self.canvas.create_line(x1, y1, x2, y2, fill=self.select_color,
                                       width=3, dash=(5, 5), tags="floor_preview")
        
        # Если есть выбранный тип пола и минимум 3 точки, показываем предпросмотр заливки
        if len(points_px) >= 3 and self.selected_floor_type:
            # Проверяем, что полигон не самопересекается
            if not self.is_polygon_self_intersecting(sorted_points):
                # Показываем предпросмотр с полупрозрачной заливкой
                self.canvas.create_polygon(points_px, 
                                          fill=self.selected_floor_type["color"],
                                          stipple='gray50', 
                                          outline=self.select_color,
                                          width=2, 
                                          tags="floor_preview")
                
                # Добавляем подпись с площадью
                area = self.calculate_polygon_area(sorted_points)
                center_x = sum(p[0] for p in points_px) / len(points_px)
                center_y = sum(p[1] for p in points_px) / len(points_px)
                self.canvas.create_text(center_x, center_y, 
                                       text=f"Площадь: {area:.1f} м²",
                                       fill=self.select_color, 
                                       font=("Arial", 10, "bold"),
                                       tags="floor_preview")
            else:
                # Предупреждение о самопересечении
                self.canvas.create_text(points_px[0][0], points_px[0][1] - 30,
                                       text="⚠️ Самопересечение!",
                                       fill="red", font=("Arial", 10, "bold"),
                                       tags="floor_preview")
    
    def is_polygon_self_intersecting(self, points):
        """Проверка на самопересечение полигона"""
        n = len(points)
        if n < 4:
            return False
        
        def on_segment(p, q, r):
            if (q[0] <= max(p[0], r[0]) and q[0] >= min(p[0], r[0]) and
                q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1])):
                return True
            return False
        
        def orientation(p, q, r):
            val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
            if abs(val) < 1e-10:
                return 0
            return 1 if val > 0 else 2
        
        for i in range(n):
            p1 = points[i]
            p2 = points[(i + 1) % n]
            
            for j in range(i + 1, n):
                if j == i or j == (i + 1) % n or j == (i - 1) % n:
                    continue
                
                p3 = points[j]
                p4 = points[(j + 1) % n]
                
                o1 = orientation(p1, p2, p3)
                o2 = orientation(p1, p2, p4)
                o3 = orientation(p3, p4, p1)
                o4 = orientation(p3, p4, p2)
                
                if o1 != o2 and o3 != o4:
                    return True
                
                if o1 == 0 and on_segment(p1, p3, p2):
                    return True
                if o2 == 0 and on_segment(p1, p4, p2):
                    return True
                if o3 == 0 and on_segment(p3, p1, p4):
                    return True
                if o4 == 0 and on_segment(p3, p2, p4):
                    return True
        
        return False
    
    def calculate_polygon_area(self, points):
        """Вычисление площади полигона"""
        if len(points) < 3:
            return 0
        
        area = 0
        n = len(points)
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]
            area += x1 * y2 - x2 * y1
        
        return abs(area) / 2
    
    def add_opening(self, x, y, gx, gy):
        """Добавить дверь или окно в стену"""
        # Ищем ближайшую стену
        closest_wall = None
        min_dist = float('inf')
        closest_point = None
        
        for wall in self.walls:
            # Находим проекцию точки на стену
            wx1, wy1 = wall.x1, wall.y1
            wx2, wy2 = wall.x2, wall.y2
            
            # Вектор стены
            dx = wx2 - wx1
            dy = wy2 - wy1
            length = math.sqrt(dx**2 + dy**2)
            
            if length == 0:
                continue
            
            # Нормализованный вектор
            nx = dx / length
            ny = dy / length
            
            # Вектор от начала стены до точки
            vx = gx - wx1
            vy = gy - wy1
            
            # Проекция на стену
            t = (vx * nx + vy * ny) / length
            t = max(0, min(1, t))  # ограничиваем от 0 до 1
            
            # Точка проекции
            px = wx1 + t * dx
            py = wy1 + t * dy
            
            # Расстояние до стены
            dist = math.sqrt((gx - px)**2 + (gy - py)**2)
            
            # Проверяем, что точка достаточно близка к стене
            if dist < wall.thickness * 2 and dist < min_dist:
                min_dist = dist
                closest_wall = wall
                closest_point = t
        
        if closest_wall and min_dist < 0.5:
            if self.adding_mode == "door":
                width = float(self.door_width_var.get())
                door = Door(closest_point, width)
                closest_wall.doors.append(door)
                self.status.config(text=f"Дверь добавлена в стену")
            else:
                width = float(self.window_width_var.get())
                window = Window(closest_point, width)
                closest_wall.windows.append(window)
                self.status.config(text=f"Окно добавлено в стену")
            
            self.adding_mode = None
            self.canvas.delete("opening_preview")
            self.redraw()
        else:
            self.status.config(text="Кликните ближе к стене")
    
    def wall_click(self, gx, gy):
        """Клик для стены"""
        # Прилипание к сетке
        if self.grid_snap:
            gx = round(gx / self.grid_size) * self.grid_size
            gy = round(gy / self.grid_size) * self.grid_size
        
        # Прилипание к стенам
        snap = self.snap_to_walls(gx, gy)
        if snap:
            gx, gy = snap
        
        if self.current_wall_start is None:
            self.current_wall_start = (gx, gy)
            self.status.config(text=f"Начало: ({gx:.2f}, {gy:.2f})")
        else:
            try:
                thick = float(self.thickness_var.get())
            except:
                thick = 0.2
            
            wall = Wall(
                self.current_wall_start[0], self.current_wall_start[1],
                gx, gy, thick, self.wall_colors["walls"]
            )
            self.walls.append(wall)
            
            # Перерисовываем с правильным порядком слоев
            self.redraw()
            
            self.status.config(text=f"Стена создана")
            self.current_wall_start = None
            self.canvas.delete("preview")
            self.update_info()
    
    def furniture_click(self, gx, gy):
        """Клик для мебели"""
        if not self.selected_furniture_type:
            self.status.config(text="Сначала выберите мебель из списка сверху")
            return
        
        if self.grid_snap:
            gx = round(gx / self.grid_size) * self.grid_size
            gy = round(gy / self.grid_size) * self.grid_size
        
        f = self.selected_furniture_type
        furn = Furniture(f["name"], f["w"], f["h"], f["color"], f["icon"], f["category"], gx, gy)
        self.furniture.append(furn)
        
        # Перерисовываем с правильным порядком слоев
        self.redraw()
        
        self.status.config(text=f"Размещено: {f['name']}")
        self.furniture_preview = None
        self.canvas.delete("furniture_preview")
        self.update_info()
    
    def select_click(self, x, y, gx, gy):
        """Клик для выбора"""
        items = self.canvas.find_overlapping(x-5, y-5, x+5, y+5)
        
        # Ищем мебель (сначала мебель, чтобы можно было сразу тащить)
        for item in items:
            for furn in self.furniture:
                if hasattr(furn, 'canvas_ids') and item in furn.canvas_ids:
                    self.select_item(furn)
                    # Запоминаем смещение для перетаскивания
                    self.drag_furniture = furn
                    self.drag_offset_x = gx - furn.x
                    self.drag_offset_y = gy - furn.y
                    return
        
        # Ищем стены
        for item in items:
            for wall in self.walls:
                if hasattr(wall, 'canvas_id') and wall.canvas_id == item:
                    self.select_item(wall)
                    self.drag_data = (gx, gy, "wall", wall)
                    return
        
        # Ищем пол
        for item in items:
            for floor in self.floors:
                if hasattr(floor, 'canvas_id') and floor.canvas_id == item:
                    self.select_item(floor)
                    return
        
        # Клик в пустоту - снимаем выбор
        self.cancel_select()
    
    def select_item(self, item):
        """Выделить объект"""
        self.cancel_select()  # снимаем предыдущее
        
        self.selected_item = item
        
        if isinstance(item, Wall):
            self.canvas.itemconfig(item.canvas_id, outline=self.select_color, width=3)
            self.status.config(text="Стена выбрана")
        elif isinstance(item, Floor):
            self.canvas.itemconfig(item.canvas_id, outline=self.select_color, width=3)
            self.status.config(text=f"Пол выбран: {item.floor_type}")
        else:
            # Мебель
            for i, cid in enumerate(item.canvas_ids):
                if i == 0:  # прямоугольник
                    self.canvas.itemconfig(cid, outline=self.select_color, width=3)
                else:  # текст
                    self.canvas.itemconfig(cid, fill=self.select_color)
            
            self.status.config(text=f"Выбрано: {item.name}")
    
    def cancel_select(self):
        """Отменить выбор"""
        if self.selected_item:
            if isinstance(self.selected_item, Wall):
                self.canvas.itemconfig(self.selected_item.canvas_id, outline='black', width=1)
            elif isinstance(self.selected_item, Floor):
                self.canvas.itemconfig(self.selected_item.canvas_id, outline='black', width=1)
            else:
                for i, cid in enumerate(self.selected_item.canvas_ids):
                    if i == 0:  # прямоугольник
                        self.canvas.itemconfig(cid, outline='black', width=2)
                    else:  # текст
                        self.canvas.itemconfig(cid, fill='black')
            
            # Сохраняем имя объекта для сообщения
            if isinstance(self.selected_item, Wall):
                obj_name = "стена"
            elif isinstance(self.selected_item, Floor):
                obj_name = f"пол ({self.selected_item.floor_type})"
            else:
                obj_name = self.selected_item.name
            
            self.selected_item = None
            self.status.config(text=f"Выбор отменен: {obj_name}")
        
        self.current_wall_start = None
        self.adding_mode = None
        self.furniture_preview = None
        self.canvas.delete("preview")
        self.canvas.delete("opening_preview")
        self.canvas.delete("furniture_preview")
        self.drag_data = None
        self.drag_furniture = None
    
    def snap_to_walls(self, x, y):
        """Прилипание к стенам"""
        closest = None
        min_dist = self.SNAP_THRESHOLD
        
        for wall in self.walls:
            # Концы стен
            d1 = math.sqrt((x - wall.x1)**2 + (y - wall.y1)**2)
            if d1 < min_dist:
                min_dist = d1
                closest = (wall.x1, wall.y1)
            
            d2 = math.sqrt((x - wall.x2)**2 + (y - wall.y2)**2)
            if d2 < min_dist:
                min_dist = d2
                closest = (wall.x2, wall.y2)
        
        return closest
    
    def on_mouse_move(self, event):
        """Движение мыши"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.floor_mode:
            # Показываем текущую линию
            self.draw_floor_preview()
            if self.floor_points:
                last_x = 50 + self.floor_points[-1][0] * self.PIXELS_PER_METER
                last_y = 50 + self.floor_points[-1][1] * self.PIXELS_PER_METER
                self.canvas.create_line(last_x, last_y, x, y, fill=self.select_color,
                                       width=2, dash=(5, 5), tags="floor_preview_line")
        elif self.mode == "walls" and self.current_wall_start:
            self.draw_preview(x, y)
        elif self.mode == "furniture" and self.selected_furniture_type:
            self.show_furniture_preview(x, y)
        elif self.mode == "select":
            self.check_hover(x, y)
        elif self.adding_mode:
            self.show_opening_preview(x, y)
    
    def show_furniture_preview(self, x, y):
        """Показать предпросмотр мебели"""
        self.canvas.delete("furniture_preview")
        
        gx = (x - 50) / self.PIXELS_PER_METER
        gy = (y - 50) / self.PIXELS_PER_METER
        
        if self.grid_snap:
            gx = round(gx / self.grid_size) * self.grid_size
            gy = round(gy / self.grid_size) * self.grid_size
            x = 50 + gx * self.PIXELS_PER_METER
            y = 50 + gy * self.PIXELS_PER_METER
        
        f = self.selected_furniture_type
        w = f["w"] * self.PIXELS_PER_METER
        h = f["h"] * self.PIXELS_PER_METER
        
        # Рисуем предпросмотр мебели
        self.canvas.create_rectangle(
            x - w/2, y - h/2, x + w/2, y + h/2,
            outline=self.select_color, width=2, dash=(5, 5),
            fill='', tags="furniture_preview"
        )
        
        self.canvas.create_text(
            x, y, text=f["icon"],
            font=("Arial", int(min(w, h)/2)),
            fill=self.select_color, tags="furniture_preview"
        )
        
        # Подпись с размерами
        self.canvas.create_text(
            x, y - h/2 - 10,
            text=f"{f['name']} ({f['w']}x{f['h']}м)",
            fill=self.select_color, font=("Arial", 8),
            tags="furniture_preview"
        )
    
    def show_opening_preview(self, x, y):
        """Показать предпросмотр двери/окна"""
        self.canvas.delete("opening_preview")
        
        gx = (x - 50) / self.PIXELS_PER_METER
        gy = (y - 50) / self.PIXELS_PER_METER
        
        # Ищем ближайшую стену
        for wall in self.walls:
            wx1, wy1 = wall.x1, wall.y1
            wx2, wy2 = wall.x2, wall.y2
            
            dx = wx2 - wx1
            dy = wy2 - wy1
            length = math.sqrt(dx**2 + dy**2)
            
            if length == 0:
                continue
            
            nx = dx / length
            ny = dy / length
            
            vx = gx - wx1
            vy = gy - wy1
            
            t = (vx * nx + vy * ny) / length
            t = max(0, min(1, t))
            
            px = wx1 + t * dx
            py = wy1 + t * dy
            
            dist = math.sqrt((gx - px)**2 + (gy - py)**2)
            
            if dist < wall.thickness * 2:
                # Рисуем предпросмотр
                x1 = 50 + px * self.PIXELS_PER_METER
                y1 = 50 + py * self.PIXELS_PER_METER
                
                # Перпендикуляр
                perp_x = -dy / length * wall.thickness * self.PIXELS_PER_METER / 2
                perp_y = dx / length * wall.thickness * self.PIXELS_PER_METER / 2
                
                width = float(self.door_width_var.get() if self.adding_mode == "door" else self.window_width_var.get())
                width_px = width * self.PIXELS_PER_METER
                
                color = self.select_color
                
                # Рисуем прямоугольник
                self.canvas.create_rectangle(
                    x1 - width_px/2 - perp_x, y1 - width_px/2 - perp_y,
                    x1 + width_px/2 - perp_x, y1 + width_px/2 - perp_y,
                    outline=color, width=2, dash=(5, 5), tags="opening_preview"
                )
                
                # Подпись
                self.canvas.create_text(
                    x1, y1 - 20,
                    text=f"{'Дверь' if self.adding_mode == 'door' else 'Окно'} {width:.1f}м",
                    fill=color, font=("Arial", 8), tags="opening_preview"
                )
                break
    
    def draw_preview(self, x, y):
        """Предпросмотр стены"""
        self.canvas.delete("preview")
        
        gx = (x - 50) / self.PIXELS_PER_METER
        gy = (y - 50) / self.PIXELS_PER_METER
        
        if self.grid_snap:
            gx = round(gx / self.grid_size) * self.grid_size
            gy = round(gy / self.grid_size) * self.grid_size
            x = 50 + gx * self.PIXELS_PER_METER
            y = 50 + gy * self.PIXELS_PER_METER
        
        snap = self.snap_to_walls(gx, gy)
        if snap:
            gx, gy = snap
            x = 50 + gx * self.PIXELS_PER_METER
            y = 50 + gy * self.PIXELS_PER_METER
        
        sx = 50 + self.current_wall_start[0] * self.PIXELS_PER_METER
        sy = 50 + self.current_wall_start[1] * self.PIXELS_PER_METER
        
        self.canvas.create_line(sx, sy, x, y, fill=self.select_color, width=3, dash=(5, 5), tags="preview")
        
        length = math.sqrt((gx - self.current_wall_start[0])**2 + (gy - self.current_wall_start[1])**2)
        mx, my = (sx + x)/2, (sy + y)/2
        self.canvas.create_text(mx, my - 20, text=f"{length:.2f}м", fill=self.select_color, tags="preview")
    
    def check_hover(self, x, y):
        """Проверка наведения"""
        items = self.canvas.find_overlapping(x-3, y-3, x+3, y+3)
        
        # Убираем старую подсветку
        if self.highlighted_item:
            if isinstance(self.highlighted_item, Wall):
                self.canvas.itemconfig(self.highlighted_item.canvas_id, outline='black', width=1)
            elif isinstance(self.highlighted_item, Floor):
                self.canvas.itemconfig(self.highlighted_item.canvas_id, outline='black', width=1)
            else:
                for i, cid in enumerate(self.highlighted_item.canvas_ids):
                    if i == 0:
                        self.canvas.itemconfig(cid, outline='black', width=2)
                    else:
                        self.canvas.itemconfig(cid, fill='black')
            self.highlighted_item = None
        
        # Подсвечиваем новый
        for item in items:
            for wall in self.walls:
                if hasattr(wall, 'canvas_id') and wall.canvas_id == item:
                    self.canvas.itemconfig(wall.canvas_id, outline='blue', width=3)
                    self.highlighted_item = wall
                    return
            
            for furn in self.furniture:
                if hasattr(furn, 'canvas_ids') and item in furn.canvas_ids:
                    for i, cid in enumerate(furn.canvas_ids):
                        if i == 0:
                            self.canvas.itemconfig(cid, outline='blue', width=3)
                        else:
                            self.canvas.itemconfig(cid, fill='blue')
                    self.highlighted_item = furn
                    return
            
            for floor in self.floors:
                if hasattr(floor, 'canvas_id') and floor.canvas_id == item:
                    self.canvas.itemconfig(floor.canvas_id, outline='blue', width=3)
                    self.highlighted_item = floor
                    return
    
    def on_mouse_leave(self, event):
        """Мышь ушла"""
        if self.highlighted_item:
            if isinstance(self.highlighted_item, Wall):
                self.canvas.itemconfig(self.highlighted_item.canvas_id, outline='black', width=1)
            elif isinstance(self.highlighted_item, Floor):
                self.canvas.itemconfig(self.highlighted_item.canvas_id, outline='black', width=1)
            else:
                for i, cid in enumerate(self.highlighted_item.canvas_ids):
                    if i == 0:
                        self.canvas.itemconfig(cid, outline='black', width=2)
                    else:
                        self.canvas.itemconfig(cid, fill='black')
            self.highlighted_item = None
        self.canvas.delete("opening_preview")
        self.canvas.delete("furniture_preview")
        self.canvas.delete("floor_preview_line")
    
    def on_drag(self, event):
        """Перетаскивание"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        gx = (x - 50) / self.PIXELS_PER_METER
        gy = (y - 50) / self.PIXELS_PER_METER
        
        if self.grid_snap:
            gx = round(gx / self.grid_size) * self.grid_size
            gy = round(gy / self.grid_size) * self.grid_size
        
        # Перетаскивание мебели
        if self.drag_furniture and self.mode == "select":
            # Новые координаты с учетом смещения
            new_x = gx - self.drag_offset_x
            new_y = gy - self.drag_offset_y
            
            if self.grid_snap:
                new_x = round(new_x / self.grid_size) * self.grid_size
                new_y = round(new_y / self.grid_size) * self.grid_size
            
            # Обновляем позицию
            furn = self.drag_furniture
            furn.x = new_x
            furn.y = new_y
            
            # Перерисовываем
            self.canvas.delete(f"furniture_{id(furn)}")
            self.draw_furniture(furn)
            
            # Если мебель была выделена, возвращаем выделение
            if self.selected_item == furn:
                for i, cid in enumerate(furn.canvas_ids):
                    if i == 0:
                        self.canvas.itemconfig(cid, outline=self.select_color, width=3)
                    else:
                        self.canvas.itemconfig(cid, fill=self.select_color)
        
        # Перетаскивание стены
        elif self.drag_data and self.mode == "select" and self.selected_item:
            _, _, typ, item = self.drag_data
            if typ == "wall":
                # Перемещаем конец стены
                d1 = math.sqrt((gx - item.x1)**2 + (gy - item.y1)**2)
                d2 = math.sqrt((gx - item.x2)**2 + (gy - item.y2)**2)
                
                snap = self.snap_to_walls(gx, gy)
                if snap:
                    gx, gy = snap
                
                if d1 < d2:
                    item.x1, item.y1 = gx, gy
                else:
                    item.x2, item.y2 = gx, gy
                
                self.canvas.delete(f"wall_{id(item)}")
                self.draw_wall(item)
                self.canvas.itemconfig(item.canvas_id, outline=self.select_color, width=3)
    
    def on_release(self, event):
        """Отпускание"""
        self.drag_data = None
        self.drag_furniture = None
        self.update_info()
    
    def on_right_click(self, event):
        """Правый клик"""
        if self.selected_item:
            return
            
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        items = self.canvas.find_overlapping(x-5, y-5, x+5, y+5)
        
        for item in items:
            for wall in self.walls:
                if hasattr(wall, 'canvas_id') and wall.canvas_id == item:
                    self.select_item(wall)
                    menu = tk.Menu(self.root, tearoff=0, bg=self.bg_medium, fg=self.fg_color,
                                 activebackground=self.bg_light, activeforeground=self.fg_color)
                    menu.add_command(label="Удалить", command=self.delete_selected)
                    menu.add_command(label="Цвет", command=self.change_wall_color)
                    menu.add_separator()
                    menu.add_command(label="Добавить дверь", 
                                   command=lambda w=wall: self.add_door_to_wall(w))
                    menu.add_command(label="Добавить окно", 
                                   command=lambda w=wall: self.add_window_to_wall(w))
                    menu.post(event.x_root, event.y_root)
                    return
            
            for furn in self.furniture:
                if hasattr(furn, 'canvas_ids') and item in furn.canvas_ids:
                    self.select_item(furn)
                    menu = tk.Menu(self.root, tearoff=0, bg=self.bg_medium, fg=self.fg_color,
                                 activebackground=self.bg_light, activeforeground=self.fg_color)
                    menu.add_command(label="Удалить", command=self.delete_selected)
                    menu.add_command(label="Повернуть", command=self.rotate_selected)
                    menu.add_command(label="Цвет", command=self.change_furniture_color)
                    menu.post(event.x_root, event.y_root)
                    return
            
            for floor in self.floors:
                if hasattr(floor, 'canvas_id') and floor.canvas_id == item:
                    self.select_item(floor)
                    menu = tk.Menu(self.root, tearoff=0, bg=self.bg_medium, fg=self.fg_color,
                                 activebackground=self.bg_light, activeforeground=self.fg_color)
                    menu.add_command(label="Удалить", command=self.delete_selected)
                    menu.post(event.x_root, event.y_root)
                    return
    
    def add_door_to_wall(self, wall):
        """Добавить дверь в стену (через меню)"""
        self.adding_mode = "door"
        self.status.config(text="Нажмите на стену в месте где добавить дверь")
    
    def add_window_to_wall(self, wall):
        """Добавить окно в стену (через меню)"""
        self.adding_mode = "window"
        self.status.config(text="Нажмите на стену в месте где добавить окно")
    
    def draw_grid(self):
        """Рисование сетки и объектов"""
        self.canvas.delete("all")
        
        # Сетка
        for i in range(-10, 51):
            x = 50 + i * self.PIXELS_PER_METER
            self.canvas.create_line(x, 50 - 10*self.PIXELS_PER_METER,
                                   x, 50 + 50*self.PIXELS_PER_METER,
                                   fill='lightgray', dash=(2, 4), tags="grid")
            
            y = 50 + i * self.PIXELS_PER_METER
            self.canvas.create_line(50 - 10*self.PIXELS_PER_METER, y,
                                   50 + 50*self.PIXELS_PER_METER, y,
                                   fill='lightgray', dash=(2, 4), tags="grid")
        
        # Сначала рисуем полы (самый нижний слой)
        for floor in self.floors:
            self.draw_floor(floor)
        
        # Потом мебель (средний слой)
        for furn in self.furniture:
            self.draw_furniture(furn)
        
        # Потом стены (самый верхний слой)
        for wall in self.walls:
            self.draw_wall(wall)
    
    def redraw(self):
        """Перерисовать"""
        self.draw_grid()
        if self.selected_item:
            self.select_item(self.selected_item)
    
    def draw_wall(self, wall):
        """Рисование стены с дверями и окнами"""
        x1 = 50 + wall.x1 * self.PIXELS_PER_METER
        y1 = 50 + wall.y1 * self.PIXELS_PER_METER
        x2 = 50 + wall.x2 * self.PIXELS_PER_METER
        y2 = 50 + wall.y2 * self.PIXELS_PER_METER
        
        dx, dy = x2 - x1, y2 - y1
        length = math.sqrt(dx**2 + dy**2)
        
        if length > 0:
            px = -dy / length * wall.thickness * self.PIXELS_PER_METER / 2
            py = dx / length * wall.thickness * self.PIXELS_PER_METER / 2
            
            # Рисуем стену
            points = [
                x1 + px, y1 + py,
                x2 + px, y2 + py,
                x2 - px, y2 - py,
                x1 - px, y1 - py
            ]
            
            wall.canvas_id = self.canvas.create_polygon(
                points, fill=wall.color, outline='black', width=1,
                tags=("wall", f"wall_{id(wall)}")
            )
            
            # Поднимаем стену на самый верх
            self.canvas.tag_raise(wall.canvas_id)
            
            # Рисуем двери
            for door in wall.doors:
                self.draw_door(wall, door, x1, y1, x2, y2, dx, dy, length, px, py)
            
            # Рисуем окна
            for window in wall.windows:
                self.draw_window(wall, window, x1, y1, x2, y2, dx, dy, length, px, py)
            
            # Длина стены
            mx, my = (x1 + x2)/2, (y1 + y2)/2
            self.canvas.create_text(mx, my, text=f"{self.wall_length(wall):.1f}м",
                                   font=("Arial", 8), tags=f"wall_{id(wall)}")
    
    def draw_door(self, wall, door, x1, y1, x2, y2, dx, dy, length, px, py):
        """Рисование двери"""
        # Позиция вдоль стены
        t = door.position
        mx = x1 + t * dx
        my = y1 + t * dy
        
        # Ширина двери в пикселях
        door_width = door.width * self.PIXELS_PER_METER
        
        # Рисуем прямоугольник двери
        door_id = self.canvas.create_rectangle(
            mx - door_width/2 - px, my - door_width/2 - py,
            mx + door_width/2 - px, my + door_width/2 - py,
            fill=door.color, outline='black', width=2,
            tags=f"door_{id(wall)}_{id(door)}"
        )
        # Поднимаем дверь над стеной
        self.canvas.tag_raise(door_id)
    
    def draw_window(self, wall, window, x1, y1, x2, y2, dx, dy, length, px, py):
        """Рисование окна"""
        # Позиция вдоль стены
        t = window.position
        mx = x1 + t * dx
        my = y1 + t * dy
        
        # Ширина окна в пикселях
        window_width = window.width * self.PIXELS_PER_METER
        
        # Рисуем прямоугольник окна
        window_id = self.canvas.create_rectangle(
            mx - window_width/2 - px, my - window_width/2 - py,
            mx + window_width/2 - px, my + window_width/2 - py,
            fill=window.color, outline='black', width=2,
            tags=f"window_{id(wall)}_{id(window)}"
        )
        
        # Рисуем крест (переплет окна)
        line1_id = self.canvas.create_line(
            mx - window_width/2 - px, my - window_width/2 - py,
            mx + window_width/2 - px, my + window_width/2 - py,
            fill='black', width=1, tags=f"window_{id(wall)}_{id(window)}"
        )
        line2_id = self.canvas.create_line(
            mx - window_width/2 - px, my + window_width/2 - py,
            mx + window_width/2 - px, my - window_width/2 - py,
            fill='black', width=1, tags=f"window_{id(wall)}_{id(window)}"
        )
        
        # Поднимаем окно над стеной
        self.canvas.tag_raise(window_id)
        self.canvas.tag_raise(line1_id)
        self.canvas.tag_raise(line2_id)
    
    def draw_furniture(self, furn):
        """Рисование мебели"""
        x = 50 + furn.x * self.PIXELS_PER_METER
        y = 50 + furn.y * self.PIXELS_PER_METER
        w = furn.width * self.PIXELS_PER_METER
        h = furn.height * self.PIXELS_PER_METER
        
        rect = self.canvas.create_rectangle(
            x - w/2, y - h/2, x + w/2, y + h/2,
            fill=furn.color, outline='black', width=2,
            tags=("furniture", f"furniture_{id(furn)}")
        )
        
        text = self.canvas.create_text(
            x, y, text=furn.icon,
            font=("Arial", int(min(w, h)/2)), fill='black',
            tags=("furniture", f"furniture_{id(furn)}")
        )
        
        furn.canvas_ids = [rect, text]
        
        # Поднимаем мебель над полом, но оставляем под стенами
        self.canvas.tag_raise(rect)
        self.canvas.tag_raise(text)
    
    def draw_floor(self, floor):
        """Рисование пола с текстурой"""
        points_px = []
        for gx, gy in floor.points:
            x = 50 + gx * self.PIXELS_PER_METER
            y = 50 + gy * self.PIXELS_PER_METER
            points_px.append((x, y))
        
        # Рисуем основной полигон (самый нижний слой)
        floor.canvas_id = self.canvas.create_polygon(
            points_px, fill=floor.color, outline='black', width=1,
            stipple='', tags=("floor", f"floor_{id(floor)}")
        )
        
        # Опускаем пол в самый низ
        self.canvas.tag_lower(floor.canvas_id)
        
        # Добавляем текстуру в зависимости от типа
        self.add_floor_texture(floor, points_px)
    
    def add_floor_texture(self, floor, points_px):
        """Добавление текстуры к полу"""
        if floor.pattern == "wood_plank":
            self.draw_wood_plank_texture(floor, points_px)
        elif floor.pattern == "wood_light":
            self.draw_wood_light_texture(floor, points_px)
        elif floor.pattern == "wood_dark":
            self.draw_wood_dark_texture(floor, points_px)
        elif floor.pattern == "tile_grid":
            self.draw_tile_grid_texture(floor, points_px)
        elif floor.pattern == "marble":
            self.draw_marble_texture(floor, points_px)
        elif floor.pattern == "carpet":
            self.draw_carpet_texture(floor, points_px)
        elif floor.pattern == "concrete":
            self.draw_concrete_texture(floor, points_px)
        elif floor.pattern == "stone":
            self.draw_stone_texture(floor, points_px)
        elif floor.pattern == "mosaic":
            self.draw_mosaic_texture(floor, points_px)
    
    def draw_wood_plank_texture(self, floor, points_px):
        """Текстура паркета"""
        xs = [p[0] for p in points_px]
        ys = [p[1] for p in points_px]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        # Рисуем линии-доски
        for y in range(int(min_y), int(max_y), 20):
            line_id = self.canvas.create_line(min_x, y, max_x, y, fill='#8B4513',
                                            width=1, tags=f"floor_texture_{id(floor)}")
            self.canvas.tag_lower(line_id)
        
        # Короткие поперечные линии
        for x in range(int(min_x), int(max_x), 40):
            line_id = self.canvas.create_line(x, min_y, x, max_y, fill='#8B4513',
                                            width=1, tags=f"floor_texture_{id(floor)}")
            self.canvas.tag_lower(line_id)
    
    def draw_wood_light_texture(self, floor, points_px):
        """Светлая древесная текстура"""
        xs = [p[0] for p in points_px]
        ys = [p[1] for p in points_px]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        for y in range(int(min_y), int(max_y), 15):
            line_id = self.canvas.create_line(min_x, y, max_x, y, fill='#A0522D',
                                            width=1, tags=f"floor_texture_{id(floor)}")
            self.canvas.tag_lower(line_id)
    
    def draw_wood_dark_texture(self, floor, points_px):
        """Темная древесная текстура"""
        xs = [p[0] for p in points_px]
        ys = [p[1] for p in points_px]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        for y in range(int(min_y), int(max_y), 25):
            line_id = self.canvas.create_line(min_x, y, max_x, y, fill='#5D3A1A',
                                            width=2, tags=f"floor_texture_{id(floor)}")
            self.canvas.tag_lower(line_id)
    
    def draw_tile_grid_texture(self, floor, points_px):
        """Сетка плитки"""
        xs = [p[0] for p in points_px]
        ys = [p[1] for p in points_px]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        tile_size = 30
        for x in range(int(min_x), int(max_x), tile_size):
            line_id = self.canvas.create_line(x, min_y, x, max_y, fill='black',
                                            width=1, tags=f"floor_texture_{id(floor)}")
            self.canvas.tag_lower(line_id)
        for y in range(int(min_y), int(max_y), tile_size):
            line_id = self.canvas.create_line(min_x, y, max_x, y, fill='black',
                                            width=1, tags=f"floor_texture_{id(floor)}")
            self.canvas.tag_lower(line_id)
    
    def draw_marble_texture(self, floor, points_px):
        """Мраморная текстура"""
        xs = [p[0] for p in points_px]
        ys = [p[1] for p in points_px]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        for _ in range(50):
            x1 = random.uniform(min_x, max_x)
            y1 = random.uniform(min_y, max_y)
            x2 = x1 + random.uniform(-20, 20)
            y2 = y1 + random.uniform(-20, 20)
            line_id = self.canvas.create_line(x1, y1, x2, y2, fill='#A9A9A9',
                                            width=random.randint(1, 2),
                                            tags=f"floor_texture_{id(floor)}")
            self.canvas.tag_lower(line_id)
    
    def draw_carpet_texture(self, floor, points_px):
        """Ковровая текстура"""
        xs = [p[0] for p in points_px]
        ys = [p[1] for p in points_px]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        for _ in range(200):
            x = random.uniform(min_x, max_x)
            y = random.uniform(min_y, max_y)
            dot_id = self.canvas.create_oval(x-1, y-1, x+1, y+1, fill='#5D3A1A',
                                           outline='', tags=f"floor_texture_{id(floor)}")
            self.canvas.tag_lower(dot_id)
    
    def draw_concrete_texture(self, floor, points_px):
        """Бетонная текстура"""
        xs = [p[0] for p in points_px]
        ys = [p[1] for p in points_px]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        for _ in range(100):
            x1 = random.uniform(min_x, max_x)
            y1 = random.uniform(min_y, max_y)
            x2 = x1 + random.uniform(-5, 5)
            y2 = y1 + random.uniform(-5, 5)
            line_id = self.canvas.create_line(x1, y1, x2, y2, fill='#696969',
                                            width=1, tags=f"floor_texture_{id(floor)}")
            self.canvas.tag_lower(line_id)
    
    def draw_stone_texture(self, floor, points_px):
        """Каменная текстура"""
        xs = [p[0] for p in points_px]
        ys = [p[1] for p in points_px]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        for _ in range(30):
            x = random.uniform(min_x, max_x)
            y = random.uniform(min_y, max_y)
            size = random.uniform(5, 15)
            oval_id = self.canvas.create_oval(x-size, y-size, x+size, y+size,
                                            outline='#696969', width=1,
                                            tags=f"floor_texture_{id(floor)}")
            self.canvas.tag_lower(oval_id)
    
    def draw_mosaic_texture(self, floor, points_px):
        """Мозаичная текстура"""
        xs = [p[0] for p in points_px]
        ys = [p[1] for p in points_px]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        size = 15
        colors = ['#CD853F', '#8B4513', '#A0522D', '#D2691E']
        
        for x in range(int(min_x), int(max_x), size):
            for y in range(int(min_y), int(max_y), size):
                color = random.choice(colors)
                rect_id = self.canvas.create_rectangle(x, y, x+size, y+size,
                                                     outline='black', fill='',
                                                     tags=f"floor_texture_{id(floor)}")
                line_id = self.canvas.create_line(x, y, x+size, y+size,
                                                fill=color, width=1,
                                                tags=f"floor_texture_{id(floor)}")
                self.canvas.tag_lower(rect_id)
                self.canvas.tag_lower(line_id)
    
    def wall_length(self, wall):
        """Длина стены"""
        return math.sqrt((wall.x2 - wall.x1)**2 + (wall.y2 - wall.y1)**2)
    
    def select_furniture(self, f):
        """Выбор мебели из каталога"""
        self.selected_furniture_type = f
        self.mode_var.set("furniture")
        self.mode = "furniture"
        self.adding_mode = None
        self.floor_mode = False
        self.status.config(text=f"Разместите {f['name']} кликом")
    
    def delete_selected(self):
        """Удалить выбранное"""
        if not self.selected_item:
            self.status.config(text="Нет выбранного объекта")
            return
        
        if isinstance(self.selected_item, Wall):
            self.canvas.delete(f"wall_{id(self.selected_item)}")
            self.walls.remove(self.selected_item)
        elif isinstance(self.selected_item, Floor):
            self.canvas.delete(f"floor_{id(self.selected_item)}")
            self.canvas.delete(f"floor_texture_{id(self.selected_item)}")
            self.floors.remove(self.selected_item)
        else:
            self.canvas.delete(f"furniture_{id(self.selected_item)}")
            self.furniture.remove(self.selected_item)
        
        self.selected_item = None
        self.update_info()
        self.status.config(text="Объект удален")
    
    def rotate_selected(self):
        """Повернуть мебель"""
        if not self.selected_item or isinstance(self.selected_item, Wall) or isinstance(self.selected_item, Floor):
            self.status.config(text="Выберите мебель для поворота")
            return
        
        f = self.selected_item
        f.rotation = (f.rotation + 90) % 360
        if f.rotation in [90, 270]:
            f.width, f.height = f.height, f.width
        
        self.canvas.delete(f"furniture_{id(f)}")
        self.draw_furniture(f)
        
        # Возвращаем выделение
        for i, cid in enumerate(f.canvas_ids):
            if i == 0:
                self.canvas.itemconfig(cid, outline=self.select_color, width=3)
            else:
                self.canvas.itemconfig(cid, fill=self.select_color)
    
    def change_wall_color(self):
        """Цвет стены"""
        if not self.selected_item or not isinstance(self.selected_item, Wall):
            return
        
        color = colorchooser.askcolor(title="Цвет стены")[1]
        if color:
            self.selected_item.color = color
            self.canvas.itemconfig(self.selected_item.canvas_id, fill=color)
    
    def change_furniture_color(self):
        """Цвет мебели"""
        if not self.selected_item or isinstance(self.selected_item, Wall) or isinstance(self.selected_item, Floor):
            return
        
        color = colorchooser.askcolor(title="Цвет мебели")[1]
        if color:
            self.selected_item.color = color
            self.canvas.delete(f"furniture_{id(self.selected_item)}")
            self.draw_furniture(self.selected_item)
            
            # Возвращаем выделение
            for i, cid in enumerate(self.selected_item.canvas_ids):
                if i == 0:
                    self.canvas.itemconfig(cid, outline=self.select_color, width=3)
                else:
                    self.canvas.itemconfig(cid, fill=self.select_color)
    
    def choose_wall_color(self):
        """Цвет стен по умолчанию"""
        color = colorchooser.askcolor(title="Цвет стен")[1]
        if color:
            self.wall_colors["walls"] = color
    
    def update_info(self):
        """Обновить информацию"""
        total = sum(self.wall_length(w) for w in self.walls)
        doors_count = sum(len(w.doors) for w in self.walls)
        windows_count = sum(len(w.windows) for w in self.walls)
        text = f"Стен: {len(self.walls)}\nДлина: {total:.1f}м\nДверей: {doors_count}\nОкон: {windows_count}\nМебель: {len(self.furniture)}\nПол: {len(self.floors)}"
        self.info_label.config(text=text)
    
    def new_project(self):
        """Новый проект"""
        if messagebox.askyesno("Новый проект", "Начать заново?"):
            self.walls.clear()
            self.furniture.clear()
            self.floors.clear()
            self.selected_item = None
            self.current_wall_start = None
            self.adding_mode = None
            self.furniture_preview = None
            self.floor_mode = False
            self.floor_points = []
            self.draw_grid()
            self.update_info()
            self.status.config(text="Новый проект")
    
    def clear_all(self):
        """Очистить всё"""
        if messagebox.askyesno("Очистить всё", "Удалить все стены, мебель и полы?"):
            self.walls.clear()
            self.furniture.clear()
            self.floors.clear()
            self.selected_item = None
            self.current_wall_start = None
            self.adding_mode = None
            self.furniture_preview = None
            self.floor_mode = False
            self.floor_points = []
            self.draw_grid()
            self.update_info()
            self.status.config(text="Всё очищено")
    
    def save_project(self):
        """Сохранить"""
        fname = filedialog.asksaveasfilename(defaultextension=".json")
        if not fname:
            return
        
        walls_data = []
        for w in self.walls:
            walls_data.append({
                "x1": w.x1, "y1": w.y1, "x2": w.x2, "y2": w.y2,
                "thickness": w.thickness, "color": w.color,
                "doors": [[d.position, d.width] for d in w.doors],
                "windows": [[w.pos.position, w.pos.width] for w.pos in w.windows]
            })
        
        furniture_data = [[f.name, f.width, f.height, f.color, f.icon, f.category, f.x, f.y, f.rotation] for f in self.furniture]
        
        floors_data = [[f.floor_type, f.color, f.pattern, f.points] for f in self.floors]
        
        data = {
            "walls": walls_data,
            "furniture": furniture_data,
            "floors": floors_data
        }
        
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.status.config(text=f"Сохранено")
    
    def load_project(self):
        """Загрузить"""
        fname = filedialog.askopenfilename()
        if not fname:
            return
        
        try:
            with open(fname, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.walls.clear()
            self.furniture.clear()
            self.floors.clear()
            
            for w_data in data["walls"]:
                wall = Wall(w_data["x1"], w_data["y1"], w_data["x2"], w_data["y2"],
                          w_data.get("thickness", 0.2), w_data.get("color", "#8B4513"))
                
                for door_data in w_data.get("doors", []):
                    door = Door(door_data[0], door_data[1])
                    wall.doors.append(door)
                
                for window_data in w_data.get("windows", []):
                    window = Window(window_data[0], window_data[1])
                    wall.windows.append(window)
                
                self.walls.append(wall)
            
            for f_data in data["furniture"]:
                furn = Furniture(f_data[0], f_data[1], f_data[2], f_data[3], f_data[4], f_data[5], f_data[6], f_data[7])
                furn.rotation = f_data[8] if len(f_data) > 8 else 0
                self.furniture.append(furn)
            
            for fl_data in data.get("floors", []):
                floor = Floor(fl_data[0], fl_data[1], fl_data[2], fl_data[3])
                self.floors.append(floor)
            
            self.draw_grid()
            self.update_info()
            self.status.config(text=f"Загружено")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")

def main():
    root = tk.Tk()
    app = InteriorDesignApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()