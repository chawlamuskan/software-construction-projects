# file for interpreter of little german language

# 1 True , 0 False 

import sys
import json
import time     # for tracing

TRACE = "--trace" in sys.argv
call_stack = []  # store current active function calls
trace_tree = []  # store the tree of completed calls

env = dict()      # global dict to keep track of defined variables   - but using envs stack to allow local variables inside functions                   

def do_set(args,envs):                          # sets a variable to a value - ["set", "x", 5] - create variable x and set to value 5 
    assert len(args) == 2                       # must have 2 arguemnts: name and value 
    assert isinstance(args[0],str)              # first argument must be a string
    var_name = args[0]                          # extract variable name from args
    var_value = do(args[1],envs)                # evaluate right hand side (second argument)            
    env_set(var_name,var_value,envs)            # store it in the envs 
    return var_value

def env_set(name,value,envs):                   # store a variable in the current environment - last one in stack 
    assert isinstance(name,str)                 # envs = [ {"a": 1}, {"b": 2} ] env_set("c", 3, envs) After this: envs = [ {"a": 1}, {"b": 2, "c": 3} ]
    envs[-1][name] = value                      # put in most recent scope 
    
def do_get(args,envs):                          # getting a value - ["get", "x"] - look up value of var x and return it 
    assert len(args) == 1                       # only var name 
    assert isinstance(args[0],str)
    var_name = args[0]                          # extract variable name
    return env_get(var_name,envs)               # look up in envoíronment 
    #assert args[0] in env, f"Unknown variable {args[0]}"
    #return env[args[0]]

def env_get(name,envs):                         # search for variable in ALL environment - start from most recent envs (top of stack) and move outward
    assert isinstance(name,str)                 # envs = [ {"x": 10},# global. {"y": 5, "x": 99}# local (top of stack)]     env_get("x", envs)  -> 99    env_get("y", envs)  -> 5
    # envs = [{"same":["func",...]},{"num":3}]
    # we do dynamic scoping
    for env in reversed(envs):                  # check from recent to oldest
        if name in env:
            return env[name]
    assert False, f"Unknown variable {name}"    # variable not found anywhere

def do_seq(args,env):                           # executes multiple operations in right order - if i first set a var x, then set another var y and add it to x - it will first add n then print y 
    # ["addieren", 2, 3], ["addieren", 4, 5]
    for each_ops in args:                       # go through each operation in the list 
        res = do(each_ops,env)                  # evaluate each one by one 
    return res                                  # return last operation - in example above var y


#region ######################### Arithmethic Operations ##############################

def do_addieren(args,envs):          # add       # ["addieren", 2, 3]  -> 5
    assert len(args) == 2               # must have 2 arguments
    left = do(args[0],envs)             # evaluate left side
    right = do(args[1],envs)            # evaluate right side
    return left + right                 # return sum

def do_absolutwert(args,envs):        # abs      # ["absolutwert", -5]  -> 5
    assert len(args) == 1
    value = do(args[0],envs)
    if value >= 0:                      # if value non-negarive, return as is
        return value
    return -value

def do_subtrahieren(args,envs):      # sub       # ["subtrahieren", ["get","x"], 2]  # if x = 5 ->  3
    assert len(args) == 2
    left = do(args[0],envs)
    right = do(args[1],envs)
    return left - right             # return difference

def do_multiplizieren(args,envs):   # mult      # ["multiplizieren", 4, 5]  -> 20
    assert len(args) == 2 
    left = do(args[0],envs)
    right = do(args[1],envs)
    return left * right

def do_teilen(args,envs):           # div       # ["teilen", 10, 3]  -> 3
    assert len(args) == 2
    left = do(args[0],envs)
    right = do(args[1],envs)
    assert right != 0, "no division by 0"      # prevent division by 0
    return left // right            # as our interpreter supports all operations only with int the division should also return an int 

def do_potenzieren(args, envs):     # power     # ["potenzieren", 2, 3]  -> 8  (2^3)
    assert len(args) == 2
    base = do(args[0], envs)
    exponent = do(args[1], envs)
    return base ** exponent

def do_modulo(args,envs):           # modulo    # ["modulo", 10, 3]  -> 1 
    assert len(args) == 2
    dividend = do(args[0], envs)
    divisor = do(args[1], envs)
    return dividend % divisor 
    
#endregion


#region ######################### Comparison Operations ###############################

def do_kleiner(args,envs):              # less than: returns 1 if left < right, else 0
    assert len(args) == 2
    left = do(args[0],envs)
    right = do(args[1],envs)
    if left < right: return 1
    else: return 0

def do_groesser(args,envs):             # greater than: returns 1 if left > right, else 0
    assert len(args) == 2
    left = do(args[0],envs)
    right = do(args[1],envs)
    if left > right: return 1
    else: return 0

