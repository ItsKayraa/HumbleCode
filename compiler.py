# uhh so
# \/////////////////////////////////////////////////\
# im not the best compile crator out there and i made this as a solo
# please give me comments on how could i make this better
# thanks!
# /\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\/


import sys
import subprocess

outputlines = ["; Created by HC Compiler // Feel free to delete this line!\n"]
enabled = []
variables = {}
label_counter = 0

def giveOutput(): # give the output file
    loc = input("Compile was done. Where would you like to save the output (This compiler compiles to assembly and works with NASM.)? [path]: ")
    with open(loc, "w") as output:
        output.write("".join(outputlines))
        print(f"Output by HumbleCode: {loc}")
    yn = input("Would you like to transform to bin? (Make sure you have NASM if you want to transform to bin.) [ Y/n ]: ")
    if yn.lower() in ["y", "yes"]:
        print("Transforming to bin...")
        subprocess.call(["nasm", "-f", "bin", loc, "-o", loc.replace(".asm", ".bin") if loc.endswith(".asm") else loc + ".bin"])
    else:
        print("Abort. Finishing...")

def addAsm(code: list): # assembly code adder
    addAsmCodes = code
    outputlines.append("\n".join(addAsmCodes) + "\n")
    addAsmCodes.clear()

def addOrg(loc: str): # workloc func
    outputlines.append(f"org {loc}\n")


def bootstart(args = None): # shortened version of bits and workloc
    """
    Set up the bootloader environment with optional bit mode and work location.
    
    Args:
        args: List of arguments for customizing the bootloader setup
    """
    if args is None:
        args = []
    
    bits_added = False
    org_added = False
    i = 0
    while i < len(args):
        if i >= len(args):
            break
            
        if args[i] in ["-b", "--bits"]:
            if i + 1 < len(args):
                bit = args[i + 1]
                addBits(bit)
                bits_added = True
                i += 2
            else:
                print("Error: Missing value for bits argument")
                i += 1
        elif args[i] in ["-wl", "--workloc", "--worklocation"]:
            if i + 1 < len(args):
                org = args[i + 1]
                addOrg(org)
                org_added = True
                i += 2
            else:
                print("Error: Missing value for work location argument")
                i += 1
        else:
            i += 1
    
    if not org_added:
        addOrg("0x7c00")
    
    if not bits_added:
        addBits("16")

def addBits(bits: str): # bits 16-32-64
    if bits not in ["16", "32", "64"]:
        print(f"Error: Not an available bit type: {bits}")
    outputlines.append(f"bits {bits}\n")

def enable(func: str): # function enabler
    if func not in enabled:
        enabled.append(func)
    match func:
        case "printtext":
            outputlines.append("; Print Text Functions\nstart:\n    mov si, printtext\n    call printString\n    jmp $\n\nprintString:\n    lodsb\n    cmp al, 0\n    je .done\n    mov ah, 0x0e\n    int 0x10\n    jmp printString\n.done:\n   ret\n\n")
        case "startprinttext":
            outputlines.append("start:\n    mov si, printtext\n    call printString\n    jmp $\n")
        # maybe later soon?

def printtext(text: str): # printtext
    if "printtext" in enabled:
        if "{{" in text and "}}" in text:
            while "{{" in text and "}}" in text:
                start = text.find("{{")
                end = text.find("}}", start)
                variable = text[start+2:end]
                if variable in variables:
                    text = text[:start] + str(variables[variable]) + text[end+2:]
                else:
                    print(f"Error: Variable '{variable}' not found.")
                    return

        outputlines.append(f"printtext: db {text}, 0\n")
    else:
        print("Error: Please enable printtext if it's not enabled before printtext function.")
        return

    if "printtext" in enabled:
        outputlines.append("mov si, printtext\n")

def allPT(text: str): # shortened version of enable printtext + printtext
    enable("printtext")
    if "{{" in text and "}}" in text:
        while "{{" in text and "}}" in text:
            start = text.find("{{")
            end = text.find("}}", start)
            variable = text[start+2:end]
            if variable in variables:
                text = text[:start] + str(variables[variable]) + text[end+2:]
            else:
                print(f"Error: Variable '{variable}' not found.")
                return

    outputlines.append(f"printtext: db {text}, 0\n")

def addVar(name: str, value: str):
    try:
        evaluated = eval(value)
        variables[name] = evaluated
    except Exception as e:
        variables[name] = value

