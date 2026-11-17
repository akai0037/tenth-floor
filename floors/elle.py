"""Floor 7: the Computer Lab.

Three rooms, west to east: the hallway off the West elevator, the computer lab, and the server closet
by the East elevator. The digit is in the filing cabinet on the high shelf in the computer lab:
climb the desk ledge, ride the moving platform, and jump up to the shelf.
Practise it: py main.py --floor elle    Check it: py check.py --floor elle
"""
import random

import pygame

from engine import config as C
from engine.kit import (CeilingLight, Crusher, Drone, FilingCabinet, FloorLaser, Locker, MovingPlatform,
                        PatrolBot, Plant, Poster, ServerRack, Sign, VendingMachine, Window)
from engine.room import Furniture, Platform, Room

NAME = "Floor 7: Computer Lab"     # the name on the elevator panel
AUTHOR = "Elle"                    # your name


class ComputerDesk(Furniture):
    """A lab desk with a monitor: code scrolls up the screen and the cursor blinks.
    Once searched, the screen goes dark (someone logged out)."""

    W, H = 110, 80
    CODE = [(120, 220, 140), (110, 190, 250), (240, 140, 200), (230, 220, 150), (180, 180, 200)]

    def __init__(self, x, y, name="computer", holds_piece=False):
        super().__init__(x, y, self.W, self.H, name, holds_piece)
        rng = random.Random(x * 7 + y)               # each desk scrolls its own code
        self.lines = [(rng.randint(0, 3) * 4, rng.randint(8, 34), rng.choice(self.CODE)) for _ in range(12)]
        self.speed = rng.uniform(10, 18)             # pixels a second the code scrolls
        self.phase = rng.uniform(0, 6)

    def draw(self, surf):
        r = self.rect
        wood = (150, 110, 70) if not self.searched else (110, 96, 84)
        legs = (120, 88, 56) if not self.searched else (92, 82, 72)
        top = pygame.Rect(r.left, r.bottom - 34, r.w, 8)
        pygame.draw.rect(surf, wood, top)
        pygame.draw.rect(surf, legs, (r.left + 6, top.bottom, 8, r.bottom - top.bottom))
        pygame.draw.rect(surf, legs, (r.right - 14, top.bottom, 8, r.bottom - top.bottom))
        pygame.draw.rect(surf, C.INK, top, 2)
        # keyboard and mouse
        pygame.draw.rect(surf, (60, 62, 72), (r.left + 18, top.top - 4, 46, 4))
        pygame.draw.ellipse(surf, (60, 62, 72), (r.left + 72, top.top - 5, 9, 5))
        # monitor on a stand
        mon = pygame.Rect(r.centerx - 30, r.top, 60, 40)
        pygame.draw.line(surf, (30, 32, 40), (r.centerx, mon.bottom), (r.centerx, top.top - 4), 4)
        pygame.draw.rect(surf, (30, 32, 40), mon, border_radius=3)
        screen = mon.inflate(-6, -6)
        if self.searched:
            pygame.draw.rect(surf, (14, 16, 22), screen)
            return
        t = pygame.time.get_ticks() / 1000.0 + self.phase
        pygame.draw.rect(surf, (16, 22, 34), screen)
        surf.set_clip(screen)
        step = 5
        scroll = int(t * self.speed) % (step * len(self.lines))
        for i, (indent, width, col) in enumerate(self.lines):
            y = screen.top + 3 + i * step - scroll
            if y < screen.top - step:
                y += step * len(self.lines)
            pygame.draw.line(surf, col, (screen.left + 3 + indent, y), (screen.left + 3 + indent + width, y), 2)
        if int(t * 2) % 2 == 0:                       # blinking cursor
            pygame.draw.rect(surf, (230, 230, 230), (screen.left + 4, screen.bottom - 6, 4, 3))
        surf.set_clip(None)
        pygame.draw.rect(surf, (90, 160, 220), screen, 1)    # screen glow edge


