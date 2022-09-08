import math
import resource
from logic.utils.ships import HAULER, SHIPPER
from space_tycoon_client.models.data import Data
from space_tycoon_client.models.ship import Ship
from space_tycoon_client.models.planet import Planet
from utils.general import SharedComms, countDistanceShips, count_distance_between_positions, get_ship_speed
from utils.ship_helpers import get_ship_cargo_size
from typing import Dict

# TEST HELPER FUNCTIONS
def test_is_trade_same(tradeA, tradeB):
    all_same = (
        tradeA['resource_id'] == tradeB['resource_id']
        and tradeA['sell_planet_id'] == tradeB['sell_planet_id']
        and tradeA['distance'] == tradeB['distance']
        and tradeA['money'] == tradeB['money']
        and tradeA['ticks'] == tradeB['ticks']
        and tradeA['mpt'] == tradeB['mpt']
    )
    return all_same

def test_calculated_resources(trades_1, trades_2):
    for planet_id, trade in trades_1.items():
        is_best_trade_same = test_is_trade_same(trade['best_trade'], trades_2[planet_id]['best_trade'])
        all_resources_same = True
        for resource_id, resource_trade in trade['resource_trades'].items():
            if not test_is_trade_same(resource_trade, trades_2[planet_id]['resource_trades'][resource_id]):
                all_resources_same = False
        
        if not is_best_trade_same or not all_resources_same:
            print('OLD', trade['best_trade'])
            print('NEW', trades_2[planet_id]['best_trade'])
            raise Exception('COUNT IS NOT SAME')
        else:
            print('ALL SAME!')


def getResourceWithLowestPrice(resources):
    lowestPrice = 99999999999
    resourceIdToBuy = -1
    # resourceToBuy = NULL

    for resourceId, resource in resources.items():
        if resource.buy_price != None and resource.buy_price < lowestPrice and resource.amount >= 10:
            lowestPrice = resource.buy_price
            resourceIdToBuy = resourceId

    return resourceIdToBuy

def count_money_per_tick_from_position_to_planet(resource_id, start_position, planet, speed = 18, amount = 10):
    distance = count_distance_between_positions(start_position, planet.position)
    ticks = math.ceil(distance / speed) + 1
    resource = planet.resources[resource_id]
    resource_price = 0

    if resource.sell_price:
        resource_price = resource.sell_price
    
    money = resource_price * amount

    money_per_ticks = money / ticks

    return (money_per_ticks, ticks, money, distance)

def count_money_per_tick_base(distance, sell_price, speed = 18, amount = 10):
    ticks = math.ceil(distance / speed) + 1
    resource_price = sell_price

    if not resource_price:
        resource_price = 0
    
    money = resource_price * amount

    money_per_ticks = money / ticks

    return (money_per_ticks, ticks, money, distance)

def count_money_per_tick_from_ship_to_planet(ship: Ship, planet: Planet, resource_id_to_sell: str, amount = 10):
    distance = countDistanceShips(ship, planet)
    resource = planet.resources[resource_id_to_sell]
    resource_price = 0

    if resource.sell_price:
        resource_price = resource.sell_price
    
    ship_speed = get_ship_speed(ship)
    mpt_struct = count_money_per_tick_base(distance, resource_price, ship_speed, amount)
    
    return mpt_struct[0]

def select_nearest_trader(traders, planet):
    lowest_distance = 999999999999
    trader_id = list(traders.items())[0][0]

    for t_id, trader in traders.items():
        distance_to_planet = countDistanceShips(trader, planet)
        if distance_to_planet < lowest_distance:
            lowest_distance = distance_to_planet
            trader_id = t_id

    return trader_id