def evaluate_condition(condition: str) -> bool:
    for var_name, var_value in variables.items():
        placeholder = f"{{{{{var_name}}}}}"
        if placeholder in condition:
            condition = condition.replace(placeholder, str(var_value))
        if var_name in condition:
            condition = condition.replace(f" {var_name} ", f" {str(var_value)} ")
            if condition.startswith(f"{var_name} "):
                condition = f"{str(var_value)} " + condition[len(var_name)+1:]
            if condition.endswith(f" {var_name}"):
                condition = condition[:-len(var_name)-1] + f" {str(var_value)}"
            if condition == var_name:
                condition = str(var_value)
    if " == " in condition:
        left, right = condition.split(" == ", 1)
        return eval(left.strip()) == eval(right.strip())
    elif " != " in condition:
        left, right = condition.split(" != ", 1)
        return eval(left.strip()) != eval(right.strip())
    elif " > " in condition:
        left, right = condition.split(" > ", 1)
        return eval(left.strip()) > eval(right.strip())
    elif " < " in condition:
        left, right = condition.split(" < ", 1)
        return eval(left.strip()) < eval(right.strip())
    elif " >= " in condition:
        left, right = condition.split(" >= ", 1)
        return eval(left.strip()) >= eval(right.strip())
    elif " <= " in condition:
        left, right = condition.split(" <= ", 1)
        return eval(left.strip()) <= eval(right.strip())
    else:
        try:
            result = eval(condition)
            if isinstance(result, bool):
                return result
            return bool(result)
        except:
            return False

def handle_if(condition: str, code_block: list) -> list: # handler
    if evaluate_condition(condition):
        return code_block
    return []

def endAll(): # adds the required ends to assembly output
    outputlines.append("times 510-($-$$) db 0\ndw 0xAA55\n")
    giveOutput()

