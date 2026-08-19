import sys

from PyQt5.QtWidgets  import *
from PyQt5.uic import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class MyWidget(QWidget):

    def __init__(self):
        super(MyWidget, self).__init__()
        self.setGeometry(100,100, 200,200)
        self.initUI()
        self.show()
		
    def initUI(self):
        self.button = imgButton("recursos/afganistán.png", "Afganistán", self)
        self.button.setStyleSheet('font: 10pt "Bahnschrift SemiBold"; background-color: rgb(255, 255, 255); border-radius: 20px; padding-left: 20px; margin-bottom: 3px;')
        self.button.clicked.connect(lambda: print("Button Pressed!"))

        self.button.resize(100, 100)


class imgButton(QPushButton):
    def __init__(self, img, text, parent):
        super(imgButton, self).__init__(parent)
        # Create a QHBoxLayout instance
        layout = QVBoxLayout(self)

        # Add icon/image to the layout (Left)
        icon = QIcon(img)
        pixmap = icon.pixmap(80, 160, QIcon.Active, QIcon.On)
        self.bandera = QLabel(self)
        self.bandera.setPixmap(pixmap)
        self.bandera.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.bandera, 0) # (stretch factor 0)

        # Add label to the layout (Center)
        self.iconLabel = QLabel(text)
        self.iconLabel.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.iconLabel, 1)

        self.show()
    
if __name__ == "__main__":
    try:
        myApp = QApplication(sys.argv)
        myWindow = MyWidget()
        myApp.exec_()
        sys.exit(0)
    except NameError:
        print("Name Error:", sys.exc_info()[1])
    except SystemExit:
        print("Closing Window...")
    except Exception:
        print(sys.exc_info()[1])