def canBeTradeCommandFullfiled(ship, data):
    target_resource = ship.command.resource
    target_amount = ship.command.amount
    target_target = ship.command.target

    # non trade commands are fullfiled
    if ship.command.type != 'trade':
        return True
    
    command_type = 'buy'

    if target_amount < 0:
        command_type = 'sell'

    planet_resource = data.planets[target_target].resources[target_resource]

    if not planet_resource:
        return False
    

    if command_type == 'buy':
        if planet_resource.amount < target_amount:
            return False
        elif planet_resource.buy_price == None:
            return False
        elif (ship.position[0] == ship.prev_position[0] and ship.position[1] == ship.prev_position[1]):
            return False
    else:
        if planet_resource.sell_price == None:
            return False
        elif (ship.position[0] == ship.prev_position[0] and ship.position[1] == ship.prev_position[1]):
            return False

    return True


def hasPlanetResourcesToSell(planet, amount = 10):
    for id, resource in planet.resources.items():
        if resource.buy_price != None and resource.amount >= amount:
            return True
    return False

def hasPlanetResourcesToSell_v2(planet_to_trade_map, planet_id, amount = 10, is_hauler = False):
    
    trade_key = 'best_trade'

    if is_hauler:
        trade_key = 'hauler_best_trade'

    if planet_to_trade_map[planet_id][trade_key] == None or planet_to_trade_map[planet_id][trade_key]['resource_id'] == None:
        return False

    best_trade_for_planet = planet_to_trade_map[planet_id][trade_key]
    resource_id = best_trade_for_planet['resource_id']

    
    if planet_to_trade_map[planet_id]['resources'][resource_id]['amount'] >= amount:
        return True

    return False

def hasResourceWithAmount(ship):
    for id, resource in ship.resources.items():
        if resource['amount'] > 0:
            return True
    return False

def isPlanetBuyingResource(planet, resourceId):
    for id, resource in planet.resources.items():
        if resource.sell_price != None and id == resourceId:
            return True
    return False

def countDistance(ship, planet):
    return countDistanceShips(ship, planet)


def findTradingOption(ship, data, planetsToExclude):
    planetsWithTradingOptions = {key: planet for key, planet in data.planets.items() if key not in planetsToExclude and hasPlanetResourcesToSell(planet)}

    sortedPlanets = sorted(planetsWithTradingOptions.items(), key=lambda x: countDistance(ship, x[1]))

    # print(sortedPlanets)

    target_planet = sortedPlanets[0]

    return {
        "planet_id": target_planet[0],
        "resource_id": getResourceWithLowestPrice(target_planet[1].resources)
    }

def find_optimal_buy_option(ship, data, planets_to_exclude, trades_by_planet, num_of_nearest_planets_to_compare = -1):
    ship_cargo_size = get_ship_cargo_size(ship)
    is_hauler = ship_cargo_size == 40

    # filter possible planets
    planetsWithTradingOptions = {
        planet_id: planet for planet_id, planet in data.planets.items() if planet_id not in planets_to_exclude and hasPlanetResourcesToSell_v2(
            trades_by_planet,
            planet_id,
            ship_cargo_size,
            is_hauler
        )
    }

    sortedPlanets = sorted(planetsWithTradingOptions.items(), key=lambda x: countDistance(ship, x[1]))

    target_planet = sortedPlanets[0]
    best_mpt = 0

    if num_of_nearest_planets_to_compare == -1:
        num_of_nearest_planets_to_compare = len(sortedPlanets)

    for i in range(num_of_nearest_planets_to_compare):
        current_planet = sortedPlanets[i]
        distance_ship_planet = count_distance_between_positions(ship.position, current_planet[1].position)

        if is_hauler:
            # HAULER
            best_trade = trades_by_planet[current_planet[0]]['hauler_best_trade']
            best_trade_hauler_info = best_trade['hauler']

            current_mpt_planet_to_planet = best_trade_hauler_info['mpt']
            mpt_ship_to_planet_mult = (best_trade['distance'] + distance_ship_planet) / best_trade['distance']
            current_mpt = current_mpt_planet_to_planet / mpt_ship_to_planet_mult
            if current_mpt > best_mpt:
                best_mpt = current_mpt
                target_planet = current_planet

        else: 
            best_trade = trades_by_planet[current_planet[0]]['best_trade']
            current_mpt_planet_to_planet = best_trade['mpt']
            mpt_ship_to_planet_mult = (best_trade['distance'] + distance_ship_planet) / best_trade['distance']
            current_mpt = current_mpt_planet_to_planet / mpt_ship_to_planet_mult
            if current_mpt > best_mpt:
                best_mpt = current_mpt
                target_planet = current_planet
    
    if is_hauler:
        return {
            "planet_id": target_planet[0],
            "resource_id": trades_by_planet[target_planet[0]]['hauler_best_trade']['resource_id']
        }
    return {
        "planet_id": target_planet[0],
        "resource_id": trades_by_planet[target_planet[0]]['best_trade']['resource_id']
    }

