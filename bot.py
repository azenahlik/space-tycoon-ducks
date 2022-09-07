import random
import traceback
from collections import Counter
from pprint import pprint
from typing import Dict
from typing import Optional
import yaml
from space_tycoon_client import ApiClient
from space_tycoon_client import Configuration
from space_tycoon_client import GameApi
from space_tycoon_client.models.credentials import Credentials
from space_tycoon_client.models.current_tick import CurrentTick
from space_tycoon_client.models.data import Data
from space_tycoon_client.models.destination import Destination
from space_tycoon_client.models.end_turn import EndTurn
from space_tycoon_client.models.move_command import MoveCommand
from space_tycoon_client.models.construct_command import ConstructCommand
from space_tycoon_client.models.player import Player
from space_tycoon_client.models.player_id import PlayerId
from space_tycoon_client.models.ship import Ship
from space_tycoon_client.models.static_data import StaticData
from space_tycoon_client.rest import ApiException
import logging.config
from logic.evasion import get_evasion_commands

CONFIG_FILE = "config.yml"

# Configure log
config = yaml.safe_load(open(CONFIG_FILE))
configuration = Configuration()
if config["logging_config"]:
    logging.config.fileConfig(config["logging_config"])
    logger = logging.getLogger(__name__)
else:
    raise FileNotFoundError("Logging config not found!")


from logic.fighting import get_fighter_fighting_commands, get_ms_fighting_commands, get_repair_commands
from logic.construction import get_fighter_construction_commands
from logic.trading import get_trading_commands
from logic.special import rename_ships, kill_specific_player_fighters


class ConfigException(Exception):
    pass


class Game:
    def __init__(self, api_client: GameApi, config: Dict[str, str]):
        self.me: Optional[Player] = None
        self.config = config
        self.client = api_client
        self.player_id = self.login()
        self.static_data: StaticData = self.client.static_data_get()
        self.data: Data = self.client.data_get()
        self.season = self.data.current_tick.season
        self.tick = self.data.current_tick.tick
        self.init: str = ""
        # this part is custom logic, feel free to edit / delete
        if self.player_id not in self.data.players:
            raise Exception("Logged as non-existent player")
        self.recreate_me()
        logger.info(f"playing as [{self.me.name}] id: {self.player_id}")

    def recreate_me(self):
        self.me: Player = self.data.players[self.player_id]

    def game_loop(self):
        while True:
            logger.info("-" * 30)
            try:
                logger.info(f"tick {self.tick} season {self.season}")
                self.data: Data = self.client.data_get()
                if self.data.player_id is None:
                    raise Exception("I am not correctly logged in. Bailing out")
                self.game_logic()
                current_tick: CurrentTick = self.client.end_turn_post(EndTurn(
                    tick=self.tick,
                    season=self.season
                ))
                self.tick = current_tick.tick
                self.season = current_tick.season
            except ApiException as e:
                if e.status == 403:
                    logger.info(f"New season started or login expired: {e}")
                    break
                else:
                    raise e
            except Exception as e:
                logger.exception(f"!!! EXCEPTION !!! Game logic error {e}", exc_info=True)
                traceback.print_exc()

    def game_logic(self):
        # todo throw all this away
        self.recreate_me()
        my_ships: Dict[Ship] = {ship_id: ship for ship_id, ship in
                                self.data.ships.items() if ship.player == self.player_id}

        ship_type_cnt = Counter(
            (self.static_data.ship_classes[ship.ship_class].name for ship in my_ships.values()))
        pretty_ship_type_cnt = ', '.join(
            f"{k}:{v}" for k, v in ship_type_cnt.most_common())
        logger.info(f"I have {len(my_ships)} ships ({pretty_ship_type_cnt})")

        commands = {}
        for ship_id, ship in my_ships.items():
            pass
            # if ship.command is not None:
            #     continue
            # random_planet_id = random.choice(list(self.data.planets.keys()))
            # print(f"sending {ship_id} to {self.data.planets[random_planet_id].name}({random_planet_id})")
            # commands[ship_id] = MoveCommand(type="move", destination=Destination(target=random_planet_id))

        # Attack Commands
        if self.tick > 30:
            ms_attack_commands = get_ms_fighting_commands(self.data, self.player_id)
            commands.update(ms_attack_commands)
            fighter_attack_commands = get_fighter_fighting_commands(self.data, self.player_id, 300)
            commands.update(fighter_attack_commands)
        fixing_commands = get_repair_commands(self.data, self.player_id)
        commands.update(fixing_commands)

        # Construction Commands
        construction_commands = get_fighter_construction_commands(self.data, self.player_id, 1)
        commands.update(construction_commands)

        # Evasion
        # evasion_commands = get_evasion_commands(self.data, self.player_id)
        # commands.update(evasion_commands)

        # # Trade Commands
        trade_commands = get_trading_commands(self.data, self.player_id)
        # print('TRADE COMMANDS', trade_commands)
        commands.update(trade_commands)

        # Special Commands
        special_commands = rename_ships(self.data, self.player_id)
        commands.update(special_commands)
        # if self.tick > 30:
            # special_kill_commands = kill_specific_player_fighters(self.data, self.player_id, "amazon", 400)
            # commands.update(special_kill_commands)

        logger.info(commands)
        pprint(commands) if commands else None
        try:
            self.client.commands_post(commands)
        except ApiException as e:
            if e.status == 400:
                logger.error("some commands failed")
                logger.error(e.body)

    def login(self) -> str:
        if self.config["user"] == "?":
            raise ConfigException
        if self.config["password"] == "?":
            raise ConfigException
        player, status, headers = self.client.login_post_with_http_info(Credentials(
            username=self.config["user"],
            password=self.config["password"],
        ), _return_http_data_only=False)
        self.client.api_client.cookie = headers['Set-Cookie']
        player: PlayerId = player
        return player.id


def main_loop(api_client, config):
    game_api = GameApi(api_client=api_client)
    while True:
        try:
            game = Game(game_api, config)
            game.game_loop()
            logger.info("season ended")
        except ConfigException as e:
            logger.error(f"User / password was not configured in the config file [{CONFIG_FILE}]")
            return
        except Exception as e:
            logger.error(f"Unexpected error {e}")


def main():
    logger.info('Staring')
    config = yaml.safe_load(open(CONFIG_FILE))
    logger.info(f"Loaded config file {CONFIG_FILE}")
    logger.info(f"Loaded config values {config}")
    configuration = Configuration()
    if config["host"] == "?":
        logger.error(f"Host was not configured in the config file [{CONFIG_FILE}]")
        return

    configuration.host = config["host"]

    main_loop(ApiClient(configuration=configuration, cookie="SESSION_ID=1"), config)


if __name__ == '__main__':
    main()
