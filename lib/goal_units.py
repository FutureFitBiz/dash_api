
goal_units = [
    'kilojoule',
    'kilowatt-hour',
    'watt-hour',
    'calorie (nutritional)',
    'horsepower (metric) hour',
    'Btu (IT)',
    'Btu (th)',
    'gigajoule',
    'megajoule',
    'millijoule',
    'microjoule',
    'nanojoule',
    'attojoule',
    'megaelectron-volt',
    'kiloelectron-volt',
    'electron-volt',
    'erg',
    'gigawatt-hour',
    'megawatt-hour',
    'kilowatt-second',
    'watt-second',
    'newton meter',
    'horsepower hour',
    'kilocalorie (IT)',
    'kilocalorie (th)',
    'calorie (IT)',
    'calorie (th)',
    'mega Btu (IT)',
    'ton-hour (refrigeration)',
    'fuel oil equivalent @kiloliter',
    'fuel oil equivalent @barrel (US)',
    'gigaton',
    'megaton',
    'kiloton',
    'ton (explosives)',
    'dyne centimeter',
    'gram-force meter',
    'gram-force centimeter',
    'kilogram-force centimeter',
    'kilogram-force meter',
    'kilopond meter',
    'pound-force foot',
    'pound-force inch',
    'ounce-force inch',
    'foot-pound',
    'inch-pound',
    'inch-ounce',
    'poundal foot',
    'therm',
    'therm (EC)',
    'therm (US)',
    'Hartree energy',
    'Rydberg constant'
]

if __name__ == '__main__':
    units = []

    with open('lib/units.txt', "r") as file:
        for line in file.readlines():
            name = line.split('[')[0]
            name = name.split('1')[1]
            name = name.split('=')[0]
            name = name.replace(',', '')
            name = name.strip()
            units.append(name)

        print(units)
