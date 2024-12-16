from random import random, randint, choice
import faker

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox, QLabel, QToolBar, QAction, QSpinBox
)

import pyodbc
import loguru

connection = pyodbc.connect('DSN=odbc_source')

class PhoneDirectoryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Телефонный справочник")
        self.setGeometry(100, 100, 800, 600)

        self.init_ui()
        self.init_db()

    def init_ui(self):
        # Основной виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        toolbar = QToolBar("Main Toolbar", self)
        self.addToolBar(toolbar)

        # Создаем кнопку "Очистить таблицу"
        clear_action = QAction("Очистить таблицу", self)
        clear_action.triggered.connect(self.clear_table)
        toolbar.addAction(clear_action)

        # Создаем кнопку "Заполнить таблицу"
        fill_action = QAction("Заполнить таблицу", self)
        fill_action.triggered.connect(self.fill_table)
        toolbar.addAction(fill_action)

        # Основной макет
        main_layout = QVBoxLayout()

        # Поле для поиска
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск")
        self.search_input.textChanged.connect(self.search)

        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)

        # Таблица для отображения данных
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "id", "Имя", "Фамилия", "Отчество", "Улица", "Дом", "Квартира", "Телефон"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.table)

        # Поля ввода
        form_layout = QHBoxLayout()
        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("Имя")
        self.second_name_input = QLineEdit()
        self.second_name_input.setPlaceholderText("Фамилия")
        self.patronymic_input = QLineEdit()
        self.patronymic_input.setPlaceholderText("Отчество")
        self.street_input = QLineEdit()
        self.street_input.setPlaceholderText("Улица")
        self.house_input = QLineEdit()
        self.house_input.setPlaceholderText("Дом")
        self.apartment_input = QLineEdit()
        self.apartment_input.setPlaceholderText("Квартира")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Телефон")

        form_layout.addWidget(self.first_name_input)
        form_layout.addWidget(self.second_name_input)
        form_layout.addWidget(self.patronymic_input)
        form_layout.addWidget(self.street_input)
        form_layout.addWidget(self.house_input)
        form_layout.addWidget(self.apartment_input)
        form_layout.addWidget(self.phone_input)
        main_layout.addLayout(form_layout)

        # Кнопки управления
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_entry)
        self.update_button = QPushButton("Обновить")
        self.update_button.clicked.connect(self.update_entry)
        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_entry)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        main_layout.addLayout(button_layout)

        self.central_widget.setLayout(main_layout)
        self.table.cellClicked.connect(self.fill_input_fields)

    def fill_input_fields(self):
        # Загружаем данные в поля ввода по выбранной строке и колонке
        # ckjdfhbr
        info = {
            1: self.first_name_input,
            2: self.second_name_input,
            3: self.patronymic_input,
            4: self.street_input,
            5: self.house_input,
            6: self.apartment_input,
            7: self.phone_input
        }
        # цикл для загрузки данных в поля ввода по выбранной строке и колонке
        row = self.table.currentRow()
        for i in info.keys():
            info[i].setText(self.table.item(row, i).text().strip() if self.table.item(row, i) else "")

    def init_db(self):
        self.faker = faker.Faker('ru_RU')
        # Подключение к базе данных
        try:
            self.cursor = connection.cursor()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка подключения", str(e))

    def load_data(self):
        scroll_position = self.table.verticalScrollBar().value()
        current_row = self.table.currentRow()
        try:
            self.cursor.execute("""
                SELECT
                    phone_directory.u_id,
                    first_name.name,
                    second_name.second_name,
                    patronymic.patronymic,
                    street.street,
                    phone_directory.u_building,
                    phone_directory.u_aprt,
                    phone_directory.u_phone
                FROM phone_directory
                JOIN first_name ON phone_directory.u_name = first_name.id
                JOIN second_name ON phone_directory.u_surname = second_name.id
                JOIN patronymic ON phone_directory.u_patronymic = patronymic.id
                JOIN street ON phone_directory.u_street = street.id
            """)
            records = self.cursor.fetchall()
            self.table.setRowCount(len(records))
            for row_idx, row_data in enumerate(records):
                for col_idx, col_data in enumerate(row_data):  # Пропускаем u_id
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
                loguru.logger.info(f"Загрузка записи с id {row_data[0]}")
            self.table.hideColumn(0)

            # Восстанавливаем позицию прокрутки и выбор строки
            if current_row != -1 and current_row < self.table.rowCount():
                        self.table.selectRow(current_row)
                        self.table.setCurrentCell(current_row, 0)
            self.table.verticalScrollBar().setValue(scroll_position)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки данных", str(e))
            loguru.logger.error(f"Ошибка загрузки данных: {e}")

    def clear_table(self):
        # Создаем окно подтверждения
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение очистки")
        msg_box.setText("Вы уверены, что хотите очистить все данные?")
        msg_box.setIcon(QMessageBox.Question)

        yes_button = msg_box.addButton("Да", QMessageBox.YesRole)
        no_button = msg_box.addButton("Нет", QMessageBox.NoRole)

        # Отображаем окно и ждем выбора
        msg_box.exec()

        # Проверяем, какая кнопка была нажата
        if msg_box.clickedButton() == yes_button:
            try:
                self.cursor.execute(
                    "DELETE FROM phone_directory;"
                    "DELETE FROM first_name;"
                    "DELETE FROM patronymic;"
                    "DELETE FROM street;"
                    "DELETE FROM second_name;"

                    "ALTER SEQUENCE first_name_id_seq RESTART WITH 1;"
                    "ALTER SEQUENCE patronymic_id_seq RESTART WITH 1;"
                    "ALTER SEQUENCE street_id_seq RESTART WITH 1;"
                    "ALTER SEQUENCE second_name_id_seq RESTART WITH 1;"
                    "ALTER SEQUENCE phone_directory_u_id_seq RESTART WITH 1;"
                )
                self.cursor.commit()
                self.load_data()
                QMessageBox.information(self, "Успех", "Таблица успешно очищена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось очистить таблицу: {str(e)}")

    def fill_table(self):
        # Создаем окно подтверждения
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение заполнения")
        msg_box.setText("Сколько записей вы хотите добавить?")
        msg_box.setIcon(QMessageBox.Question)

        spin_box = QSpinBox(msg_box)
        spin_box.setRange(1, 100)
        spin_box.setValue(10)
        spin_box.setGeometry(100, 35, 200, 20)

        yes_button = msg_box.addButton("Заполнить", QMessageBox.YesRole)
        no_button = msg_box.addButton("Отмена", QMessageBox.NoRole)


        # Отображаем окно и ждем выбора
        msg_box.exec()

        if msg_box.clickedButton() == yes_button:
            try:
            # Проверяем, какая кнопка была нажата
                for _ in range(spin_box.value()):
                    # Генерируем случайное имя
                    name = self.faker.first_name_male() if choice(
                        [True, False]) else self.faker.first_name_female()

                    # Генерируем фамилию
                    second_name = self.faker.last_name_male() if 'male' in name else self.faker.last_name_female()

                    # Генерируем отчество
                    patronymic = self.faker.middle_name_male() if 'male' in name else self.faker.middle_name_female()

                    # Другие параметры
                    street = self.faker.street_name()
                    house = self.faker.building_number()
                    apartment = str(randint(1, 200))
                    phone = self.faker.phone_number()
                    try:
                        # Обработка имени (как в предыдущем примере)
                        self.cursor.execute("SELECT id FROM first_name WHERE name = ?", (name,))
                        name_id = self.cursor.fetchone()
                        if not name_id:
                            self.cursor.execute("INSERT INTO first_name (name) VALUES (?) RETURNING id", (name,))
                            name_id = self.cursor.fetchone()[0]
                        else:
                            name_id = name_id[0]

                        # Аналогично для фамилии
                        self.cursor.execute("SELECT id FROM second_name WHERE second_name = ?", (second_name,))
                        second_name_id = self.cursor.fetchone()
                        if not second_name_id:
                            self.cursor.execute("INSERT INTO second_name (second_name) VALUES (?) RETURNING id",
                                                (second_name,))
                            second_name_id = self.cursor.fetchone()[0]
                        else:
                            second_name_id = second_name_id[0]

                        # Аналогично для отчества
                        self.cursor.execute("SELECT id FROM patronymic WHERE patronymic = ?", (patronymic,))
                        patronymic_id = self.cursor.fetchone()
                        if not patronymic_id:
                            self.cursor.execute("INSERT INTO patronymic (patronymic) VALUES (?) RETURNING id",
                                                (patronymic,))
                            patronymic_id = self.cursor.fetchone()[0]
                        else:
                            patronymic_id = patronymic_id[0]

                        # Аналогично для улицы
                        self.cursor.execute("SELECT id FROM street WHERE street = ?", (street,))
                        street_id = self.cursor.fetchone()
                        if not street_id:
                            self.cursor.execute("INSERT INTO street (street) VALUES (?) RETURNING id", (street,))
                            street_id = self.cursor.fetchone()[0]
                        else:
                            street_id = street_id[0]

                        # Добавление записи в основную таблицу
                        self.cursor.execute("""
                            INSERT INTO phone_directory (u_name, u_surname, u_patronymic, u_street, u_building, u_aprt, u_phone)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (name_id, second_name_id, patronymic_id, street_id, house, apartment, phone))

                        loguru.logger.info(f"Добавление в phone_directory: {name} {second_name} {patronymic} {street} {house} {apartment} {phone}")

                    except Exception as e:
                        loguru.logger.info(f"Ошибка при добавлении записи: {e}")
            except Exception as e:
                loguru.logger.info(f"Ошибка при добавлении записи: {e}")

            self.cursor.commit()
            self.load_data()
            QMessageBox.information(self, "Успех", "Таблица заполнена успешно")

    def search(self):
        # Получаем текст поиска
        search_text = self.search_input.text().lower().strip()

        # Если поиск пустой, загружаем все записи
        if not search_text:
            self.load_data()
            return

        try:
            # Выполняем основной запрос
            self.cursor.execute("""
                SELECT
                    phone_directory.u_id,
                    first_name.name,
                    second_name.second_name,
                    patronymic.patronymic,
                    street.street,
                    phone_directory.u_building,
                    phone_directory.u_aprt,
                    phone_directory.u_phone
                FROM phone_directory
                JOIN first_name ON phone_directory.u_name = first_name.id
                JOIN second_name ON phone_directory.u_surname = second_name.id
                JOIN patronymic ON phone_directory.u_patronymic = patronymic.id
                JOIN street ON phone_directory.u_street = street.id
            """)
            records = self.cursor.fetchall()

            # Фильтруем записи
            filtered_records = [
                record for record in records
                if any(search_text in str(field).lower() for field in record[1:])
            ]

            # Очищаем и заполняем таблицу
            self.table.setRowCount(len(filtered_records))
            for row_idx, row_data in enumerate(filtered_records):
                for col_idx, col_data in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

            self.table.hideColumn(0)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка поиска", str(e))
            loguru.logger.error(f"Ошибка при поиске: {e}")

    def add_entry(self):
        # Добавление новой записи
        name = self.first_name_input.text()
        second_name = self.second_name_input.text()
        patronymic = self.patronymic_input.text()
        street = self.street_input.text()
        house = self.house_input.text()
        apartment = self.apartment_input.text()
        phone = self.phone_input.text()

        try:
            # Добавление или получение ID имени
            self.cursor.execute("SELECT id FROM first_name WHERE name = ?", (name,))
            name_id = self.cursor.fetchone()
            if not name_id:
                self.cursor.execute("INSERT INTO first_name (name) VALUES (?) RETURNING id", (name,))
                name_id = self.cursor.fetchone()[0]
            else:
                name_id = name_id[0]

            # Добавление или получение ID фамилии
            self.cursor.execute("SELECT id FROM second_name WHERE second_name = ?", (second_name,))
            surname_id = self.cursor.fetchone()
            if not surname_id:
                self.cursor.execute("INSERT INTO second_name (second_name) VALUES (?) RETURNING id", (second_name,))
                surname_id = self.cursor.fetchone()[0]
            else:
                surname_id = surname_id[0]

            # Добавление или получение ID отчества
            self.cursor.execute("SELECT id FROM patronymic WHERE patronymic = ?", (patronymic,))
            patronymic_id = self.cursor.fetchone()
            if not patronymic_id:
                self.cursor.execute("INSERT INTO patronymic (patronymic) VALUES (?) RETURNING id", (patronymic,))
                patronymic_id = self.cursor.fetchone()[0]
            else:
                patronymic_id = patronymic_id[0]

            # Добавление или получение ID улицы
            self.cursor.execute("SELECT id FROM street WHERE street = ?", (street,))
            street_id = self.cursor.fetchone()
            if not street_id:
                self.cursor.execute("INSERT INTO street (street) VALUES (?) RETURNING id", (street,))
                street_id = self.cursor.fetchone()[0]
            else:
                street_id = street_id[0]

        # Добавление записи в основную таблицу
            self.cursor.execute("""
                            INSERT INTO phone_directory (u_name, u_surname, u_patronymic, u_street, u_building, u_aprt, u_phone)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (name_id, surname_id, patronymic_id, street_id, house, apartment, phone))

            self.cursor.commit()
            self.load_data()
            QMessageBox.information(self, "Успех", "Запись добавлена успешно")
            loguru.logger.info(f"Добавление в phone_directory: {name} {second_name} {patronymic} {street} {house} {apartment} {phone}")


        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            loguru.logger.error(f"Ошибка добавления записи: {e}")

    def update_entry(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для обновления")
            return

        # Получаем текущие значения из полей ввода
        name = self.first_name_input.text()
        second_name = self.second_name_input.text()
        patronymic = self.patronymic_input.text()
        street = self.street_input.text()
        house = self.house_input.text()
        apartment = self.apartment_input.text()
        phone = self.phone_input.text()

        u_id = self.table.item(selected_row, 0).text()

        try:
            self.cursor.execute("SELECT id FROM first_name WHERE name = ?", (name,))
            name_id = self.cursor.fetchone()
            if not name_id:
                self.cursor.execute("INSERT INTO first_name (name) VALUES (?) RETURNING id", (name,))
                name_id = self.cursor.fetchone()[0]
            else:
                name_id = name_id[0]

            self.cursor.execute("SELECT id FROM second_name WHERE second_name = ?", (second_name,))
            surname_id = self.cursor.fetchone()
            if not surname_id:
                self.cursor.execute("INSERT INTO second_name (second_name) VALUES (?) RETURNING id", (second_name,))
                surname_id = self.cursor.fetchone()[0]
            else:
                surname_id = surname_id[0]

            self.cursor.execute("SELECT id FROM patronymic WHERE patronymic = ?", (patronymic,))
            patronymic_id = self.cursor.fetchone()
            if not patronymic_id:
                self.cursor.execute("INSERT INTO patronymic (patronymic) VALUES (?) RETURNING id", (patronymic,))
                patronymic_id = self.cursor.fetchone()[0]
            else:
                patronymic_id = patronymic_id[0]

            self.cursor.execute("SELECT id FROM street WHERE street = ?", (street,))
            street_id = self.cursor.fetchone()
            if not street_id:
                self.cursor.execute("INSERT INTO street (street) VALUES (?) RETURNING id", (street,))
                street_id = self.cursor.fetchone()[0]
            else:
                street_id = street_id[0]

            # Обновляем запись в основной таблице
            self.cursor.execute("""
                UPDATE phone_directory 
                SET u_name = ?, u_surname = ?, u_patronymic = ?, 
                    u_street = ?, u_building = ?, u_aprt = ?, u_phone = ?
                WHERE u_id = ?
            """, (name_id, surname_id, patronymic_id, street_id, house, apartment, phone, u_id))

            # Удаляем неиспользуемые записи в справочных таблицах
            self.cursor.execute(
                "DELETE FROM first_name WHERE name = ? AND id NOT IN (SELECT u_name FROM phone_directory)", (name,))
            self.cursor.execute(
                "DELETE FROM second_name WHERE second_name = ? AND id NOT IN (SELECT u_surname FROM phone_directory)",
                (second_name,))
            self.cursor.execute(
                "DELETE FROM patronymic WHERE patronymic = ? AND id NOT IN (SELECT u_patronymic FROM phone_directory)",
                (patronymic,))
            self.cursor.execute(
                "DELETE FROM street WHERE street = ? AND id NOT IN (SELECT u_street FROM phone_directory)", (street,))

            self.cursor.commit()
            self.load_data()

            QMessageBox.information(self, "Успех", "Запись обновлена успешно")
            loguru.logger.info(
                f"Обновление записи с id {u_id}: {name} {second_name} {patronymic} {street} {house} {apartment} {phone}")

        except Exception as e:
            # Обработка ошибок
            QMessageBox.critical(self, "Ошибка", str(e))
            loguru.logger.error(f"Ошибка обновления записи: {e}")

        # # Ищу конкретную ячейку в таблице
        # selected_cell = self.table.currentItem()
        # selected_cell_id = self.table.item(selected_cell.row(), 0)
        #
        # if not selected_cell:
        #     QMessageBox.warning(self, "Ошибка", "Выберите запись для обновления")
        #     return
        #
        # # Список названий в интерфейсе
        # labels = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())][1:]
        #
        # # Названия таблиц
        # table_names = ['u_name', 'u_surname', 'u_patronymic', 'u_street']
        # # Ориентация таблиц по заголовкам в интерфейсе
        # table_name = dict(zip(labels, table_names))
        # try:
        #     loguru.logger.info(f"Обновление записи с id, заголовком "
        #                        f"{selected_cell_id.text(), self.table.horizontalHeaderItem(selected_cell.column()).text(), table_name[self.table.horizontalHeaderItem(selected_cell.column()).text()]}")
        #     self.cursor.execute(f"UPDATE phone_directory SET {table_name[self.table.horizontalHeaderItem(selected_cell.column()).text()]} = ? WHERE u_id = ?",
        #                         ('абрикос', selected_cell_id.text()))
        # except Exception as e:
        #     QMessageBox.critical(self, "Ошибка", str(e))
        #     loguru.logger.error(f"Ошибка обновления записи: {e}")


    def delete_entry(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления")
            return

        try:
            # Получаем u_id из скрытой первой колонки
            u_id_item = self.table.item(selected_row, 0)
            if not u_id_item:
                QMessageBox.warning(self, "Ошибка", "Не удалось получить идентификатор записи")
                return

            u_id = u_id_item.text()

            # Удаляем запись из базы данных
            self.cursor.execute("DELETE FROM phone_directory WHERE u_id = ?", (u_id,))

            self.cursor.execute("DELETE FROM first_name WHERE name = ? "
                                "AND id NOT IN (SELECT u_name FROM phone_directory)",
                                (self.table.item(selected_row, 1).text(),))
            self.cursor.execute("DELETE FROM second_name WHERE second_name = ? "
                                "AND id NOT IN (SELECT u_surname FROM phone_directory)",
                                (self.table.item(selected_row, 2).text(),))
            self.cursor.execute("DELETE FROM patronymic WHERE patronymic = ? "
                                "AND id NOT IN (SELECT u_patronymic FROM phone_directory)",
                                (self.table.item(selected_row, 3).text(),))
            self.cursor.execute("DELETE FROM street WHERE street = ? "
                                "AND id NOT IN (SELECT u_street FROM phone_directory)",
                                (self.table.item(selected_row, 4).text(),))
            loguru.logger.info(f"Удаление записи {self.table.item(selected_row, 1).text().strip()} "
                               f"{self.table.item(selected_row, 2).text().strip()} "
                               f"{self.table.item(selected_row, 3).text().strip()} "
                               f"{self.table.item(selected_row, 4).text().strip()}")

            # Обновляем таблицу
            self.cursor.commit()
            self.load_data()
            QMessageBox.information(self, "Успех", "Запись удалена успешно")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = PhoneDirectoryApp()
    window.show()
    sys.exit(app.exec_())
