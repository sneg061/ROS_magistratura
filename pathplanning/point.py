import math


# ДЛЯ АЛОГРИТМА D* РАССМАТРИВАЕТСЯ ПОСТРОЕНИЕ ТРАЕКТОРИИ ОТ КОНЕЧНОЙ ТОЧКИ ДО НАЧАЛЬНОЙ, СЛЕДОВАТЕЛЬНО В ОПИСАНИЯХ
# ФУНКЦИЙ СЛЕДУЕТ ЗАМЕНИТЬ НАЧАЛЬНУЮ ТОЧКУ НА КОНЕЧНУЮ И НАОБОРОТ


class StartPoint:
    """Класс, созданный для определения основных характеристик начальной точки"""

    def __init__(self, x, y, obstacles, x_direction=1, y_direction=0):
        # Координаты
        self.__x = x
        self.__y = y
        # Наличие препятствия в данной точке (True - есть препятствие, False - нет)
        self.__obstacles = obstacles
        #Длина пути от начальной точки
        self.__LenFromStart = 0
        # Ориентация робота по x и y
        self.__x_direction = x_direction
        self.__y_direction = y_direction

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, x):
        self.__x = x

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, y):
        self.__y = y

    @property
    def obstacles(self):
        return self.__obstacles

    @obstacles.setter
    def obstacles(self, obstacles):
        self.__obstacles = obstacles

    @property
    def x_direction(self):
        return self.__x_direction

    @x_direction.setter
    def x_direction(self, x_direction):
        self.__x_direction = x_direction

    @property
    def y_direction(self):
        return self.__y_direction

    @y_direction.setter
    def y_direction(self, y_direction):
        self.__y_direction = y_direction

    @property
    def LenFromStart(self):
        return self.__LenFromStart

    @LenFromStart.setter
    def LenFromStart(self, LenFromStart):
        self.__LenFromStart = LenFromStart

    def __getattr__(self, previousPoint):
        return False

    def fromStart(self):
        """Считает расстояние, пройденное от начальной точки до текущей"""
        return 0

    def count(self):
        """Номер шага на текущей точке"""
        return 0

    def nextPoint(self, dx, dy, dObstacles):
        """Создание следующей точки: dx, dy - сдвиги относительно текущей точки по осям x и y соответственно,
        dObstacles - наличие препятствия"""
        return Point(self.x + dx, self.y + dy, dObstacles, self)


class Obstacles(StartPoint):
    """Класс для точек, являющихся препятствиями"""

    def __init__(self, x, y, obstacles=True, x_direction=1, y_direction=0):
        super(Obstacles, self).__init__(x, y, obstacles, x_direction, y_direction)
        self.__LenFromStart = math.inf

    def fromStart(self):
        """Считает расстояние, пройденное от начальной точки до текущей"""
        return math.inf

    def expectedDistance(self, finishPointX, finishPointY):
        """Ожидаемое расстояние от начальной точки до целевой через текущую точку (сумма 2 расстояний:
        расстояния от начальной точки до текущей и расстояние, полученное с помощью эвристической функции"""
        return math.inf

    def weight(self):
        """Определяет вес точки, который равен Расстоянию от предыдущей точки до текущей, если ячейка
        свободна или бесконечно большому значению, если ячейка занята (сложность попадания в ячейку)"""
        return math.inf

    def count(self):
        """Номер шага на текущей точке"""
        return None

    def nextPoint(self, dx, dy, dObstacles):
        """Создание следующей точки: dx, dy - сдвиги относительно текущей точки по осям x и y соответственно,
         dObstacles - наличие препятствия"""
        return None


class Point(StartPoint):
    """Класс, созданный для определения основных характеристик всех рассматриваемых точек кроме начальной"""

    def __init__(self, x, y, obstacles, previousPoint, x_direction=1, y_direction=0):
        super(Point, self).__init__(x, y, obstacles, x_direction, y_direction)
        # Точка, из которой мы попали в текущую
        self.__previousPoint = previousPoint
        self.__LenFromStart = self.previousPoint.LenFromStart + self.weight()

    @property
    def previousPoint(self):
        return self.__previousPoint

    @previousPoint.setter
    def previousPoint(self, previousPoint):
        self.__previousPoint = previousPoint

    def fromStart(self):
        """Считает расстояние, пройденное от начальной точки до текущей"""
        return math.sqrt(math.pow(self.x - self.previousPoint.x, 2) + math.pow(self.y - self.previousPoint.y,
                                                                               2)) + self.previousPoint.fromStart()

    def updateFromStart(self):
        return self.weight() + self.previousPoint.LenFromStart

    def count(self):
        """Номер шага на текущей точке"""
        return self.previousPoint.count() + 1

    def heuristic(self, finishPointX, finishPointY):
        """Значение эвристической функции для данной точки, в данном случае определяется просто как расстояние
        по прямой от данной точки до целевой"""
        return math.sqrt(math.pow(self.x - finishPointX, 2) + math.pow(self.y - finishPointY, 2))

    def expectedDistance(self, finishPointX, finishPointY):
        """Ожидаемое расстояние от начальной точки до целевой через текущую точку (сумма 2 расстояний: расстояния
         от начальной точки до текущей и расстояние, полученное с помощью эвристической функции"""
        return self.heuristic(finishPointX, finishPointY) + self.LenFromStart

    def weight(self):
        """Определяет вес точки, который равен Расстоянию от предыдущей точки до текущей, если ячейка свободна или
         бесконечно большому значению, если ячейка занята (сложность попадания в ячейку)"""
        if self.obstacles == False:
            return math.sqrt(math.pow(self.x - self.previousPoint.x, 2) + math.pow(self.y - self.previousPoint.y, 2))
        else:
            return math.inf
