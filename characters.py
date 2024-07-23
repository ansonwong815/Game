from PIL import Image
from utils import *


class EnemyLoader:
    def __init__(self, setting, game):
        self.game = game
        # Load the enemy settings from the provided settings
        self.setting = {}
        for k, v in setting.items():
            v["chances"] = list(v["chances"].values())
            self.setting[k] = v

    def get_enemy(self, type):
        # return a new instance of enemy
        return Enemy(*self.setting[type].values(), self.game)


class SpriteLoader:
    def __init__(self, player, sprite_sheet):
        self.player = player
        self.sprite_sheet = Path(__file__).resolve().parent / sprite_sheet
        self.sprites = self.divide_sprite_sheet()
        self.current_sprite = self.sprites[0][0]
        self.current_sprite_arr = [(0, 0)]
        self.sprite_idx = 0
        self.next_sprite_cooldown = 12
        self.frames_till_next = self.next_sprite_cooldown
        self.loop = True
        self.last_operation = None
        self.animationEnd = None
        self.params = None

    def walk(self, direction):
        # Change the array of indexes to walk and based on the direction
        self.loop = True
        if self.last_operation != (self.walk, direction):
            self.sprite_idx = 0
        if direction == Direction.UP:
            self.current_sprite_arr = [(4, 2), (4, 3)]
        if direction == Direction.DOWN:
            self.current_sprite_arr = [(0, 2), (0, 3)]
        if direction == Direction.LEFT:
            self.current_sprite_arr = [(6, 2), (6, 3)]
        if direction == Direction.RIGHT:
            self.current_sprite_arr = [(2, 2), (2, 3)]
        self.update()
        self.last_operation = (self.walk, direction)

    def idle(self, direction):
        self.loop = True
        if self.last_operation != (self.idle, direction):
            self.sprite_idx = 0
        if direction == Direction.UP:
            self.current_sprite_arr = [(4, 0), (4, 1)]
        if direction == Direction.DOWN:
            self.current_sprite_arr = [(0, 0), (0, 1)]
        if direction == Direction.LEFT:
            self.current_sprite_arr = [(6, 0), (6, 1)]
        if direction == Direction.RIGHT:
            self.current_sprite_arr = [(2, 0), (2, 1)]
        self.update()
        self.last_operation = (self.idle, direction)

    def sword(self, func=None, *params):
        self.params = params
        self.loop = False
        self.animationEnd = func
        self.sprite_idx = 0
        if self.player.facing == Direction.UP:
            self.current_sprite_arr = [(4, 4), (4, 5), (4, 6), (4, 7)]
        if self.player.facing == Direction.DOWN:
            self.current_sprite_arr = [(0, 4), (0, 5), (0, 6), (0, 7)]
        if self.player.facing == Direction.LEFT:
            self.current_sprite_arr = [(6, 4), (6, 5), (6, 6), (6, 7)]
        if self.player.facing == Direction.RIGHT:
            self.current_sprite_arr = [(2, 4), (2, 5), (2, 6), (2, 7)]
        self.update()
        self.last_operation = (self.sword, self.player.facing)

    def bow(self, func=None, *params):
        self.params = params
        self.loop = False
        self.animationEnd = func
        self.sprite_idx = 0
        if self.player.facing == Direction.UP:
            self.current_sprite_arr = [(4, 8), (4, 9), (4, 10), (4, 11)]
        if self.player.facing == Direction.DOWN:
            self.current_sprite_arr = [(0, 8), (0, 9), (0, 10), (0, 11)]
        if self.player.facing == Direction.LEFT:
            self.current_sprite_arr = [(6, 8), (6, 9), (6, 10), (6, 11)]
        if self.player.facing == Direction.RIGHT:
            self.current_sprite_arr = [(2, 8), (2, 9), (2, 10), (2, 11)]
        self.update()
        self.last_operation = (self.sword, self.player.facing)

    def wand(self, func=None, *params):
        self.params = params
        self.loop = False
        self.animationEnd = func
        self.sprite_idx = 0
        if self.player.facing == Direction.UP:
            self.current_sprite_arr = [(4, 13), (4, 14), (4, 15)]
        if self.player.facing == Direction.DOWN:
            self.current_sprite_arr = [(0, 13), (0, 14), (0, 15)]
        if self.player.facing == Direction.LEFT:
            self.current_sprite_arr = [(6, 13), (6, 14), (6, 15)]
        if self.player.facing == Direction.RIGHT:
            self.current_sprite_arr = [(2, 13), (2, 14), (2, 15)]
        self.update()
        self.last_operation = (self.wand, self.player.facing)

    def die(self, func=None, *params):
        self.params = params
        self.loop = False
        self.animationEnd = func
        self.sprite_idx = 0
        if self.player.facing == Direction.UP:
            self.current_sprite_arr = [(4, 20), (4, 21), (4, 22), (4, 23)]
        if self.player.facing == Direction.DOWN:
            self.current_sprite_arr = [(0, 20), (0, 21), (0, 22), (0, 23)]
        if self.player.facing == Direction.LEFT:
            self.current_sprite_arr = [(6, 20), (6, 21), (6, 22), (6, 23)]
        if self.player.facing == Direction.RIGHT:
            self.current_sprite_arr = [(2, 20), (2, 21), (2, 22), (2, 23)]
        self.update()
        self.last_operation = (self.die, self.player.facing)

    def hurt(self, func=None, *params):
        self.params = params
        self.loop = False
        self.animationEnd = func
        self.sprite_idx = 0
        if self.player.facing == Direction.UP:
            self.current_sprite_arr = [(4, 19)]
        if self.player.facing == Direction.DOWN:
            self.current_sprite_arr = [(0, 19)]
        if self.player.facing == Direction.LEFT:
            self.current_sprite_arr = [(6, 19)]
        if self.player.facing == Direction.RIGHT:
            self.current_sprite_arr = [(2, 19)]
        self.update()
        self.last_operation = (self.die, self.player.facing)

    def dead(self):
        self.loop = True
        direction = self.player.facing
        if self.last_operation != (self.idle, direction):
            self.sprite_idx = 0
        if direction == Direction.UP:
            self.current_sprite_arr = [(4, 23)]
        if direction == Direction.DOWN:
            self.current_sprite_arr = [(0, 23)]
        if direction == Direction.LEFT:
            self.current_sprite_arr = [(6, 23)]
        if direction == Direction.RIGHT:
            self.current_sprite_arr = [(2, 23)]
        self.update()
        self.last_operation = (self.dead, direction)

    def next(self):
        # Update the current sprite index based on the cooldown
        if self.frames_till_next == 0:
            self.frames_till_next = self.next_sprite_cooldown
            self.sprite_idx += 1
            if self.loop:
                # Loop the animation if the loop flag is set
                self.sprite_idx %= len(self.current_sprite_arr)
            elif self.sprite_idx >= len(self.current_sprite_arr):
                # Stop the animation if the loop flag is not set and run function if provided
                self.idle(self.player.facing)
                if self.animationEnd:
                    if self.params:
                        self.animationEnd(*self.params)
                    else:
                        self.animationEnd()
        else:
            self.frames_till_next -= 1
        self.update()

    def update(self):
        # Update the current sprite based on the current sprite index
        y, x = self.current_sprite_arr[self.sprite_idx]
        self.current_sprite = self.sprites[y][x]

    def get_sprite(self):
        # Convert the current sprite to a pygame image
        return pygame.image.frombytes(self.current_sprite.tobytes(), self.current_sprite.size, "RGBA")

    def divide_sprite_sheet(self, segment_width=32, segment_height=32):
        # Open the spritesheet image
        spritesheet = Image.open(self.sprite_sheet)
        spritesheet_width, spritesheet_height = spritesheet.size
        # Calculate the number of segments horizontally and vertically
        num_segments_x = spritesheet_width // segment_width
        num_segments_y = spritesheet_height // segment_height
        # Create a 2D list to store the segments
        segments = []
        # Loop over the sprite sheet and extract each segment
        for y in range(num_segments_y):
            row = []
            for x in range(num_segments_x):
                left = x * segment_width
                upper = y * segment_height
                right = left + segment_width
                lower = upper + segment_height
                segment = spritesheet.crop((left, upper, right, lower))
                row.append(segment)
            segments.append(row)
        return segments


