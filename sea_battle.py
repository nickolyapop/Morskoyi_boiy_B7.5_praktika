from random import  randint

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # сравнение двух точек
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"

# Классы исключений
class BoardException(Exception):    #общий класс
    pass
class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь высьрелить за доску!"
class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

#исключение для размещения кореблей
class BoardWrongShipException(BoardException):
    pass

# =========Класс КОРАБЛЯ ==============

class Ship:
    #конструктор корабля
    def __init__(self, bow, l, o):  # o -orientation
        self.bow = bow
        self.l = l  # длина корабля
        self.o = o  # Ориенатцяи корабля 0 -вертикаль 1- горизонталь
        self.lives = l # кол-во жизней

    @property # метод  вычисляет cвойство
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i
            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    # метод выстрел, проверка попадания
    def shooten(self, shot):
        return shot in self.dots

# ==========КЛАСС "ИГРОВОЕ ПОЛЕ" ==================

class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count_kill = 0      #счетчик подбитых кораблей
        # состояние полей
        self.field = [ ["0"]*size for _ in range(size)] # заполняем 0

        self.busy = []  # занятые точки, корабль либо выстрел
        self.ships = [] # список кораблей

        # вывод корабля на доску

    def __str__(self): # метод вывода доски, вызовом print доски
        res = ""
        i = 0
        for row in self.field:  # счетчик-цикл  прохода по строкам доски
            res += f"\n{i+1} ▌ " + " | ".join(row) + " ▌"# +f" {i+1} | " + " | ".join(row) + " ▌"  # номер строки +
            i += 1
        # скрытие клетки
        if self.hid:
            res = res.replace("■", "0")
        return res


    # метод проверяющий выхода точки за пределы поля
    def out(self, d):
        return not((0 <=d.x < self.size) and (0 <= d.y < self.size))

    # КОРАБЛЬ НА ДОСКЕ
    # МЕТОД КОНТУР КОРАБЛЯ

    def contur(self, ship, verb =False):
        # поле вокруг корабля
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1),
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    # МЕТОД ДОБАВЛЕНИЯ КОРАБЛЯ
    def add_ship(self, ship):
        for d in ship.dots:
            # не выходит точка за границу или не занята
            if self.out(d) or d in self.busy:  #
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d) # добав. точку в список занятых

        self.ships.append(ship)
        self.contur(ship)

    # Выстрел ПО ДОСКЕ ===================
    def shot(self, d):
        if self.out(d):
            # исключение если точка вне границы
            raise BoardOutException()

        if d in self.busy:
            # исключение если точка занята
            raise BoardUsedException()

        self.busy.append(d)

        # проверка точки на принадлежность кораблю
        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count_kill += 1
                    self.contur(ship, verb= True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Попадание в корабль!")
                    return True
        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count_kill == len(self.ships)

# КЛАСС "ИГРОК" ==========================

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise  NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask() # запрос координат на выстрел
                repeat = self.enemy.shot(target)
                return  repeat
            # неправльный выстрел, вызвать исключение
            except BoardException as e:
                print(e)

# Классы игроков компьютера и пользователя

class AI(Player):
    def ask(self):
        # генерация случайной точки для выстрела компа
        d = Dot(randint(0,5), randint(0, 5))
        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d

# запрос координат от пользователя
class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print("Введите 2 координаты! ")
                continue

            x, y = cords

            if not(x.isdigit()) or not(y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return  Dot(x-1, y-1)

# ==============================
# Класс ИГРА И ГЕНЕРАЦИЯ ДОСОК
# ==============================

class Game:
    def try_bord(self):
        lens = [3, 2, 2, 1, 1, 1, 1] # длина кораблей
        board = Board(size = self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000: # кол-во попыток итераций для создания доски
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0,1))
                try:
                    board.add_ship(ship)    # добавление корабля
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    # генерация доски
    def random_board(self):
        board = None
        while board is None:
            board = self.try_bord()
        return  board

    # конструктор и ПРИВЕТСТВИЕ ===================

    def __init__(self, size = 6):
        self.size = size
        #  создаем две доски для игрока и компьютера
        pl = self.random_board()
        pc = self.random_board()
        pc.hid = True

        # создаем двух игроков
        self.ai = AI(pc, pl)
        self.us = User(pl, pc)

    def greet(self):
        print("==========================")
        print("|    игра МОРСКОЙ БОЙ    |")
        print("==========================")
        print(" формат ввода: х у        ")
        print(" x - номер строки ")
        print(" у - номер столбца")

    #   Игровой цикл ===========================

    def print_boards(self):
        print("-" * 20)
        print("Доска пользователя: ")#+" "*10+"Доска компьютера:")
        print("  ▌ 1 | 2 | 3 | 4 | 5 | 6 ▌ ", end=" ")
        print(self.us.board)
        print("-" * 20)
        print("Доска компьютера:")
        print("  ▌ 1 | 2 | 3 | 4 | 5 | 6 ▌ ", end=" ")
        print(self.ai.board)

           # for i in range(self.size):

        print("-" * 20)

    def loop(self):
        num = 0 # номер хода
        while True:
            self.print_boards()

            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.defeat():
                self.print_boards()
                print("-"*20)
                print("Пользователь выиграл!")
                break

            if self.us.board.defeat():
                self.print_boards()
                print("-"*20)
                print("Компьютер выиграл!")
                break
            num += 1
    # МЕТОД "СТАРТ"

    def start(self):
        self.greet()
        self.loop()

    # ЗАПУСК ИГРЫ

g = Game()
g.start()

