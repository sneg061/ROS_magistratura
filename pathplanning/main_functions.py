import math
import random
import point
import settings
import drive
import distancesensor
import servo
import RPi.GPIO as GPIO
import time
import wiringpi2

global deterministicObstacles
deterministicObstacles = []


def addObstacles(currentPoint):
    global deterministicObstacles
    currentPoint.obstacles = True
    deterministicObstacles.append(currentPoint)


def distanceSensor(direction, angle = 1000):
    # Передний датчик
    if direction == 1:
        if angle != 1000:
            servo.servo(angle)
        minDistance=100
        for i in range(10):
            curDistance = distancesensor.findDistance("front")
            if curDistance<minDistance:
                minDistance = curDistance
    # Задний датчик
    elif direction == -1:
        minDistance = 100
        for i in range(10):
            curDistance = distancesensor.findDistance("back")
            if curDistance < minDistance:
                minDistance = curDistance
    # Переводим результат в метры
    return minDistance/100

def a_Star(startPoint, finishPointX, finishPointY):
    """Построение траектории с помощью A-star (Необходимо для построения начальной траектории)"""
    # Создаем 2 списка ячеек – открытый и закрытый. В открытом списке изначально находится
    # только ячейка, соответствующая начальному положе-нию робота, в закрытом – ячейки содержащие препятствия
    open = []
    global close
    global history
    global deterministicObstacles
    history = []
    open.append(startPoint)
    close = []
    for l in deterministicObstacles:
        close.append(l)

    def addNewToOpen(currentPoint):
        """обавляет все точки, в которые можно попасть из данной точки в открытый список, текущую точку и точки,
        в которые попасть нельзя - в закрытый.
        Возвращает минимальную по параметру expectedDistance(L=h+l) точку из списка open для дальнейшего рассмотрения"""
        # Добавляем рассматриваемую точку в закрытый список и удаляем из открытого, так
        # как она переходит в категорию рассмотренных
        close.append(currentPoint)
        open.remove(currentPoint)
        """Для рассмотрения всех соседних точек создадим цикл, рассматривающий смещения относительно текущей 
        точки на -1, 0, 1 по координатам x и y"""
        for i in range(-1, 2):
            for j in range(-1, 2):
                # Смещение на (0 , 0) нас не интересует
                if i == 0 and j == 0:
                    continue
                """Проверяем, не является ли новая рассматриваемая точка препятствием или рассмотренной ранее точкой"""
                obstaclesCounter = 0
                addedPoint = currentPoint.nextPoint(i, j, False)
                for k in close:
                    if addedPoint.x == k.x and addedPoint.y == k.y: obstaclesCounter += 1
                if obstaclesCounter != 0:
                    addedPoint.obstacles = True
                else:
                    open.append(addedPoint)
                    history.append(addedPoint)
        """Теперь необходимо выбрать наименьший по параметру expectedDistance(L=h+l) элемент из списка open"""
        minOpenPoint = open[0]
        for k in open:
            if k.expectedDistance(finishPointX, finishPointY) < minOpenPoint.expectedDistance(finishPointX,
                                                                                              finishPointY):
                minOpenPoint = k
        return minOpenPoint

    # Сначала добавим в открытый список все  точки, в которые можно попасть из начальной и найдем
    # оптимальную из этого списка, рассмотрим ее:
    nextCurrentPoint = addNewToOpen(startPoint)
    # Выполняем работу алгоритма A*, пока не придем к финишу
    while (nextCurrentPoint.x != finishPointX or nextCurrentPoint.y != finishPointY):
        nextCurrentPoint = addNewToOpen(nextCurrentPoint)
    # Таким образом найдена финальная точка
    return nextCurrentPoint


def checkObstacles(pointX, pointY):
    """Проверяет на наличие препятствий по координате x, y"""
    global deterministicObstacles
    for currentObstacles in deterministicObstacles:
        if currentObstacles.x == pointX and currentObstacles.y == pointY: return True
        else: return False