def do_kleiner_gleich(args, envs):      # less than or equal: return 1 if left <= right, else 0
    assert len(args) == 2
    left = do(args[0], envs)
    right = do(args[1], envs)
    return 1 if left <= right else 0

def do_groesser_gleich(args, envs):     # greater than or equal: return 1 if left >= right, else 0 
    assert len(args) == 2
    left = do(args[0], envs)
    right = do(args[1], envs)
    return 1 if left >= right else 0

def do_gleich(args, envs):              # equal: return 1 if True or 0 for False
    assert len(args) == 2
    left = do(args[0], envs)
    right = do(args[1], envs)
    return 1 if left == right else 0

def do_ungleich(args, envs):            # not equal, return 1 (True) if left not equal to right, else 0 (False) if left equal to right
    assert len(args) == 2
    left = do(args[0], envs)
    right = do(args[1], envs)
    return 1 if left != right else 0     #return 1 if left is not equal to right, else 0
    
#endregion


#region ######################### Boolean Operations ##################################

def do_und(args,envs):              # AND implemented with 1 and 1 = 1 else 0
    assert len(args) == 2
    left = do(args[0],envs)
    right = do(args[1],envs)
    if left == 1 and right == 1: return 1
    else: return 0

def do_oder(args, envs):            # OR implemented with 0 = 0, else 1 - because if both false in an OR then its false. otherwise true
    assert len(args) == 2
    left = do(args[0], envs)
    right = do(args[1], envs)
    if left == 0 and right == 0:
        return 0                    # 0 = "false"
    else:
        return 1                    # 1 = "true"

def do_not(args, envs):             # NOT implemented with 0 meaning false and 1 meaning true and then it gives the opposite back
    assert len(args) == 1
    value = do(args[0], envs)
    if value == 0:
        return 1                    # 1 = "true"
    else:   
        return 0                    # 0 = "false"

#endregion


#region ######################### do ... until loop ##################################

def do_wiederhole_bis(args, envs):
    assert len(args) == 2                  # must have 2 arguments
    body = args[0]                         # first arg in the loop body - what i want to repeat 
    condition = args[1]                    # second arg is the exit condition 

    while True:                            # start infinite loop 
        do(body, envs)                     # execute the loop body once 
        if do(condition, envs):            # check condition after each iteration
            break                          # if condition is True - stop loop 
    return None                            # loop doesn't return a value

# endregion


#region ######################### Array Operations ##################################

# initialize new array of fixed size filled with 0  -   ["set", "A", ["array", 4]]  # creates [0,0,0,0]
def do_array(args, envs):               # create new array of fixed size
    assert len(args) == 1               # must have 1 argument: size
    size = do(args[0], envs)
    assert isinstance(size, int) and size >= 0, "Array size must be a non-negative integer"
    return [0 for _ in range(size)]         # return new array filled with zeros

# get element in array at index     -   ["get_element", ["get", "A"], 1]  # gets element at index 1
def do_get_element(args, envs):         
    assert len(args) == 2                       # array and index , must have 2 arguments
    arr = do(args[0], envs)
    index = do(args[1], envs)
    assert isinstance(arr, list), "First argument must be an array"
    assert 0 <= index < len(arr), f"Index {index} out of bounds"
    return arr[index]                   # return element at specified index

# set element in array at index     -   ["set_element", ["get", "A"], 2, 10]  # sets A[2] = 10
def do_set_element(args, envs):
    assert len(args) == 3                       # array, index, value 
    arr = do(args[0], envs)
    index = do(args[1], envs)
    value = do(args[2], envs)
    assert isinstance(arr, list), "First argument must be an array"
    assert 0 <= index < len(arr), f"Index {index} out of bounds"
    arr[index] = value              # set element at specified index
    return arr                      #return modified array

# get size of array     -   ["array_size", ["get", "A"]] - [0,0,0,0] would be 4 
def do_array_size(args, envs):
    assert len(args) == 1                            # must have 1 argument
    arr = do(args[0], envs)
    assert isinstance(arr, list), "Argument must be an array"
    return len(arr)

# concatenate two arrays    -   ["concatenate", ["get", "A"], ["array", 2]]  # join A with a new [0,0]
def do_concatenate(args, envs):
    assert len(args) == 2               # must have 2 arguments: two arrays
    arr1 = do(args[0], envs)            # first array
    arr2 = do(args[1], envs)            # second array
    assert isinstance(arr1, list) and isinstance(arr2, list), "Both arguments must be arrays"
    return arr1 + arr2
#endregion


#region ######################### Set Operations ####################################

# create new empty set  -   ["set", "K", ["setnew"]]  # creates an empty set K {}
def do_setnew(args, envs):  
    assert len(args) == 0, "set() takes no arguments"       # must have no arguments
    return set()

