#!/usr/bin/env python3

from math import sqrt, pi
from argparse import ArgumentParser, FileType
import json

from pint import UnitRegistry

# tools

notes = {
    "c"  :  0,
    "c#" :  1, "db" :  1,
    "d"  :  2,
    "d#" :  3, "eb" :  3,
    "e"  :  4,
    "f"  :  5,
    "f#" :  6, "gb" :  6,
    "g"  :  7,
    "g#" :  8, "ab" :  8,
    "a"  :  9,
    "a#" : 10, "bb" : 10,
    "b"  : 11
}

def note_to_freq(note="a", octave=4, basefreq=440):
    return basefreq * 2 ** (octave-4 + (notes[note]-9)/12)

def radius_to_linear_mass(radius, volumic_mass):
    return volumic_mass * pi * radius ** 2

def linear_mass_to_radius(linear_mass, volumic_mass):
    return sqrt(linear_mass / (volumic_mass * pi))

# Mersenne's law formulas
# see https://en.wikipedia.org/wiki/Mersenne%27s_laws

def get_freq(length, tension, linear_mass):
    return sqrt(tension / linear_mass) / (2 * length)

def get_tension(linear_mass, length, freq):
    return (2 * freq * length) ** 2 * linear_mass

def get_linear_mass(tension, length, freq):
    return tension / (2 * freq * length) ** 2

def get_length(linear_mass, tension, freq):
    return sqrt(tension / linear_mass) / (2 * freq)

# data processing

param_names = {
    # Main params
    'freq',
    'tension',
    'linear_mass',
    'length',
    # Auxilary params
    'note',
    'octave',
    'basefreq',
    'diameter',
    'radius',
    'volumic_mass'
}

param_units = {
    # auxiliary params
    "basefreq": "Hz",
    "diameter": "m",
    "radius": "m",
    "volumic_mass": "kg/m³",
    # main params
    "freq": "Hz",
    "tension": "N",
    "linear_mass": "kg/m",
    "length": "m"
}

param_output_units = {
    # auxiliary params
    "basefreq": "Hz",
    "diameter": "mm",
    "radius": "mm",
    "volumic_mass": "kg/m³",
    # main params
    "freq": "Hz",
    "tension": "kgf",
    "linear_mass": "g/m",
    "length": "mm"
}

def to_SI(data, ureg):
    for param in param_units:
        if param in data:
            if type(data[param]) == int or type(data[param]) == float:
                continue

            quantity = ureg(data[param])

            if type(quantity) == int or type(quantity) == float:
                # No unit : we assume it's already in SI unit
                data[param] = quantity
                continue

            data[param] = quantity.to(param_units[param]).magnitude

def print_data(data, ureg):
    print("Frequency: {:n~P}".format(ureg.Quantity(data["freq"], param_units["freq"]).to(param_output_units["freq"])), end='')
    if "note" in data:
        print(' (Note: {}'.format(data["note"]), end='')
        if "octave" in data:
            print(', octave: {}'.format(data["octave"]), end='')
        if "basefreq" in data:
            print(', base frequency: {:n~P}'.format(ureg.Quantity(data["basefreq"], param_units["basefreq"]).to(param_output_units["basefreq"])), end='')
        print(')', end='')
    print()

    print("Tension: {:n~P}".format(ureg.Quantity(data["tension"], param_units["tension"]).to(param_output_units["tension"])))

    print("Length: {:n~P}".format(ureg.Quantity(data["length"], param_units["length"]).to(param_output_units["length"])))

    print("Linear mass: {:n~P}".format(ureg.Quantity(data["linear_mass"], param_units["linear_mass"]).to(param_output_units["linear_mass"])), end='')
    if "radius" in data:
        print(' (radius: {:n~P}'.format(ureg.Quantity(data["radius"], param_units["radius"]).to(param_output_units["radius"])), end='')
        print(', diameter: {:n~P}'.format(ureg.Quantity(data["diameter"], param_units["diameter"]).to(param_output_units["diameter"])), end='')
        print(', volumic_mass: {:n~P}'.format(ureg.Quantity(data["volumic_mass"], param_units["volumic_mass"]).to(param_output_units["volumic_mass"])), end='')
        print(')', end='')
    print()