def calculate_best_optimal_trade_by_planet(data: Data):
    trades_by_planet = {}
    for planet_id, planet in data.planets.items():
        trade_by_resource = {}
        best_trade = {
            "resource_id": None,
            "mpt": 0,
            "distance": 0,
            "sell_planet_id": None,
            "money": 0,
            "ticks": 0,
        }

        for resource_id, resource in planet.resources.items():
            # print(resource_id, resource)
            if resource.buy_price == None or resource.amount < 10:
                continue
            
            # only buyable
            optimalTrade = find_optimal_sell_option_for_resource(data, resource_id, planet.position)
            trade_by_resource[resource_id] = {
                "mpt": optimalTrade[1],
                "ticks": optimalTrade[2],
                "money": optimalTrade[3],
                "resource_id": resource_id,
                "sell_planet_id":optimalTrade[0][0],
                "distance": optimalTrade[4],
            }

            if trade_by_resource[resource_id]["mpt"] > best_trade["mpt"]:
                best_trade = trade_by_resource[resource_id]
        
        trades_by_planet[planet_id] = {
            "best_trade": best_trade,
            "resource_trades": trade_by_resource
        }
    return trades_by_planet

def calculate_best_optimal_trade_by_planet_v2(data: Data):
    trades_by_planet = {}
    resources = {}

    for planet_id, planet in data.planets.items():
        for resource_id, resource in planet.resources.items():
            if resource.buy_price:
                resources[resource_id] = {
                    "amount": resource.amount
                }


        trade_by_resource = {}
        best_trade = {
            "resource_id": None,
            "mpt": 0,
            "distance": 0,
            "sell_planet_id": None,
            "money": 0,
            "ticks": 0,
            "hauler": None
        }
        hauler_best_trade = None

        for resource_id, resource in planet.resources.items():
            # print(resource_id, resource)
            if resource.buy_price == None or resource.amount < 10:
                continue
            
            # only buyable
            optimalTrade = find_optimal_sell_option_for_resource_from_planet(data, resource_id, planet_id)
            trade_by_resource[resource_id] = {
                "mpt": optimalTrade[1],
                "ticks": optimalTrade[2],
                "money": optimalTrade[3],
                "resource_id": resource_id,
                "sell_planet_id":optimalTrade[0][0],
                "distance": optimalTrade[4],
                # "amount": resource.amount,
                "hauler": optimalTrade[5]
            }

            if trade_by_resource[resource_id]["mpt"] > best_trade["mpt"]:
                best_trade = trade_by_resource[resource_id]
            
            if hauler_best_trade == None  or trade_by_resource[resource_id]["hauler"]["mpt"] > hauler_best_trade["hauler"]["mpt"]:
                hauler_best_trade = trade_by_resource[resource_id]
        
        trades_by_planet[planet_id] = {
            "best_trade": best_trade,
            "hauler_best_trade": hauler_best_trade,
            "resource_trades": trade_by_resource,
            "resources": resources
        }
    return trades_by_planet

def findSellOption(ship, data):
    resourceIdToSell = list(ship.resources.keys())[0]
    planetsWithTradingOptions = {key: planet for key, planet in data.planets.items() if isPlanetBuyingResource(planet, resourceIdToSell)}
    sortedPlanets = sorted(planetsWithTradingOptions.items(), key=lambda x: x[1].resources[resourceIdToSell].sell_price, reverse=True)
    return sortedPlanets[0]

