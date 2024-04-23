from PyQt6 import QtWidgets, QtGui, QtCore
import random

from game_over import Ui_Form
from main_gui import Ui_MainWindow
import settings

max_apple = 1

class Food:
    def __init__(self, width, height) -> None:
        self.bag = []

        self.width = width
        self.height = height
        self.image = QtGui.QImage('./snake/food/apple.png')

    def generate_food(self):
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)

        self.bag.append([x, y])

class Snake:
    def __init__(self, width, height) -> None:
        self.body = [[5, 5], [5, 6]]
        self.head = [5, 5]

        self.direction = 'left'
        self.height = height
        self.width = width
        self.grow = False

        self.left_image = QtGui.QImage('./snake/food/head_left.png')
        self.right_image = QtGui.QImage('./snake/food/head_right.png')
        self.up_image = QtGui.QImage('./snake/food/head_up.png')
        self.down_image = QtGui.QImage('./snake/food/head_down.png')

        self.image = self.left_image
    
    def move(self):
        if self.direction == 'left':
            self.image = self.left_image
            self.head = [self.head[0] - 1, self.head[1]]
            if self.head[0] == -1:
                self.head[0] = self.width - 1
        elif self.direction == 'right':
            self.image = self.right_image
            self.head = [self.head[0] + 1, self.head[1]]
            if self.head[0] == self.width:
                self.head[0] = 0
        elif self.direction == 'up':
            self.image = self.up_image
            self.head = [self.head[0], self.head[1] - 1]
            if self.head[1] == -1:
                self.head[1] = self.height - 1
        elif self.direction == 'down':
            self.image = self.down_image
            self.head = [self.head[0], self.head[1] + 1]
            if self.head[1] == self.height:
                self.head[1] = 0

        self.body.insert(0, self.head)
        if self.grow == False:
            self.body.pop()
        else:
            self.grow = False

    def is_dead(self):
        pass

