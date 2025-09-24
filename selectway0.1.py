# SELECTWAY Interpreter
# This is a simple interpreter for the SELECTWAY language
# SELECTWAY supports variable assignment, math, and print statements

import sys

variables = {}

def eval_expr(expr):
    global variables
    try:
        expr = expr.strip()
        # Support string concatenation with variables, e.g. "Hello " + name
        # Only treat as string if any part is a quoted string, otherwise treat as math
        if '+' in expr:
            parts = [p.strip() for p in expr.split('+')]
            # If any part is a quoted string, do string concat
            if any((p.startswith('"') and p.endswith('"')) or (p.startswith("'") and p.endswith("'")) for p in parts):
                result = ''
                for part in parts:
                    if (part.startswith('"') and part.endswith('"')) or (part.startswith("'") and part.endswith("'")):
                        result += part[1:-1]
                    elif part in variables:
                        result += str(variables[part])
                    else:
                        # Try to evaluate as number or variable
                        try:
                            val = eval(part, {}, variables)
                            result += str(val)
                        except:
                            result += part
                return result
            else:
                # Treat as math
                safe_vars = variables.copy()
                import re
                for var in re.findall(r'\b[a-zA-Z_]\w*\b', expr):
                    if var not in safe_vars:
                        safe_vars[var] = 0
                try:
                    return eval(expr, {}, safe_vars)
                except Exception as e:
                    print(f"Error evaluating expression: {expr}")
                    return None
        # If the expression is a quoted string, return as is
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]
        # Treat undefined variables as 0
        safe_vars = variables.copy()
        import re
        for var in re.findall(r'\b[a-zA-Z_]\w*\b', expr):
            if var not in safe_vars:
                safe_vars[var] = 0
        return eval(expr, {}, safe_vars)
    except Exception as e:
        print(f"Error evaluating expression: {expr}")
        return None

