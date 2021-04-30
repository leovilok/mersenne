#!/usr/bin/env python3

from math import sqrt, pi
from argparse import ArgumentParser

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
    return length * sqrt(tension / linear_mass) / 2

def get_tension(linear_mass, length, freq):
    return (2 * freq / length) ** 2 * linear_mass

def get_linear_mass(tension, length, freq):
    return tension / (2 * freq / length) ** 2

def get_length(linear_mass, tension, freq):
    return 2 * freq / sqrt(tension / linear_mass)

# data processing

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

def to_SI(data, ureg):
    for param in param_units:
        if param in data:
            if type(data) == int or type(data) == float:
                continue

            quantity = ureg(data[param])

            if type(data) == int or type(data) == float:
                # No unit : we assume it's already in SI unit
                data[param] = quantity
                continue

            data[param] = quantity.to(param_units[param]).magnitude

def print_data(data, ureg):
    print("Frequency: {} Hz".format(data["freq"]), end='')
    if "note" in data:
        print(' (Note: {}'.format(data["note"]), end='')
        if "octave" in data:
            print(', octave: {}'.format(data["octave"]), end='')
        if "basefreq" in data:
            print(', base frequency: {}'.format(data["basefreq"]), end='')
        print(')', end='')
    print()

    print("Tension: {} N".format(data["tension"]))

    print("Length: {:~P}".format(ureg.Quantity(data["length"], param_units["length"]).to_compact()))

    print("Linear mass: {:~P}".format(ureg.Quantity(data["linear_mass"], param_units["linear_mass"]).to_compact()), end='')
    if "radius" in data:
        print(' (radius: {:~P}'.format(ureg.Quantity(data["radius"], param_units["radius"]).to_compact()), end='')
        print(', diameter: {:~P}'.format(ureg.Quantity(data["diameter"], param_units["diameter"]).to_compact()), end='')
        print(', volumic_mass: {:~P}'.format(ureg.Quantity(data["volumic_mass"], param_units["volumic_mass"]).to_compact()), end='')
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
        data["linear_mass"] = radius_to_linear_mass(data["radius"], data["linear_mass"])

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
        data["diameter"] = data["radius"]/2

if __name__ == "__main__":
    parser = ArgumentParser(description="Apply Mersenne's law formulas.")

    parser.add_argument('-n','--note', nargs=1, help='Note of the string')
    parser.add_argument('-o','--octave', nargs=1, type=int, help='Octave of the note')
    parser.add_argument('-b','--basefreq', nargs=1, help='Base frequency for 4th octave A (in Hz by default)')
    parser.add_argument('-d','--diameter', nargs=1, help='Diameter of the string (in m by default)')
    parser.add_argument('-r','--radius', nargs=1, help='Radius of the string (in m by default)')
    parser.add_argument('-v','--volumic_mass', nargs=1, help='Volumic mass of the string material (in kg/m³ by default)')
    parser.add_argument('-f','--freq', nargs=1, help='Frequency (in Hz by default)')
    parser.add_argument('-t','--tension', nargs=1, help='Tension of the string (in N by default)')
    parser.add_argument('-m','--linear_mass', nargs=1, help='Linear mass of the string (in kg/m by default)')
    parser.add_argument('-l','--length', nargs=1, help='Length of the string (in m by default)')

    ureg = UnitRegistry()

    data = vars(parser.parse_args())

    # Remove empty params
    data = {k:data[k][0] for k in data if data[k] != None}

    to_SI(data, ureg)

    complete_data(data)

    print_data(data, ureg)
