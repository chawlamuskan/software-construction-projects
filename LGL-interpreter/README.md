# HS25_SoCo-group_020-a2 

**By:**  
**Dhani Arora – 24-730-590**  
**Muskan Chawla – 24-730-509**  
**Noémie Hungerbühler – 23-927-684**

---

## Overview

This repository contains our Little German Language interpreter project. We started with the **classroom version of `interpreter.py`** and extended it to implement all the assignment requirements. 
The main goal of this assignment was to extend a basic interpreter provided in class, by implementing additional operations and features. The interpreter executes **LGL programs**, which are represented as JSON-like lists.   

---

## Repository Structure

- `interpreter.py` – the main interpreter code, combining classroom code and our assignment implementations
- `extensions.lgl` – LGL program showcasing arithmetic, boolean, comparison operations and the do ... until loop
- `data structures.lgl` – LGL program showcasing arrays and sets (step 2)  
- `functional.lgl` – LGL program showcasing map, reduce, and filter (step 3)  
- `tracing.lgl` – LGL program showcasing tracing (step 4)  
- `repository.md` – Contains the link to our GitLab repository  

---

## In Class Code (Base)

The base code provided in class includes:

- **Variables**  
  - `set` assigns a value to a variable  
  - `get` retrieves a variable's value  
  - Uses an **environment stack** (`envs`) for dynamic scoping  

- **Basic Arithmetic**  
  - `addieren` (addition)  
  - `subtrahieren` (subtraction)  
  - `absolutewert` (absolute value)  

- **Functions**  
  - `func` defines a function  
  - `call` calls a function with parameters  

- **Sequences & Printing**  
  - `seq` executes multiple operations in order  
  - `print` displays output  

- **Interpreter Core**  
  - `do()` executes operations  
  - `OPS` dictionary that maps operation names to functions  
  - `main()` runs a LGL program  

- **Changes**
  - We modified the `main()` function to display intermediate steps of the interpreter. This makes the terminal output clearer and helps to better understand which function returns which value
  - We also modified the `do()` function such that it does not only return integers and operations but also strings. The string can either be a function name or a variable which will be fetched from the environment if it exists but it can also be just a string and then it will be returned as such (in the assertion block).  

**Example classroom LGL code:**

```lgl
["set", "x", 5]
["addieren", 2, 3]
["seq", ["set", "x", 5], ["print", "x"]]
["func", ["n"], ["addieren", "n", 1]]
["call", "my_func", 3]
```
--- 

### Features Added to the Class Code

---
## Step 01 
## How Operations Work in Our Interpreter

In our LGL interpreter, **all operations follow a similar structure**:

1. Each operation is a **Python function** that takes one or more arguments 
2. Arguments can be **values** (like integers) or **references to variables** (retrieved using `get`)
3. The `do()` function executes each operation by looking it up in the `OPS` dictionary and calling the corresponding function
4. Most operations **return a value**, which can be stored in a variable, used in a loop, or passed to another function 

Because of this shared structure, adding new operations is straightforward: we define Python functions and register them in `OPS`

---

## 1. Arithmetic Operations

These operations handle **basic calculations**:

- `multiplizieren(a, b)` – Multiplies `a` and `b` 
- `teilen(a, b)` – Performs integer division of `a` by `b`  
- `potenzieren(a, b)` – Raises `a` to the power of `b`  
- `modulo(a, b)` – Returns the remainder of `a` divided by `b`  

**Example usage from `extensions.lgl`:**
```lgl
["addieren", 2, 3]         # Returns 5
["multiplizieren", 4, 5]    # Returns 20
["potenzieren", 2, 3]       # Returns 8
```

--- 

## 2. Comparison Operations

These operations evaluate **relationships between two values**:

- `kleiner(a, b)` – Returns `1` if `a < b`, else `0` 
- `groesser(a, b)` – Returns `1` if `a > b`, else `0` 
- `kleiner_gleich(a, b)` – Returns `1` if `a <= b`, else `0` 
- `groesser_gleich(a, b)` – Returns `1` if `a >= b`, else `0` 
- `gleich(a, b)` – Returns `1` if `a == b`, else `0`
- `ungleich(a, b)` – Returns `1` if `a != b`, else `0`  

