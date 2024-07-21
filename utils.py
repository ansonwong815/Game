import enum
import random
import pygame
import csv
from pathlib import Path


class WeaponLoader:
    def __init__(self):
        self.weapons = []
        self.setup()

    def setup(self):
        with open(Path(__file__).resolve().with_name("swords.csv"), mode='r', newline='') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                self.weapons.append(Weapon(*row, WeaponType.SWORD))
        with open(Path(__file__).resolve().with_name("wands.csv"), mode='r', newline='') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                self.weapons.append(Weapon(*row, WeaponType.WANDS))
        with open(Path(__file__).resolve().with_name("bows.csv"), mode='r', newline='') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                self.weapons.append(Weapon(*row, WeaponType.BOWS))

    def get_random(self):
        total_rarity = sum(weapon.rarity for weapon in self.weapons)
        pick = random.randint(1, total_rarity)
        current = 0
        for weapon in self.weapons:
            current += weapon.rarity
            if current >= pick:
                return weapon


class Weapon:
    def __init__(self, name, damage, crit_rate, crit_damage, DOTTurns, DOTDam, rarity, iconPath, weaponType):
        self.name = name
        self.damage = float(damage)
        self.critRate = float(crit_rate)
        self.critDamage = float(crit_damage)
        self.DOTTurns = int(DOTTurns)
        self.DOTDam = float(DOTDam)
        self.rarity = int(rarity)
        self.weaponType = weaponType
        self.iconPath = Path(__file__).resolve().parent / iconPath
        self.icon = pygame.image.load(self.iconPath).convert_alpha()
        if self.rarity == 1:
            self.background_colour = (255, 215, 0)
        elif self.rarity == 2:
            self.background_colour = (200, 145, 255)
        else:
            self.background_colour = (96, 222, 247)
        self.stats_surface = self.update_stats()

    def roll(self):
        self.damage = round(self.damage * random.uniform(0.75, 1.25), 2)
        self.critRate = round(self.critRate * random.uniform(0.75, 1.25), 2)
        self.critDamage = round(self.critDamage * random.uniform(0.75, 1.25), 2)
        self.DOTDam = round(self.DOTDam * random.uniform(0.75, 1.25), 2)
        self.stats_surface = self.update_stats()

    def info(self):
        res = [(f"{self.name}", 20),
               (f"Dam: {self.damage}", 10), ]
        if self.critRate != 0:
            res.append((f"CritRate: {round(self.critRate * 100, 2)}%", 10))
            res.append((f"CritDam: {round(self.critDamage * 100, 2)}%", 10))
        if self.DOTTurns != 0:
            res.append((f"DOTTurns: {round(self.DOTTurns, 2)}", 10))
            res.append((f"DOTDam: {round(self.DOTDam * 100, 2)}%", 10))
        return res

    def update_stats(self):
        text_color = (255, 255, 255)  # White
        background_color = (0, 0, 255)  # Blue
        total_height = 0
        width = 0
        for string, font_size in self.info():
            font = pygame.font.SysFont("Arial", font_size)
            total_height += font.get_linesize()
            width = max(width, font.size(string)[0])
        surface = pygame.Surface((width, total_height))
        rect = pygame.Rect(0, 0, width, total_height)
        text_x = rect.centerx - width / 2
        text_y = rect.centery - total_height / 2
        pygame.draw.rect(surface, background_color, rect, 0)
        y_offset = text_y
        for string, font_size in self.info():
            font = pygame.font.SysFont("Arial", font_size)
            text_surface = font.render(string, True, text_color)
            text_rect = text_surface.get_rect(x=text_x, y=y_offset)
            surface.blit(text_surface, text_rect)
            y_offset += font.get_linesize()
        return surface


class Button:
    def __init__(self, x, y, w, h, data, callback, toggle, background=None, info=None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.data = data
        self.callback = callback
        self.font = pygame.font.SysFont("Arial", round(h * 0.75))
        self.toggled = False
        self.toggle = toggle
        self.info = info
        self.selected = False
        button_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        if isinstance(data, pygame.Surface):
            self.surface = pygame.Surface(data.get_size())
            if background is not None:
                self.surface.fill(background)
            self.surface.blit(data, (0, 0))
            self.surface = pygame.transform.scale(self.surface, (self.w, self.h))
            self.rect = self.surface.get_rect(center=button_rect.center)
        else:
            self.surface = pygame.Surface((w, h))
            if background is not None:
                self.surface.fill(background)
            text_rect = self.font.render(self.data, True, (255, 255, 255))
            self.surface.blit(text_rect, (self.surface.get_width() // 2 - text_rect.get_width() // 2,
                                          self.surface.get_height() // 2 - text_rect.get_height() // 2))
            self.rect = self.surface.get_rect(center=button_rect.center)
        if isinstance(info, Weapon):
            img = pygame.image.load(Path(__file__).resolve().with_name("delete.png")).convert_alpha()
            img = pygame.transform.scale(img, (8, 8))
            self.surface.blit(img, (0, 0))
        self.top_rect = pygame.Rect(self.x, self.y, self.w, 1)
        self.bottom_rect = pygame.Rect(self.x, self.y + self.h, self.w, 1)

    def move(self, x, y):
        self.x = x
        self.y = y
        button_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.rect = self.surface.get_rect(center=button_rect.center)


class Alert:
    def __init__(self, game):
        self.game = game
        self.text = ""
        self.txtArr = [["", float("inf")]]
        self.font = pygame.font.SysFont("Arial", int(self.game.cell_size * 0.75))
        self.text_surface = self.font.render(self.text, True, (255, 0, 0))

    def change_text(self):
        if callable(self.txtArr[0][0]):
            self.text = self.txtArr[0][0]() + " "
        else:
            self.text = self.txtArr[0][0] + " "
        self.text_surface = self.font.render(self.text, True, (255, 0, 0))

    def add_text(self, data, time):
        self.txtArr.insert(0, [data, time * 60])
        pass

    def render(self):
        for i in self.txtArr:
            i[1] -= 1
            if i[1] == 0:
                self.txtArr.remove(i)
        self.change_text()
        self.game.screen.blit(self.text_surface, (self.game.screen.get_width() - self.text_surface.get_width(), 0))


class Direction(enum.Enum):
    UP = [0, -1]
    DOWN = [0, 1]
    LEFT = [-1, 0]
    RIGHT = [1, 0]
    NONE = [0, 0]

    def opposite(self):
        if self == Direction.UP:
            return Direction.DOWN
        if self == Direction.DOWN:
            return Direction.UP
        if self == Direction.LEFT:
            return Direction.RIGHT
        if self == Direction.RIGHT:
            return Direction.LEFT


class WeaponType(enum.Enum):
    SWORD = 0
    BOWS = 1
    WANDS = 2
