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
        # Initialize combat with player, enemies, game context, and the specific cave
        self.enemies = enemies
        self.player = player
        # Determine the turn order based on player's weapon type
        if player.weapon.weaponType == WeaponType.SWORDS:
            self.turnQueue = enemies + [player]
        else:
            self.turnQueue = [player] + enemies
        self.turnIdx = 0
        # Set player sprite to idle and facing direction to right
        self.player.sprite.idle(Direction.RIGHT)
        self.player.facing = Direction.RIGHT
        self.game = game
        self.cave = cave
        self.turn = self.turnQueue[0]
        self.damages = []
        self.setup()
        self.next()

    def next(self):
        # Logic to advance to the next turn in combat
        # Check if the player has died
        if self.player.health <= 0:
            self.player.sprite.die(self.game.game_over, "You Died")
            return
        # Check if any enemy has been defeated
        self.game.buttons["Combat"] = [i for i in self.game.buttons["Combat"] if
                                       not isinstance(i.info, Enemy) or i.info.health > 0]
        for i in self.enemies:
            if i.health <= 0:
                self.player.coins += i.coins
                self.turnIdx -= self.turnQueue.index(i) < self.turnIdx
        self.enemies = [i for i in self.enemies if i.health > 0]
        self.turnQueue = [i for i in self.turnQueue if i.health > 0]
        self.turnIdx %= len(self.turnQueue)
        # Check if all enemies have been defeated
        if not self.enemies:
            if self.cave.cave_type == CaveType.BOSS:
                self.game.game_over("You Have Beaten The Game!")
            self.player.coins += self.cave.reward
            self.cave.reward = 0
            self.cave.cave_type = CaveType.BLANK
            self.exit()
        # Advance to the next turn
        if self.turn != self.player:
            self.turn.combat_turn(self.player, self)
        else:
            # Player's turn and update the player's health based on damage over time effects
            self.player.affected_dot = [i for i in self.player.affected_dot if i[1]]
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
        # Add a damage display to the damage list for rendering
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
        # Retreat from combat and exit the combat screen
        if self.turn == self.player:
            self.exit()

    def setup(self):
        # Set up the combat screen with buttons for player actions
        self.game.alert.add_text("Press enemy to attack!", 5)
        self.game.buttons["Combat"] = [
            Button(10, self.game.screen.get_height() - 40, 100, 30, "RETREAT", self.retreat, self.game.toggle_board)]
        self.player.canMove = False
        self.player.inCombat = True
        self.game.need_render_maze = False
        w, h = self.game.screen.get_size()
        # Add buttons for each enemy in the combat so players can click to attack
        for i in range(len(self.enemies)):
            # Space out the buttons for each enemy
            x = w - 5 * self.game.cell_size + ((i + 1) // 2) * self.game.cell_size // 4
            y = self.game.offY + (w - self.game.offY) // 2 + ((-1) ** (i % 2)) * (
                    (i + 1) // 2) * self.game.cell_size * 2
            self.game.buttons["Combat"].append(
                Button(x, y, 32, 32, "", self.player_attack, self.enemies[i].display_stats, None, self.enemies[i]))
            self.enemies[i].button = self.game.buttons["Combat"][-1]

    def exit(self):
        # Exit combat and return to the maze
        self.player.affected_dot = []
        self.cave.enemies = self.enemies
        self.game.buttons["Combat"] = []
        self.game.combat = None
        self.player.canMove = True
        self.player.inCombat = False
        self.game.need_render_maze = True

    def render(self):
        # Update and draw the player's sprite
        self.player.sprite.next()
        player_sprite = pygame.transform.scale2x(self.player.sprite.get_sprite())
        self.game.screen.blit(player_sprite, (self.game.offX * self.game.cell_size + 100,
                                              self.game.offY * self.game.cell_size - 16 + (
                                                      self.game.screen.get_height() - self.game.offY * self.game.cell_size) // 2))
        # Iterate through each enemy and draw their sprites and health bars
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
        # Render damage numbers with a fade effect
        for i in self.damages:
            i[2].set_alpha(i[3])
            self.game.screen.blit(i[2], (i[0], i[1]))
            i[3] -= 3
        self.damages = [i for i in self.damages if i[3] > 0]

    def player_attack(self, button):
        # Check if it's the player's turn; if not, exit the function
        if not self.turn == self.player:
            return
        # Advance the turn index and ensure it wraps correctly around the turn queue
        self.turnIdx += 1
        self.turnIdx %= len(self.turnQueue)
        # Update the current turn to the next entity in the turn queue
        self.turn = self.turnQueue[self.turnIdx]
        # Calculate damage and apply critical hit multiplier if applicable
        if random.random() < self.player.weapon.critRate:
            damage_dealt = self.player.damage * self.player.weapon.critDamage
            self.add_damage_display(*button.rect.center, damage_dealt, True)
        else:
            damage_dealt = self.player.damage
            self.add_damage_display(*button.rect.center, damage_dealt, False)
        button.info.health -= damage_dealt
        # Check if the enemy's health has dropped to zero or below
        if button.info.health <= 0:
            button.info.SpriteSheet.die(button.info.SpriteSheet.dead)
        # Apply DOT effects if the weapon has any
        button.info.affected_dot.append([self.player.damage * self.player.weapon.DOTDam, self.player.weapon.DOTTurns])
        # Update the enemy's health bar to reflect the new health status
        button.info.update_health_bar()
        # Trigger the player's attack animation based on the weapon type
        if self.player.weapon.weaponType == WeaponType.SWORDS:
            self.player.sprite.sword(self.next)
        if self.player.weapon.weaponType == WeaponType.WANDS:
            self.player.sprite.wand(self.next)
        if self.player.weapon.weaponType == WeaponType.BOWS:
            self.player.sprite.bow(self.next)


class Game:
    def __init__(self):
        pygame.init()  # Initialize all imported pygame modules
        pygame.key.set_repeat(60)  # Set the delay before keys repeat during long presses
        # Load game settings from a JSON file
        with open(Path(__file__).resolve().with_name("settings.json"), mode="r", encoding="utf-8") as read_file:
            self.settings = json.load(read_file)
        self.clock = pygame.time.Clock()  # Clock object for controlling the game's framerate
        # Define the game window's dimensions based on cell size and offsets
        self.width = 25
        self.height = 15
        self.offX = 0
        self.offY = 6
        self.cell_size = 32
        screen_size = ((self.width + self.offX) * self.cell_size, (self.height + self.offY) * self.cell_size)
        self.screen = pygame.display.set_mode(screen_size)  # Initialize the game window
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
        # Clear any existing menu buttons
        self.buttons["menu"] = []
        # Load game settings based on the difficulty selected (button.info)
        setting = self.settings[button.info]
        self.weaponLoader = WeaponLoader()
        # Determine a random starting position for the player within the maze
        start = (random.randint(0, self.width // 2) * 2, random.randint(0, self.height // 2) * 2)
        # Initialize player
        self.player = Player(*start, setting["player"])
        # Set up the inventory button for the player's weapon
        self.buttons["inv"] = [
            Button(0, 0, self.cell_size, self.cell_size, self.weaponLoader.weapons[0].icon, self.equip_weapon,
                   self.display_stats, self.weaponLoader.weapons[0].background_colour,
                   copy.copy(self.weaponLoader.weapons[0]))]
        self.buttons["inv"][0].selected = True
        # Assign the selected weapon to the player
        self.player.weaponButton = self.buttons["inv"][0]
        self.player.weapon = self.player.weaponButton.info
        self.player.damage = self.player.weapon.damage
        self.update_inv()
        # Generate a new maze based on the game settings
        self.gen = MazeGen(self.width, self.height, start, setting, self)
        self.maze = self.gen.getMaze()
        # Initialize an alert system for in-game notifications
        self.alert = Alert(self)
        self.need_render_maze = True
        self.need_render_stats = True
        self.combat = None
        # Start the main game loop
        self.run_game()

    def game_over(self, txt):
        # Game over screen and start new game
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
        # heal player and deduct coins
        if self.player.coins < 10:
            self.alert.add_text("Insufficient Coins", 1)
            return
        self.player.coins -= 10
        self.player.health = min(self.player.health + self.player.maxHealth * 0.3, self.player.maxHealth)

    def equip_weapon(self, button):
        # equip or delete weapon and update inventory
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
        # Player's turn end if weapon is changed
        if self.combat:
            self.combat.turnIdx += 1
            self.combat.turnIdx %= len(self.combat.turnQueue)
            self.combat.turn = self.combat.turnQueue[self.combat.turnIdx]
            self.combat.next()

    def exit_cave(self, _):
        # exit cave
        self.need_render_maze = True
        self.buttons[self.maze[self.player.x][self.player.y].cave_type] = []
        self.player.canMove = True

    def display_stats(self, button):
        # display weapon stats when mouse hovers over weapon
        surface = button.info.stats_surface
        x, y = pygame.mouse.get_pos()
        self.screen.blit(surface, (min(self.screen.get_width() - surface.get_width(), x + 10), y))

    def update_inv(self):
        # update inventory button positions
        y = self.cell_size * 2 + 3
        x = self.screen.get_width() - 10 * (self.cell_size + 3)
        for c in range(len(self.buttons["inv"])):
            _x = x + (self.cell_size + 3) * (c % 10)
            _y = y + (c // 10) * (self.cell_size + 3)
            self.buttons["inv"][c].move(_x, _y)

    def add_random_weapon(self):
        # checks if inventory is full
        if len(self.buttons["inv"]) >= 20:
            self.alert.add_text("Inventory Full", 1)
            return
        # adds a random weapon to the inventory
        weapon = copy.copy(self.weaponLoader.get_random())
        weapon.roll()
        self.buttons["inv"].append(
            Button(0, 0, self.cell_size, self.cell_size, weapon.icon, self.equip_weapon,
                   self.display_stats,
                   weapon.background_colour, weapon))
        # sort inventory based on rarity, weapon type and damage
        self.buttons["inv"].sort(
            key=lambda weapon: (weapon.info.rarity, weapon.info.weaponType.value, -weapon.info.damage))
        self.update_inv()

    def buy_random_weapon(self, _):
        # buy random weapon and deduct coins
        if self.player.coins < 15:
            self.alert.add_text("Insufficient Coins", 1)
            return
        self.player.coins -= 15
        self.add_random_weapon()

    def health_buff(self, _):
        # buy health buff and deduct coins
        if self.player.coins < 10:
            self.alert.add_text("Insufficient Coins", 1)
            return
        self.player.coins -= 10
        self.player.maxHealth += 50
        self.player.health += 50

    def node_effect(self):
        # Retrieve the current node the player is on
        node = self.maze[self.player.x][self.player.y]
        # Check the type of the cave and execute corresponding actions
        if node.cave_type == CaveType.BOSS:
            # If the cave is of type BOSS, initiate combat with the enemies in the cave
            self.combat = Combat(self.player, node.enemies, self, node)
        if node.cave_type == CaveType.BAT:
            # If the cave is of type BAT, teleport the player to a random location
            self.alert.add_text("A bat sent you to a random location", 1)
            self.player.x, self.player.y = self.gen.caves[random.randint(0, len(self.gen.caves) - 1)]
            self.move_player(Direction.NONE)
        if node.cave_type == CaveType.SHOP:
            # If the cave is of type SHOP, display shop options and disable player movement
            self.player.canMove = False
            self.buttons[CaveType.SHOP] = []
            self.need_render_maze = False
            # Add buttons for shop actions
            self.buttons[CaveType.SHOP].append(
                Button(450, 200, 330, 30, "Buy Health Buff (10 coins)", self.health_buff, self.toggle_board))
            self.buttons[CaveType.SHOP].append(
                Button(450, 250, 330, 30, "Buy Healing Potion (10 coins)", self.heal, self.toggle_board))
            self.buttons[CaveType.SHOP].append(
                Button(450, 300, 330, 30, "Buy Random Weapon (15 coins)", self.buy_random_weapon, self.toggle_board))
            self.buttons[CaveType.SHOP].append(Button(450, 450, 300, 30, "Exit", self.exit_cave, self.toggle_board))
        if node.cave_type == CaveType.HOLE:
            # If the cave is of type HOLE, end the game with a loss message
            self.game_over("You fell into a bottomless hole")
        if node.cave_type == CaveType.ORC:
            # If the cave is of type ORC, initiate combat with the enemies in the cave
            self.combat = Combat(self.player, node.enemies, self, node)
        if node.cave_type == CaveType.REWARD:
            # If the cave is of type REWARD, grant the player a reward and reset the cave type
            self.alert.add_text("You Received a Reward", 1)
            self.add_random_weapon()
            self.player.maxHealth += 50
            self.player.health += 50
            node.cave_type = CaveType.BLANK

    def move_player(self, direction, auto=False):
        # Prevent movement if player movement is disabled
        if not self.player.canMove:
            return
        # Reset player's target position if not moving automatically
        if not auto:
            self.player.goto = (None, None)
        # Update player's facing direction and initiate walking animation if moving
        if direction != Direction.NONE:
            self.player.actioning = 5
            self.player.facing = direction
            self.player.sprite.walk(direction)
        # Calculate new position based on direction
        nx = self.player.x + direction.value[0]
        ny = self.player.y + direction.value[1]
        # Move player if new position is within bounds and not a wall
        if 0 <= nx < self.gen.width and 0 <= ny < self.gen.height and self.maze[nx][ny].type != MazeNodeType.WALL:
            self.player.x, self.player.y = nx, ny
        else:
            return
        # Using bfs to reveal nearby maze nodes within a certain range
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
        # Trigger node effects (e.g., combat, rewards) at the new position
        self.node_effect()

    def go(self, pos):
        # Check if player movement is allowed
        if not self.player.canMove:
            return
        # Validate the target position is within bounds, not a wall, visible, and rendering is needed
        if not (0 <= pos[0] < self.gen.width and 0 <= pos[1] < self.gen.height and self.maze[pos[0]][
            pos[1]].type != MazeNodeType.WALL and self.maze[pos[0]][
                    pos[1]].visible and self.need_render_maze):
            return
        # If the target position is the current player position, reset the goto attribute
        if pos == [self.player.x, self.player.y]:
            self.player.goto = (None, None)
            return
        # Set the target position as the new goto attribute for the player
        self.player.goto = pos
        # Initialize a queue for BFS and visited array to keep track of visited nodes
        q = deque()
        q.append(pos)
        visited = np.zeros((self.width, self.height), dtype=bool)
        # Perform BFS to find the shortest path to the target position
        while len(q):
            x, y = q.popleft()
            assert (self.maze[x][y].type != MazeNodeType.WALL)
            visited[x][y] = True
            for i in Direction:
                [nx, ny] = np.add([x, y], i.value)
                # If the next position is the player's current position, move the player in the opposite direction
                if nx == self.player.x and ny == self.player.y:
                    self.move_player(i.opposite(), True)
                    return
                # If the next position is valid and not visited, add it to the queue
                if 0 <= nx < self.gen.width and 0 <= ny < self.gen.height and self.maze[nx][
                    ny].type != MazeNodeType.WALL and self.maze[nx][
                    ny].visible and not visited[nx][ny]:
                    q.append((nx, ny))

    def toggle_board(self, button):
        # Toggle the boards of buttons
        pygame.draw.rect(self.screen, (255, 255, 255), button.top_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), button.bottom_rect)

    def get_info(self):
        # Get the distance to the nearest enemies
        dist_to_boss = float('inf')
        dist_to_orc = float('inf')
        dist_to_bat = float('inf')
        for x, y in self.gen.caves:
            # Calculate the minimum Euclidean distance to enemies
            if self.maze[x][y].cave_type == CaveType.ORC:
                dist_to_orc = min(dist_to_orc, math.hypot(x - self.player.x, y - self.player.y))
            if self.maze[x][y].cave_type == CaveType.BOSS:
                dist_to_boss = min(dist_to_boss, math.hypot(x - self.player.x, y - self.player.y))
            if self.maze[x][y].cave_type == CaveType.BAT:
                dist_to_bat = min(dist_to_bat, math.hypot(x - self.player.x, y - self.player.y))
        # Round up the distances to a multiple of 5
        dist_to_bat = ((dist_to_bat - 1) // 5 + 1) * 5
        dist_to_boss = ((dist_to_boss - 1) // 5 + 1) * 5
        dist_to_orc = ((dist_to_orc - 1) // 5 + 1) * 5
        # Return the distances to the enemies as a string
        return ("" if math.isnan(dist_to_orc) else f"Orc ~{int(dist_to_orc)}m. ") + (
            "" if math.isnan(dist_to_bat) else f"Bat ~{int(dist_to_bat)}m. ") + (
            "" if math.isnan(dist_to_boss) else f"Boss ~{int(dist_to_boss)}m.")

    def manage_input(self):
        # Process all events from the event queue
        for event in pygame.event.get():
            # Close the game if the quit event is triggered
            if event.type == pygame.QUIT:
                exit(0)
            # Handle keyboard inputs for player movement
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.move_player(Direction.UP)
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.move_player(Direction.DOWN)
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.move_player(Direction.LEFT)
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.move_player(Direction.RIGHT)
            # Handle mouse button clicks for player actions and UI interactions
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                # Calculate the position in the maze grid
                pos = [x // self.cell_size - self.offX, y // self.cell_size - self.offY]
                # Attempt to move the player to the clicked position
                self.go(pos)
                # Check if any UI button is clicked and trigger its callback
                for arr in self.buttons.values():
                    for button in arr:
                        if button.x < x < button.x + button.w and button.y < y < button.y + button.h:
                            button.callback(button)
            # Handle mouse movement for UI button hover effects
            if event.type == pygame.MOUSEMOTION:
                x, y = pygame.mouse.get_pos()
                # Toggle button hover state based on mouse position
                for arr in self.buttons.values():
                    for button in arr:
                        button.toggled = button.x < x < button.x + button.w and button.y < y < button.y + button.h

        # Process button toggle actions outside the event loop
        for arr in self.buttons.values():
            for button in arr:
                if button.toggle and button.toggled:
                    button.toggle(button)

    def render_maze(self):
        # Render the maze grid, colour is stored in the maze node class
        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect((x + self.offX) * self.cell_size, (y + self.offY) * self.cell_size,
                                   self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, self.maze[x, y].colour(), rect)
        # Handle rendering of the player sprite and animation
        if self.player.actioning:
            self.player.actioning -= 1
        else:
            self.player.sprite.idle(self.player.facing)
        self.player.sprite.next()
        sprite = self.player.sprite.get_sprite()
        self.screen.blit(sprite,
                         ((self.player.x + self.offX) * self.cell_size, (self.player.y + self.offY) * self.cell_size))

    def render_stats(self):
        # Render the player's stats
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
                # Render the button on the screen
                self.screen.blit(button.surface, button.rect)
                # Create a board around the button if it is selected (mainly for weapon)
                if button.selected:
                    border_thickness = 3
                    width = button.w + 2 * border_thickness
                    height = button.h + 2 * border_thickness
                    rect = pygame.Rect(button.x - border_thickness, button.y - border_thickness, width, height)
                    pygame.draw.rect(self.screen, (255, 0, 0), rect, border_thickness)

    def menu(self):
        # Initialize the menu screen with difficulty selection buttons
        self.buttons["menu"] = [Button(240, 250, 330, 30, "Easy", self.setup, self.toggle_board, None, "easy"),
                                Button(240, 300, 330, 30, "Normal", self.setup, self.toggle_board, None, "normal"),
                                Button(240, 350, 330, 30, "Hard", self.setup, self.toggle_board, None, "hard")
                                ]
        running = True
        # Manage input of the menu screen loop
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
        # Main game loop
        self.move_player(Direction.NONE)
        frame = 0
        running = True
        while running:
            # Update the game's clock and clear the screen
            self.clock.tick(60)
            self.screen.fill((0, 0, 0))
            frame += 1
            # Render the maze, stats, buttons, and alert system
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