class Enemy:
    def __init__(self, name, health, maxHealth, damage, crit_rate, crit_damage, DOTTurns, DOTDam, heal_amount, coins,
                 chances, SpriteSheet, game, size=(32, 32)):
        self.name = name
        self.health = float(health)
        self.maxHealth = float(maxHealth)
        self.damage = float(damage)
        self.critRate = float(crit_rate)
        self.critDamage = float(crit_damage)
        self.DOTTurns = int(DOTTurns)
        self.DOTDam = float(DOTDam)
        self.heal_amount = float(heal_amount)
        self.coins = int(coins)
        self.game = game
        self.facing = Direction.LEFT
        self.SpriteSheet = SpriteLoader(self, SpriteSheet)
        self.SpriteSheet.idle(Direction.LEFT)
        self.game = game
        self.w, self.h = size
        self.affected_dot = []
        self.chances = chances
        self.button = None
        self.HealthBar = None
        self.stats_surface = None
        self.update_stats()
        self.update_health_bar()

    def update_health_bar(self):
        # Create a health bar based on the current health
        self.HealthBar = pygame.Surface((self.w, 4))
        health_rect = pygame.Rect(0, 0, int(self.health * self.w / self.maxHealth), 4)
        pygame.draw.rect(self.HealthBar, (255, 0, 0), health_rect)

    def combat_turn(self, player, combat):
        # Update the turn index
        combat.turnIdx += 1
        combat.turnIdx %= len(combat.turnQueue)
        combat.turn = combat.turnQueue[combat.turnIdx]
        # Apply the damage over time effects
        self.affected_dot = [i for i in self.affected_dot if i[1]]
        for i in self.affected_dot:
            self.health -= i[0]
            combat.add_damage_display(*self.button.rect.center, i[0], True)
            i[1] -= 1
            self.update_health_bar()
        if self.health >= 0:
            # Randomly choose an action based on the chances
            _ = random.random()
            action = next((action for action, chance in zip(['sword', 'bow', 'wand', 'heal', 'buff'], self.chances) if
                           _ < chance), 'buff')
            getattr(self, action)(player, combat)
        else:
            combat.next()

    def sword(self, player, combat):
        self.SpriteSheet.sword(combat.next)
        self.damage_player(player, combat)

    def bow(self, player, combat):
        self.SpriteSheet.bow(combat.next)
        self.damage_player(player, combat)

    def wand(self, player, combat):
        self.SpriteSheet.wand(combat.next)
        self.damage_player(player, combat)

    def heal(self, _, combat):
        target = random.choice(combat.enemies)
        target.health += self.heal_amount
        target.health = max(target.health, target.maxHealth)
        self.SpriteSheet.wand(combat.next)

    def buff(self, _, combat):
        target = random.choice(combat.enemies)
        target.damage *= 1.2
        target.update_stats()
        combat.game.alert.add_text(f"{self.name} buffed {target.name}", 1)
        self.SpriteSheet.wand(combat.next)

    def damage_player(self, player, combat):
        # Deal damage to the player based on the crit rate
        if random.random() < self.critRate:
            player.health -= self.damage * self.critDamage
            combat.add_damage_display(combat.game.offX * combat.game.cell_size + 100,
                                      combat.game.offY * combat.game.cell_size - 16 + (
                                              combat.game.screen.get_height() - combat.game.offY * combat.game.cell_size) // 2,
                                      self.damage * self.critDamage, False)
        else:
            player.health -= self.damage
            combat.add_damage_display(combat.game.offX * combat.game.cell_size + 100,
                                      combat.game.offY * combat.game.cell_size - 16 + (
                                              combat.game.screen.get_height() - combat.game.offY * combat.game.cell_size) // 2,
                                      self.damage, False)
        # Apply the damage over time effect
        player.affected_dot.append([self.damage * self.DOTDam, self.DOTTurns])

    def display_stats(self, button):
        # display weapon stats when mouse hovers over weapon
        surface = button.info.stats_surface
        x, y = pygame.mouse.get_pos()
        self.game.screen.blit(surface, (min(self.game.screen.get_width() - surface.get_width(), x + 10), y))

    def info(self):
        # Returns the stats of the enemy
        res = [(f"{self.name}", 15),
               (f"Dam: {self.damage}", 10), ]
        if self.critRate != 0:
            res.append((f"CritRate: {round(self.critRate * 100, 2)}%", 10))
            res.append((f"CritDam: {round(self.critDamage * 100, 2)}%", 10))
        if self.DOTTurns != 0:
            res.append((f"DOTTurns: {round(self.DOTTurns, 2)}", 10))
            res.append((f"DOTDam: {round(self.DOTDam * 100, 2)}%", 10))
        return res

    def update_stats(self):
        # Create a surface with the stats of the enemy which can be rendered
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
        self.stats_surface = surface


class Player:
    def __init__(self, x, y, setting):
        # Initialize the player with the provided settings
        self.x = x
        self.y = y
        self.facing = Direction.DOWN
        self.actioning = 5
        self.maxHealth = setting['maxHealth']
        self.health = setting['health']
        self.coins = setting['coins']
        self.damage = 1
        self.goto = (None, None)
        self.closest_bat = None
        self.closest_boss = None
        self.closest_mouse = None
        self.sprite = SpriteLoader(self, "Characters/Warrior-Red.png")
        self.healthIcon = pygame.image.load(Path(__file__).resolve().with_name("heart.png")).convert_alpha()
        self.coinIcon = pygame.image.load(Path(__file__).resolve().with_name("coin.png")).convert_alpha()
        self.damIcon = pygame.image.load(Path(__file__).resolve().with_name("attack.png")).convert_alpha()
        self.weaponButton = None
        self.weapon = None
        self.canMove = True
        self.inCombat = False
        self.affected_dot = []
