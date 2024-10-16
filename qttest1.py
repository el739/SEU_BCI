import sys  
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout  

class MyApp(QWidget):  
    def __init__(self):  
        super().__init__()  

        self.initUI()  

    def initUI(self):  
        self.setWindowTitle('PyQt5 Example')  
        self.setGeometry(100, 100, 300, 200)  

        self.label = QLabel('Hello, PyQt5!', self)  
        self.label.setStyleSheet("font-size: 20px;")  

        self.button = QPushButton('Click Me', self)  
        self.button.clicked.connect(self.on_button_click)  

        layout = QVBoxLayout()  
        layout.addWidget(self.label)  
        layout.addWidget(self.button)  

        self.setLayout(layout)  

    def on_button_click(self):  
        self.label.setText('Button Clicked!')  

if __name__ == '__main__':  
    app = QApplication(sys.argv)  
    ex = MyApp()  
    ex.show()  
    sys.exit(app.exec_())