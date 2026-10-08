"""Extensible simulation material taxonomy. Abstract resource IDs are not chemical species."""
from __future__ import annotations

RESOURCE_GROUPS = {
    "metals": ["iron","copper","gold","silver","tin","lead","zinc","nickel","cobalt","chromium","manganese","titanium","tungsten","molybdenum","vanadium","lithium","beryllium","magnesium","aluminum","platinum","palladium","rhodium","iridium","osmium","ruthenium","mercury","antimony","bismuth","cadmium","zirconium","hafnium","niobium","tantalum","rhenium","gallium","germanium","indium","scandium","yttrium","lanthanum","cerium","neodymium","praseodymium","dysprosium","terbium","europium","gadolinium","samarium","erbium","ytterbium","lutetium","thulium","holmium","promethium"],
    "industrial_minerals": ["stone","granite","basalt","limestone","marble","sandstone","slate","shale","clay","kaolin","gypsum","quartz","silica","sand","gravel","salt","halite","potash","phosphate","sulfur","fluorite","barite","borax","graphite","talc","mica","feldspar","asbestos","bentonite","diatomite","perlite","pumice","vermiculite","zeolite","olivine","magnesite","dolomite","calcite","apatite"],
    "gemstones": ["diamond","ruby","sapphire","emerald","amethyst","topaz","opal","turquoise","jade","garnet","aquamarine","spinel","tourmaline","zircon","moonstone","amber","pearl"],
    "fuels": ["coal","lignite","peat","crude_oil","natural_gas","bitumen","oil_shale","uranium","thorium","methane_hydrate"],
    "forest": ["timber","hardwood","softwood","bamboo","cork","resin","latex","bark","wood_fiber","medicinal_herbs","wild_fruit","mushrooms"],
    "food": ["grain","wheat","rice","barley","oats","rye","maize","millet","sorghum","potatoes","cassava","soybeans","beans","lentils","peas","tomatoes","onions","carrots","cabbage","apples","citrus","bananas","olives","grapes","cocoa","coffee","tea","sugarcane","sugar_beet","cotton","flax","hemp","sunflower","rapeseed","peanuts","sesame","fish","shellfish","seaweed","livestock","meat","milk","eggs","honey"],
    "water_ecology": ["freshwater","groundwater","spring_water","river_water","glacier_ice","seawater","geothermal_heat","fertile_soil","topsoil","peatland_biomass"],
    "animals": ["wool","leather","hides","silk","beeswax","feathers","bone","ivory","fish_oil","tallow","manure"],
    "gases": ["oxygen","nitrogen","hydrogen","helium","argon","neon","krypton","xenon","carbon_dioxide"],
    "alloys": ["steel","stainless_steel","cast_iron","bronze","brass","solder","nichrome","duralumin","titanium_alloy","superalloy"],
    "construction": ["cement","concrete","reinforced_concrete","brick","glass","fiberglass","ceramic","porcelain","plaster","asphalt","road_bitumen","insulation","board","plywood","particleboard","paper","cardboard"],
    "chemicals": ["sulfuric_acid","nitric_acid","hydrochloric_acid","ammonia","fertilizer","urea","soda_ash","caustic_soda","chlorine","ethanol","methanol","acetone","propane","butane","ethylene","propylene","benzene","phenol","polyethylene","polypropylene","pvc","polystyrene","nylon","polyester","epoxy","rubber","synthetic_rubber"],
    "manufacturing": ["semiconductor_silicon","silicon_wafer","microchip","battery_cell","lithium_ion_battery","photovoltaic_cell","optical_fiber","copper_wire","aluminum_sheet","steel_beam","electric_motor"],
    "energy": ["electricity","hydrogen_fuel","biofuel","diesel","gasoline","kerosene","coke","charcoal","steam"],
    "consumer": ["textile","fabric","cloth","clothing","bread","flour","cheese","wine","soap","medicine","ink","dye","paint","plastic_packaging"],
}

RAW_GROUPS = ["metals","industrial_minerals","gemstones","fuels","forest","food","water_ecology","animals","gases"]
RENEWABLE_GROUPS = ["forest","food","water_ecology","animals"]

def build_catalog():
    catalog = {}
    for group, names in RESOURCE_GROUPS.items():
        for name in names:
            if name in catalog:
                raise ValueError(f'Duplicate resource ID: {name}')
            is_raw = group in RAW_GROUPS
            renewable = group in RENEWABLE_GROUPS and name not in {'fertile_soil', 'topsoil', 'groundwater', 'glacier_ice', 'peatland_biomass', 'ivory'}
            catalog[name] = {
                'category': group,
                'raw': is_raw,
                'renewable': renewable,
                'strategic': group in {'metals', 'fuels', 'water_ecology'},
                'value': 2 + (3 if group in {'metals', 'fuels'} else 1) + (2 if group == 'gemstones' else 0),
                'unit': 'abstract_unit',
            }
    return catalog

MATERIAL_CATALOG = build_catalog()
RAW_RESOURCES = {k: v for k, v in MATERIAL_CATALOG.items() if v['raw']}
PROCESSED_MATERIALS = {k: v for k, v in MATERIAL_CATALOG.items() if not v['raw']}
