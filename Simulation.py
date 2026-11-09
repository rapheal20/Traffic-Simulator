timeframe = 1
#1 timeframe represets 1 sec


driverConstants = [
    #Aggressive
        {"GAP_CONSTANT" : 0.10,
         "BASE_GAP" : 2,
         "ACC_CONSTANT" : 0.,
         "BRAKING_CONSTANT": 0.80
         },
    #Calm
        {"GAP_CONSTANT" : 0.15,
         "BASE_GAP" : 3,
         "ACC_CONSTANT" : 0.15,
         "BRAKING_CONSTANT": 0.55
         },
    #Nervous
        {"GAP_CONSTANT" : 0.20,
         "BASE_GAP" : 4,
         "ACC_CONSTANT" : 0.10,
         "BRAKING_CONSTANT": 0.95
         }
]

DEFAULT_LIMITS = {   # km/h, by OSM 'highway' tag
    'motorway': 100, 'trunk': 80, 'primary': 60,
    'secondary': 50, 'tertiary': 40, 'residential': 30,
}