class CodeRainRoom(Room):
    """A room whose wall is hacker-style code rain. Every room on this floor uses it:
    subclass it and call self.build_code_rain() at the end of build()."""

    # --- hacker-style code rain on the wall behind everything ---
    RAIN_CHARS = "0101010123456789ABCDEF{}<>/=;#$*+"
    RAIN_ROW = 16          # pixels between characters in a column
    RAIN_COL = 18          # pixels between columns

    def build_code_rain(self):
        """Fonts and glyphs are made once here, never in draw (they are slow to build)."""
        font = pygame.font.Font(None, 20)
        shades = [(16, 50, 26), (24, 85, 40), (36, 130, 60), (60, 190, 95), (200, 255, 210)]  # tail -> head
        self.glyphs = [[font.render(ch, True, col) for ch in self.RAIN_CHARS] for col in shades]
        self.rng = random.Random(self.title)
        self.rain = [self.new_drop(x, start=True) for x in range(4, C.W, self.RAIN_COL)]

    def new_drop(self, x, start=False):
        r = self.rng
        length = r.randint(6, 18)
        return {"x": x,
                "y": r.uniform(0, C.FLOOR_Y) if start else -r.uniform(0, 300),
                "speed": r.uniform(60, 160),
                "length": length,
                "chars": [r.randrange(len(self.RAIN_CHARS)) for _ in range(length)]}

    def update(self, dt, player):
        for i, d in enumerate(self.rain):
            d["y"] += d["speed"] * dt
            if d["y"] - d["length"] * self.RAIN_ROW > C.FLOOR_Y:
                self.rain[i] = self.new_drop(d["x"])
            elif self.rng.random() < dt * 4:             # characters flicker and change
                d["chars"][self.rng.randrange(d["length"])] = self.rng.randrange(len(self.RAIN_CHARS))

    def draw_background(self, surf):
        surf.fill((6, 12, 10))
        for d in self.rain:
            head = int(d["y"])
            n = d["length"]
            for k in range(n):
                y = head - k * self.RAIN_ROW
                if y < 0 or y > C.FLOOR_Y - 12:
                    continue
                level = 4 if k == 0 else 3 - min(3, k * 4 // n)
                surf.blit(self.glyphs[level][d["chars"][k]], (d["x"], y))


class Hallway(CodeRainRoom):
    """Off the West elevator: lockers, a vending machine, and a patrol bot by the lab door."""

    title = "Floor 7: Hallway"

    def build(self):
        self.decor += [Sign(330, 46, "FLOOR 7  COMPUTER LAB"), CeilingLight(300), CeilingLight(700),
                       Poster(130, 90, "SVA"), Poster(220, 90, "CRIT", (70, 130, 180)), Window(560, 70, seed=7)]
        self.platforms.append(Platform(250, 400, 160))          # a bench to hop onto, away from the bot
        self.furniture += [Plant(110, C.FLOOR_Y), VendingMachine(440, C.FLOOR_Y),
                           Locker(650, C.FLOOR_Y), Locker(700, C.FLOOR_Y), Locker(750, C.FLOOR_Y)]
        self.hazards.append(PatrolBot(500, C.FLOOR_Y, left=200, right=820, speed=85))
        self.build_code_rain()


class ComputerLab(CodeRainRoom):
    """The digit is in the filing cabinet on the high shelf: desk ledge -> moving platform -> shelf."""

    title = "Floor 7: Computer Lab"

    def build(self):
        self.decor += [Sign(360, 46, "COMPUTER LAB"), CeilingLight(250), CeilingLight(700),
                       Poster(110, 90, "RENDER", (150, 90, 160)), Window(380, 70, seed=2)]
        self.platforms.append(Platform(200, 410, 200))                              # the desk ledge
        self.platforms.append(MovingPlatform(430, 560, 320, width=110, speed=70))  # rides you across
        self.platforms.append(Platform(720, 230, 170))                              # the high shelf
        self.furniture += [ComputerDesk(100, C.FLOOR_Y, "front computer"), ComputerDesk(240, 410, "monitor row"),
                           ComputerDesk(520, C.FLOOR_Y, "teacher's computer"),
                           FilingCabinet(800, 230, "filing cabinet", holds_piece=True)]
        self.hazards.append(Drone(620, y_top=340, y_bottom=C.FLOOR_Y, speed=80))
        self.build_code_rain()


class ServerCloset(CodeRainRoom):
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
        self.build_code_rain()


ROOMS = [Hallway, ComputerLab, ServerCloset]