def complete_data(data):

    # Handle note to frequency conversion
    if not "freq" in data and "note" in data:
        note_data = {"note" : data["note"]}
        if "octave" in data:
            note_data["octave"] = data["octave"]
        if "basefreq" in data:
            note_data["basefreq"] = data["basefreq"]

        data["freq"] = note_to_freq(**note_data)

    # Handle radius to linear mass conversion

    if "diameter" in data:
        data["radius"] = data["diameter"]/2

    if not "linear_mass" in data and "radius" in data and "volumic_mass" in data:
        data["linear_mass"] = radius_to_linear_mass(data["radius"], data["volumic_mass"])

    # Find missing parameters

    missing = []
    available = {}

    for param in ["freq", "tension", "linear_mass", "length"]:
        if not param in data:
            missing.append(param)
        else:
            available[param] = data[param]

    if len(missing) == 0:
        raise RuntimeWarning("Nothing to compute")
        return

    if len(missing) > 1:
        raise RuntimeError("Not enough data : please leave only one parameter missing among {}".format(missing))

    # Compute the missing parameter

    missing = missing[0]

    if missing == "freq":
        data["freq"] = get_freq(**available)
    elif missing == "tension":
        data["tension"] = get_tension(**available)
    elif missing == "linear_mass":
        data["linear_mass"] = get_linear_mass(**available)
    elif missing == "length":
        data["length"] = get_length(**available)

    # Compute radius if needed

    if not "radius"in data and "volumic_mass" in data:
        data["radius"] = linear_mass_to_radius(data["linear_mass"], data["volumic_mass"])
        data["diameter"] = data["radius"]*2

if __name__ == "__main__":
    parser = ArgumentParser(description="Apply Mersenne's law formulas.")

    # Main params
    parser.add_argument('-f','--freq', nargs=1, help='Frequency (in Hz by default)')
    parser.add_argument('-t','--tension', nargs=1, help='Tension of the string (in N by default)')
    parser.add_argument('-m','--linear_mass', nargs=1, help='Linear mass of the string (in kg/m by default)')
    parser.add_argument('-l','--length', nargs=1, help='Length of the string (in m by default)')

    # Auxilary params
    parser.add_argument('-n','--note', nargs=1, help='Note of the string')
    parser.add_argument('-o','--octave', nargs=1, type=int, help='Octave of the note')
    parser.add_argument('-b','--basefreq', nargs=1, help='Base frequency for 4th octave A (in Hz by default)')
    parser.add_argument('-d','--diameter', nargs=1, help='Diameter of the string (in m by default)')
    parser.add_argument('-r','--radius', nargs=1, help='Radius of the string (in m by default)')
    parser.add_argument('-v','--volumic_mass', nargs=1, help='Volumic mass of the string material (in kg/m³ by default)')

    # Options
    parser.add_argument('-u', '--unit', nargs=1, action='append', metavar='param:unit', help='Select an unit to display a param in default output')
    parser.add_argument('-j', '--json_output', action='store_true', help='Format output data as JSON')
    parser.add_argument('-J', '--json_input', type=FileType('r'), help="Use JSON file as input (use '-' for stdin)")

    args = parser.parse_args()

    if args.json_input:
        data = json.load(args.json_input)
    else: # Get data parameters from program arguments
        dargs = vars(args)
        data = {k:dargs[k][0] for k in dargs if dargs[k] != None and k in param_names}

    ureg = UnitRegistry()

    to_SI(data, ureg)

    complete_data(data)

    if args.json_output:
        print(json.dumps(data, indent=4))
    else:
        if args.unit:
            for param_unit in args.unit:
                param, unit = param_unit[0].split(':')
                param_output_units[param] = unit

        print_data(data, ureg)