def run_selectway(code):
    global variables
    lines = code.strip().split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith('#'):
            i += 1
            continue
        if line.startswith('/print '):
            expr = line[7:].strip()
            val = eval_expr(expr)
            print(val)
        elif line.startswith('/input '):
            rest = line[7:].strip()
            if (rest.startswith('"') or rest.startswith("'")):
                quote = rest[0]
                end_quote = rest.find(quote, 1)
                if end_quote != -1:
                    prompt = rest[1:end_quote]
                    varname = rest[end_quote+1:].strip()
                else:
                    prompt = f"Enter value: "
                    varname = rest
            else:
                prompt = f"Enter value for {rest}: "
                varname = rest
            val = input(prompt)
            try:
                if '.' in val:
                    val = float(val)
                else:
                    val = int(val)
            except:
                pass
            variables[varname] = val
        elif line.startswith('/random '):
            import random
            parts = line[8:].strip().split()
            if len(parts) == 3:
                varname, minval, maxval = parts
                try:
                    minval = int(minval)
                    maxval = int(maxval)
                    variables[varname] = random.randint(minval, maxval)
                except:
                    print(f"Invalid /random usage: /random <var> <min> <max>")
            else:
                print(f"Invalid /random usage: /random <var> <min> <max>")
        elif line.startswith('/') and '=' in line:
            assign = line[1:]
            var, expr = assign.split('=', 1)
            var = var.strip()
            expr = expr.strip()
            val = eval_expr(expr)
            variables[var] = val
        elif line.startswith('/if '):
            cond = line[4:].strip()
            cond_result = False
            try:
                cond_result = bool(eval_expr(cond))
            except:
                pass
            block = []
            i += 1
            while i < len(lines) and lines[i].startswith('    '):
                block.append(lines[i][4:])
                i += 1
            if cond_result:
                for block_line in block:
                    # Directly process each line
                    block_line = block_line.strip()
                    if not block_line or block_line.startswith('#'):
                        continue
                    bl = block_line.lstrip()
                    if bl.startswith('/print '):
                        expr = bl[7:].strip()
                        val = eval_expr(expr)
                        print(val)
                    elif bl.startswith('/input '):
                        rest = bl[7:].strip()
                        if (rest.startswith('"') or rest.startswith("'")):
                            quote = rest[0]
                            end_quote = rest.find(quote, 1)
                            if end_quote != -1:
                                prompt = rest[1:end_quote]
                                varname = rest[end_quote+1:].strip()
                            else:
                                prompt = f"Enter value: "
                                varname = rest
                        else:
                            prompt = f"Enter value for {rest}: "
                            varname = rest
                        val = input(prompt)
                        try:
                            if '.' in val:
                                val = float(val)
                            else:
                                val = int(val)
                        except:
                            pass
                        variables[varname] = val
                    elif bl.startswith('/') and '=' in bl:
                        assign = bl[1:]
                        var, expr = assign.split('=', 1)
                        var = var.strip()
                        expr = expr.strip()
                        val = eval_expr(expr)
                        # Always treat assignment as number if possible
                        try:
                            if isinstance(val, str):
                                if val.isdigit():
                                    val = int(val)
                                else:
                                    val = float(val)
                        except:
                            pass
                        variables[var] = val
                    else:
                        print(f"Unknown statement: {block_line}")
            # Check for /else
            if i < len(lines) and lines[i].startswith('/else'):
                i += 1
                else_block = []
                while i < len(lines) and lines[i].startswith('    '):
                    else_block.append(lines[i][4:])
                    i += 1
                if not cond_result:
                    for else_line in else_block:
                        else_line = else_line.strip()
                        if not else_line or else_line.startswith('#'):
                            continue
                        el = else_line.lstrip()
                        if el.startswith('/print '):
                            expr = el[7:].strip()
                            val = eval_expr(expr)
                            print(val)
                        elif el.startswith('/input '):
                            rest = el[7:].strip()
                            if (rest.startswith('"') or rest.startswith("'")):
                                quote = rest[0]
                                end_quote = rest.find(quote, 1)
                                if end_quote != -1:
                                    prompt = rest[1:end_quote]
                                    varname = rest[end_quote+1:].strip()
                                else:
                                    prompt = f"Enter value: "
                                    varname = rest
                            else:
                                prompt = f"Enter value for {rest}: "
                                varname = rest
                            val = input(prompt)
                            try:
                                if '.' in val:
                                    val = float(val)
                                else:
                                    val = int(val)
                            except:
                                pass
                            variables[varname] = val
                        elif el.startswith('/') and '=' in el:
                            assign = el[1:]
                            var, expr = assign.split('=', 1)
                            var = var.strip()
                            expr = expr.strip()
                            val = eval_expr(expr)
                            variables[var] = val
                        else:
                            print(f"Unknown statement: {else_line}")
            continue
        elif line.startswith('/while '):
            cond = line[7:].strip()
            block_start = i + 1
            block = []
            while block_start < len(lines) and lines[block_start].startswith('    '):
                block.append(lines[block_start][4:])
                block_start += 1
            loop_error = False
            while True:
                try:
                    cond_result = bool(eval_expr(cond))
                except Exception as e:
                    print(f"Error evaluating expression: {cond}")
                    cond_result = False
                    loop_error = True
                if not cond_result or loop_error:
                    break
                for block_line in block:
                    block_line = block_line.strip()
                    if not block_line or block_line.startswith('#'):
                        continue
                    if block_line.startswith('/print '):
                        expr = block_line[7:].strip()
                        val = eval_expr(expr)
                        print(val)
                    elif block_line.startswith('/input '):
                        rest = block_line[7:].strip()
                        if (rest.startswith('"') or rest.startswith("'")):
                            quote = rest[0]
                            end_quote = rest.find(quote, 1)
                            if end_quote != -1:
                                prompt = rest[1:end_quote]
                                varname = rest[end_quote+1:].strip()
                            else:
                                prompt = f"Enter value: "
                                varname = rest
                        else:
                            prompt = f"Enter value for {rest}: "
                            varname = rest
                        val = input(prompt)
                        try:
                            if '.' in val:
                                val = float(val)
                            else:
                                val = int(val)
                        except:
                            pass
                        variables[varname] = val
                    elif block_line.startswith('/') and '=' in block_line:
                        assign = block_line[1:]
                        var, expr = assign.split('=', 1)
                        var = var.strip()
                        expr = expr.strip()
                        val = eval_expr(expr)
                        variables[var] = val
                    else:
                        print(f"Unknown statement: {block_line}")
            i = block_start
            continue
        else:
            print(f"Unknown statement: {line}")
        i += 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("SELECTWAY Interactive Mode (type '/exit' to quit, '/edit <file.sw>' to edit a file)")
        current_file = None
        file_lines = []
        while True:
            try:
                line = input('>>> ')
            except EOFError:
                break
            cmd = line.strip().lower()
            if cmd == '/list':
                print("\nAvailable commands:")
                print("/list                Show all commands and what they do")
                print("/new <file.sw>         Create a new .sw file")
                print("/edit [file.sw]        Edit a .sw file (shows a list if no filename)")
                print("/run [file.sw]         Run a .sw file (shows a list if no filename)")
                print("/exit                  Exit the interpreter")
                print("Statements:")
                print("  /print <expr>          Print a value or string")
                print("  /input <var>           Input a value for a variable")
                print("  /input \"Prompt\" var  Input with a custom prompt")
                print("  /x = 5                 Variable assignment")
                print("  /name = \"Alice\"        String assignment")
                print("  # ...                  Comment")
                print("\nUse case examples:")
                print("  /input name")
                print("  /print name")
                print("  /input \"What is your age?\" age")
                print("  /age = 10")
                print("  /print \"Hello, \" + name")
                continue
            elif cmd.startswith('/new'):
                filename = line.strip()[5:].strip()
                if not filename:
                    filename = input("Enter new file name (with .sw extension): ").strip()
                if not filename.endswith('.sw'):
                    print("File name must end with .sw")
                    continue
                try:
                    with open(filename, 'w') as f:
                        f.write("")
                    print(f"Created new file: {filename}")
                except Exception as e:
                    print(f"Could not create file: {e}")
            elif cmd.startswith('/edit'):
                import os
                filename = line.strip()[6:].strip()
                if not filename:
                    sw_files = [f for f in os.listdir('.') if f.endswith('.sw')]
                    if not sw_files:
                        print("No .sw files found in current directory.")
                        continue
                    print("Select a file to edit:")
                    for idx, f in enumerate(sw_files):
                        print(f"{idx+1}: {f}")
                    try:
                        choice = int(input("Enter file number: ")) - 1
                        if 0 <= choice < len(sw_files):
                            filename = sw_files[choice]
                        else:
                            print("Invalid selection.")
                            continue
                    except:
                        print("Invalid input.")
                        continue
                try:
                    with open(filename, 'r') as f:
                        file_lines = f.read().split('\n')
                    current_file = filename
                    print(f"Editing {filename}.")
                    while True:
                        print("\n--- File Editor ---")
                        for i, l in enumerate(file_lines):
                            print(f"{i+1}: {l}")
                        print("Options: [A]dd line, [E]dit line, [D]elete line, [S]ave, [Q]uit editor")
                        choice = input("Select option: ").strip().lower()
                        if choice == 'a':
                            new_line = input("Enter new line: ")
                            file_lines.append(new_line)
                        elif choice == 'e':
                            try:
                                idx = int(input("Line number to edit: ")) - 1
                                if 0 <= idx < len(file_lines):
                                    new_text = input("New text: ")
                                    file_lines[idx] = new_text
                                else:
                                    print("Invalid line number.")
                            except:
                                print("Invalid input.")
                        elif choice == 'd':
                            try:
                                idx = int(input("Line number to delete: ")) - 1
                                if 0 <= idx < len(file_lines):
                                    file_lines.pop(idx)
                                else:
                                    print("Invalid line number.")
                            except:
                                print("Invalid input.")
                        elif choice == 's':
                            try:
                                with open(current_file, 'w') as f:
                                    f.write('\n'.join(file_lines))
                                print(f"Saved {current_file}.")
                            except Exception as e:
                                print(f"Could not save: {e}")
                        elif choice == 'q':
                            print(f"Stopped editing {current_file}.")
                            current_file = None
                            file_lines = []
                            break
                        else:
                            print("Unknown option.")
                except Exception as e:
                    print(f"Could not open {filename}: {e}")
            elif cmd.startswith('/run'):
                import os
                filename = line.strip()[5:].strip()
                if not filename:
                    sw_files = [f for f in os.listdir('.') if f.endswith('.sw')]
                    if not sw_files:
                        print("No .sw files found in current directory.")
                        continue
                    print("Select a file to run:")
                    for idx, f in enumerate(sw_files):
                        print(f"{idx+1}: {f}")
                    try:
                        choice = int(input("Enter file number: ")) - 1
                        if 0 <= choice < len(sw_files):
                            filename = sw_files[choice]
                        else:
                            print("Invalid selection.")
                            continue
                    except:
                        print("Invalid input.")
                        continue
                try:
                    with open(filename, 'r') as f:
                        code = f.read()
                    print(f"Running {filename}:")
                    run_selectway(code)
                except Exception as e:
                    print(f"Could not run {filename}: {e}")
            elif cmd == '/exit':
                break
            else:
                run_selectway(line)
