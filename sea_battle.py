from random import randint

class BoardException(Exception):  # exceptions
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Выстрел за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Уже был выстрел в эту клетку!"


class BoardWrongShipException(BoardException):
    pass


class Pos:
    def __init__(self, x: int, y: int) -> None:  # initialization of ship's position dots
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'x={self.y+1}, y={self.x+1}'


class Ship:
    def __init__(self, pos: object, direction: int, lives: int) -> None:
        self.pos = pos

        self.direction = direction  # 0 stands for horizontal, 1 stands for vertical
        self.lives = lives

        self.ship_dots = []
        self.set_dots()

    def set_dots(self) -> None:  # setting dots of the ship
        for i in range(self.lives):
            cur_x = self.pos.x
            cur_y = self.pos.y
            if self.direction == 0:         # horizontal
                cur_x += i
            elif self.direction == 1:       # vertical
                cur_y -= i

            self.ship_dots.append(Pos(cur_x, cur_y))

    def hit(self, shot):                    # hit check
        return shot in self.ship_dots

    def get_lives(self) -> int:  # getting lives
        return self.lives

    def get_dots(self) -> list:  # dots of the ship
        return self.ship_dots


class Board:                                           # inside logic for board
    def __init__(self, board_size=6) -> None:
        self.board_size = board_size

        self.count = 0

        self.alive_ships = []
        self.alive_ships_dots = []

        self.busy_dots = []
        self.shots = []
        self.hit = []

    def contour(self, ship: Ship) -> None:             # dots around ship for not putting them too close
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        for dot in ship.ship_dots:
            for dot_x, dot_y in near:
                current_dot = Pos(dot.x + dot_x, dot.y + dot_y)
                if current_dot not in self.busy_dots and not(self.out(current_dot)):
                    self.busy_dots.append(current_dot)

    def out(self, d) -> bool:                          # checking of range of possibles dots
        return not((0 <= d.x < self.board_size) and (0 <= d.y < self.board_size))

    def ship_placement(self):                          # random placement of a ship
        ship_length = [3, 2, 2, 1, 1, 1, 1]

        attempts = 0

        for length in ship_length:
            while True:

                attempts += 1
                if attempts > 2000:
                    return None

                cur_ship = Ship(Pos(randint(0, self.board_size), randint(0, self.board_size)), randint(0, 1), length)

                try:
                    self.add_ship(cur_ship)
                    break
                except BoardWrongShipException:
                    pass

    def add_ship(self, ship: Ship) -> None:                        # method for adding dots of a ship to ships' dots

        for d in ship.ship_dots:
            if self.out(d) or d in self.busy_dots:
                raise BoardWrongShipException()

        for d in ship.ship_dots:
            self.alive_ships_dots.append(d)
            self.busy_dots.append(d)

        self.alive_ships.append(ship)
        self.contour(ship)

    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException()

        if dot in self.shots:
            raise BoardUsedException()

        self.shots.append(dot)

        for ship in self.alive_ships:
            if dot in ship.ship_dots:
                self.hit.append(dot)
                self.count += 1
                ship.ship_dots.remove(dot)
                if len(ship.ship_dots) == 0:
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

class Player:                                                # parent class players for makings moves and asking man
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

        self.letters_1 = {
            'a': 1,
            'b': 2,
            'c': 3,
            'd': 4,
            'e': 5,
            'f': 6
        }

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):                                                   # class for computer
    def ask(self):
        dot = Pos(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {dot.x + 1} {dot.y + 1}")
        return dot

class Human(Player):   # class for human
    def ask(self):
        while True:
            coordinates = input("Ваш ход: ").split()

            if len(coordinates) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = coordinates

            if not (x.isdigit()) or (y.isdigit()) or y.lower() not in self.letters_1:
                print(" Введите правильные координаты ! ")
                continue

            x, y = int(self.letters_1.get(y.lower())), int(x)

            return Pos(x - 1, y - 1)

class ConsoleGraphicInterface:                                       # putting board to console
    def __init__(self, busy_dots: list, alive_ship_dots: list, shots: list, hit: list,
                 hidden: bool, board_size=6) -> None:
        self.board_size = board_size
        self.field = [['0'] * self.board_size for _ in range(self.board_size)]

        self.busy_dots = busy_dots
        self.alive_ship_dots = alive_ship_dots
        self.shots = shots
        self.hit = hit
        self.hidden = hidden

    def transfer(self) -> None:
        for d in self.alive_ship_dots:
            self.field[d.x][d.y] = '■'

        for d in self.shots:
            self.field[d.x][d.y] = 'T'

        for d in self.hit:
            self.field[d.x][d.y] = 'X'

    def __str__(self):
        letters = {
            1: 'A',
            2: 'B',
            3: 'C',
            4: 'D',
            5: 'E',
            6: 'F'
        }
        self.transfer()
        res = '  | 1 | 2 | 3 | 4 | 5 | 6 |'
        for i, row in enumerate(self.field):
            res += f'\n{letters.get(i+1)} | ' + ' | '.join(row) + ' |'

        if self.hidden:
            res = res.replace("■", "O")
        return res

class Game:                                                            # class for game 
    def __init__(self):
        self.human_board = Board()
        self.human_board.ship_placement()

        self.ai_board = Board()
        self.ai_board.ship_placement()

        self.ai = AI(self.ai_board, self.human_board)
        self.human = Human(self.human_board, self.ai_board)

    @staticmethod
    def greet():
        print(" Добро пожаловать в игру Морской Бой !")                                        # some rules and hi words
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        moves = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")                                                                            # displaying of boards
            print(ConsoleGraphicInterface(self.human.board.busy_dots, self.human.board.alive_ships_dots,
                                          self.human.board.shots, self.human.board.hit, False))
            print("-" * 20)
            print("Доска компьютера:")
            print(ConsoleGraphicInterface(self.ai.board.busy_dots, self.ai.board.alive_ships_dots,
                                          self.ai.board.shots, self.ai.board.hit, True))
            if moves % 2 == 0:                                                                                    # logic of moves
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.human.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                moves -= 1

            if self.ai.board.count == 11:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.human.board.count == 11:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            moves += 1

    def start(self):
        self.greet()
        self.loop()


c1 = Game()
c1.start()
