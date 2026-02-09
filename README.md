# Software Construction Projects

**Authors of the University of Zurich:**  
- Dhani Arora
- Muskan Chawla
- Noémie Hungerbühler

---

## Repository Overview

This repository contains **three software construction projects** implemented as part of the HS25 course.  
Each project focuses on different aspects of software design, implementation, and system-level programming.

---

## Projects Included

### 1. `.zvfs` Virtual Filesystem
A virtual filesystem implemented in **Python** and **Java**, supporting basic filesystem operations:

- Create a filesystem (`mkfs`)
- Add files (`addfs`)
- List files (`lsfs`)
- Read file content (`catfs`)
- Extract files to host system (`getfs`)
- Delete files (`rmfs`)
- Display filesystem info (`gifs`)
- Defragment filesystem (`dfrgfs`)

**Key Highlights:**
- Cross-language compatibility: Python and Java can read each other's `.zvfs` files
- Binary file handling with structured headers and file entries
- 64-byte aligned data storage and deletion flags

**Files & Folder:**  
`zvfs.py`, `zvfs.java`, `filesystem1.zvfs`, `filesystem2.zvfs`

---

### 2. Little German Language (LGL) Interpreter
A Python interpreter for the **Little German Language (LGL)** that extends the classroom interpreter with additional features.  
LGL programs are represented as JSON-like lists and executed by the interpreter.

**Key Features:**
- Executes LGL programs with variables, arithmetic, boolean, comparison operations, loops, and sequences
- Supports arrays and sets with operations like element access, concatenation, insertion, merging, and size checking
- Implements functional programming elements: `map`, `reduce`, and `filter`
- Includes a visual tracing system for function calls, showing hierarchy and execution duration
- Enhanced interpreter output for clearer terminal results

**Files & Folder:**  
`interpreter.py`, `extensions.lgl`, `data_structures.lgl`, `functional.lgl`, `tracing.lgl`, `repository.md`

--- 

### 3. `SmartHouse` Home Automation System
A smart home simulation implemented in **Python**, supporting device management, automation rules, and status monitoring:

- Add devices (`add_device`)
- Remove devices (`remove_device`)
- List all devices (`list_devices`)
- Read device status (`status_device`)
- Execute automation rules (`run_rule`)
- Schedule tasks (`schedule_task`)
- Display system information (`system_info`)

**Key Highlights:**
- Simulates a variety of smart devices: lights, thermostats, sensors, cameras
- Supports automation rules like "turn on lights if motion detected" or "set thermostat at 22°C at 7:00 AM"
- Provides both real-time status updates and historical logs
- Designed with modularity in mind: Python classes for each device type
- Includes examples for adding devices, executing rules, and checking status

**Files & Folder:**  
`smarthouse.py`, `test_smart_house.py`
