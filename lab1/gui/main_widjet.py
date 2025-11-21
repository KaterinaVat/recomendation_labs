import os
import sys
import time
from typing import Any, Dict, List

from PySide6 import QtCore, QtGui, QtWidgets

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from api.spell_check_pro import SpellCheckProApi
from api.textgears_api import TextGrearsApi
from config import API_HOST_API2, API_HOST_API1, RAPIDAPI_KEY

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.api_1 = TextGrearsApi(
            api_key=RAPIDAPI_KEY,
            base_url=API_HOST_API1
        )
        self.api_2 = SpellCheckProApi(
            api_key=RAPIDAPI_KEY,
            base_url=API_HOST_API2
        )
        self.set_display()
        self.setup_layout()

    def set_display(self)->None:
        """
        Настройка внешнего вида и стиля окна приложения.
        """
        screen = QtWidgets.QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()

        screen_width = screen_rect.width()
        screen_height = screen_rect.height()
        window_width = int(screen_width * 0.5)
        window_height = int(screen_height * 0.65)
            
        self.resize(window_width, window_height)

        self.move(
            (screen_width - window_width) // 2,
            (screen_height - window_height) // 2
        )

        self.setStyleSheet("""
            QWidget {
                background-color: #fffef7;
                }
            QPushButton {
                background-color: #ffeaa7;  
                border: 1px solid #fdcb6e; 
                border-radius: 8px;       
                padding: 10px 20px;         
                font-weight: bold;        
                font-size: 14px;
                color: #2d3436;           
            }
            QPushButton:hover {
                background-color: #fdcb6e; 
                border: 1px solid #e17055; 
            }

            QTextEdit {
                background-color: white;
                border: 2px solid #dfe6e9;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                selection-background-color: #ffeaa7;  
            }
            QLabel[objectName="title_label"] {
                color: #5d4037; 
            }
            QLabel[objectName="panel_title"] {
                color: #2d3436;   
                border-radius: 2px;
                padding: 2px;
            }
        """)

        self.text = QtWidgets.QLabel("Анализ текста на ошибки", 
                                    alignment=QtCore.Qt.AlignCenter)
        # создает новый объект типа, которому можно 
        # придавать разные характеристики начертания
        self.text.setObjectName("title_label")
        font = QtGui.QFont() 
        font.setPointSize(20)  
        font.setBold(True)     
        self.text.setFont(font)

        self.input_field = QtWidgets.QTextEdit()
        self.input_field.setPlaceholderText("Введите текст для анализа здесь...")
        self.input_field.setMaximumHeight(150)  
    
        self.button = QtWidgets.QPushButton("Выполнить проверку")
        self.button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor)) 
        #обработчик события нажатия кнопки
        self.button.clicked.connect(self.analyze_text) 
        self.results_panels()
            
    def results_panels(self) -> None:
            """
            Создает вертикальные панели для отображения результатов от двух API.
            """
            # Создаем горизонтальный разделитель для двух панелей результатов
            # п это виджет, который позволяет пользователю динамически изменять 
            # размер дочерних виджетов, перетаскивая разделитель между ними.
            self.results_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal) 
            self.results_splitter.setHandleWidth(8)  
            self.results_splitter.setChildrenCollapsible(False)  
            # Левая панель - результат первого API
            # Создается пустой виджет-контейнер, который будет служить левой 
            # панелью для отображения результатов первого API.
            self.left_panel = QtWidgets.QWidget() #контейнер виджетов

            # Создается вертикальный layout и сразу устанавливается 
            # для left_panel. 
            # Теперь все виджеты, добавленные в left_layout, будут 
            # автоматически располагаться внутри left_panel вертикально.
            # left_layout - это layout manager (менеджер компоновки), 
            # который управляет расположением виджетов внутри контейнера.
            left_layout = QtWidgets.QVBoxLayout(self.left_panel) #правила расстановки

            #виджет
            left_title = QtWidgets.QLabel(
                "Результат TextGears", alignment=QtCore.Qt.AlignCenter
                )
            
            # Для применения стиля заголовков панелей
            left_title.setObjectName("panel_title") 

            # создает новый объект типа, которому можно придавать 
            # разные характеристики начертания
            left_title_font = QtGui.QFont()
            left_title_font.setPointSize(12)
            left_title_font.setBold(True)
            left_title.setFont(left_title_font)

            #виджет
            self.left_content = QtWidgets.QLabel()
            self.left_content.setObjectName("content_label")
            self.left_content.setStyleSheet("""
                QTextEdit {
                    background-color: #fafafa;
                    border: 1px solid #dfe6e9;
                    border-radius: 5px;
                    padding: 12px;
                    font-size: 13px;
                    color: #2d3436;
                }
            """)
            self.left_content.setWordWrap(True)  
            self.left_content.setAlignment(QtCore.Qt.AlignTop)
            left_layout.addWidget(left_title) #правила расстановки
            left_layout.addWidget(self.left_content)


            self.right_panel = QtWidgets.QWidget()
            right_layout = QtWidgets.QVBoxLayout(self.right_panel)
            right_title = QtWidgets.QLabel("Результат Spell Chech Pro", alignment=QtCore.Qt.AlignCenter)
            right_title.setObjectName("panel_title")
            right_title_font = QtGui.QFont()
            right_title_font.setPointSize(12)
            right_title_font.setBold(True)
            right_title.setFont(right_title_font)
            
            self.right_content = QtWidgets.QLabel()
            self.right_content.setObjectName("content_label")
            self.right_content.setStyleSheet("""
                QTextEdit {
                    background-color: #fafafa; 
                    border: 1px solid #dfe6e9; 
                    border-radius: 5px;
                    padding: 3px;
                    font-size: 10px;
                    color: #2d3436; 
                }
            """)
            self.right_content.setWordWrap(True)
            self.right_content.setAlignment(QtCore.Qt.AlignTop)
            right_layout.addWidget(right_title)
            right_layout.addWidget(self.right_content)

        
            self.results_splitter.addWidget(self.left_panel)
            self.results_splitter.addWidget(self.right_panel)
    
 
    def setup_layout(self) -> None:
            """
            Настройка компоновки виджетов в основном окне.
            
            """
            self.layout = QtWidgets.QVBoxLayout(self)
            self.layout.addWidget(self.text)
            self.layout.addWidget(self.input_field)
            self.layout.addWidget(self.button)
            self.layout.addWidget(self.results_splitter)

            # Настройка пропорций (поле ввода занимает меньше места, результаты - больше)
            self.layout.setStretchFactor(self.input_field, 1)
            self.layout.setStretchFactor(self.results_splitter, 3)

    
    def analyze_text(self) -> None:
        """
        Обработчик нажатия кнопки анализа текста
        """
        # Получаем текст из поля ввода

        text_to_analyze: str = self.input_field.toPlainText().strip()
        try:
            api_1_time_start: time = time.time()
            result_text_gears: Dict[str, Any] = self.api_1.check_spelling(text_to_analyze)
            api_1_time: time = time.time() - api_1_time_start

            api_2_time_start: time = time.time()
            result_spell_check_pro: Dict[str, Any] = self.api_2.check_spelling(text_to_analyze)
            api_2_time: time = time.time() - api_2_time_start   

            parse_time_start_1: time = time.time()
            errors_text_gears: List[str] = self.api_1.parse_json(result_text_gears)
            parse_time_1: time = time.time() - parse_time_start_1

            parse_time_start_2: time = time.time()
            errors_spell_check_pro: List[str] = self.api_2.parse_json(result_spell_check_pro)
            parse_time_2: time = time.time() - parse_time_start_2
            

            self.update_results_display(errors_text_gears,errors_spell_check_pro, api_1_time, api_2_time, parse_time_1, parse_time_2)
            
        except Exception as e:
            print("Ошибка API", f"Произошла ошибка при анализе текста: {str(e)}")
    
    def update_results_display(self, errors_1: List[str], errors_2: List[str], api_1_time: time, api_2_time: time, parse_time_1: time, parse_time_2) -> None:
        """
        Обновляет отображение результатов в интерфейсе.
        
        На вход:
            errors_1: Список найденных ошибок первым апи
            errors_2: Список найденных ошибок вторым апи
            api_1_time: Время запроса первого апи
            api_2_time: Время запроса второго апи
            parse_time_1: Время парсинга первого апи
            parse_time_2: Время парсинга второго апи    
        
        """
        if not errors_1:
            self.left_content.setText("Ошибок не найдено!\n\nТекст прошел проверку орфографии.")
        else:
            errors_text =  "\n".join(errors_1)
            full_text = f"{errors_text}\n\nВремя запроса API: {api_1_time:.6f} сек\nВремя парсинга: {parse_time_1:.6f} сек"
            self.left_content.setText(full_text)
        if not errors_2:
            self.right_content.setText("Ошибок не найдено!\n\nТекст прошел проверку орфографии.")
        else:
            errors_text =  "\n".join(errors_2)
            full_text = f"{errors_text}\n\nВремя запроса API: {api_2_time:.6f} сек\nВремя парсинга: {parse_time_2:.6f} сек"
            self.right_content.setText(full_text)
