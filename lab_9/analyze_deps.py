import json

# Name of the file that contains the dependency JSON data.
JSON_FILENAME = 'pydeps.json'

def load_dependency_data(filename):
    """Load dependency data from a JSON file."""
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def calculate_fan_out(deps):
    """
    Fan-out: Number of modules a given module depends on.
    This is based on the length of the "imports" list in the JSON.
    """
    fan_out = {}
    for module, info in deps.items():
        # Get the list of modules that this module imports.
        imports = info.get("imports", [])
        fan_out[module] = len(imports)
    return fan_out

def calculate_fan_in(deps):
    """
    Fan-in: Number of modules that depend on a given module.
    This is based on the length of the "imported_by" list in the JSON.
    """
    fan_in = {}
    for module, info in deps.items():
        # Get the list of modules that import this module.
        imported_by = info.get("imported_by", [])
        fan_in[module] = len(imported_by)
    return fan_in

def main():
    # Load the dependency data from the JSON file.
    deps = load_dependency_data(JSON_FILENAME)
    
    # Calculate and display fan-out.
    fan_out = calculate_fan_out(deps)
    print("Fan-Out (Modules that each module depends on):")
    for module, count in fan_out.items():
        print(f"{module}: {count}")
    
    print("\n" + "="*40 + "\n")
    
    # Calculate and display fan-in.
    fan_in = calculate_fan_in(deps)
    print("Fan-In (Modules that depend on each module):")
    for module, count in fan_in.items():
        print(f"{module}: {count}")

if __name__ == '__main__':
    main()
