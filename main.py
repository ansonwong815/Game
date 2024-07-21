import math
from mazeGen import *
from characters import *
import random
import sys
import time
from collections import deque
import numpy as np
import pygame
import copy
import json

sys.setrecursionlimit(10000)


class Combat:
    def __init__(self, player, enemies, game, cave):
        self.enemies = enemies
        self.player = player
        if player.weapon.weaponType == WeaponType.SWORD:
            self.turnQueue = enemies + [player]
        else:
            self.turnQueue = [player] + enemies
        self.turnIdx = 0
        self.player.sprite.idle(Direction.RIGHT)
        self.player.facing = Direction.RIGHT
        self.game = game
        self.cave = cave
        self.turn = self.turnQueue[0]
        self.damages = []
        self.setup()
        self.next()

    def next(self):
        if self.player.health <= 0:
            self.player.sprite.die(self.game.game_over, "You Died")
            return
        _buttons = []
        for i in self.game.buttons["Combat"]:
            if not isinstance(i.info, Enemy):
                _buttons.append(i)
                continue
            if i.info.health <= 0:
                self.player.coins += i.info.coins
            else:
                _buttons.append(i)
        self.game.buttons["Combat"] = _buttons
        for i in self.enemies:
            if i.health <= 0:
                self.enemies.remove(i)
                self.turnIdx -= self.turnQueue.index(i) < self.turnIdx
                self.turnQueue.remove(i)
                self.turnIdx %= len(self.turnQueue)
        if not self.enemies:
            if self.cave.cave_type == CaveType.WUMPUS:
                self.game.game_over("You Have Beaten The Game!")
            self.player.coins += self.cave.reward
            self.cave.reward = 0
            self.cave.cave_type = CaveType.BLANK
            self.exit()
        if self.turn != self.player:
            self.turn.combat_turn(self.player, self)
        else:
            for i in self.player.affected_dot:
                if not i[1]:
                    self.player.affected_dot.remove(i)
            for i in self.player.affected_dot:
                self.player.health -= i[0]
                self.add_damage_display(self.game.offX * self.game.cell_size + 100,
                                        self.game.offY * self.game.cell_size - 16 + (
                                                self.game.screen.get_height() - self.game.offY * self.game.cell_size) // 2,
                                        i[0], False)
                i[1] -= 1
            if self.player.health <= 0:
                self.game.game_over("You Died")

    def add_damage_display(self, x, y, amount, crit):
        if not amount:
            return
        font_size = 15
        font = pygame.font.SysFont("Arial", font_size)
        font.set_bold(crit)
        colour = (random.randint(175, 255), random.randint(175, 255), random.randint(175, 255))
        s = font.render(str(round(amount, 2)), True, colour)
        x += random.randint(-20, 20)
        y += random.randint(-20, 20)
        self.damages.append([x, y, s, 252])

    def retreat(self, button):
        if self.turn == self.player:
            self.exit()

    def setup(self):
        self.game.buttons["Combat"] = [
            Button(10, self.game.screen.get_height() - 40, 100, 30, "RETREAT", self.retreat, self.game.toggle_board)]
        self.player.canMove = False
        self.player.inCombat = True
        self.game.need_render_maze = False
        w, h = self.game.screen.get_size()
        for i in range(len(self.enemies)):
            x = w - 5 * self.game.cell_size + ((i + 1) // 2) * self.game.cell_size // 4
            y = self.game.offY + (w - self.game.offY) // 2 + ((-1) ** (i % 2)) * (
                    (i + 1) // 2) * self.game.cell_size * 2
            self.game.buttons["Combat"].append(
                Button(x, y, 32, 32, "", self.player_attack, None, None, self.enemies[i]))
            self.enemies[i].button = self.game.buttons["Combat"][-1]

    def exit(self):
        self.player.affected_dot = []
        self.cave.enemies = self.enemies
        self.game.buttons["Combat"] = []
        self.game.combat = None
        self.player.canMove = True
        self.player.inCombat = False
        self.game.need_render_maze = True

    def render(self):
        self.player.sprite.next()
        player_sprite = pygame.transform.scale2x(self.player.sprite.get_sprite())
        self.game.screen.blit(player_sprite, (self.game.offX * self.game.cell_size + 100,
                                              self.game.offY * self.game.cell_size - 16 + (
                                                      self.game.screen.get_height() - self.game.offY * self.game.cell_size) // 2))
        for i in self.game.buttons["Combat"]:
            if not isinstance(i.info, Enemy):
                continue
            sprite = i.info.SpriteSheet.get_sprite()
            sprite = pygame.transform.scale2x(sprite)
            self.game.screen.blit(sprite, (i.x - 16, i.y - 16))
            w, h = i.rect.center
            x, y = i.info.HealthBar.get_size()
            i.info.update_health_bar()
            self.game.screen.blit(i.info.HealthBar, (w - x // 2, h - i.rect.height))
        for i in self.enemies:
            i.SpriteSheet.next()
        _damages = []
        for i in self.damages:
            scr = i[2].set_alpha(i[3])
            self.game.screen.blit(i[2], (i[0], i[1]))
            i[3] -= 3
            if i[3]:
                _damages.append(i)

    def player_attack(self, button):
        if not self.turn == self.player:
            return
        self.turnIdx += 1
        self.turnIdx %= len(self.turnQueue)
        self.turn = self.turnQueue[self.turnIdx]
        if random.random() < self.player.weapon.critRate:
            button.info.health -= self.player.damage * self.player.weapon.critDamage
            self.add_damage_display(*button.rect.center, self.player.damage * self.player.weapon.critDamage, True)
        else:
            button.info.health -= self.player.damage
            self.add_damage_display(*button.rect.center, self.player.damage, False)
        if button.info.health <= 0:
            button.info.SpriteSheet.die(button.info.SpriteSheet.dead)
        button.info.affected_dot.append([self.player.damage * self.player.weapon.DOTDam, self.player.weapon.DOTTurns])
        button.info.update_health_bar()
        if self.player.weapon.weaponType == WeaponType.SWORD:
            self.player.sprite.sword(self.next)
        if self.player.weapon.weaponType == WeaponType.WANDS:
            self.player.sprite.wand(self.next)
        if self.player.weapon.weaponType == WeaponType.BOWS:
            self.player.sprite.bow(self.next)


class Game:
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(60)
        with open(Path(__file__).resolve().with_name("settings.json"), mode="r", encoding="utf-8") as read_file:
            self.settings = json.load(read_file)
        self.clock = pygame.time.Clock()
        self.width = 25
        self.height = 15
        self.offX = 0
        self.offY = 6
        self.cell_size = 32
        screen_size = ((self.width + self.offX) * self.cell_size, (self.height + self.offY) * self.cell_size)
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption("Game")
        self.font = pygame.font.SysFont("Arial", 50)
        self.buttons = {}
        self.combat = None
        self.need_render_stats = None
        self.need_render_maze = None
        self.maze = None
        self.gen = None
        self.player = None
        self.enemyLoader = None
        self.weaponLoader = None
        self.alert = None
        self.menu()

    def setup(self, button):
        self.buttons["menu"] = []
        setting = self.settings[button.info]
        self.alert = Alert(self)
        self.weaponLoader = WeaponLoader()
        start = (random.randint(0, self.width // 2) * 2, random.randint(0, self.height // 2) * 2)
        self.player = Player(*start, setting["player"])
        self.buttons["inv"] = [
            Button(0, 0, self.cell_size, self.cell_size, self.weaponLoader.weapons[0].icon, self.equip_weapon,
                   self.display_stats, self.weaponLoader.weapons[0].background_colour
                   , copy.copy(self.weaponLoader.weapons[0]))]
        self.buttons["inv"][0].selected = True
        self.player.weaponButton = self.buttons["inv"][0]
        self.player.weapon = self.player.weaponButton.info
        self.player.damage = self.player.weapon.damage
        self.update_inv()
        self.gen = MazeGen(self.width, self.height, start, setting)
        self.maze = self.gen.getMaze()
        self.need_render_maze = True
        self.need_render_stats = True
        self.combat = None
        self.run_game()

    def get_valid_adj(self, x, y):
        pass

    def game_over(self, txt):
        global game
        font = pygame.font.SysFont("Arial", 50)
        self.screen.fill((0, 0, 0))
        txt = font.render(txt, True, (255, 255, 255))
        self.screen.blit(txt, (
            (self.screen.get_width() - txt.get_width()) // 2, (self.screen.get_height() - txt.get_height()) // 2))
        pygame.display.flip()
        time.sleep(2)
        game = Game()

    def heal(self, _):
        if self.player.coins < 10:
            self.alert.add_text("Insufficient Coins", 3)
            return
        self.player.coins -= 10
        self.player.health = min(self.player.health + self.player.maxHealth * 0.3, self.player.maxHealth)

    def equip_weapon(self, button):
        if self.player.weaponButton == button:
            return
        x, y = pygame.mouse.get_pos()
        if x - button.x < 8 and y - button.y < 8:
            self.buttons["inv"].remove(button)
            self.update_inv()
            return
        if self.combat and self.combat.turn != self.player:
            return
        self.player.weaponButton.selected = False
        self.player.weaponButton = button
        self.player.weapon = button.info
        self.player.damage = self.player.weapon.damage
        button.selected = True
        if self.combat:
            self.combat.turnIdx += 1
            self.combat.turnIdx %= len(self.combat.turnQueue)
            self.combat.turn = self.combat.turnQueue[self.combat.turnIdx]
            self.combat.next()

    def exit_cave(self, _):
        self.need_render_maze = True
        self.buttons[self.maze[self.player.x][self.player.y].cave_type] = []
        self.player.canMove = True

    def cover_maze(self):
        self.need_render_maze = False
        rect = pygame.Rect(self.offX * self.cell_size, self.offY * self.cell_size,
                           self.width * self.cell_size, self.height * self.cell_size)
        pygame.draw.rect(self.screen, (0, 0, 0), rect)

    def display_stats(self, button):
        surface = button.info.stats_surface
        x, y = pygame.mouse.get_pos()
        self.screen.blit(surface, (min(self.screen.get_width() - surface.get_width(), x + 10), y))

    def update_inv(self):
        y = self.cell_size * 2 + 3
        x = self.screen.get_width() - 10 * (self.cell_size + 3)
        for c in range(len(self.buttons["inv"])):
            _x = x + (self.cell_size + 3) * (c % 10)
            _y = y + (c // 10) * (self.cell_size + 3)
            self.buttons["inv"][c].move(_x, _y)

    def add_random_weapon(self):
        if len(self.buttons["inv"]) >= 20:
            self.alert.add_text("Inventory Full", 3)
            return
        weapon = copy.copy(self.weaponLoader.get_random())
        weapon.roll()
        self.buttons["inv"].append(
            Button(0, 0, self.cell_size, self.cell_size, weapon.icon, self.equip_weapon,
                   self.display_stats,
                   weapon.background_colour, weapon))
        self.buttons["inv"].sort(
            key=lambda weapon: (weapon.info.rarity, weapon.info.weaponType.value, -weapon.info.damage))
        self.update_inv()

    def buy_random_weapon(self, _):
        if self.player.coins < 15:
            self.alert.add_text("Insufficient Coins", 3)
            return
        self.player.coins -= 15
        self.add_random_weapon()

    def health_buff(self, _):
        if self.player.coins < 10:
            self.alert.add_text("Insufficient Coins", 3)
            return
        self.player.coins -= 10
        self.player.maxHealth += 50
        self.player.health += 50

    def node_effect(self):
        node = self.maze[self.player.x][self.player.y]
        if node.cave_type == CaveType.WUMPUS:
            self.combat = Combat(self.player, node.enemies, self, node)
        if node.cave_type == CaveType.BAT:
            self.alert.add_text("A bat sent you to a random location", 3)
            self.player.x, self.player.y = self.gen.caves[random.randint(0, len(self.gen.caves) - 1)]
            self.move_player(Direction.NONE)
        if node.cave_type == CaveType.SHOP:
            self.player.canMove = False
            self.buttons[CaveType.SHOP] = []
            self.cover_maze()
            self.buttons[CaveType.SHOP].append(
                Button(450, 200, 330, 30, "Buy Health Buff (10 coins)", self.health_buff, self.toggle_board))
            self.buttons[CaveType.SHOP].append(
                Button(450, 250, 330, 30, "Buy Healing Potion (10 coins)", self.heal, self.toggle_board))
            self.buttons[CaveType.SHOP].append(
                Button(450, 300, 330, 30, "Buy Random Weapon (15 coins)", self.buy_random_weapon, self.toggle_board))
            self.buttons[CaveType.SHOP].append(Button(450, 450, 300, 30, "Exit", self.exit_cave, self.toggle_board))
        if node.cave_type == CaveType.HOLE:
            self.game_over("You fell into a bottomless hole")
        if node.cave_type == CaveType.ORC:
            self.combat = Combat(self.player, node.enemies, self, node)
        if node.cave_type == CaveType.REWARD:
            self.alert.add_text("You Received a Reward", 3)
            self.add_random_weapon()
            self.player.maxHealth += 50
            self.player.health += 50
            node.cave_type = CaveType.BLANK

    def move_player(self, direction, auto=False):
        if not self.player.canMove:
            return
        if not auto:
            self.player.goto = (None, None)
        if direction != Direction.NONE:
            self.player.actioning = 5
            self.player.facing = direction
            self.player.sprite.walk(direction)
        nx = self.player.x + direction.value[0]
        ny = self.player.y + direction.value[1]
        if 0 <= nx < self.gen.width and 0 <= ny < self.gen.height and self.maze[nx][ny].type != MazeNodeType.WALL:
            self.player.x, self.player.y = nx, ny
        else:
            return

        visited = np.zeros((self.width, self.height), dtype=bool)
        q = deque()
        q.append([(self.player.x, self.player.y), 0])
        while len(q):
            [(x, y), c] = q.popleft()
            visited[x][y] = True
            if c > 5:
                continue
            self.maze[x][y].visible = True
            for i in Direction:
                [nx, ny] = np.add([x, y], i.value)
                if 0 <= ny < self.gen.height and 0 <= nx < self.gen.width and self.maze[nx][
                    ny].type != MazeNodeType.WALL and not visited[nx][ny]:
                    q.append([(nx, ny), c + 1])
        self.node_effect()

    def go(self, pos):
        if not self.player.canMove:
            return
        visited = np.zeros((self.width, self.height), dtype=bool)
        if not (0 <= pos[0] < self.gen.width and 0 <= pos[1] < self.gen.height and self.maze[pos[0]][
            pos[1]].type != MazeNodeType.WALL and self.maze[pos[0]][
                    pos[1]].visible and self.need_render_maze):
            return
        if pos == [self.player.x, self.player.y]:
            self.player.goto = (None, None)
            return
        self.player.goto = pos
        q = deque()
        q.append(pos)
        while len(q):
            x, y = q.popleft()
            assert (self.maze[x][y].type != MazeNodeType.WALL)
            visited[x][y] = True
            for i in Direction:
                [nx, ny] = np.add([x, y], i.value)
                if nx == self.player.x and ny == self.player.y:
                    self.move_player(i.opposite(), True)
                    return
                if 0 <= nx < self.gen.width and 0 <= ny < self.gen.height and self.maze[nx][
                    ny].type != MazeNodeType.WALL and self.maze[nx][
                    ny].visible and not visited[nx][ny]:
                    q.append((nx, ny))

    def toggle_board(self, button):
        pygame.draw.rect(self.screen, (255, 255, 255), button.top_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), button.bottom_rect)

    def get_info(self):
        dist_to_wumpas = float('inf')
        dist_to_orc = float('inf')
        dist_to_bat = float('inf')
        for x, y in self.gen.caves:
            if self.maze[x][y].cave_type == CaveType.ORC:
                dist_to_orc = min(dist_to_orc, math.hypot(x - self.player.x, y - self.player.y))
            if self.maze[x][y].cave_type == CaveType.WUMPUS:
                dist_to_wumpas = min(dist_to_wumpas, math.hypot(x - self.player.x, y - self.player.y))
            if self.maze[x][y].cave_type == CaveType.BAT:
                dist_to_bat = min(dist_to_bat, math.hypot(x - self.player.x, y - self.player.y))
        dist_to_bat = ((dist_to_bat - 1) // 5 + 1) * 5
        dist_to_wumpas = ((dist_to_wumpas - 1) // 5 + 1) * 5
        dist_to_orc = ((dist_to_orc - 1) // 5 + 1) * 5
        return ("" if math.isnan(dist_to_orc) else f"Orc ~{int(dist_to_orc)}m. ") + (
            "" if math.isnan(dist_to_bat) else f"Bat ~{int(dist_to_bat)}m. ") + (
            "" if math.isnan(dist_to_wumpas) else f"Boss ~{int(dist_to_wumpas)}m.")

    def manage_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.move_player(Direction.UP)
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.move_player(Direction.DOWN)
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.move_player(Direction.LEFT)
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.move_player(Direction.RIGHT)
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                pos = [x // self.cell_size - self.offX, y // self.cell_size - self.offY]
                self.go(pos)
                for arr in self.buttons.values():
                    for button in arr:
                        if button.x < x < button.x + button.w and button.y < y < button.y + button.h:
                            button.callback(button)
            if event.type == pygame.MOUSEMOTION:
                x, y = pygame.mouse.get_pos()
                for arr in self.buttons.values():
                    for button in arr:
                        button.toggled = button.x < x < button.x + button.w and button.y < y < button.y + button.h

        for arr in self.buttons.values():
            for button in arr:
                if button.toggle and button.toggled:
                    button.toggle(button)

    def render_maze(self):
        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect((x + self.offX) * self.cell_size, (y + self.offY) * self.cell_size,
                                   self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, self.maze[x, y].colour(), rect)
        if self.player.actioning:
            self.player.actioning -= 1
        else:
            self.player.sprite.idle(self.player.facing)
        self.player.sprite.next()
        sprite = self.player.sprite.get_sprite()
        self.screen.blit(sprite,
                         ((self.player.x + self.offX) * self.cell_size, (self.player.y + self.offY) * self.cell_size))

    def render_stats(self):
        stats = [(self.player.coinIcon, self.player.coins),
                 (self.player.healthIcon, f"{round(self.player.health, 2)}/{round(self.player.maxHealth, 2)}"),
                 (self.player.damIcon, round(self.player.damage, 2))]
        for c, (img, val) in enumerate(stats):
            img = pygame.transform.scale(img, (
                self.cell_size * self.offY / len(stats), self.cell_size * self.offY / len(stats)))
            num = self.font.render(str(val), True, (255, 255, 255))
            self.screen.blit(num, (75, c * self.offY * self.cell_size / len(stats)))
            self.screen.blit(img, (0, c * self.offY * self.cell_size / len(stats)))

    def render_buttons(self):
        for arr in self.buttons.values():
            for button in arr:
                self.screen.blit(button.surface, button.rect)
                if button.selected:
                    border_thickness = 3
                    width = button.w + 2 * border_thickness
                    height = button.h + 2 * border_thickness
                    rect = pygame.Rect(button.x - border_thickness, button.y - border_thickness, width, height)
                    pygame.draw.rect(self.screen, (255, 0, 0), rect, border_thickness)

    def menu(self):
        self.buttons["menu"] = [Button(240, 250, 330, 30, "Easy", self.setup, self.toggle_board, None, "easy"),
                                Button(240, 300, 330, 30, "Normal", self.setup, self.toggle_board, None, "normal"),
                                Button(240, 350, 330, 30, "Hard", self.setup, self.toggle_board, None, "hard")
                                ]
        running = True
        while running:
            self.clock.tick(60)
            self.screen.fill((0, 0, 0))
            self.render_buttons()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit(0)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    for arr in self.buttons.values():
                        for button in arr:
                            if button.x < x < button.x + button.w and button.y < y < button.y + button.h:
                                button.callback(button)
                if event.type == pygame.MOUSEMOTION:
                    x, y = pygame.mouse.get_pos()
                    for arr in self.buttons.values():
                        for button in arr:
                            button.toggled = button.x < x < button.x + button.w and button.y < y < button.y + button.h
            for arr in self.buttons.values():
                for button in arr:
                    if button.toggled:
                        button.toggle(button)
            pygame.display.flip()

    def run_game(self):
        self.move_player(Direction.NONE)
        frame = 0
        running = True
        self.alert.add_text(self.get_info, float('inf'))
        while running:
            self.clock.tick(60)
            self.screen.fill((0, 0, 0))
            frame += 1
            self.render_buttons()
            self.alert.render()
            if self.need_render_maze:
                self.render_maze()
            if self.need_render_stats:
                self.render_stats()
            if self.combat:
                self.combat.render()
            self.manage_input()
            if self.player.goto != (None, None):
                self.go(self.player.goto)
            pygame.display.flip()

        pygame.quit()


game = Game()