**Example usage from `extensions.lgl`:**
```lgl
["kleiner", 2, 3]       # Returns 1 (true)
["ungleich", 5, 5]      # Returns 0 (false)
["gleich", ["addieren", 2, 3], 5]  # Returns 1 (true)
```

---

## 3. Boolean Operations

These operations work with **logical values**, where `1` represents true and `0` represents false:

- `und(a, b)` – Returns `1` if **both** `a` and `b` are `1`, otherwise returns `0`.  
- `oder(a, b)` – Returns `1` if **at least one** of `a` or `b` is `1`, otherwise returns `0`.  
- `not(a)` – Returns `1` if `a` is `0`, and returns `0` if `a` is `1`.  

**Example usage from `extensions.lgl`:**
```lgl
["und", 1, 0]           # Returns 0
["oder", 0, 1]          # Returns 1
["not", 0]              # Returns 1
["und", ["gleich", 2, 2], ["kleiner", 3, 5]]  # Returns 1
```

---

**Implementation note for all Operations:** Each function retrieves its arguments using `do()`, so that variables and nested operations are correctly evaluated, and then performs the calculation.

---

## 4. Loops

The `wiederhole_bis` operation implements a **do ... until loop**, which repeatedly executes a sequence of operations until a specified condition becomes true.

- `wiederhole_bis(sequence, condition)`  
  - `sequence` – A list of operations (`seq`) to execute in each iteration  
  - `condition` – A comparison or boolean expression that stops the loop when it evaluates to `1` (true)

**Implementation note:**  
- The loop executes the `sequence` **once per iteration**
- After each iteration, the interpreter evaluates the `condition` using `do()` 
- If the condition returns `1`, the loop stops, otherwise, it continues 
- This allows loops to work with **variables, arithmetic, comparisons, and nested operations**

**Algorithms Implemented in `extensions.lgl`**
- Algo 2.29 - Even or Odd 
  - checks if a given number is even or odd, returns 1 if odd, 0 if even
- Algo 2.31 - Sum up to N
  - computes the sum of all numbers from 1 up to `n`
- Algo Factorial 
  - self-designed example to showcase the loop, return `n!`
- Algo Countdown
  - prints to the terminal the countdown from a given number until one 

**Example usage from `extensions.lgl`:**
```lgl
["set", "i", 0]
["wiederhole_bis",
    ["seq",
        ["set", "i", ["addieren", ["get", "i"], 1]],
        ["print", ["get", "i"]]
    ],
    ["gleich", ["get", "i"], 5]
]                                                   # print 5 4 3 2 1 
```

---

## Step 02 

## Overview
In Step 2, we extended the LGL interpreter to support **arrays** and **sets**, including operations such as getting and setting elements, checking size, concatenation, and merging.  
All operations follow the standard LGL pattern: each operation is a Python function, arguments are evaluated via `do()`, and results can be stored, printed, or passed to other operations.

---

## 1. Array Operations

### Operations implemented:

| Operation | Description |
|-----------|-------------|
| `array(size)` | Creates a new array of the given size, initialized with zeros. Example: `["array", 4] --> [0,0,0,0]` |
| `get_element(array, index)` | Returns the element at the specified index. Example: `["get_element", ["get", "A"], 1] --> 20` |
| `set_element(array, index, value)` | Sets the element at `index` to `value`. Example: `["set_element", ["get", "A"], 2, 30]` |
| `array_size(array)` | Returns the length of the array. Example: `["array_size", ["get", "A"]] --> 4` |
| `concatenate(array1, array2)` | Joins two arrays into a single array. Example: `["concatenate", ["get", "A"], ["get", "B"]] --> [1,2,3,4,10,11]` |

### Implementation notes:
- Arrays are represented as Python lists
- Indexes are checked for bounds to avoid errors.
- `do()` is used to evaluate arguments so that variable references and nested expressions work without problems 
- Concatenation creates a new array and the original arrays remain unchanged

### Checks in `data_structures.lgl`
- Array:
  - verifing that initialization fills all position with 0
  - setting all values correctly
  - getting element returns individual items
  - counting lenght of array
  - concatennating arrays 
  - concatennating with empty array