def find_nearest_sell_option(ship, data, radius_for_best_sell):
    resourceIdToSell = list(ship.resources.keys())[0]
    planetsWithTradingOptions = {key: planet for key, planet in data.planets.items() if isPlanetBuyingResource(planet, resourceIdToSell)}
    sorted_planets_by_distance = sorted(planetsWithTradingOptions.items(), key=lambda x: countDistanceShips(ship, x[1]))

    biggest_sell_option = sorted_planets_by_distance[0][1].resources[resourceIdToSell].sell_price
    return_planet = sorted_planets_by_distance[0]

    for planet_tuple in sorted_planets_by_distance:
        current_sell_price = planet_tuple[1].resources[resourceIdToSell].sell_price
        if current_sell_price > biggest_sell_option and countDistanceShips(ship, planet_tuple[1]) <= radius_for_best_sell:
            biggest_sell_option = current_sell_price
            return_planet = planet_tuple

def find_optimal_sell_option(ship, data):
    resourceIdToSell = list(ship.resources.keys())[0]
    ship_cargo_size = get_ship_cargo_size(ship)
    planetsWithTradingOptions = {key: planet for key, planet in data.planets.items() if isPlanetBuyingResource(planet, resourceIdToSell)}
    sorted_planets_by_mpt = sorted(planetsWithTradingOptions.items(), key=lambda x: count_money_per_tick_from_ship_to_planet(ship, x[1], resourceIdToSell, ship_cargo_size), reverse=True)

    return sorted_planets_by_mpt[0]

def find_optimal_sell_option_for_resource(data, resource_id, position, amount = 10, expected_speed = 18):
    planets_whos_buying = {key: planet for key, planet in data.planets.items() if isPlanetBuyingResource(planet, resource_id)}
    
    result_planet = None
    best_mpt = 0
    best_ticks = 0
    best_money = 0
    best_distance = 0

    for planet_id, planet in planets_whos_buying.items():
        current_planet_mpt_info = count_money_per_tick_from_position_to_planet(resource_id, position, planet, amount, expected_speed)
        mpt = current_planet_mpt_info[0]
        ticks = current_planet_mpt_info[1]
        money = current_planet_mpt_info[2]
        distance = current_planet_mpt_info[3]
        if mpt > best_mpt or result_planet == None:
            best_mpt = mpt
            result_planet = (planet_id, planet)
            best_ticks = ticks
            best_money = money
            best_distance = distance

    return (result_planet, best_mpt, best_ticks, best_money, best_distance)

def find_optimal_sell_option_for_resource_from_planet(data, resource_id, planet_id, amount = 10, expected_speed = 18):
    planet_distances = SharedComms().planet_distances
    planets_whos_buying = {key: planet for key, planet in data.planets.items() if isPlanetBuyingResource(planet, resource_id)}
    
    result_planet = None
    best_mpt = 0
    best_ticks = 0
    best_money = 0
    best_distance = 0

    hauler_result_planet_id = None
    hauler_best_mpt = 0
    hauler_best_ticks = 0
    hauler_best_money = 0
    hauler_best_distance = 0

    for current_planet_id, planet in planets_whos_buying.items():
        resource_sell_price = planet.resources[resource_id].sell_price

        if planet_id == current_planet_id or not resource_sell_price:
            continue

        # print('REACHING FOR DISTANCE', planet_id, current_planet_id, planet_distances[planet_id])
        distance = planet_distances[planet_id][current_planet_id]


        current_planet_mpt_info = count_money_per_tick_base(distance, resource_sell_price, amount, expected_speed)

        mpt = current_planet_mpt_info[0]
        ticks = current_planet_mpt_info[1]
        money = current_planet_mpt_info[2]

        if mpt > best_mpt or result_planet == None:
            best_mpt = mpt
            result_planet = (current_planet_id, planet)
            best_ticks = ticks
            best_money = money
            best_distance = distance
        
        # hauler
        # print('HAULER MPT')
        current_planet_mpt_info_hauler = count_money_per_tick_base(distance, resource_sell_price, 40, 13)

        hauler_mpt = current_planet_mpt_info_hauler[0]
        hauler_ticks = current_planet_mpt_info_hauler[1]
        hauler_money = current_planet_mpt_info_hauler[2]
        
        if mpt > best_mpt or result_planet == None:
            hauler_best_mpt = hauler_mpt
            hauler_result_planet_id = current_planet_id
            hauler_best_ticks = hauler_ticks
            hauler_best_money = money
            hauler_best_distance = hauler_money

    return (result_planet, best_mpt, best_ticks, best_money, best_distance, {
        "mpt": hauler_best_mpt,
        "money": hauler_best_money,
        "ticks": hauler_best_ticks,
        "sell_planet_id": hauler_result_planet_id,
        "distance": hauler_best_distance
    })