# insert element into set -- insertion should only happen if element not already in set --> uniqueness nature of the set 
def do_insert(args, envs):      # ["insert", ["get", "K"], 1] - inserts 1 into K        ["insert", ["get", "K"], 2] - # inserts 2 into K         ["insert", ["get", "K"], 2]  # duplicate, ignored --> {1, 2}
    assert len(args) == 2                   # must have 2 arguments: set and value
    s = do(args[0], envs)                   # needs set and value
    value = do(args[1], envs)
    assert isinstance(s, set), "First argument must be a set"
    s.add(value)                            # add value to set (ignore duplicates)
    return s

# check if element exists in set    -   ["exists", ["get", "K"], 2]  # check if 2 exists in K output 1 True
def do_exists(args, envs):
    assert len(args) == 2
    s = do(args[0], envs)
    value = do(args[1], envs)
    assert isinstance(s, set), "First argument must be a set"
    return 1 if value in s else 0           #return 1 if value in set, else 0

# get size of set   -   ["set_size", ["get", "K"]] -- output w of K = {1, 2}
def do_set_size(args, envs):
    assert len(args) == 1
    s = do(args[0], envs)
    assert isinstance(s, set), "Argument must be a set"
    return len(s)

# merge two sets -- no duplicates   -   ["set", "M", ["merge", ["get", "K"], ["get", "L"]]]  # merge K={1,2} and L={2,20} --> {1, 2, 20}
def do_merge(args, envs):               
    assert len(args) == 2
    s1 = do(args[0], envs)
    s2 = do(args[1], envs)
    assert isinstance(s1, set) and isinstance(s2, set), "Both arguments must be sets"
    return s1.union(s2)                 #return merged set

#endregion


#region ######################### Functional Programming Elements ###################
# used the version where func is passed by its name, they are defined beforehand in the programm - use "set" to define func

def do_map(args, envs):
    assert len(args) == 2                           # array and func name 
    input_array = do(args[0], envs)                 # evaluate first arg should produce array 
    func_name = args[1]  # "sq_func"
    func_def = env_get(func_name, envs) # get the function from the environment: ['func', ['n'], ['multiplizieren', 'n', 'n']]

    assert isinstance(input_array, list), "First argument must be an array"
    assert isinstance(func_def, list) and func_def[0] == "func", "Second argument must be a function"

    params = func_def[1]                            # get the parameter list of the func 
    assert len(params) == 1, f"Function {func_name} must take exactly one argument"

    output_array = []
    for val in input_array:                          
        # create a LGL function call expression for each element
        call_expr = ["call", func_name, val]
        # evaluate it using the interpreter
        result = do(call_expr, envs)
        output_array.append(result)
    
    return output_array


def do_reduce(args, envs):
    assert len(args) == 2                           # array and function name
    input_array = do(args[0], envs)
    func_name = args[1]
    func_def = env_get(func_name, envs) # get the func from the envs: ["func", ["a", "b"] ["addieren", "a", "b"]]

    assert isinstance(input_array, list), "First argument must be array"
    assert isinstance(func_def, list) and func_def[0] == "func", "Second argument must be function"

    params = func_def[1]
    assert len(params) == 2, f"Function {func_name} must take two arguments"
    assert len(input_array) > 0, "Cannot reduce an empty array"

    output_array = input_array
    while len(output_array) > 1:        # loop until array is reduced to a single value 
        val1 = output_array[0]
        val2 = output_array[1]
        # create LGL function call expression for each element
        call_expr = ["call", func_name, val1, val2]
        # evalute using interpreter 
        res = do(call_expr, envs)

        if len(output_array) > 2:           # replace the first two elements with the result of res 
            end = output_array[2:]
            output_array = [res] + end      # if more elements exists still, combine it with the rest
        else:
            output_array = [res]            # if only two elements exist, output one res 

    return output_array[0]


def do_filter(args, envs):                          # filter operation: keep elements where function returns true
    assert len(args) == 2                           # must have 2 arguments
    input_array = do(args[0], envs)                 # first arg should be array 
    func_name = args[1]                             # name func
    func_def = env_get(func_name, envs)             # get function from environment

    assert isinstance(input_array, list), "First argument must be an array"
    assert isinstance(func_def, list) and func_def[0] == "func", "Second argument must be a function"

    params = func_def[1]                           
    assert len(params) == 1, f"Function {func_name} must take exactly one argument"

    output_array = []                       #initialize output array
    for val in input_array:
        call_expr = ["call", func_name, val]
        # evaluate using interpreter
        result = do(call_expr, envs)
        # if function returns 1 (true), keep the element
        if result == 1:
            output_array.append(val)
    
    return output_array                 #return filtered array
    

#endregion


#region ######################### Tracing System ####################################
# for every user defined function we store the name, duration of the call and it's children 

