import json
from collections import defaultdict

# Load dependency data from the JSON file.
def load_dependency_data(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

# Build a directed graph from the dependency data.
def build_graph(deps):
    # Each key in the graph is a module, and its value is the list of modules it imports.
    graph = {}
    for module, info in deps.items():
        # Use the "imports" list if available; otherwise, an empty list.
        graph[module] = info.get("imports", [])
    return graph

# Detect cycles in the graph using DFS.
def find_cycles(graph):
    cycles = []
    visited = set()

    def dfs(node, stack):
        if node in stack:
            # Cycle found; extract the cycle slice.
            cycle = stack[stack.index(node):] + [node]
            cycles.append(cycle)
            return
        if node in visited:
            return
        visited.add(node)
        stack.append(node)
        for neighbor in graph.get(node, []):
            dfs(neighbor, stack)
        stack.pop()

    for node in graph.keys():
        dfs(node, [])
    return cycles

# Find modules that are unused or disconnected (i.e., not imported by any other module).
def find_unused_modules(deps):
    unused = []
    for module, info in deps.items():
        # If the module has no "imported_by" entry or it's an empty list, mark as unused.
        if "imported_by" not in info or len(info["imported_by"]) == 0:
            unused.append(module)
    return unused

def compute_dependency_depth(graph):
    from collections import defaultdict
    
    # Count incoming edges for each module.
    incoming = defaultdict(int)
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            incoming[neighbor] += 1
    
    # Identify root modules (modules with no incoming dependencies).
    roots = [node for node in graph if incoming[node] == 0]
    
    depth_cache = {}
    
    def dfs_depth(node, visited):
        # If this node is already in the current path, we've hit a cycle.
        if node in visited:
            return 0  # Cycle detected, stop here.
        if node in depth_cache:
            return depth_cache[node]
        
        visited.add(node)
        max_depth = 0
        for neighbor in graph.get(node, []):
            max_depth = max(max_depth, dfs_depth(neighbor, visited))
        visited.remove(node)
        
        depth_cache[node] = max_depth + 1
        return depth_cache[node]
    
    max_depth = 0
    for root in roots:
        max_depth = max(max_depth, dfs_depth(root, set()))
    
    return max_depth, roots


# Identify highly coupled modules based on fan-out.
def highly_coupled_modules(deps, threshold=5):
    # Use the "imports" list length as fan-out.
    high_coupling = {}
    for module, info in deps.items():
        fan_out = len(info.get("imports", []))
        if fan_out >= threshold:
            high_coupling[module] = fan_out
    return high_coupling

# Main function to perform the analysis.
def main():
    # Load the dependency data.
    deps = load_dependency_data('pydeps.json')
    
    # Build the graph from the dependency data.
    graph = build_graph(deps)
    
    # 1. Identify Highly Coupled Modules
    print("Highly Coupled Modules (Fan-Out >= 5):")
    high_coupling = highly_coupled_modules(deps, threshold=5)
    for module, fan_out in high_coupling.items():
        print(f"{module}: {fan_out}")
    
    print("\n" + "="*50 + "\n")
    
    # 2. Detect Cyclic Dependencies
    cycles = find_cycles(graph)
    if cycles:
        print("Cyclic Dependencies Detected:")
        for cycle in cycles:
            print(" -> ".join(cycle))
        print("\nCycles can make the codebase hard to maintain because changes in one module may indirectly affect modules in the cycle, creating unexpected side effects.")
    else:
        print("No cyclic dependencies detected.")
    
    print("\n" + "="*50 + "\n")
    
    # 3. Check for Unused/Disconnected Modules
    unused = find_unused_modules(deps)
    print("Unused or Disconnected Modules:")
    for module in unused:
        print(module)
    
    print("\n" + "="*50 + "\n")
    
    # 4. Assess the Depth of Dependencies
    max_depth, roots = compute_dependency_depth(graph)
    print(f"Maximum Dependency Depth (Longest Path): {max_depth}")
    print("Root Modules (with no incoming dependencies):")
    for root in roots:
        print(root)
    
    print("\n" + "="*50 + "\n")
    
    # 5. Dependency Impact Assessment
    # Identify a core module. A core module is one with high fan-in (i.e., many modules depend on it).
    # From your output, for example, "requests.compat" had the highest fan-in (11).
    core_module = "requests.compat"
    impacted = deps.get(core_module, {}).get("imported_by", [])
    print(f"Core Module: {core_module}")
    print("Modules impacted if the core module is changed:")
    for mod in impacted:
        print(mod)
    print("\nA change in the core module may affect these modules, risking system-wide breakage if not managed carefully.")

if __name__ == '__main__':
    main()
