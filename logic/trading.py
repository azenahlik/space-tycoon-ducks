import math
from logic.utils.ships import HAULER, SHIPPER
from space_tycoon_client.models.data import Data
from space_tycoon_client.models.ship import Ship
from space_tycoon_client.models.planet import Planet
from utils.general import countDistanceShips, get_ship_speed
from typing import Dict
from random import randint

def getResourceWithLowestPrice(resources):
    lowestPrice = 99999999999
    resourceIdToBuy = -1
    # resourceToBuy = NULL

    for resourceId, resource in resources.items():
        if resource.buy_price != None and resource.buy_price < lowestPrice and resource.amount >= 10:
            lowestPrice = resource.buy_price
            resourceIdToBuy = resourceId

    return resourceIdToBuy


def count_money_per_tick(ship: Ship, planet: Planet, resource_id_to_sell: str, amount = 10):
    distance = countDistanceShips(ship, planet)
    ship_speed = get_ship_speed(ship)
    ticks = math.ceil(distance / ship_speed) + 1
    resource = planet.resources[resource_id_to_sell]
    resource_price = 0

    if resource.sell_price:
        resource_price = resource.sell_price
    
    money_per_ticks = (resource_price * amount) / ticks

    return money_per_ticks

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
    command_type = 'buy'

    if target_amount < 0:
        command_type = 'sell'

    planet_resource = data.planets[target_target].resources[target_resource]

    if not planet_resource:
        return False
    

    if command_type == 'buy':
        print('BUY CHECK', planet_resource.amount < target_amount, planet_resource.buy_price == None, ship.position[0] == ship.prev_position[0] and ship.position[1] == ship.prev_position[1])
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


def hasPlanetResourcesToSell(planet):
    for id, resource in planet.resources.items():
        if resource.buy_price != None and resource.amount >= 10:
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

def isPlanetInRadius(ship, planet, radius):
    pass

def countDistance(ship, planet):
    return countDistanceShips(ship, planet)



def findTradingOption(ship, data, planetsToExclude):
    planetsWithTradingOptions = {key: planet for key, planet in data.planets.items() if key not in planetsToExclude and hasPlanetResourcesToSell(planet)}

    sortedPlanets = sorted(planetsWithTradingOptions.items(), key=lambda x: countDistance(ship, x[1]))

    print(sortedPlanets)

    target_planet = sortedPlanets[0]

    return {
        "planet_id": target_planet[0],
        "resource_id": getResourceWithLowestPrice(target_planet[1].resources)
    }

def find_optimal_buy_option(ship, data, planetsToExclude):
    planetsWithTradingOptions = {key: planet for key, planet in data.planets.items() if key not in planetsToExclude and hasPlanetResourcesToSell(planet)}

    # sortedPlanets = sorted(planetsWithTradingOptions.items(), key=lambda x: countDistance(ship, x[1]))

    # for planet_touple in planetsWithTradingOptions:


    # print(sortedPlanets)

    target_planet = sortedPlanets[0]

    return {
        "planet_id": target_planet[0],
        "resource_id": getResourceWithLowestPrice(target_planet[1].resources)
    }


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
    planetsWithTradingOptions = {key: planet for key, planet in data.planets.items() if isPlanetBuyingResource(planet, resourceIdToSell)}
    sorted_planets_by_mpt = sorted(planetsWithTradingOptions.items(), key=lambda x: count_money_per_tick(ship, x[1], resourceIdToSell), reverse=True)

    return sorted_planets_by_mpt[0]

def orderRanges(ranges):
    return sorted(ranges.items(), key=lambda x: x[1]['diff'], reverse=True)

def distanceSqr(A, B):
    x = (A[0] - B[0])
    y = (A[1] - B[1])
    return x * x + y * y + 1

def getResourcesRanges(planets, position):
    # planets = planetsInrange(planets, position, 300)
    resources = ["1","10","11","12","13","14","15","16","17","18","19","2","20","21","22","23","3","4","5","6","7","8","9"]
    ranges = {}

    # prepare dict
    for i in resources:
        ranges[i] = {
            'from': None,
            'to': None,
            'sell': 0,
            'buy': 99999999,
            'diff': 0,
            'resource': i
        }

    # find ranges
    # print(planets)
    for i in planets.keys():
        for j in planets[i].resources:
            if (planets[i].resources[j].amount > 10):
                d = distanceSqr(position, planets[i].position)
                d = d * d
                if (planets[i].resources[j].buy_price != None and ranges[j]['buy'] > planets[i].resources[j].buy_price / d):
                    ranges[j]['buy'] = planets[i].resources[j].buy_price
                    ranges[j]['from'] = i
                if (planets[i].resources[j].sell_price != None and ranges[j]['sell'] < planets[i].resources[j].sell_price / d):
                    ranges[j]['sell'] = planets[i].resources[j].sell_price
                    ranges[j]['to'] = i

    # compute diff
    for i in ranges:
        ranges[i]['diff'] = ranges[i]['sell'] - ranges[i]['buy']

    return ranges

def planetsInrange(planets, position, maxDistance):
    return {i: planets[i] for i in planets if distanceSqr(planets[i].position, position) < maxDistance * maxDistance}

def get_trading_commands(data: Data, player_id):
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

    traders_without_cargo_keys = list(traders_without_cargo.keys())

    commands = {}
    planetsToExclude = []
    resources_to_exclude = []
    traders_with_new_command = []


    # print('TRADERS WITH CARGO', traders_with_cargo)
    # print('TRADERS WITH CARGO', traders_without_cargo)

    # buy_command_index = 0

    # buy commands
    # for index in range(len(traders_without_cargo_keys)):
    #     # print('BUY COMMAND', index)
    #     # Resoure buying options
    #     resources_ranges = getResourcesRanges(data.planets, data.ships[traders_without_cargo_keys[index]].position)
    #     sorted_ranges = orderRanges(resources_ranges)

    #     # planet_trade = sorted_ranges[index]
    #     print('FROM', planet_trade)
    #     # planet_trade[1]
    #     planet = data.planets[planet_trade[1]['from']]

    #     the_chosen_one_id = select_nearest_trader({
    #         ship_id: ship for ship_id, ship in traders_without_cargo.items() if ship_id not in traders_with_new_command
    #     }, planet)

    #     traders_with_new_command.append(the_chosen_one_id)

    #     commands[the_chosen_one_id] = {
    #         "amount": 10,
    #         "resource": planet_trade[1]['resource'],
    #         "target": planet_trade[1]['from'],
    #         "type": 'trade'
    #     }

    for shipId, ship in traders_without_cargo.items():
        trade_option = findTradingOption(ship, data, planetsToExclude)

        planetsToExclude.append(trade_option['planet_id'])
        commands[shipId] = {
            "amount": 10,
            "resource": trade_option['resource_id'],
            "target": trade_option['planet_id'],
            "type": 'trade'
        }

    # sell commands
    for shipId, ship in traders_with_cargo.items():
        # print('SELL COMMAND FOR', shipId)
        resourceIdToSell = list(ship.resources.keys())[0]
        # resources map
        # resources_ranges = getResourcesRanges(data.planets, ship.position)

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
            "amount": -10,
            "resource": resourceIdToSell,
            "target": target_planet[0],
            "type": 'trade'
        }

    return commands
    


# if __name__ == "__main__":
#     print(MOTHERSHIP)