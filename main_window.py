from PySide6.QtWidgets import QMainWindow, QApplication, QMessageBox, QFrame, QDialog, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox
from user_class import Polzovatels, Platezs, Connect
from PySide6.QtGui import QIcon
from datetime import datetime
from PySide6.QtCore import Qt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import black

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Основное окно")
        self.setFixedSize(725,600)
        self.setWindowIcon(QIcon('icon.png'))
        self.session = Connect.create_connection()
        
        self.setStyleSheet("Qwidget {background-color: white}")
        self.is_logged_in = self.pLog()
        if self.is_logged_in == True:
            self.setup_ui()

        

    
    
    def setup_ui(self):

    
        self.table = QTableWidget()
        self.table.setHorizontalHeaderLabels([])

        
        self.btnPlus = QPushButton("+")
        self.btnPlus.setFixedWidth(20)
        self.btnMinus = QPushButton("-")
        self.btnMinus.setFixedWidth(20)
        self.line1 = QFrame()
        self.line1.setFrameShape(QFrame.VLine)
        self.line1.setFrameShadow(QFrame.Raised)
        self.labelS = QLabel("С")
        self.cbox1 = QComboBox()
        self.labelP = QLabel("ПО")
        self.cbox2 = QComboBox()
        self.labelCat = QLabel("Категория")
        self.cbox3 = QComboBox()
        self.cbox3.setFixedWidth(160)
        self.btnVib = QPushButton("Выбрать")
        self.btnCle = QPushButton("Очистить")
        self.btnOtch = QPushButton("Отчет")
        
        self.btnVib.setFixedWidth(57)
        self.btnCle.setFixedWidth(65)
        self.btnOtch.setFixedWidth(47)
        
        self.layoutAF = QHBoxLayout()
        self.layoutAF.addWidget(self.btnPlus)
        self.layoutAF.addWidget(self.btnMinus)
        self.layoutAF.addWidget(self.line1)
        self.layoutAF.addWidget(self.labelS)
        self.layoutAF.addWidget(self.cbox1)
        self.layoutAF.addWidget(self.labelP)
        self.layoutAF.addWidget(self.cbox2)
        self.layoutAF.addWidget(self.labelCat)
        self.layoutAF.addWidget(self.cbox3)
        self.layoutAF.addWidget(self.btnVib)
        self.layoutAF.addWidget(self.btnCle)
        self.layoutAF.addWidget(self.btnOtch)
        

        
        
        self.layoutT = QHBoxLayout()
        self.layoutT.addWidget(self.table)
        self.mlayout = QVBoxLayout()
        self.mlayout.addLayout(self.layoutAF)
        self.mlayout.addLayout(self.layoutT)
        
        widget = QWidget()
        widget.setLayout(self.mlayout)
        self.setCentralWidget(widget)
        self.update_table()
        
        self.btnPlus.clicked.connect(self.addPlat)
        
        self.table.itemClicked.connect(self.select_table_item)  # Связь с обработчиком выбора строки
        self.selected_id = None  # Переменная для хранения ID выбранной записи
        self.btnMinus.clicked.connect(self.delete_record)
        self.btnOtch.clicked.connect(self.generate_report)
        
        
        self.cbox1.addItems(["2016-11-01", "2016-11-02", "2016-11-03"])  # Пример дат
        self.cbox2.addItems(["2016-11-19", "2016-11-28", "2016-12-29"])  # Пример дат
        self.cbox3.addItems(["Все", "Коммунальные платежи", "Автомобиль", "Питание и быт", "Медицина", "Разное"])  # Пример категорий
    
        self.btnVib.clicked.connect(self.filter_table)
        self.btnCle.clicked.connect(self.clear_filters)
        
    def filter_table(self):
        # Получение значений из ComboBox
        start_date = self.cbox1.currentText()
        end_date = self.cbox2.currentText()
        category = self.cbox3.currentText()

        # Построение запроса
        query = self.session.query(Platezs)
        
        # Фильтр по дате
        if start_date:
            query = query.filter(Platezs.data >= start_date)
        if end_date:
            query = query.filter(Platezs.data <= end_date)
        
        # Фильтр по категории
        if category and category != "Все":
            query = query.filter(Platezs.category == category)
        
        # Выполнение запроса и обновление таблицы
        filtered_data = query.order_by(Platezs.data).all()
        self.update_filtered_table(filtered_data)
        
    def update_filtered_table(self, data):
        self.table.setRowCount(0)  # Очистка таблицы
        for item in data:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.populate_row(row_position, item)
            
            
    def clear_filters(self):
        # Сброс значений в ComboBox
        self.cbox1.setCurrentIndex(-1)
        self.cbox2.setCurrentIndex(-1)
        self.cbox3.setCurrentIndex(0)

        # Отображение всех данных
        self.update_table()


        
    def select_table_item(self, item):
        row = item.row()
        id_item = self.table.item(row, 0)  # Получаем элемент в 0-й колонке
        self.selected_id = id_item.data(Qt.UserRole)  # Извлекаем ID из данных элемента
        print(f"Выбран ID: {self.selected_id}")  # Для отладки
            
            
    def delete_record(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления!")
            return  
        
        confirm = QMessageBox.question(self,
        "Подтверждение удаления",
        f"Вы уверены, что хотите удалить запись с ID {self.selected_id}?",
        QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            try:
                # Запрос на удаление из базы
                record_to_delete = self.session.query(Platezs).filter_by(id=self.selected_id).first()
                if record_to_delete:
                    self.session.delete(record_to_delete)
                    self.session.commit()
                    QMessageBox.information(self, "Успех", "Запись успешно удалена.")
                    self.update_table()  # Обновление таблицы
                else:
                    QMessageBox.warning(self, "Ошибка", "Запись не найдена.")
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении записи: {e}")
            
        
    def update_table(self):
        self.table.setRowCount(0)
        
        
        platez = self.session.query(Platezs).order_by(Platezs.id).all()
        self.table.setColumnCount(5)
        self.current_table_data = platez
        self.table.setHorizontalHeaderLabels(["Наименование платежа","Количество","Цена","Сумма","Категория"])
        self.table.setColumnWidth(0, 185)  
        self.table.setColumnWidth(1, 85)  
        self.table.setColumnWidth(2, 63)  
        self.table.setColumnWidth(3, 63)   
        self.table.setColumnWidth(4, 260)
        for platezs in platez:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.populate_row(row_position, platezs)
            
    def populate_row(self, row_position, item):
        if isinstance(item, Platezs):
            name_item = QTableWidgetItem(item.name)
            count_item = QTableWidgetItem(str(item.count))
            price_item = QTableWidgetItem(str(item.price))
            checks_item = QTableWidgetItem(str(item.checks))
            category_item = QTableWidgetItem(item.category)
            
            # Привязываем ID как скрытые данные к первому элементу строки
            name_item.setData(Qt.UserRole, item.id)
            
            # Добавляем элементы в таблицу
            self.table.setItem(row_position, 0, name_item)
            self.table.setItem(row_position, 1, count_item)
            self.table.setItem(row_position, 2, price_item)
            self.table.setItem(row_position, 3, checks_item)
            self.table.setItem(row_position, 4, category_item)
        
    
    def pLog(self):
        return self.logins()  
        

        
    def logins(self):
        self.dialog = QDialog()
        self.dialog.setWindowTitle("Авторизация")
        self.dialog.setWindowIcon(QIcon('login.png'))
        self.dialog.setModal(True)
        self.dialog.setFixedSize(300, 200)
            
        user = QLabel("Имя пользователя:")
        passw = QLabel("Пароль:")
        self.us1 = QComboBox()
        self.pas1 = QLineEdit()
        self.pas1.setEchoMode(QLineEdit.Password)
        
        
    
        logBtn = QPushButton("Войти")
        exBtn = QPushButton("Выход")
    
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()
        layout1.addWidget(user)
        layout2.addWidget(passw)
        layout1.addWidget(self.us1)
        layout2.addWidget(self.pas1)
        layout3.addWidget(logBtn)
        layout3.addWidget(exBtn)
    
        self.data_combo()
        
        flayout = QVBoxLayout()
        flayout.addLayout(layout1)
        flayout.addLayout(layout2)
        flayout.addLayout(layout3)



        
        self.dialog.setLayout(flayout)
        
        def check_password():
            # Получаем выбранного пользователя
            selected_user = self.us1.currentText()
            
            # Получаем данные пользователя из базы
            user_data = self.session.query(Polzovatels).filter_by(login=selected_user).first()
            
            if user_data and Polzovatels.verify_password(self.pas1.text(), user_data.ppassword):
                QMessageBox.information(self.dialog, "Успех", "Вы успешно вошли!")
                self.dialog.accept()
            else:
                QMessageBox.warning(self.dialog, "Ошибка", "Неверный пароль!")
            
        
        logBtn.clicked.connect(check_password)  # "Войти" завершает диалог с успехом
        exBtn.clicked.connect(self.dialog.reject)  # "Выход" завершает диалог с отказом

        return self.dialog.exec() == QDialog.Accepted  # True, если "Войти", иначе False
        
        
    def data_combo(self):
        self.us1.clear()
        names = self.session.query(Polzovatels.login).order_by(Polzovatels.login).all()
        login_values = [login[0] for login in names]
        self.us1.addItems(login_values)
    
    
            
        
        
    
    
    def addPlat(self): 
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавление платежа")
        dialog.setWindowIcon(QIcon('add.png'))
        dialog.setModal(True)
        dialog.setFixedSize(300, 200)

        # Создание виджетов
        cat_label = QLabel("Категория")
        cat_box = QComboBox()
        cat_box.addItems(["Коммунальные платежи", "Автомобиль", "Питание и быт", "Медицина", "Разное"])  # Пример категорий

        naz_label = QLabel("Назначение платежа")
        naz_line = QLineEdit()

        col_label = QLabel("Количество")
        col_line = QLineEdit()

        price_label = QLabel("Цена")
        price_line = QLineEdit()

        doBtn = QPushButton("Добавить")
        caBtn = QPushButton("Отменить")

        # Макеты
        layoutD1 = QHBoxLayout()
        layoutD1.addWidget(cat_label)
        layoutD1.addWidget(cat_box)

        layoutD2 = QHBoxLayout()
        layoutD2.addWidget(naz_label)
        layoutD2.addWidget(naz_line)

        layoutD3 = QHBoxLayout()
        layoutD3.addWidget(col_label)
        layoutD3.addWidget(col_line)

        layoutD4 = QHBoxLayout()
        layoutD4.addWidget(price_label)
        layoutD4.addWidget(price_line)

        layoutD5 = QHBoxLayout()
        layoutD5.addWidget(doBtn)
        layoutD5.addWidget(caBtn)

        layoutDia = QVBoxLayout()
        layoutDia.addLayout(layoutD1)
        layoutDia.addLayout(layoutD2)
        layoutDia.addLayout(layoutD3)
        layoutDia.addLayout(layoutD4)
        layoutDia.addLayout(layoutD5)

        # Логика сохранения
        def save_plat():
            data = datetime.now().strftime("%Y-%m-%d")
            category = cat_box.currentText().strip()
            name = naz_line.text().strip()
            count = col_line.text().strip()
            price = price_line.text().strip()

            # Проверка на заполненность
            if not category or not name or not count or not price:
                QMessageBox.warning(dialog, "Ошибка", "Все поля должны быть заполнены!")
                return

            # Проверка корректности чисел
            try:
                check = int(count) * int(price)
                checks = str(check)
            except ValueError:
                QMessageBox.warning(dialog, "Ошибка", "Количество и Цена должны быть числами!")
                return

            # Добавление записи в базу
            new_plat = Platezs(data=data ,name=name, count=count, price=price, checks=checks, category=category)
            self.session.add(new_plat)
            self.session.commit()

            # Обновление таблицы
            self.update_table()
            dialog.accept()

        # Связывание кнопок
        doBtn.clicked.connect(save_plat)
        caBtn.clicked.connect(dialog.reject)

        dialog.setLayout(layoutDia)
        dialog.exec()
        
        
        
        
    def generate_report(self):
        # Создаем PDF-файл
        c = canvas.Canvas("report.pdf", pagesize=A4)
        pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf"))  # Шрифт с поддержкой кириллицы

        # Заголовок
        c.setFont("DejaVuSans", 14)
        c.drawString(200, 800, "Список платежей")
        y = 750  # Начальная позиция по вертикали
        
        # Получаем данные из базы
        data = self.session.query(Platezs).order_by(Platezs.category, Platezs.name).all()

        if not data:
            c.setFont("DejaVuSans", 12)
            c.drawString(100, y, "Нет данных для формирования отчета.")
            c.save()
            return

        c.setFont("DejaVuSans", 10)
        current_category = None  # Текущая категория
        total_sum = 0  # Общая сумма стоимости всех платежей

        for item in data:
            if current_category != item.category:
                # Рисуем новую категорию
                if current_category is not None:
                    y -= 10  # Отступ перед следующей категорией
                
                current_category = item.category
                y -= 20
                c.setFont("DejaVuSans", 12)
                c.drawString(10, y, f"[{current_category}]")
            
            # Рисуем платеж в рамках категории
            y -= 15
            c.setFont("DejaVuSans", 10)
            c.drawString(30, y, item.name)
            c.drawString(400, y, f"{item.checks:.2f} руб.")  # Цена справа

            # Добавляем стоимость к общей сумме
            total_sum += item.checks

            # Проверяем, если достигли конца страницы
            if y < 50:
                c.showPage()
                c.setFont("DejaVuSans", 10)
                y = 800  # Сбрасываем позицию на следующей странице

        # Добавление горизонтальной полосы и итоговой суммы
        if y < 100:
            c.showPage()  # Переход на новую страницу, если места недостаточно
            y = 750
        
        # Горизонтальная линия
        y -= 30
        c.setLineWidth(1)
        c.setStrokeColor(black)
        c.line(10, y, 550, y)

        # Итоговая сумма
        y -= 20
        c.setFont("DejaVuSans", 12)
        c.drawString(10, y, "ИТОГО:")
        c.drawString(400, y, f"{total_sum:.2f} руб.")

        # Сохранение PDF
        c.save()
        print("Отчет успешно сохранен как report.pdf")

                