def findDirection(currentPoint, nextPoint):
    # Словарь для помещения информации о направлении движения и угле и направлении поворота робота
    resultDirection = dict()
    # Определяем положение следующей точки относительно текущей
    deltaX = nextPoint.x - currentPoint.x
    deltaY = nextPoint.y - currentPoint.y
    # Найдем cos угла между прямыми, соединяющими центр и текущую точку и центр со следующей точкой
    cosAlpha = (2 * currentPoint.x_direction * deltaX + 2 * currentPoint.y_direction * deltaY) / (2 * math.sqrt(currentPoint.x_direction ** 2 + currentPoint.y_direction ** 2) * math.sqrt(deltaX ** 2 + deltaY ** 2))
    # resultDirection["direction"]: если равно 1, то движение вперед, если -1, то назад
    if cosAlpha >= 0:
        resultDirection["direction"] = 1
    else:
        resultDirection["direction"] = -1
    # Применим векторное произведение для нахождения направления поворота
    vectorMultiply = currentPoint.x_direction * deltaY - currentPoint.y_direction * deltaX
    # resultDirection["turnDirection"]: если -1 - направо, 1 - налево
    if vectorMultiply * resultDirection["direction"] < 0:
        resultDirection["turnDirection"] = -1
    elif vectorMultiply * resultDirection["direction"] > 0:
        resultDirection["turnDirection"] = 1
    else:
        resultDirection["turnDirection"] = 0
    # Угол поворота
    if resultDirection["direction"] >= 0:
        resultDirection["turnAngle"] = round(math.degrees(math.acos(cosAlpha)))
    else:
        resultDirection["turnAngle"] = 180-round(math.degrees(math.acos(cosAlpha)))
    return resultDirection

def simpleMotion(currentPoint):
    motion = findDirection(currentPoint, currentPoint.previousPoint)
    if motion["turnDirection"] == -1:
        drive.motor_go("right", motion["turnAngle"])
    elif motion["turnDirection"] == 1:
        drive.motor_go("left", motion["turnAngle"])
    else:
        pass
    if motion["direction"] == 1:
        drive.motor_go("front")
    elif motion["direction"] == -1:
        drive.motor_go("back")


def motionToNextPoint(currentPoint):
    """Движение от текущей точки до следующей"""
    # Находим вектор, на который нам необходимо переместить робота
    deltaX = currentPoint.previousPoint.x - currentPoint.x
    deltaY = currentPoint.previousPoint.y - currentPoint.y
    # Направление к точке
    motionDirection = findDirection(currentPoint, currentPoint.previousPoint)
    # Проверяем, является ли следующая точка соседней по диагонали
    if motionDirection["direction"] == 1:
        if motionDirection["turnDirection"] == -1:
            obstacleDistance = distanceSensor(1, 90 + motionDirection["turnAngle"])
            if deltaX != 0 and deltaY != 0:
                if obstacleDistance <= settings.cell_lenght * math.sqrt(2):
                    addObstacles(currentPoint.previousPoint)
                    return False
            else:
                if obstacleDistance <= settings.cell_lenght:
                    addObstacles(currentPoint.previousPoint)
                    return False
        else:
            obstacleDistance = distanceSensor(1, 90 - motionDirection["turnAngle"])
            if deltaX != 0 and deltaY != 0:
                if obstacleDistance <= settings.cell_lenght * math.sqrt(2):
                    addObstacles(currentPoint.previousPoint)
                    return False
            else:
                if obstacleDistance <= settings.cell_lenght:
                    addObstacles(currentPoint.previousPoint)
                    return False
    else:
        obstacleDistance = distanceSensor(-1)
        if obstacleDistance <= settings.cell_lenght:
            addObstacles(currentPoint.previousPoint)
            return False

    if deltaX != 0 and deltaY != 0:
        # Следующая точка - на диагонали, значит необходима проверка соседних к ней точек на препятствие
        if checkObstacles(currentPoint.x, currentPoint.y + deltaY)!= True and checkObstacles(currentPoint.x +deltaX, currentPoint.y)!= True:
            simpleMotion(currentPoint)
            currentPoint.previousPoint.x_direction = deltaX * findDirection(currentPoint, currentPoint.previousPoint)["direction"]
            currentPoint.previousPoint.y_direction = deltaY * findDirection(currentPoint,currentPoint.previousPoint)["direction"]
        else:
            tempPoint = currentPoint.previousPoint
            if checkObstacles(currentPoint.x, currentPoint.y + deltaY)!= True:
                middlePoint = point.Point(currentPoint.x, currentPoint.y + deltaY, False, tempPoint, 0)
            elif checkObstacles(currentPoint.x + deltaX, currentPoint.y)!= True:
                middlePoint = point.Point(currentPoint.x + deltaX, currentPoint.y, False, tempPoint, 0)
            else: pass
            middlePoint.x_direction = (middlePoint.x - currentPoint.x) * findDirection(currentPoint, middlePoint)[
                "direction"]
            middlePoint.y_direction = (middlePoint.y - currentPoint.y) * findDirection(currentPoint, middlePoint)[
                "direction"]
            tempPoint.x_direction = (tempPoint.x - middlePoint.x) * findDirection(middlePoint, tempPoint)[
                "direction"]
            tempPoint.y_direction = (tempPoint.y - middlePoint.y) * findDirection(middlePoint, tempPoint)[
                "direction"]
            currentPoint.previousPoint = middlePoint
            simpleMotion(currentPoint)
            print(currentPoint.previousPoint.x, currentPoint.previousPoint.y)
            simpleMotion(middlePoint)
            print(middlePoint.previousPoint.x, middlePoint.previousPoint.y)
            currentPoint.previousPoint = tempPoint
    else:
        simpleMotion(currentPoint)
        currentPoint.previousPoint.x_direction = deltaX * findDirection(currentPoint, currentPoint.previousPoint)[
            "direction"]
        currentPoint.previousPoint.y_direction = deltaY * findDirection(currentPoint, currentPoint.previousPoint)[
            "direction"]
    return True


