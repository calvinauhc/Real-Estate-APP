def get_all_properties():
    try:
        with open("properties.txt", "r") as f:
            return f.readlines()
    except FileNotFoundError:
        return []