from src.game_constants import RobotType, Direction, Team, TileState
from src.game_state import GameState, GameInfo
from src.player import Player
from src.map import TileInfo, RobotInfo
import random

class BotPlayer(Player):
    """
    Players will write a child class that implements (notably the play_turn method)
    """

    def __init__(self, team: Team):
        self.team = team
        return

    def play_turn(self, game_state: GameState) -> None:

        # get info
        ginfo = game_state.get_info()

        # get turn/team info
        height, width = len(ginfo.map), len(ginfo.map[0])

        # print info about the game
        print(f"Turn {ginfo.turn}, team {ginfo.team}")
        print("Map height", height)
        print("Map width", width)

        # find un-occupied ally tile
        ally_tiles = []
        for row in range(height):
            for col in range(width):
                # get the tile at (row, col)
                tile = ginfo.map[row][col]
                # skip fogged tiles
                if tile is not None: # ignore fogged tiles
                    if tile.robot is None: # ignore occupied tiles
                        if tile.terraform > 0: # ensure tile is ally-terraformed
                            ally_tiles += [tile]

        print("Ally tiles", ally_tiles)

        # spawn on a random tile
        print(f"My metal {game_state.get_metal()}")
        robots = game_state.get_ally_robots()

        num_explorers = 0
        num_terraformers = 0
        num_miners = 0

        for robot in robots.values():
            if robot.type == RobotType.EXPLORER:
                num_explorers += 1
            elif robot.type == RobotType.TERRAFORMER:
                num_terraformers += 1
            elif robot.type == RobotType.MINER:
                num_miners += 1

        total_robots = num_explorers + num_terraformers + num_miners

        if total_robots == 0:
            spawn_types = [RobotType.EXPLORER]
        else:
            if game_state.get_metal() == 200:
                spawn_types = [RobotType.EXPLORER, RobotType.TERRAFORMER]
            elif num_explorers / total_robots < 0.35:
                spawn_types = [RobotType.EXPLORER]
            elif num_terraformers / total_robots < 0.55:
                spawn_types = [RobotType.TERRAFORMER]
            elif num_miners / total_robots < 0.10:
                spawn_types = [RobotType.MINER]
            else:
                spawn_types = []

        spawned_robots = []
        # find un-occupied ally tile
        for spawn_type in spawn_types:
            spawned_occupied_tiles = []
            at = ally_tiles
            for x in spawned_occupied_tiles:
                at.remove(x)
            if len(at) > 0:
                # pick a random one to spawn on
                spawn_loc = random.choice(at)
                # spawn the robot
                if game_state.can_spawn_robot(spawn_type, spawn_loc.row, spawn_loc.col):
                    spawned_robots += [game_state.spawn_robot(spawn_type, spawn_loc.row, spawn_loc.col)]
                spawned_occupied_tiles += [spawn_loc]

        # move robots
        robots = game_state.get_ally_robots()

        # iterate through dictionary of robots
        for rname, rob in robots.items():
            print(f"Robot {rname} at {rob.row, rob.col}")

            # randomly move if possible
            all_dirs = [dir for dir in Direction]
            random.shuffle(all_dirs)
            # move_dir = random.choice(all_dirs)
            for move_dir in all_dirs:
                # check if we can move in this direction
                if game_state.can_move_robot(rname, move_dir):
                    # try to not collide into robots from our team
                    dest_loc = (rob.row + move_dir.value[0], rob.col + move_dir.value[1])
                    dest_tile = game_state.get_map()[dest_loc[0]][dest_loc[1]]
                    if dest_tile.robot is None or dest_tile.robot.team != self.team:
                        game_state.move_robot(rname, move_dir)
                        print(dest_tile)
                        break

            # action if possible
            if game_state.can_robot_action(rname):
                game_state.robot_action(rname)

        

