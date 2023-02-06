import sys, time
from PyQt6.QtCore import pyqtSignal, QThread, Qt
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

# Can also get the refresh rate from system monitor
# but here I hard-code it
refresh_rate = 1/60

class Colour(QWidget):
    def __init__(self, color, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAutoFillBackground(True)
        # self.setMaximumHeight(100)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)

class My_Slider(QSlider):
    def __init__(self, type, start, end, val, interval, minimum_height=75):
        super().__init__(type)
        self.titles = [0, 20, 40, 60, 80, 100]
        self.setMinimumHeight(minimum_height)
        self.setMinimum(start)
        self.setMaximum(end)
        self.setValue(val)
        self.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.setTickInterval(interval)

class FlickerThread(QThread):
    boolean_value_flipped = pyqtSignal(bool)

    def __init__(self, val):
        super().__init__()
        self.cancelled = False
        self.val = val
        self.show = True

    def run(self) -> None:
        while not self.cancelled:
            sleeping_time = 0
            if self.val != 0:
                self.show = not self.show
                if self.show:
                    sleeping_time = refresh_rate
                else:
                    sleeping_time = (1-refresh_rate*self.val)/((self.val)+1)
                    if sleeping_time < 0:
                        sleeping_time = 0
            else:
                self.show = False

            self.boolean_value_flipped.emit(self.show)
            time.sleep(sleeping_time)

        self.exit(0)

class MainWin(QMainWindow):
    def __init__(self, size):
        super().__init__()
        self.title = 'flicker(s) per second'
        self.setWindowTitle(self.title)
        self.setFixedSize(size[0],size[1])

        ## Elements:
            ## set-up slider and its titles:
        orginal_val = 0
        self.slider = My_Slider(Qt.Orientation.Horizontal, orginal_val, 100, 0, 5, minimum_height=30)
        self.slider.valueChanged.connect(self.sliderValueChanged)

        # Set-up Layout:
        main_layout = QVBoxLayout()

            ## configure the top -- slider area:
        self.top = QGridLayout()
        self.top.setSpacing(0)
        self.top.setRowMinimumHeight(0, 20)
        self.top.setRowMinimumHeight(1, 50)
        self.top.addWidget(self.slider, 1, 0, 1, 5)

            ## and add the slider's titles:
        self.addLabelsToSlider()

            ## the bottom area - image area
        self.down = QGridLayout()
        self.img = QLabel('drawing area')
        background = Colour('black')

            ## set the image
        self.change_image('imgs/borot_white.png')

        self.down.addWidget(background,0,0,1,1)
        self.down.addWidget(self.img, 0, 0, 1, 1)

        # set-up the thread for flicker process:
        self.flicker_thread = FlickerThread(orginal_val)
        self.flicker_thread.boolean_value_flipped.connect(self.flicker)
        self.flicker_thread.start()

        main_layout.addLayout(self.top)
        main_layout.addLayout(self.down)
        main_layout.setStretch(0,1) # top area to be stretch size of 1
        main_layout.setStretch(1,3) # set the down area (index 1) to be twice the height

        # Use a dummy widget...
        dummy_widget = QWidget()
        dummy_widget.setLayout(main_layout)
            ## ...and add it to the main window
        self.setCentralWidget(dummy_widget)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Q:
            # closing
            print("Closing")
            self.flicker_thread.cancelled = True
            self.close()

    def change_image(self, path):
        self.img.setPixmap(QPixmap(path))
        self.img.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

    def sliderValueChanged(self, val):
        self.setWindowTitle(f'{self.title}: {val}')
        self.flicker_thread.val = val

    def flicker(self, show):
        if show:
            self.img.show()
            self.update()
        else:
            self.img.hide()
            self.update()

    def addLabelsToSlider(self):
        for i, title in enumerate(self.slider.titles):
            num = QLabel(str(title))
            num.setMaximumHeight(15)
            num.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
            self.top.addWidget(num, 0, i, 1, 1)
            if i == 4:
                last_num = QLabel(str(self.slider.titles[i+1]))
                last_num.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
                self.top.addWidget(last_num,0, i, 1, 1)
                break

if __name__ == '__main__':
    app = QApplication(sys.argv)
    size = 700,700
    main_window = MainWin(size)
    main_window.show()

    sys.exit(app.exec())