def start_call(func_name):
    node = {
        "name": func_name,
        "start": time.time(),
        "duration": 0,
        "children": []
    }
    if call_stack: # if stack not empty
        # add as child to current top of stack
        call_stack[-1]["children"].append(node)
    else: # stack is empty -> node is top-level function
        trace_tree.append(node)
    call_stack.append(node)


def end_call(): # function has ended, update duration time of function call
    node = call_stack.pop()
    node["duration"] = int((time.time() - node["start"]) * 1000)  # ms


def print_trace(nodes, indent=""): # prints the trace tree to terminal
    for node in nodes:
        if "duration" in node:      # for all user defined functions
            print(f"{indent}+-- {node['name']} ({node['duration']}ms)")
        else:                       # for print 
            print(f"{indent}+-- {node['name']}")
        if node.get("children"):    # recursively fetch children 
            print_trace(node["children"], indent + "|   ")   

#endregion


# ["call",
#   "same", 3]
def do_call(args,envs):                         # call user defined func - ["call", "sq_func", 3] - If sq_func(n) = n*n,  returns 9
    assert len(args) >= 1
    assert isinstance(args[0], str)
    name_func = args[0]
    values = [do(a, envs) for a in args[1:]]

    func = env_get(name_func, envs)
    assert isinstance(func, list) and func[0] == "func"
    params = func[1]
    body = func[2]
    assert len(values) == len(params), f"You passed {len(values)} parameters instead of {len(params)}"

    local_env = dict()
    for index, param_name in enumerate(params):
        local_env[param_name] = values[index]
    envs.append(local_env)

    if TRACE:
        start_call(name_func)   # start tracing

    result = do(body, envs)     # run the func

    if TRACE:
        end_call()              # end tracing

    envs.pop()
    return result



def do_print(args, envs): # prints evaluated args to the console -    ["print", 1, ["addieren", 2, 3]] --> 1 5
    args = [do(a, envs) for a in args]
    print(*args)

    if TRACE:
        if call_stack:  # if call_stack not empty (there is a func on call stack), add print as a child of current function
            call_stack[-1]["children"].append({"name": "print", "children": []})
        else:
            trace_tree.append({"name": "print", "children": []}) # if call_stack empty add print as top-level node in trace_tree
    
    return None


def do_func(args, env): # user defined funtion - ["set", "sq_func", ["func", ["n"], ["multiplizieren", "n", "n"]]] -  creates  sq_func(n) = n * n
    assert len(args) == 2
    params = args[0]
    body = args[1]
    return ["func",params,body]



# dictionary matching: {"addieren": do_addieren, ...}
OPS = {
    name.replace("do_",""): func
    for (name,func) in globals().items()
    if name.startswith("do_")
}
# more detailed way of coding the above block:
# OPS_EASY = {}
# for (name,func) in globals().items():
#     if name.startswith("do_"): #do_addieren
#         operation_name = name.replace("do_","") # addieren
#         OPS_EASY[operation_name] = func # "addieren" : do_addieren

def do(program, envs):
    # if it's an integer
    if isinstance(program, int):
        return program

    # if it's a string (variable or function name)
    if isinstance(program, str):
        try:                                # try to fetch from environment if it exists
            return env_get(program, envs)
        except AssertionError:              # if not in env, treat as literal string
            return program
    
    # if it's an operation
    assert program[0] in OPS, f"Unkown operation {program[0]}"
    func = OPS[program[0]]                                           # do(["addieren", 2, 3], envs)  
    return func(program[1:], envs)                                   # calls do_addieren([2,3], envs)  --> 5 


def main():
    # sys.argv[0] is the script name
    # sys.argv[1:] is everything after that (user-provided arguments)

    # find the filename(s) in argv and filter out the --trace flag
    args = [arg for arg in sys.argv[1:] if arg != "--trace"]

    # checks if the user didn’t provide a filename (or only gave --trace)
    # if no filename is given, print a usage message and exits main early
    if not args:
        print("Usage: python ass2.py [--trace] <filename>")
        return

    filename = args[0]  # the first non-flag argument
    with open(filename, 'r') as f:
        program = json.load(f)
        envs = [dict()]

        if TRACE:       # make sure we can start tracing from empty tree and stack
            trace_tree.clear()
            call_stack.clear()

        print("=== Starting Program ===")
        for idx, expr in enumerate(program):
            print(f"\n>>> Step {idx+1}: {expr}")
            result = do(expr, envs)
            if result is not None:
                print(f"Result: {result}")
        print("\n=== Program Finished ===")
        # uncomment the next line to see what is in the environment
        #pprint.pprint(envs)

        if TRACE:
            print("\n=== Function Call Trace ===")
            print_trace(trace_tree)


if __name__ == '__main__':
    main()