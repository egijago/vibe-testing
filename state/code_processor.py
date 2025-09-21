from pycfg.pycfg import PyCFG, CFGNode
from collections import deque
import re
import os, tempfile
import coverage
import runpy

class CodeLine:
    def __init__(self, line_no, code, pseudo_code):
        self.line_no = line_no  
        self.code = code
        self.pseudo_code = pseudo_code

class CodeProcessor:
    def build_from_source(self, source): 
        cfg = PyCFG()
        CFGNode.cache = {}
        cfg.gen_cfg(src=source)
        G = CFGNode.to_graph()

        code_map = {}
        adj_list = {}

        start_node, start_node_line_no = None, None 
        end_node= None
        nodes = G.nodes()
        for node in nodes:
            node_id = str(node)
            label = node.attr.get('label', "")

            if not (label and label[0].isdigit()):
                continue

            line_no, pseudo_code = label.split(":", 1)
            prefix = pseudo_code.split(":", 1)[0].lstrip()
            if prefix.startswith("enter") and start_node is None:
                start_node = node_id
                start_node_line_no = line_no
            elif prefix.startswith("exit") and line_no == start_node_line_no:
                end_node = node_id
            code = source.splitlines()[int(line_no) - 1]
            code_map[node_id] = CodeLine(
                line_no=line_no,
                code=code,
                pseudo_code=pseudo_code
            )

            neighbors = [str(n) for n in G.neighbors(node_id)]
            adj_list[node_id] = neighbors
        
        self.source, self.code_map, self.adj_list, self.start_node, self.end_node = source, code_map, adj_list, start_node, end_node
        self.function_name = self.get_first_function_name(self.source)
        self.statements = self.get_statement_lines_from_code(source)
        self.path_to_code_lines_map = {}

    def find_shortest_path(self, start_node, end_node):
        queue = deque()
        visited = {start_node}
        queue.append([start_node])
        while queue: 
            current_path = queue.popleft()
            current_node = current_path[-1]

            if current_node == end_node:
                return current_path
            
            for neighbour in self.adj_list[current_node]:
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(current_path + [neighbour])
        
        assert self._find_shortest_path(end_node, self.end_node)
        
        return None
    
    def _find_shortest_path(self, start_node, end_node):
        queue = deque()
        visited = {start_node}
        queue.append([start_node])
        while queue: 
            current_path = queue.popleft()
            current_node = current_path[-1]

            if current_node == end_node:
                return current_path
            
            for neighbour in self.adj_list[current_node]:
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(current_path + [neighbour])
            
        return None

    
    def find_all_execution_path(self):
        visited = {self.start_node}
        path_queue = deque([[self.start_node]]) 
        result = []
        dead_paths = []
        while path_queue: 
            current_path = path_queue.popleft()
            current_node = current_path[-1]

            if current_node == self.end_node:
                result.append(current_path)
                continue
            
            dead_path = True
            for neighbour in self.adj_list[current_node]:
                if neighbour not in visited:
                    dead_path = False 
                    visited.add(neighbour)
                    path_queue.append(current_path + [neighbour])
            
            if dead_path: 
                assert self._find_shortest_path(current_node, self.end_node) is not None
                dead_paths.append(current_path)
        
        result += dead_paths

        return result

    def remove_redundant_line_coverage_path(self, paths):
        path_and_line_cov = []
        for path in paths:
            line_set = {self.code_map[node].line_no for node in path}
            path_and_line_cov.append((path, line_set))
        path_and_line_cov.sort(key=lambda x: len(x[1]), reverse=True)

        result = []
        for item in path_and_line_cov: 
            if not any(item[1] <= i[1] for i in result):
                result.append(item)
        
        return [item[0] for item in result]

    def path_to_code_lines(self, path, use_pseudo = False):
        result = []
        for node in path:
            code_line = self.code_map[node]
            result.append(f"Line {code_line.line_no}: {code_line.pseudo_code if use_pseudo else code_line.code}")
        result = result[1:-1] # First and last result are enter and exit function
        return "\n".join(result)
    
    def path_to_code_lines_refiner(self, path, use_pseudo = False):
        result = []
        for node in path:
            code_line = self.code_map[node]
            result.append(f"Line {code_line.line_no}: {code_line.pseudo_code if use_pseudo else code_line.code}")
        result = result[1:] # First is enter function
        return "\n".join(result)

    def paths_to_code_lines(self, paths, use_pseudo = False):
        return [self.path_to_code_lines(path, use_pseudo) for path in paths]

    def path_to_target_lines(self, path):     
        line_set = {self.code_map[node].line_no for node in path}
        return list(line_set)
    
    def get_first_function_name(self, src: str) -> str:
        match = re.search(r"^\s*def\s+([A-Za-z_]\w*)\s*\(", src, re.MULTILINE)
        return match.group(1) if match else ""
    
    def get_node_id_from_line_no(self, line_no):
        result = []
        for k, v in self.code_map.items():
            if str(v.line_no) == str(line_no):
                result.append(k)        
        return result

    def get_code_path_to_node(self, node_id):
        path = self.find_shortest_path(self.start_node, node_id)
        return self.path_to_code_lines(path)

    def get_statement_lines_from_code(self, code: str): 
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "snippet.py")
            with open(path, "w") as f:
                f.write(code)

            cov = coverage.Coverage()
            cov.start()
            runpy.run_path(path, run_name="__main__")  # run the file
            cov.stop(); cov.save()

            filename, statements, excluded, missing, output = cov.analysis2(path)
            return statements
    
    def check_missing_statements(self, executed):
        return sorted(set(self.statements) - set(executed))
    
    def compute_path_to_line_numbers(self, line_numbers): 
        for line in line_numbers:
            if line in self.path_to_code_lines_map:
                continue
            node_ids = self.get_node_id_from_line_no(line)
            if not node_ids: 
                continue
            path_result = self.find_shortest_path(self.start_node, node_ids[0])
            if path_result: 
                self.path_to_code_lines_map[line] = path_result
    