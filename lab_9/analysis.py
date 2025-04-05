import json
from collections import defaultdict

# File names
JSON_FILENAME = 'pydeps.json'
REPORT_FILENAME = 'analysis_report.txt'

def load_dependency_data(filename):
    """Load dependency data from a JSON file."""
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def build_graph(deps):
    """
    Build a directed graph from the dependency data.
    Each key is a module and its value is the list of modules it imports.
    """
    graph = {}
    for module, info in deps.items():
        graph[module] = info.get("imports", [])
    return graph

def find_cycles(graph):
    """
    Detect cycles in the dependency graph using DFS.
    Returns a list of cycles (each cycle is a list of module names).
    """
    cycles = []
    visited = set()

    def dfs(node, stack):
        if node in stack:
            # Cycle found; extract the cycle from the current stack.
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

def find_unused_modules(deps):
    """
    Identify modules that are unused/disconnected (i.e., not imported by any other module).
    """
    unused = []
    for module, info in deps.items():
        if "imported_by" not in info or len(info["imported_by"]) == 0:
            unused.append(module)
    return unused

def compute_dependency_depth(graph):
    """
    Compute the maximum dependency chain length (depth) starting from root modules.
    Returns a tuple: (max_depth, list of root modules)
    """
    incoming = defaultdict(int)
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            incoming[neighbor] += 1
    
    # Modules with no incoming edges are considered roots.
    roots = [node for node in graph if incoming[node] == 0]
    depth_cache = {}
    
    def dfs_depth(node, visited):
        if node in visited:
            return 0  # Cycle detected; stop here.
        if node in depth_cache:
            return depth_cache[node]
        visited.add(node)
        max_depth = 0
        for neighbor in graph.get(node, []):
            max_depth = max(max_depth, dfs_depth(neighbor, visited))
        visited.remove(node)
        depth_cache[node] = max_depth + 1
        return depth_cache[node]
    
    overall_max_depth = 0
    for root in roots:
        overall_max_depth = max(overall_max_depth, dfs_depth(root, set()))
    
    return overall_max_depth, roots

def highly_coupled_modules(deps, threshold=5):
    """
    Identify highly coupled modules based on their fan-out (number of imports).
    Returns a dictionary mapping module name to its fan-out.
    """
    high_coupling = {}
    for module, info in deps.items():
        fan_out = len(info.get("imports", []))
        if fan_out >= threshold:
            high_coupling[module] = fan_out
    return high_coupling

def calculate_fan_out(deps):
    """
    Compute the fan-out for each module (number of modules it depends on).
    """
    fan_out = {}
    for module, info in deps.items():
        fan_out[module] = len(info.get("imports", []))
    return fan_out

def calculate_fan_in(deps):
    """
    Compute the fan-in for each module (number of modules that depend on it).
    """
    fan_in = {}
    for module, info in deps.items():
        fan_in[module] = len(info.get("imported_by", []))
    return fan_in

def dependency_impact_assessment(deps, core_module):
    """
    For a given core module, return the modules that are impacted (i.e. that import it).
    """
    impacted = deps.get(core_module, {}).get("imported_by", [])
    return impacted

def main():
    # Load dependency data.
    deps = load_dependency_data(JSON_FILENAME)
    graph = build_graph(deps)
    
    # Compute fan-in and fan-out.
    fan_out = calculate_fan_out(deps)
    fan_in = calculate_fan_in(deps)
    
    # Identify highly coupled modules (using fan-out threshold).
    high_coupling = highly_coupled_modules(deps, threshold=5)
    
    # Detect cyclic dependencies.
    cycles = find_cycles(graph)
    
    # Identify unused/disconnected modules.
    unused = find_unused_modules(deps)
    
    # Assess dependency depth.
    max_depth, roots = compute_dependency_depth(graph)
    
    # Dependency impact assessment.
    # Specify a core module (adjust if necessary). Here, we try "manimlib".
    core_module = "manimlib"
    if core_module not in deps:
        # If not available, select a module with the highest fan-in.
        core_module = max(fan_in, key=fan_in.get)
    impacted = dependency_impact_assessment(deps, core_module)
    
    # Build the report.
    report_lines = []
    report_lines.append("Dependency Analysis Report")
    report_lines.append("=" * 40)
    report_lines.append("")
    
    report_lines.append("1. Fan-Out per Module:")
    for module, count in fan_out.items():
        report_lines.append(f"  {module}: {count}")
    report_lines.append("")
    
    report_lines.append("2. Fan-In per Module:")
    for module, count in fan_in.items():
        report_lines.append(f"  {module}: {count}")
    report_lines.append("")
    
    report_lines.append("3. Highly Coupled Modules (Fan-Out >= 5):")
    for module, count in high_coupling.items():
        report_lines.append(f"  {module}: {count}")
    report_lines.append("")
    
    report_lines.append("4. Cyclic Dependencies Detected:")
    if cycles:
        for cycle in cycles:
            report_lines.append("  " + " -> ".join(cycle))
        report_lines.append("  Note: Cycles may affect maintainability due to unexpected side effects.")
    else:
        report_lines.append("  No cyclic dependencies detected.")
    report_lines.append("")
    
    report_lines.append("5. Unused/Disconnected Modules:")
    if unused:
        for module in unused:
            report_lines.append(f"  {module}")
    else:
        report_lines.append("  None")
    report_lines.append("")
    
    report_lines.append("6. Dependency Depth Assessment:")
    report_lines.append(f"  Maximum Dependency Depth (Longest Path): {max_depth}")
    report_lines.append("  Root Modules (with no incoming dependencies):")
    for root in roots:
        report_lines.append(f"    {root}")
    report_lines.append("")
    
    report_lines.append("7. Dependency Impact Assessment:")
    report_lines.append(f"  Core Module: {core_module}")
    report_lines.append("  Modules impacted if the core module is changed:")
    if impacted:
        for mod in impacted:
            report_lines.append(f"    {mod}")
    else:
        report_lines.append("    None found")
    
    # Write the report to the output file.
    with open(REPORT_FILENAME, 'w') as f:
        f.write("\n".join(report_lines))
    
    print(f"Analysis complete. Report saved to '{REPORT_FILENAME}'.")

if __name__ == '__main__':
    main()
