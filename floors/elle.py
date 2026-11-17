"""Floor 7: the Computer Lab.

Three rooms, west to east: the hallway off the West elevator, the computer lab, and the server closet
by the East elevator. The digit is in the filing cabinet on the high shelf in the computer lab:
climb the desk ledge, ride the moving platform, and jump up to the shelf.
Practise it: py main.py --floor elle    Check it: py check.py --floor elle
"""
from engine import config as C
from engine.kit import (CeilingLight, Crusher, Desk, Drone, FilingCabinet, FloorLaser, Locker, MovingPlatform,
                        PatrolBot, Plant, Poster, ServerRack, Sign, VendingMachine, Window)
from engine.room import Platform, Room

NAME = "Floor 7: Computer Lab"     # the name on the elevator panel
AUTHOR = "Elle"                    # your name


class Hallway(Room):
    """Off the West elevator: lockers, a vending machine, and a patrol bot by the lab door."""

    title = "Floor 7: Hallway"

    def build(self):
        self.decor += [Sign(330, 46, "FLOOR 7  COMPUTER LAB"), CeilingLight(300), CeilingLight(700),
                       Poster(130, 90, "SVA"), Poster(220, 90, "CRIT", (70, 130, 180)), Window(560, 70, seed=7)]
        self.platforms.append(Platform(250, 400, 160))          # a bench to hop onto, away from the bot
        self.furniture += [Plant(110, C.FLOOR_Y), VendingMachine(440, C.FLOOR_Y),
                           Locker(650, C.FLOOR_Y), Locker(700, C.FLOOR_Y), Locker(750, C.FLOOR_Y)]
        self.hazards.append(PatrolBot(500, C.FLOOR_Y, left=200, right=820, speed=85))


class ComputerLab(Room):
    """The digit is in the filing cabinet on the high shelf: desk ledge -> moving platform -> shelf."""

    title = "Floor 7: Computer Lab"

    def build(self):
        self.decor += [Sign(360, 46, "COMPUTER LAB"), CeilingLight(250), CeilingLight(700),
                       Poster(110, 90, "RENDER", (150, 90, 160)), Window(380, 70, seed=2)]
        self.platforms.append(Platform(200, 410, 200))                              # the desk ledge
        self.platforms.append(MovingPlatform(430, 560, 320, width=110, speed=70))  # rides you across
        self.platforms.append(Platform(720, 230, 170))                              # the high shelf
        self.furniture += [Desk(100, C.FLOOR_Y, "front desk"), Desk(240, 410, "monitor row"),
                           Desk(520, C.FLOOR_Y, "teacher's desk"),
                           FilingCabinet(800, 230, "filing cabinet", holds_piece=True)]
        self.hazards.append(Drone(620, y_top=340, y_bottom=C.FLOOR_Y, speed=80))


class ServerCloset(Room):
    """By the East elevator: racks, a floor laser, and a crusher before the elevator."""

    title = "Floor 7: Server Closet"

    def build(self):
        self.decor += [Sign(370, 46, "SERVER CLOSET"), CeilingLight(480),
                       Poster(120, 90, "NO FOOD", (200, 70, 60))]
        self.platforms.append(Platform(500, 400, 200))
        self.furniture += [ServerRack(150, C.FLOOR_Y), ServerRack(220, C.FLOOR_Y), ServerRack(290, C.FLOOR_Y),
                           ServerRack(560, 400), ServerRack(630, 400)]
        self.hazards.append(FloorLaser(340, 480, on_time=1.2, off_time=1.6))
        self.hazards.append(Crusher(740, y_top=250, y_bottom=C.FLOOR_Y, w=60, h=50))


ROOMS = [Hallway, ComputerLab, ServerCloset]
