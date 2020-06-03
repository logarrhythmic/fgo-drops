#!/usr/bin/env python3

"""
Figure out most efficient places for farming materials in FGO.

Use drop data from Gamepress. Calculate APD values ourselves for higher precision.
Node efficiency takes into account all materials, but not EXP, pieces/monuments, QP or gems.
NOTE: gem consideration may change.

Best node for material X is determined to be not its best single APD node,
but the highest total AP efficient node that drops that material.
"""

import json
from typing import Dict, Tuple, List

# type variables
DropTable = Dict[str, float]
APCost = int
QuestInfo = Tuple[APCost, DropTable]
SectionInfo = Dict[str, QuestInfo]

# you can add items to ignore here if you want
BLACKLIST = []
# or here to ignore everything except these
WHITELIST = ["Phoenix Feather", "Seed of Yggdrasil", "Claw of Chaos"]

# we don't want to consider these because of the high APD bias
CLASSES = ("Saber", "Caster", "Lancer", "Archer", "Assassin", "Rider", "Berserker")
PREFIX_DROPS = ("Blaze of Wisdom - Gold", "Gem of", "Magic Gem of", "Secret Gem of")
POSTFIX_DROPS = ("Piece", "Monument")
BLACKLIST += [t + " " + c for t in PREFIX_DROPS for c in CLASSES]
BLACKLIST += [c + " " + t for t in POSTFIX_DROPS for c in CLASSES ]

with open("drops.json", "r") as fo:
    drop_data: Dict[str, SectionInfo] = json.load(fo)

best_APD: Dict[str, Tuple[float, str]] = {}  # item name -> (APD, node name)
locations: Dict[str, Dict[str, float]] = {}  # item name -> (node name -> APD)

for sname, sdata in drop_data.items():
    for (name, (ap, drops)) in sdata.items():
        node_name = sname + " -- " + name
        for iname, rate in drops.items():
            if WHITELIST:
                if iname not in WHITELIST:
                    continue
            elif iname in BLACKLIST:
                continue
            apd = ap / rate
            if iname not in best_APD or best_APD[iname][0] > apd:
                best_APD[iname] = (apd, node_name)
            if iname not in locations:
                locations[iname] = {}
            locations[iname][node_name] = apd

# write these out I guess
with open("apd.json", "w") as fo:
    json.dump(best_APD, fo)
with open("locations.json", "w") as fo:
    json.dump(locations, fo)

efficiency: Dict[str, float] = {}

for sname, sdata in drop_data.items():
    for (name, (ap, drops)) in sdata.items():
        node_name = sname + " -- " + name
        # this wasn't always this ugly...
        total_ap_value = sum(
            best_APD[iname][0] * rate
            for iname, rate in drops.items()
            if (iname in WHITELIST if WHITELIST else iname not in BLACKLIST)
        )
        eff = total_ap_value / ap
        efficiency[node_name] = eff

with open("efficiency.json", "w") as fo:
    json.dump(efficiency, fo)

# location name, efficiency rating, specific item APD
LocationEfficiency = Tuple[str, float, float]

best_spot_by_item: Dict[str, LocationEfficiency] = {}
locations_efficiency: Dict[str, List[LocationEfficiency]] = {}

for iname, locs in locations.items():
    effs = [(l, efficiency[l], apd) for l, apd in locs.items()]
    effs.sort(key=lambda x: x[1], reverse=True)

    # best = max(locs, key=lambda l: efficiency[l])
    # best_spot_by_item[iname] = (best, efficiency[best])
    best_spot_by_item[iname] = effs[0]
    locations_efficiency[iname] = effs

with open("best_locations.json", "w") as fo:
    json.dump(best_spot_by_item, fo)

with open("locations_efficiency.json", "w") as fo:
    #    locations_efficiency = {i: list((sorted((n,e) for n,e in efficiency.items() if n in ls))) for i, ls in locations.items()}
    json.dump(locations_efficiency, fo)

# print(best_spot_by_item['Phoenix Feather'])