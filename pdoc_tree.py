from pdoc.doc import Class, Function, Variable, Module
import json
from datetime import datetime
from pathlib import Path
import inspect
import os

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
    """Recursively convert all Path objects to strings"""
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

def create_directory(path):
    """Create directory if it doesn't exist"""
    os.makedirs(path, exist_ok=True)

def write_json_file(data, filepath):
    """Write JSON data to file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, cls=PDOCEncoder)

def build_detailed_tree(doc_obj, base_path, current_path=''):
    """
    Build detailed tree and write files in appropriate directories
    Returns: dict of member information and creates JSON files
    """
    members = {}
    
    # Create directory for current module/submodule
    if current_path:
        full_path = os.path.join(base_path, current_path)
        create_directory(full_path)
    else:
        full_path = base_path

    # Handle submodules
    if hasattr(doc_obj, 'submodules'):
        members['submodules'] = {}
        for submodule in doc_obj.submodules:
            # Determine submodule path
            submodule_path = os.path.join(current_path, submodule.name.split('.')[-1])
            
            submember_tree = build_detailed_tree(
                submodule, 
                base_path, 
                submodule_path
            )
            
            submodule_data = {
                'name': submodule.name,
                'docstring': submodule.docstring,
                'source_file': path_to_str(submodule.source_file),
                'is_package': submodule.is_package,
                'source_code': get_source_code(submodule),
                'members': submember_tree
            }
            
            members['submodules'][submodule.name] = submodule_data
            
            # Write submodule file
            submodule_file = os.path.join(full_path, f"{submodule.name.split('.')[-1]}.json")
            write_json_file(submodule_data, submodule_file)
    
    # Process regular members
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
            
            # Methods
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
            
            # Variables
            member_info['class_variables'] = []
            for var in member.class_variables:
                var_info = {
                    'name': str(var),
                    'docstring': var.docstring if hasattr(var, 'docstring') else None,
                    'type': str(var.type) if hasattr(var, 'type') else None,
                    'source_code': get_source_code(var)
                }
                member_info['class_variables'].append(var_info)
            
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
            
            # Write class file
            class_file = os.path.join(full_path, f"class_{member_name}.json")
            write_json_file(member_info, class_file)
            
        elif isinstance(member, Function):
            member_info['signature'] = str(member.obj) if hasattr(member, 'obj') else None
            member_info['parameters'] = extract_signature(str(member))
            
            # Write function file
            function_file = os.path.join(full_path, f"function_{member_name}.json")
            write_json_file(member_info, function_file)
            
        elif isinstance(member, Variable):
            member_info['type'] = str(member.type) if hasattr(member, 'type') else None
            
            # Write variable file
            variable_file = os.path.join(full_path, f"variable_{member_name}.json")
            write_json_file(member_info, variable_file)
            
        members[member_name] = member_info
    
    return members

def process_module(module_name, output_dir):
    """Process a single module and create its directory structure"""
    print(f"Processing module: {module_name}")
    
    # Create base directory for module
    module_dir = os.path.join(output_dir, module_name)
    create_directory(module_dir)
    
    try:
        module = Module.from_name(module_name)
        tree = build_detailed_tree(module, module_dir)
        
        module_data = {
            'metadata': {
                'generation_time': datetime.now().isoformat(),
                'module_name': module.name,
                'module_docstring': module.docstring,
                'is_package': module.is_package,
                'source_file': path_to_str(module.source_file)
            },
            'tree': tree
        }
        
        # Write module overview file
        module_file = os.path.join(module_dir, '__module__.json')
        write_json_file(module_data, module_file)
        
        return module_data
    
    except Exception as e:
        print(f"Error processing module {module_name}: {str(e)}")
        return None

if __name__ == '__main__':
    # List of modules to process
    modules = ['union', 'flytekit']
    
    # Create base output directory
    output_dir = 'module_documentation'
    create_directory(output_dir)
    
    # Process each module
    all_modules = {}
    for module_name in modules:
        module_data = process_module(module_name, output_dir)
        if module_data:
            all_modules[module_name] = module_data
    
    # Write combined overview file
    combined_output = {
        'metadata': {
            'generation_time': datetime.now().isoformat(),
            'modules_processed': list(all_modules.keys())
        },
        'modules': all_modules
    }
    
    combined_output = convert_paths(combined_output)
    write_json_file(combined_output, os.path.join(output_dir, 'overview.json'))
    
    print(f"\nDocumentation has been generated in the '{output_dir}' directory")