def d_Star(finishPoint, startPointX, startPointY):
    """Реализует алгоритм D*"""
    global history
    global open
    global close
    global deterministicObstacles
    currentPoint = a_Star(finishPoint, startPointX, startPointY)
    while currentPoint != finishPoint:
        if checkObstacles(currentPoint.previousPoint.x, currentPoint.previousPoint.y) == True or currentPoint.previousPoint.obstacles == True:
            print("obstacle")
            # Если препятствие есть, выбираем как следующую точку ту точку из списка истории, в которой
            # нет препятствия и расстояние от которое до конечной в сумме с расстоянием от текущей до нее минимально)
            # Строим список всех соседних точек
            currentPoint.previousPoint.obstacles = True
            pointNear = []
            for k in history:
                # Пересчитываем расстояние для каждой точки в связи с изменениями на карте
                k.LenFromStart = k.previousPoint.LenFromStart + k.weight()
                # Составляем список из соседних точек, не являющихся препятствиями
                if math.fabs(k.x - currentPoint.x) <= 1 and math.fabs(k.y - currentPoint.y) <= 1 and (
                        k.x != currentPoint.x or k.y != currentPoint.y) and k.obstacles == False:
                    # Добавляем все соседние точки в новый список
                    pointNear.append(k)

            # Функция для сортировки по LenFromStart
            def byDistance_key(point):
                return point.LenFromStart

            # Сортировка массива по LenFromStart
            sortedPointNear = sorted(pointNear, key=byDistance_key)
            # Если нет рядом точек, в которые можно попасть - строим заново по A*
            if len(sortedPointNear) > 0:
                print("12345")
                # Если через соседние точки не попасть в конечную - строим заново по A*
                if sortedPointNear[0].LenFromStart < math.inf:
                    # Если все условия удовлетворены, идем в точку с минимальным значением LenFromStart
                    currentPoint.previousPoint = sortedPointNear[0]
                    print("D-star ")
                else:
                    print("A*")
                    for j in history:
                        history.remove(j)
                    currentPoint = a_Star(finishPoint, currentPoint.x, currentPoint.y)
            else:
                print("other A*")
                for j in history:
                    history.remove(j)
                currentPoint = a_Star(finishPoint, currentPoint.x, currentPoint.y)

        # Перемещаемся из текущей точки в следующую по траектории
        answer = motionToNextPoint(currentPoint)

        if answer!=False:
            # Берем за рассматриваемую следующую точку
            currentPoint = currentPoint.previousPoint
