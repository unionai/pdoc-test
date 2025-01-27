from pdoc.doc import Class, Function, Variable, Module
import json
from datetime import datetime
from pathlib import Path
import inspect

class PDOCEncoder(json.JSONEncoder):
    """Custom JSON encoder for handling pdoc objects"""
    def default(self, obj):
        if isinstance(obj, (Class, Function, Variable)):
            return str(obj)
        if isinstance(obj, Path):
            return str(obj)
        return super().default(obj)

def path_to_str(obj):
    if isinstance(obj, Path):
        return str(obj)
    return obj

def convert_paths(obj):
    """Recursively convert all Path objects to strings in a data structure"""
    if isinstance(obj, dict):
        return {k: convert_paths(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_paths(i) for i in obj]
    elif isinstance(obj, (Path, Class, Function, Variable)):
        return str(obj)
    return obj

def get_source_code(obj):
    """Extract source code if available"""
    try:
        return inspect.getsource(obj.obj)
    except (TypeError, AttributeError, OSError):
        return None

def extract_signature(method_str):
    """Extract method signature from the string representation"""
    if '(' not in method_str:
        return {}
    
    try:
        sig_str = method_str[method_str.index('('):method_str.rindex(')')+1]
        params = sig_str.strip('()').split(',')
        param_dict = {}
        
        for p in params:
            p = p.strip()
            if ':' in p:
                name, type_hint = p.split(':', 1)
                param_dict[name.strip()] = type_hint.strip()
            else:
                param_dict[p] = None
                
        return param_dict
    except:
        return {}

def build_detailed_tree(doc_obj):
    members = {}
    
    # Handle submodules first
    if hasattr(doc_obj, 'submodules'):
        members['submodules'] = {}
        for submodule in doc_obj.submodules:
            submember_tree = build_detailed_tree(submodule)
            members['submodules'][submodule.name] = {
                'name': submodule.name,
                'docstring': submodule.docstring,
                'source_file': path_to_str(submodule.source_file),
                'is_package': submodule.is_package,
                'source_code': get_source_code(submodule),
                'members': submember_tree
            }
    
    for member_name, member in doc_obj.members.items():
        member_info = {
            'kind': str(member.kind),
            'docstring': member.docstring,
            'source_file': path_to_str(member.source_file),
            'source_lines': member.source_lines,
            'source_code': get_source_code(member),
            'qualname': member.qualname,
            'taken_from': str(member.taken_from) if member.taken_from else None,
            'decorators': [str(d) for d in member.decorators] if hasattr(member, 'decorators') else [],
            'module_path': member.modulename
        }
        
        if isinstance(member, Class):
            member_info['bases'] = [str(base) for base in member.bases]
            
            # Methods with full signatures and source code
            member_info['methods'] = []
            for method in member.methods:
                method_str = str(method)
                method_info = {
                    'signature': method_str,
                    'parameters': extract_signature(method_str),
                    'is_inherited': 'inherited from' in method_str,
                    'source': method_str.split('#')[0].strip() if '#' in method_str else method_str,
                    'source_code': get_source_code(method)
                }
                if 'inherited from' in method_str:
                    method_info['inherited_from'] = method_str.split('inherited from')[-1].strip()
                member_info['methods'].append(method_info)
            
            # Class variables with source
            member_info['class_variables'] = []
            for var in member.class_variables:
                var_info = {
                    'name': str(var),
                    'docstring': var.docstring if hasattr(var, 'docstring') else None,
                    'type': str(var.type) if hasattr(var, 'type') else None,
                    'source_code': get_source_code(var)
                }
                member_info['class_variables'].append(var_info)
            
            # Instance variables with source
            member_info['instance_variables'] = []
            for var in member.instance_variables:
                var_info = {
                    'name': str(var),
                    'docstring': var.docstring if hasattr(var, 'docstring') else None,
                    'type': str(var.type) if hasattr(var, 'type') else None,
                    'source_code': get_source_code(var)
                }
                member_info['instance_variables'].append(var_info)
                
            member_info['staticmethods'] = [str(m) for m in member.staticmethods]
            member_info['classmethods'] = [str(m) for m in member.classmethods]
            member_info['own_members'] = [str(m) for m in member.own_members]
            member_info['inherited_members'] = {
                str(k): str(v) for k, v in member.inherited_members.items()
            }
            
        elif isinstance(member, Function):
            member_info['signature'] = str(member.obj) if hasattr(member, 'obj') else None
            member_info['parameters'] = extract_signature(str(member))
            
        elif isinstance(member, Variable):
            member_info['type'] = str(member.type) if hasattr(member, 'type') else None
            
        members[member_name] = member_info
    
    return members

def process_module(module_name):
    """Process a single module and return its tree"""
    module = Module.from_name(module_name)
    tree = build_detailed_tree(module)
    
    return {
        'metadata': {
            'generation_time': datetime.now().isoformat(),
            'module_name': module.name,
            'module_docstring': module.docstring,
            'is_package': module.is_package,
            'source_file': path_to_str(module.source_file)
        },
        'tree': tree
    }

if __name__ == '__main__':
    # List of modules to process
    modules = ['union', 'flytekit']
    
    # Process each module
    all_modules = {}
    for module_name in modules:
        try:
            print(f"Processing module: {module_name}")
            module_data = process_module(module_name)
            all_modules[module_name] = module_data
            
            # Write individual module file
            output_file = f'{module_name}_module_tree.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(module_data, f, indent=2, ensure_ascii=False, cls=PDOCEncoder)
            print(f"Module tree written to '{output_file}'")
            
        except Exception as e:
            print(f"Error processing module {module_name}: {str(e)}")
    
    # Write combined output
    combined_output = {
        'metadata': {
            'generation_time': datetime.now().isoformat(),
            'modules_processed': list(all_modules.keys())
        },
        'modules': all_modules
    }
    
    # Convert any remaining Path objects to strings
    combined_output = convert_paths(combined_output)
    
    # Write combined output to file
    with open('combined_module_tree.json', 'w', encoding='utf-8') as f:
        json.dump(combined_output, f, indent=2, ensure_ascii=False, cls=PDOCEncoder)
    
    print("Complete combined module tree has been written to 'combined_module_tree.json'")