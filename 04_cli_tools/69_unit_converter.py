"""
Script: Unit Converter CLI
What it does: Converts between different units of measurement.
Supports length, weight, temperature, and data sizes.

Run: python 69_unit_converter.py
Run: python 69_unit_converter.py --value 100 --from km --to miles
"""

import argparse

# Conversion factors relative to a base unit
# All conversions go: value → base unit → target unit

LENGTH = {
    "meters":     1.0,
    "km":         1000.0,
    "cm":         0.01,
    "mm":         0.001,
    "miles":      1609.344,
    "yards":      0.9144,
    "feet":       0.3048,
    "inches":     0.0254,
}

WEIGHT = {
    "kg":     1.0,
    "grams":  0.001,
    "pounds": 0.453592,
    "ounces": 0.0283495,
    "tonnes": 1000.0,
}

DATA = {
    "bytes":     1.0,
    "kb":        1024.0,
    "mb":        1024**2,
    "gb":        1024**3,
    "tb":        1024**4,
}

def convert(value, from_unit, to_unit, unit_table):
    """Convert value from one unit to another using a conversion table."""
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()

    if from_unit not in unit_table:
        raise ValueError(f"Unknown unit: {from_unit}. Available: {list(unit_table.keys())}")
    if to_unit not in unit_table:
        raise ValueError(f"Unknown unit: {to_unit}. Available: {list(unit_table.keys())}")

    # Convert to base unit first, then to target unit
    base_value = value * unit_table[from_unit]
    return base_value / unit_table[to_unit]

def convert_temperature(value, from_unit, to_unit):
    """Temperature needs special handling (not just multiplication)."""
    from_unit, to_unit = from_unit.lower(), to_unit.lower()

    # First convert everything to Celsius
    if from_unit == "fahrenheit":
        celsius = (value - 32) * 5 / 9
    elif from_unit == "kelvin":
        celsius = value - 273.15
    else:
        celsius = value  # already Celsius

    # Then convert from Celsius to target
    if to_unit == "fahrenheit":
        return celsius * 9 / 5 + 32
    elif to_unit == "kelvin":
        return celsius + 273.15
    else:
        return celsius

# Interactive demo
print("=== Unit Converter ===\n")

# Length examples
print("--- Length ---")
print(f"  100 km = {convert(100, 'km', 'miles', LENGTH):.2f} miles")
print(f"  6 feet = {convert(6, 'feet', 'meters', LENGTH):.4f} meters")
print(f"  1 inch = {convert(1, 'inches', 'cm', LENGTH):.2f} cm")

# Weight examples
print("\n--- Weight ---")
print(f"  70 kg = {convert(70, 'kg', 'pounds', WEIGHT):.2f} pounds")
print(f"  1 pound = {convert(1, 'pounds', 'grams', WEIGHT):.1f} grams")

# Temperature examples
print("\n--- Temperature ---")
print(f"  100°C = {convert_temperature(100, 'celsius', 'fahrenheit'):.1f}°F")
print(f"  32°F  = {convert_temperature(32, 'fahrenheit', 'celsius'):.1f}°C")
print(f"  0°C   = {convert_temperature(0, 'celsius', 'kelvin'):.2f} K")

# Data size examples
print("\n--- Data Size ---")
print(f"  1 GB = {convert(1, 'gb', 'mb', DATA):,.0f} MB")
print(f"  500 MB = {convert(500, 'mb', 'gb', DATA):.3f} GB")
