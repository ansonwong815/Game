import numpy as np
from characters import *


class MazeNodeType(enum.Enum):
    WALL = 0
    NORMAL = 1
    DEAD_END = 2
    START = 3
    END = 4


class CaveType(enum.Enum):
    BOSS = 0
    BAT = 1
    SHOP = 2
    HOLE = 3
    ORC = 4
    REWARD = 5
    BLANK = 6


class MazeNode:
    """
    0: wall
    1: normal
    2: dead end
    3: start
    4: end
    """
    colours = [(0, 0, 0), (255, 255, 255), (127, 127, 127), (0, 242, 65), (242, 0, 0), (43, 43, 43)]

    def __init__(self, type):
        self.type = type
        self.visible = False
        self.cave_type = None
        self.enemies = []
        self.reward = 0

    def colour(self):
        # Returns the colour of the node based on its type
        if self.visible:
            return self.colours[self.type.value]
        else:
            return self.colours[0]

    def setup_cave(self, enemyLoader, setting):
        # Configures the node with enemies and rewards based on the cave type and provided settings
        if self.cave_type == CaveType.ORC:
            setting = setting["Orc"]
            self.reward = 20
        elif self.cave_type == CaveType.BOSS:
            setting = setting["Boss"]
            self.reward = 500
        else:
            return
        # Generate enemies with new enemy objects
        for i in range(random.randint(*setting["Orc Leader"])):
            self.enemies.append(enemyLoader.get_enemy("Orc Leader"))
        for i in range(random.randint(*setting["Orc Soldier"])):
            self.enemies.append(enemyLoader.get_enemy("Orc Soldier"))
        for i in range(random.randint(*setting["Orc Mage"])):
            self.enemies.append(enemyLoader.get_enemy("Orc Mage"))
        for i in range(random.randint(*setting["Orc Grunt"])):
            self.enemies.append(enemyLoader.get_enemy("Orc Grunt"))
        for i in range(random.randint(*setting["Orc Villager"])):
            self.enemies.append(enemyLoader.get_enemy("Orc Villager"))


class MazeGen:
    def __init__(self, width, height, start, setting,game):
        self.visited = None
        self.maze = None
        self.caves = None
        self.setting = setting
        self.startX, self.startY = start
        self.height = height
        self.width = width
        self.start = start
        self.end = start
        self.enemyLoader = EnemyLoader(setting["enemies"],game)
        self.generate_maze()

    def generate_maze(self):
        # The maze initially would be a grid of walls with the start node being the only normal node
        self.maze = np.full((self.width, self.height), MazeNode(MazeNodeType.WALL))
        self.visited = np.zeros((self.width, self.height), dtype=bool)
        # dfs function will turn the walls into normal nodes to generate the maze
        self.dfs(self.startX, self.startY, 0)
        self.maze[self.startX][self.startY] = MazeNode(MazeNodeType.START)
        self.assign_cave()

    def assign_cave(self):
        self.caves = []
        # Assigns caves to dead ends based on the settings
        nums = list(self.setting["caves"].values())[1::]
        for i in range(len(nums)):
            # If number is a float, randomly round up or down based on the decimal value
            nums[i] = ((nums[i] - int(nums[i])) > random.random()) + int(nums[i])
        for i in range(self.width):
            for j in range(self.height):
                # If the node is a dead end, assign a cave to it
                if self.maze[i][j].type == MazeNodeType.DEAD_END:
                    self.maze[i][j].cave_type = CaveType.REWARD
                    self.caves.append((i, j))
        # If there are not enough caves, regenerate the maze
        if len(self.caves) < self.setting["caves"]["min"]:
            self.generate_maze()
            return
        # Shuffle the caves and assign them to the nodes
        random.shuffle(self.caves)
        idx = 0
        for i in range(len(nums)):
            for j in range(nums[i]):
                idx += 1
                x, y = self.caves[idx]
                self.maze[x][y].cave_type = CaveType(i)
        # Setup the caves
        for x, y in self.caves:
            self.maze[x][y].setup_cave(self.enemyLoader, self.setting["caves setup"])

    def getMaze(self):
        return self.maze

    def dfs(self, x, y, dis):
        # Randomised depth first search algorithm to generate a maze
        self.visited[x][y] = True
        self.maze[x][y] = MazeNode(MazeNodeType.NORMAL)
        directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]
        random.shuffle(directions)
        count = 0
        for dx, dy in directions:
            nx, ny = x + 2 * dx, y + 2 * dy
            if not (0 <= nx < self.width and 0 <= ny < self.height) or self.visited[nx][ny]:
                continue
            count += 1
            self.maze[x + dx][y + dy] = MazeNode(MazeNodeType.NORMAL)
            # Recursively call the function with the new coordinates
            self.dfs(nx, ny, dis + 2)
        if count == 0:
            self.maze[x][y] = MazeNode(MazeNodeType.DEAD_END)