class Board(QtWidgets.QFrame):
    SPEED = 80
    HEIGHTINBLOCKS = 10
    WIDTHINBLOCKS = 15
    def __init__(self, parent) -> None:
        super().__init__(parent)

        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

        self.timer = QtCore.QBasicTimer()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.hide_ui()

        self.snake = Snake(self.WIDTHINBLOCKS, self.HEIGHTINBLOCKS)
        self.food = Food(self.WIDTHINBLOCKS, self.HEIGHTINBLOCKS)

        self.ui.restart_pushButton.clicked.connect(self.restart_game)
        self.ui.save_pushButton.clicked.connect(self.read_name)
        self.ui.input_pushButton.clicked.connect(self.input_name)

    def hide_ui(self):
        self.ui.label.hide()
        self.ui.label_2.hide()
        self.ui.restart_pushButton.hide()
        self.ui.menu_pushButton.hide()
        self.ui.save_pushButton.hide()
        self.ui.lineEdit.hide()
        self.ui.input_pushButton.hide()

    def show_ui(self):
        self.ui.label.show()
        self.ui.label_2.show()
        self.ui.restart_pushButton.show()
        self.ui.menu_pushButton.show()
        self.ui.save_pushButton.show()
    
    def timerEvent(self, a0: QtCore.QTimerEvent) -> None:
        if a0.timerId() == self.timer.timerId():
            self.drop_food()
            self.snake.move()
            self.is_dead()
            self.colision()
            self.update()

    def block_width(self):
        return int(self.frameGeometry().width() / self.WIDTHINBLOCKS)
    
    def block_height(self):
        return int(self.frameGeometry().height() / self.HEIGHTINBLOCKS)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        
        painter = QtGui.QPainter(self)

        rect = self.contentsRect()

        boardtop = rect.bottom() - self.frameGeometry().height()
        self.drawimage(painter, rect.left() + self.snake.head[0] * self.block_width(),
                          boardtop + self.snake.head[1] * self.block_height(), self.snake.image)

        for cord in self.snake.body[1:]:
            self.drawrect(painter, rect.left() + cord[0] * self.block_width(),
                          boardtop + cord[1] * self.block_height())
            
        for cord in self.food.bag:
            self.drawimage(painter, rect.left() + cord[0] * self.block_width(),
                          boardtop + cord[1] * self.block_height(), self.food.image)


    def drawrect(self, painter: QtGui.QPainter, x, y):
        rect = QtCore.QRect(x, y, self.block_width(), self.block_height())
        painter.setBrush(QtGui.QColor(255, 0, 0, 0))
        painter.drawRect(rect)

    def drawimage(self, painter, x, y, image):
        rect = QtCore.QRect(x, y, self.block_width(), self.block_height())
        painter.drawImage(rect, image)

    def start(self):
        self.timer.start(self.SPEED, self)

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        key = a0.key()

        if key == QtCore.Qt.Key.Key_Left:
            if self.snake.direction != 'right':
                self.snake.direction = 'left'
        elif key == QtCore.Qt.Key.Key_Right:
            if self.snake.direction != 'left':
                self.snake.direction = 'right'
        elif key == QtCore.Qt.Key.Key_Up:
            if self.snake.direction != 'down':
                self.snake.direction = 'up'
        elif key == QtCore.Qt.Key.Key_Down:
            if self.snake.direction != 'up':
                self.snake.direction = 'down'
    
    def drop_food(self):

        while len(self.food.bag) < max_apple:
            self.food.generate_food()

    def colision(self):
        for i, cord in enumerate(self.food.bag):
            if cord == self.snake.head:
                self.snake.grow = True
                self.food.bag.pop(i)
                break

    def is_dead(self):
        for snake_part in self.snake.body[1:]:
            if snake_part == self.snake.head:

                self.show_ui()
                self.ui.label.setText(f'Your Score: {len(self.snake.body) - 1}')
                self.timer.stop()

    def restart_game(self):
        self.snake = Snake(self.WIDTHINBLOCKS, self.HEIGHTINBLOCKS)
        self.food = Food(self.WIDTHINBLOCKS, self.HEIGHTINBLOCKS)
        self.timer = QtCore.QBasicTimer()
        self.hide_ui()
        self.start()

    def read_name(self):
        self.ui.lineEdit.show()
        self.ui.input_pushButton.show()

    def input_name(self):
        mp = {}
        with open('snake/score.txt', 'r') as file:
            for i in file.readlines():
                g = i.split(': ')
                mp[int(g[1])] = g[0]

        mp[len(self.snake.body) - 1] = self.ui.lineEdit.text()
        mp = dict(sorted(mp.items()))
        with open('snake/score.txt', 'w') as file:
            for i in mp:
                file.write(f'{mp[i]}: {i}\n')
        self.ui.lineEdit.setText('')


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.board = Board(self)
        self.ui.stackedWidget.addWidget(self.board)

        self.ui.start_pushButton.clicked.connect(self.start_game)
        self.ui.settings_pushButton.clicked.connect(self.open_settings)
        self.ui.score_pushButton.clicked.connect(self.open_score)

        self.ui.back_pushButton.clicked.connect(self.open_menu)
        self.ui.back_pushButton_1.clicked.connect(self.open_menu)

        self.board.ui.menu_pushButton.clicked.connect(self.open_menu)

        self.SPEED = 80
        self.HEIGHTINBLOCKS = 10
        self.WIDTHINBLOCKS = 15

        self.show()
        
    def start_game(self):
        self.ui.stackedWidget.setCurrentIndex(3)
        self.board.start()
    
    def open_menu(self):
        self.ui.stackedWidget.setCurrentIndex(0)

    def open_settings(self):
        self.ui = settings.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.back.clicked.connect(self.Back)

    def Back(self):
        if self.ui.line_speed.text() != '':
            self.SPEED = int(self.ui.line_speed.text())
        if self.ui.line_sizex.text() != '':
            self.WIDTHINBLOCKS = int(self.ui.line_sizex.text())
        if self.ui.line_sizey.text() != '':
            self.HEIGHTINBLOCKS = int(self.ui.line_sizey.text())
        global max_apple
        if self.ui.line_count.text() != '':
            max_apple = int(self.ui.line_count.text())

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.board = Board(self)
        self.board.SPEED = self.SPEED
        self.board.HEIGHTINBLOCKS = self.HEIGHTINBLOCKS
        self.board.WIDTHINBLOCKS = self.WIDTHINBLOCKS
        self.ui.stackedWidget.addWidget(self.board)

        self.ui.start_pushButton.clicked.connect(self.start_game)
        self.ui.settings_pushButton.clicked.connect(self.open_settings)
        self.ui.score_pushButton.clicked.connect(self.open_score)

        self.ui.back_pushButton.clicked.connect(self.open_menu)
        self.ui.back_pushButton_1.clicked.connect(self.open_menu)

        self.board.ui.menu_pushButton.clicked.connect(self.open_menu)

        self.show()

    def open_score(self):
        f = open('./snake/score.txt', 'r')
        text = f.read()
        self.ui.textBrowser.setPlainText(text)
        self.ui.textBrowser.selectAll()
        self.ui.textBrowser.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.ui.stackedWidget.setCurrentIndex(1)

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())