### Example LGL code from `data_structures.lgl`:
```lgl
["set", "A", ["array", 4]]
["set_element", ["get", "A"], 0, 10]
["set_element", ["get", "A"], 1, 20]
["print", ["get_element", ["get", "A"], 1]]   # prints 20

["set", "B", ["array", 2]]
["set_element", ["get", "B"], 0, 99]
["set", "C", ["concatenate", ["get", "A"], ["get", "B"]]]
["print", ["C"]]                               # prints [10, 20, 0, 0, 99, 0]
```

---

## 2. Set Operations

### Operations implemented:

| Operation | Description |
|-----------|-------------|
| `setnew()` | Creates a new empty set. Example: `["setnew"] --> {}` |
| `insert(set, value)` | Adds `value` to the set if not already present. Example: `["insert", ["get", "K"], 2]` |
| `exists(set, value)` | Returns 1 if `value` is in the set, else 0. Example: `["exists", ["get", "K"], 3] --> 1` |
| `set_size(set)` | Returns the number of elements in the set. Example: `["set_size", ["get", "K"]] --> 2` |
| `merge(set1, set2)` | Combines two sets into a new set without duplicates. Example: `["merge", ["get", "K"], ["get", "L"]] --> {1,2,3,20}` |

### Implementation notes:
- Sets are represented using Python `set()`
- `insert` ignores duplicate values, preserving the uniqueness property
- `merge` uses `union()` to combine two sets while eliminating duplicates
- `do()` evaluates all arguments, allowing nested expressions or variable references

### Checks in `data_structures.lgl`
- Set:
  - creating empty set
  - inserting unique values 
  - ignoring duplicates 
  - merging sets and keeping unqiue values only
  - merging with empty set 
  - adding new element and inserting -> ignore duplicates 

### Example LGL code from `data_structures.lgl`:
```lgl
["set", "K", ["setnew"]]
["insert", ["get", "K"], 1]
["insert", ["get", "K"], 2]
["insert", ["get", "K"], 2]                 # duplicate ignored
["print", ["set_size", ["get", "K"]]]       # prints 2

["set", "L", ["setnew"]]
["insert", ["get", "L"], 20]
["set", "M", ["merge", ["get", "K"], ["get", "L"]]]
["print", ["exists", ["get", "M"], 2]]      # prints 1
["print", ["exists", ["get", "M"], 99]]     # prints 0
```

---

## Step 03

## Overview
In Step 03, we extended the LGL interpreter to support **functional programming elements**: `map`, `reduce`, and `filter`.  
These operations allow us to perform transformations on arrays using **user-defined functions**. 

All operations follow the standard LGL evaluation pattern:
- Arguments are evaluated using `do()`
- Results can be stored in variables, printed, or used in nested expressions

---

## 1. Map

### Purpose
`map` applies a user-defined function to **each element** of an array, producing a new array where each element is the result of the function applied to the corresponding element of the original array

### Syntax
```lgl
["map", array, function_name]
```

### Implementation 
- `map` requires an array and a user-defined function (defined with func)
- The function must take exactly one argument
- The original array remains unchanged and a new array with the mapped results is returned
- Arguments are evaluated using `do()` to allow nested expressions or variable references

### Checks in `functional.lgl`
- `sq_func`: squares every element in the array 
- `times_ten_func`: multiplies every element with 10 

---

## 2. Reduce 

### Purpose 
`reduce` accepts an array and a function name, and produces a single value by constantly applying the function to two elements of an array, effectively reducing the size of the array by 1 in every iteration until we are left with a single element

### Syntax 
```lgl
["reduce", array, function_name]
```

### Implementation
- `reduce` requires an array and a user-defined function
- The function must take exactly two arguments for pairwise reduction 
- The operation starts with the first element and iteratively applies the function to the current result and the next element
- The original array remains unchanged

### Checks in `functional.lgl`
- `add_func`: sum of all the values in the array
- `prod_func`: product of all values in the array 

---

## 3. Filter

### Purpose
`filter` selects elements from an array **based on a condition** defined by a user-defined function.  
Only elements for which the function returns `1` (true) are kept in the resulting array.

### Syntax
```lgl
["filter", array, function_name]
```

### Implementation
- `filter` requires an array and a user-defined function
- The function must take exactly one argument and return 0 or 1 
- The interpreter uses `do()` to evaluate both the array and each function call dynamically
- If the result is 1, the element is added to the output array, Otherwise it is ignored
- The original array remains unchanged

