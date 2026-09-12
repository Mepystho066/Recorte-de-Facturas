style = """
            QMainWindow {
                background-color: #1e1e2e;
            }
            QLabel {
                color: #cdd6f4;
                font-size: 14px;
            }
            QListWidget {
                background-color: #313244;
                border: 2px solid #45475a;
                border-radius: 8px;
                padding: 5px;
                color: #cdd6f4;
                font-size: 14px;
            }
            QListWidget::item {
                background-color: #1e1e2e;
                margin: 4px;
                padding: 10px;
                border-radius: 6px;
                border: 1px solid #45475a;
            }
            QListWidget::item:hover {
                background-color: #45475a;
                border: 1px solid #89b4fa;
            }
            QListWidget::item:selected {
                background-color: #89b4fa;
                color: #11111b;
                font-weight: bold;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #11111b;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
            QPushButton#btn_buscar {
                background-color: #45475a;
                color: #cdd6f4;
            }
            QPushButton#btn_buscar:hover {
                background-color: #585b70;
            }
        """