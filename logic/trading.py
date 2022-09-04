from asyncio.windows_events import NULL
from math import sqrt
import resource
from logic.utils.ships import MOTHERSHIP, HAULER, SHIPPER


def getResourceWithLowestPrice(resources):
    lowestPrice = 99999999999
    resourceIdToBuy = -1
    # resourceToBuy = NULL

    for resourceId, resource in resources:
        if 'buyPrice' in resource and resource.buyPrice > lowestPrice and resource.amount >= 10:
            lowestPrice = resource.buyPrice
            resourceIdToBuy = resourceId
            # re

    return resourceIdToBuy


def hasPlanetResourcesToSell(planet):
    for id, resource in planet.resources:
        if 'buyPrice' in resource and resource.amount >= 10:
            return True
    return False

def isPlanetBuyingResource(planet, resourceId):
    for id, resource in planet.resources:
        if 'sellPrice' in resource and id == resourceId:
            return True
    return False

def isPlanetInRadius(ship, planet, radius):
    pass

def countDistance(ship, planet):
    return sqrt(
        (ship.position[0] - planet.position[0])**2
        (ship.position[1] - planet.position[1])**2
    )

def findTradingOption(ship, data):
    planetsWithTradingOptions = {key: planet for key, planet in data.planets.items() if hasPlanetResourcesToSell(planet)}



    sortedPlanets = sorted(planetsWithTradingOptions.items(), key=lambda x: countDistance(ship, x[1]))

    return sortedPlanets[0]

    # if ship == SHIPPER:

    #     planetsWithinRadius = {key: planet for key, planet in data.planets.items() if isPlanetInRadius(ship, planet, 250)}


    #     for planetId, planet in planetsWithinRadius:

    #         for resourceId, resource in planet.resources:
    #             if 'buyPrice' in resource

    #         bestResoure = [[key, resource] planet.resources
    #         pass

def findSellOption(ship, data):
    planetsWithTradingOptions = {key: planet for key, planet in data.planets.items() if isPlanetBuyingResource(planet)}




def getTrandingOptions(data):

    commands = []

    for shipId, ship in data.ships:
        if ship.shipClass in [HAULER, SHIPPER] and 'command' not in ship:

            if ship.resources.amount > 0:
                targetPlanet = findSellOption(ship, data)
                commands.append({
                    amount: -10,
                    resource: resourceToBuy,
                    target: targetPlanet[0],
                    type: 'trade'
                })
            else:
                targetPlanet = findTradingOption(ship, data)
                
                resourceToBuy = getResourceWithLowestPrice(targetPlanet.resources)

                commands.append({
                    amount: 10,
                    resource: resourceToBuy,
                    target: targetPlanet[0],
                    type: 'trade'
                })

    return commands
    


if __name__ == "__main__":
    print(MOTHERSHIP)