### Checks in `functional.lgl`
- `larger_ten_func`: new array with elements > 10
- `greater_two_func`: new array with elements > 2
- `smaller_ten_func`: new array with elements < 10

### Example LGL code from `functional.lgl`:
```lgl
["print", ["map", ["get", "A"], "sq_func"]],
    ["print", ["map", ["get", "A"], "times_ten_func"]],

    ["print", ["reduce", ["get", "A"], "add_func"]],
    ["print", ["reduce", ["get", "A"], "prod_func"]],

    ["print", ["filter", ["get", "A"], "larger_ten_func"]],
    ["print", ["filter", ["get", "A"], "greater_two_func"]],
    ["print", ["filter", ["get", "A"], "smaller_ten_func"]]
```

---

## Step 04

### Overview 
In Step 04, we extended our Little German Language interpreter with a **visual tracing system** that helps us see how functions are called and executed inside an LGL program.
When the interpreter is run with the command-line flag `--trace`, it records every user-defined function call, how long each call takes, and which other functions it calls.
At the end of program execution, the interpreter prints a tree-style visualization of all function calls, showing their hierarchy and execution durations.
This is helpful for debugging.

### Purpose 
It shows which functions call which others and measures their runtime in milliseconds.
- **Basic idea**
  - Every time a user-defined `func` is called, the interpreter records its `name` and `start time` and adds it to a call stack
  - When the function finishes, its `end time` is recorded and the `duration` is calculated and the func is added to the `tree`
  - After the program finishes, the interpreter prints the entire call tree with indentation and timing

### Command - line Usage 
```
# Normal execution
python interpreter.py tracing.lgl

# Tracing mode
python interpreter.py --trace tracing.lgl
```
When using `--trace`, the interpreter will print both the program's output and a function call trace at the end

### Implementation 

#### Global Variables:

| Variable | Purpose |
|-----------|-------------|
| `TRACE` | This is a Boolean flag, which is `True`if `--trace` is passed on the command line |
| `call_stack` | Keeps track of the currently active and nested function calls |
| `trace_tree` | Stores the full hierarchy of all calls for the output later |


#### New Funtions:

| Function | Description |
|-----------|-------------|
| `start_call(func_name)` | Starts timing a function call, records its name and start time, and adds it to the current call stack |
| `end_call()` | Ends the most recent call, computes its duration, and removes it from the stack |
| `print_trace(nodes, indent="")` | Recursively prints the call hierarchy with indentation and durations (tree visualization) |

```
# each node is a py dict and corresponds to one func call
{
  "name": "function_name",
  "start": 1731263123.532,
  "duration": 53,
  "children": [ ... nested calls ... ]    # if a func calls another, its children 
}
```

#### Modification of exsiting code:

- `main()`:
  - Clears previous traces at the beginning
  - Prints the call tree at the end if tracing is enabled
- `do_call()`:
  - Wraps the call body with start_call() and end_call() so every user-defined call is timed
- `do_print()`:
  - Adds print operations to the trace tree (so they appear as leaves)


#### Example LGL code from `tracing.lgl`:
```
[
    ["seq",

        ["set", "get_cube_power", ["func", ["n"],
            ["seq",
                ["multiplizieren", "n", ["multiplizieren", "n", "n"]]
            ]
        ]],

        ["set", "add_cubes", ["func", ["a", "b"],
            ["seq",
                ["addieren",
                    ["call", "get_cube_power", "a"],
                    ["call", "get_cube_power", "b"]
                ]
            ]
        ]],

        ["set", "res", ["call", "add_cubes", 10, 12]],
        ["print", ["get", "res"]]
    ]
]
```

---

## Use of AI

- we used AI (ChatGpt) to figure out how to create tables in the Readme.md file.
Prompt: what is the syntax if I want to create a table in a readme.md file?
- we used ChatGpt to ask how we can modify our terminal output so it is better readable
Prompt: i have built my own interpreter.py for my own little German language, a .lgl file. the problem I am facing is that the output of my operations is very unclear in my terminal so I don't know which operation has which output. is there a way to change my main function in a way that I can see the operation as well as the result ? Give me a hint in words how i can achieve it

