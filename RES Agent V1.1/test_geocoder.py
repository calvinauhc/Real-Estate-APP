from layers.geocoder import get_coordinates

# Use the actual postal code for 123 Tampines St 11 (which is 521123)
postal_code = "599982"

print(f"Testing geocoding for Postal Code: {postal_code}...")

coords = get_coordinates(postal_code)

if coords:
    print(f"Success! Coordinates: {coords}")
else:
    print("Could not find coordinates for this postal code.")