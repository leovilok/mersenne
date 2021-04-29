from math import sqrt, pi

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

gravity = 9.80665
# gravity = 9.81

def note_to_freq(note="a", octave=4, basefreq=440):
    return basefreq * 2 ** (octave-4 + (notes[note]-9)/12)

def radius_to_linear_mass(radius, volumic_mass):
    return volumic_mass * pi * radius ** 2

def linear_mass_to_radius(linear_mass, volumic_mass):
    return sqrt(linear_mass / (volumic_mass * pi))

def newton_to_kgf(newton):
    return newton / gravity

def kgf_to_newton(kgf):
    return kgf * gravity

# Mersenne's law formulas
# see https://en.wikipedia.org/wiki/Mersenne%27s_laws

def get_freq(lenght, force, linear_mass):
    return length * sqrt(force / linear_mass) / 2

def get_force(linear_mass, length, freq):
    return (2 * freq / length) ** 2 * linear_mass

def get_linear_mass(force, length, freq):
    return force / (2 * freq / length) ** 2

def get_length(linear_mass, force, freq):
    return 2 * freq / sqrt(force / linear_mass)

# 
# def old2_get_tension(freq, length, diameter, density):
#     mass_lin = (diameter/2/1000)**2 * pi * density
#     return mass_lin * (2 * freq * length/1000)**2 / gravity
# 
# def old_get_tension(freq, length, diameter, density):
#     return (freq * length/1000 * diameter/1000)**2 * pi * density / gravity
# 
# def old_get_diameter(freq, length, density, tension):
#     return 1000 * sqrt(tension * 9.81 / (pi * density)) / (length/1000 * freq)
# 
# def old_get_density(freq, length, diameter, tension):
#     return tension * gravity / ((freq * length/1000 * diameter/1000)**2 * pi) 
