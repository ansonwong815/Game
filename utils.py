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
        # Load weapons from csv files
        for weapon_type in ["swords", "wands", "bows"]:
            with open(Path(__file__).resolve().with_name(f"{weapon_type}.csv"), mode='r', newline='') as file:
                reader = csv.reader(file)
                next(reader)  # Skip the heading
                for row in reader:
                    self.weapons.append(Weapon(*row, getattr(WeaponType, weapon_type.upper())))

    def get_random(self):
        # Get a random weapon based on the rarity
        # Imagine each weapon as a segment with width rarity as length on a line.
        # Random number is picked between 1 and total rarity of weapons will point to a weapon which would be returned
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
        self.background_colour = {1: (255, 215, 0), 2: (200, 145, 255), 3: (96, 222, 247)}.get(self.rarity)
        self.stats_surface = self.update_stats()

    def roll(self):
        # Randomly change the stats of the weapon
        for attr in ['damage', 'critRate', 'critDamage', 'DOTDam']:
            setattr(self, attr, round(getattr(self, attr) * random.uniform(0.75, 1.25), 2))
        self.stats_surface = self.update_stats()

    def info(self):
        # Returns the stats of the weapon
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
        # Create a surface with the stats of the weapon which can be rendered
        text_color = (255, 255, 255)  # White
        background_color = (0, 0, 255)  # Blue
        total_height = 0
        width = 0
        # Calculate the size of the surface such that it can fit all the strings
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
        # Render the strings on the surface
        for string, font_size in self.info():
            font = pygame.font.SysFont("Arial", font_size)
            text_surface = font.render(string, True, text_color)
            text_rect = text_surface.get_rect(x=text_x, y=y_offset)
            surface.blit(text_surface, text_rect)
            y_offset += font.get_linesize()
        return surface


class Button:
    def __init__(self, x, y, w, h, data, callback, toggle, background=None, info=None):
        self.x = x  # X position
        self.y = y  # Y position
        self.w = w  # Width
        self.h = h  # Height
        self.data = data  # Data to be displayed or used by the button
        self.callback = callback  # Function called when the button is pressed
        self.toggle = toggle  # Function called when the button is toggled
        self.info = info  # Additional information associated with the button
        self.font = pygame.font.SysFont("Arial", round(h * 0.75))  # Font for the button text
        self.toggled = False
        self.selected = False
        button_rect = pygame.Rect(self.x, self.y, self.w, self.h)  # Rectangle defining the button's area

        # If data is a pygame.Surface, use it directly; otherwise, render the text on a new surface.
        if isinstance(data, pygame.Surface):
            self.surface = pygame.Surface(data.get_size())
            if background is not None:
                self.surface.fill(background)  # Fill the background if specified
            self.surface.blit(data, (0, 0))  # Blit the data surface onto the button's surface
            self.surface = pygame.transform.scale(self.surface, (self.w, self.h))  # Scale the surface to button size
            self.rect = self.surface.get_rect(center=button_rect.center)  # Get the rect for positioning
        else:
            self.surface = pygame.Surface((w, h))
            if background is not None:
                self.surface.fill(background)  # Fill the background if specified
            # Render the text and blit it onto the button's surface
            text_rect = self.font.render(self.data, True, (255, 255, 255))
            self.surface.blit(text_rect, (self.surface.get_width() // 2 - text_rect.get_width() // 2,
                                          self.surface.get_height() // 2 - text_rect.get_height() // 2))
            self.rect = self.surface.get_rect(center=button_rect.center)  # Get the rect for positioning
        # If info is a Weapon, display an additional icon on the button
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
        self.game = game  # Reference to the game object
        self.text = ""  # Current text to display
        self.txtArr = [[game.get_info, float("inf")]]  # Array of texts with their display durations
        self.font = pygame.font.SysFont("Arial", int(self.game.cell_size * 0.75))  # Font for the alert text
        self.text_surface = self.font.render(self.text, True, (255, 0, 0))  # Surface for rendering the text

    def change_text(self):
        # Update the text based on the first item in txtArr
        # If the first item is callable, call it to get the text; otherwise, use it directly
        self.text = self.txtArr[0][0]() + " " if callable(self.txtArr[0][0]) else str(self.txtArr[0][0]) + " "
        self.text_surface = self.font.render(self.text, True, (255, 0, 0))  # Update the text surface with the new text

    def add_text(self, data, time):
        # Add a new text with its display duration to txtArr
        self.txtArr.insert(0, [data, time * 60])  # Convert time from seconds to frames (assuming 60 fps)

    def render(self):
        # Render the current text on the game screen
        # Update txtArr to remove texts whose duration has expired
        self.txtArr = [[text, time - 1] for text, time in self.txtArr if time > 1]
        self.change_text()  # Update the text to the next one if the current has expired
        # Blit the text surface to the game screen, positioned at the top right
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
    SWORDS = 0
    BOWS = 1
    WANDS = 2