def get_trading_commands(data: Data, player_id):
    # OLD
    # optimal_trades_by_planet = calculate_best_optimal_trade_by_planet(data)
    
    # NEW
    # MUST BE CALLED ALWAYS FOR NEW
    SharedComms().populate_planets(data)
    optimal_trades_by_planet = calculate_best_optimal_trade_by_planet_v2(data)

    # TEST
    # test_calculated_resources(optimal_trades_by_planet, optimal_trades_by_planet_2)
    
    # ship filtering
    my_traders: Dict[Ship] = {
        ship_id: ship for ship_id, ship in data.ships.items() if ship.player == player_id and ship.ship_class in [HAULER, SHIPPER]
    }

    # print('TRADERS', my_traders)

    traders_without_command = {
        ship_id: ship for ship_id, ship in my_traders.items() if not ship.command or not canBeTradeCommandFullfiled(ship, data)
    }

    # print('TRADERS WITHOUT COMMAND')
    # print(len(traders_without_command.items()))

    traders_without_cargo = {
        ship_id: ship for ship_id, ship in traders_without_command.items() if not hasResourceWithAmount(ship)
    }

    traders_with_cargo = {
        ship_id: ship for ship_id, ship in traders_without_command.items() if hasResourceWithAmount(ship)
    }

    commands = {}
    planetsToExclude = []

    for shipId, ship in traders_without_cargo.items():
        # trade_option = findTradingOption(ship, data, planetsToExclude)

        ship_amount = get_ship_cargo_size(ship)
        # planets_to_choose_from = 1


        trade_option = find_optimal_buy_option(
            ship,
            data,
            planetsToExclude,
            optimal_trades_by_planet,
        )

        planet_id = trade_option['planet_id']
        resource_id = trade_option['resource_id']

        # UPDATE PLANET AMOUNT
        current_planet_amount = optimal_trades_by_planet[planet_id]['resources'][resource_id]['amount']
        new_amount_for_resource = current_planet_amount - ship_amount

        # # UPDATE AMOUNT
        optimal_trades_by_planet[planet_id]['resources'][resource_id]['amount'] = new_amount_for_resource

        # OR EXCLUDE PLANET
        # planetsToExclude.append(trade_option['planet_id'])

        planet_resource_amount = data.planets[planet_id].resources[resource_id].amount

        commands[shipId] = {
            "amount": min(planet_resource_amount, ship_amount),
            "resource": resource_id,
            "target": planet_id,
            "type": 'trade'
        }

    # sell commands
    for shipId, ship in traders_with_cargo.items():
        # print('SELL COMMAND FOR', shipId)
        resourceIdToSell = list(ship.resources.keys())[0]

        ship_amount = min(get_ship_cargo_size(ship), ship.resources[resourceIdToSell]['amount'])
        # DEBUG
        # print('RESOURCE RANGES', resources_ranges[resourceIdToSell])

        # Best sell option
        # target_planet = findSellOption(ship, data)

        # nearet sell option
        # target_planet = find_nearest_sell_option(ship, data, 200)

        # find optimal sell option
        target_planet = find_optimal_sell_option(ship, data)

        # print('SELLING TO', target_planet)
        commands[shipId] = {
            "amount": -ship_amount,
            "resource": resourceIdToSell,
            "target": target_planet[0],
            "type": 'trade'
        }

    return commands
    


# if __name__ == "__main__":
#     print(MOTHERSHIP)