def executor(file: str): # main file executor
    with open(file, "r") as hcFile:
        lines = hcFile.read().splitlines()
        asming = False
        asmCodes = []
        funcs = {}
        handledfuncs = []
        handlingfunc = False
        curfunc = ""
        
        i = 0
        while i < len(lines):
            line = lines[i]
            if not line or line.isspace():
                i += 1
                continue

            args = line.split()
            if not args:
                i += 1
                continue
                
            if args[0].lower() == "printtext" and not asming and not handlingfunc:
                printtext(" ".join(args[1:]))
            elif args[0].lower() == "enable" and not asming and not handlingfunc:
                enable(args[1].lower())
            elif args[0].lower() == "endall" and not asming and not handlingfunc:
                endAll()
                break
            elif args[0].lower() == "bits" or args[0].lower() == "b" and not asming and not handlingfunc:
                addBits(args[1])
            elif args[0].lower() == "workloc" or args[0].lower() == "worklocation" and not asming and not handlingfunc:
                addOrg(args[1])
            elif args[0].lower() == "var" or args[0].lower() == "variable" and not asming and not handlingfunc:
                addVar(args[1], " ".join(args[2:]))
            elif args[0].lower() == "bs" or args[0].lower() == "bootstart":
                bootstart(args[1:])
            elif args[0].lower() == "allpt" or args[0].lower() == "allprinttext" and not asming:
                if handlingfunc:
                    funcs[curfunc] += f"allpt {' '.join(args[1:])}\n"
                else:
                    allPT(" ".join(args[1:]))
            elif args[0].lower() == "if" and not asming:
                if handlingfunc:
                    funcs[curfunc] += f"if {' '.join(args[1:])}\n"
                    j = i + 1
                    if_depth = 1
                    while j < len(lines) and if_depth > 0:
                        if_line = lines[j].strip()
                        if_args = if_line.split()
                        if if_args and if_args[0].lower() == "if":
                            if_depth += 1
                        elif if_args and if_args[0].lower() == "endif":
                            if_depth -= 1
                        
                        if if_depth > 0:
                            funcs[curfunc] += f"{if_line}\n"
                        j += 1
                    
                    funcs[curfunc] += "endif\n"
                    i = j - 1
                else:
                    condition = ' '.join(args[1:])
                    j = i + 1
                    if_depth = 1
                    code_block = []
                    
                    while j < len(lines) and if_depth > 0:
                        if_line = lines[j].strip()
                        if_args = if_line.split()
                        
                        if if_args and if_args[0].lower() == "if":
                            if_depth += 1
                        elif if_args and if_args[0].lower() == "endif":
                            if_depth -= 1
                            
                        if if_depth > 0 and if_depth == 1 and (not if_args or if_args[0].lower() != "endif"):
                            code_block.append(if_line)
                            
                        j += 1
                    
                    if evaluate_condition(condition):
                        for code_line in code_block:
                            code_args = code_line.split()
                            if not code_args:
                                continue
                                
                            if code_args[0].lower() == "printtext":
                                printtext(" ".join(code_args[1:]))
                            elif code_args[0].lower() == "enable":
                                enable(code_args[1].lower())
                            elif code_args[0].lower() == "allpt" or code_args[0].lower() == "allprinttext":
                                allPT(" ".join(code_args[1:]))
                            elif code_args[0].lower() == "var" or code_args[0].lower() == "variable":
                                addVar(code_args[1], " ".join(code_args[2:]))
                            elif code_args[0] == "__asm__:":
                                asm_block = []
                                k = code_block.index(code_line) + 1
                                while k < len(code_block) and code_block[k] != "__endasm__":
                                    asm_block.append(code_block[k])
                                    k += 1
                                addAsm(asm_block)
                    
                    i = j - 1
            elif args[0].lower() == "__func__":
                funcs[args[1]] = ""
                handledfuncs.append(args[1])
                handlingfunc = True
                curfunc = args[1]
            elif args[0].lower() == "__endfunc__":
                func = args[1]
                if func in handledfuncs:
                    handlingfunc = False
                    curfunc = ""
            elif args[0].lower() == "call" and not asming and not handlingfunc:
                func_name = args[1]
                if func_name in funcs:
                    func_lines = funcs[func_name].strip().split('\n')
                    
                    func_i = 0
                    while func_i < len(func_lines):
                        func_line = func_lines[func_i]
                        func_args = func_line.split()
                        
                        if not func_args:
                            func_i += 1
                            continue
                            
                        if func_args[0].lower() == "if":
                            condition = ' '.join(func_args[1:])
                            func_j = func_i + 1
                            if_depth = 1
                            func_code_block = []
                            
                            while func_j < len(func_lines) and if_depth > 0:
                                if_line = func_lines[func_j].strip()
                                if_args = if_line.split()
                                
                                if if_args and if_args[0].lower() == "if":
                                    if_depth += 1
                                elif if_args and if_args[0].lower() == "endif":
                                    if_depth -= 1
                                    
                                if if_depth > 0 and if_depth == 1 and (not if_args or if_args[0].lower() != "endif"):
                                    func_code_block.append(if_line)
                                    
                                func_j += 1
                            
                            if evaluate_condition(condition):
                                for code_line in func_code_block:
                                    code_args = code_line.split()
                                    if not code_args:
                                        continue
                                        
                                    if code_args[0].lower() == "printtext":
                                        printtext(" ".join(code_args[1:]))
                                    elif code_args[0].lower() == "enable":
                                        enable(code_args[1].lower())
                                    elif code_args[0].lower() == "allpt" or code_args[0].lower() == "allprinttext":
                                        allPT(" ".join(code_args[1:]))
                                    elif code_args[0].lower() == "var" or code_args[0].lower() == "variable":
                                        addVar(code_args[1], " ".join(code_args[2:]))
                            
                            func_i = func_j
                        elif func_args[0].lower() == "printtext":
                            printtext(" ".join(func_args[1:]))
                            func_i += 1
                        elif func_args[0].lower() == "enable":
                            enable(func_args[1].lower())
                            func_i += 1
                        elif func_args[0].lower() == "allpt" or func_args[0].lower() == "allprinttext":
                            allPT(" ".join(func_args[1:]))
                            func_i += 1
                        elif func_args[0].lower() == "var" or func_args[0].lower() == "variable":
                            addVar(func_args[1], " ".join(func_args[2:]))
                            func_i += 1
                        else:
                            func_i += 1
                else:
                    print(f"Error: Function '{func_name}' not found.")
            elif args[0] == "__asm__:" and not asming:
                asming = True
            elif args[0] == "__endAsm__" and asming:
                asming = False
                addAsm(asmCodes)
            elif asming:
                asmCodes.append(line)
            elif handlingfunc:
                funcs[curfunc] += f"{line}\n"
                
            i += 1

    print("When the compiler reaches to endall it stops the compiling and finishes it. If you weren't asked by location or any other, please add endall to the end of your code.")
    outputlines.clear()
    enabled.clear()

if __name__ == '__main__':
    executor(sys.argv[1])
