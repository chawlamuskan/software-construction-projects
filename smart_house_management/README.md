# HS25_SoCo-group_020-a1  

**By:**  
**Dhani Arora – 24-730-590**  
**Muskan Chawla – 24-730-509**  
**Noémie Hungerbuehler – 23-927-684**

## Project Overview

This project is a simplified simulation of a smart house. It shows different smart devices such as lights, thermostats and cameras, using *Python dictionaries only* and without using the built-in `class` keyword.  

The goal is to build a fully object-oriented system manually using only dictionaries and functions to show class behavior, inheritance, and polymorphism.

---

## Files and Structure

- `smart_house.py` – main source file containing all classes and logic
- `README.md` – this file, with documentation, decisions and testing
- `test_smart_house.py` - tests for smart_house.py
- `repository.md` - contains link to the GitLab repository of our group 

---

## Design Decisions

We built a mini object system by implementing:

### 1. Custom Object System
We use three key helper functions:

#### `make(cls, *args)`
Creates a new object from a class dictionary by calling its `_new` method.

#### `call(obj, method_name, *args, **kwargs)`
Finds and calls a method from the class or its parents, similar to calling `self.method()` by using the python class. 

#### `find(cls, method_name)`
Recursively searches the inheritance chain to find the requested method and it supports single and multiple inheritance.

This system lets us mimic class inheritance and instance creation. 

---

## Classes

### `Device` (Parent Class)
This is the base class for all smart devices.  
Attributes:
- `name`
- `location`
- `basepower`
- `status` (on/off)

Methods:
- `toggle_status` – switch between "on" and "off"
- `get_power_consumption` *(abstract)*
- `describe_device` *(abstract)*

We raise `NotImplementedError` for abstract methods to ensure subclasses implement them.

---

### `Connectable` (Parent Class)
The second base class for devices that can connect to a server like the thermostats and cameras.  
Attributes:
- `connected` (boolean)
- `ip` (IP address string)

Methods:
- `connect(ip)` – marks as connected and saves the IP
- `disconnect()` – marks as disconnected, but retains latest IP
- `is_connected()` – returns the connection status

---

## Subclasses

### `Light` (inherits from `Device`)
Adds:
- `brightness` (0–100) in percentage

Implements:
- `get_power_consumption` = `(basepower * brightness) / 100` (rounded)
- `describe_device` – inherits from Device but includes brightness in the description 

---

### `Thermostat` (inherits from `Device`, `Connectable`)
Adds:
- `room_temperature` - indicates the current room temperature 
- `target_temperature` - indicates the target temperature of the Thermostat

Implements:
- `get_power_consumption` = `basepower * abs(target - room)`
- `describe_device` – inherits via multiple inheritance from `Device` and `Connectable` and includes temperature and connection info
- `set_target_temperature(temp)` – update target temperature

Multiple inheritance is handled by searching both `Device` and `Connectable`.

---

### `Camera` (inherits from `Device`, `Connectable`)
Adds:
- `resolution_factor` (numeric)

Implements:
- `get_power_consumption` = `basepower * resolution_factor`
- `describe_device` – inherits via multiple inheritance from `Device` and `Connectable` and includes resolution quality (low, medium, high) and connection status

Multiple inheritance is handled by searching both `Device` and `Connectable`.

---

## Testing and Instances

We created test instances of all device types to ensure functionality:

```python
L1 = make(Light, "Bedtable Light", "Bedroom", 250, "on", 50)
T1 = make(Thermostat, "Towel Thermostat", "Bathroom", 1200, "on", 18, 24)
C1 = make(Camera, "RGB Camera", "Living Room", 500, "on", 12)

```

---

# Smart House Management

A class that prints the description and the power consumption of all smart device classes
that have been instantiated earlier in the program. 

### `Smart House Management` (Parent Class)
Attributes:
- `search_type` (Device)
- `search_room` (string)

Methods:
- `calculate_total_power_consumption(search_type, search_room)` – calculates power consumption of all devices if filter is None and else filters by room or type or both
- `get_all_device_description(search_type, search_room)` – returns descriptions of devices filtered by search_type and search_room by calling the device_description function for each device
- `get_all_connected_devices(ip)` – only works for Camera and Thermostat, should return a tuple of power consumption and description for all devices if ip is None and for all devices connected to the ip (if specifically given)

---

### Smart House Management Instances

We created instances of devices and an instance of Smart House Management to test the functionalites:

```python
L1 = make(Light, "Bedtable Light", "Bedroom", 250, "on", 50)
L2 = make(Light, "Bathroom Light", "Bathroom", 300, "on", 80)
L3 = make(Light, "Living Room Light", "Living Room", 400, "on", 100)
T1 = make(Thermostat, "Towel Thermostat", "Bathroom", 1200, "on", 18, 24)
T2 = make(Thermostat, "Bedroom Thermostat", "Bedroom", 3100, "on", 19, 21)         # room should be warmer
T3 = make(Thermostat, "Living Room Thermostat", "Living Room", 5800, "on", 24, 21)  # room should be colder
C1 = make(Camera, "New RGB Camera", "Living Room", 500, "on", 12)                   # high resolution
C2 = make(Camera, "Surveilance Camera", "Front Door", 200, "on", 2)                 # low resolution
C3 = make(Camera, "Bedroom Camera", "Bedroom", 200, "on", 7)                       # medium resolution
SHM = make(SmartHouseManagement)
```

---

# Testing of our Smart House Management System 

A file containing comprehensive test functions to verify that the smart house management system behaves as expected. 

## Testing of Device

### `test_device_attributes`: To verify correct initialization of device attributes and ensure that invalid input is properly rejected.
- Devices can be created with valid attributes:  
  `name` (non-empty string), `location` (string), `basepower` (non-negative number), and default `status = "off"`
- `status` can be explicitly set to `"on"`
- Creating a device with an empty name raises `ValueError`

### `test_valid_status`: To test that the device status can be explicitly set during creation and is correctly reported via the `device_status()` function.
- Devices correctly initialize with status `"on"` or `"off"`
- `device_status()` returns the expected state

### `test_device_name_uniqueness`: To enforce unique names. Unique names are required to avoid conflicts in the global device registry (`AllDevices`).
- Duplicate device name raises `ValueError`

### `test_device_wrong_name_type`: To validate the input types for thee device name. 
- Creating a device with a non-string name (e.g., an integer) raises a `TypeError`

### `test_device_negative_basepower`: To prevent that invalid power values are accepted. Negative poewr consumption doesn't make sense 
- Creating a device with negative `basepower` raises a `ValueError`

### `test_device_toggle_status`: To verify that the `toggle_status()` method correctly switches device status between `"on"` and `"off"`. This test ensures consistent behavior across all device types and validates inheritance.
- Toggling works on:
  - Base `Device`
  - `Light`
  - `Thermostat`
  - `Camera`
- Status changes as expected when toggled repeatedly

### `Inheritance`: These tests also ensure that subclasses (`Light`, `Thermostat`, and `Camera`) correctly inherit shared behavior from the `Device` class. 
- Name and basepower validation
- Global uniqueness of names
- Toggle functionality
- Status tracking

---

## Testing of Connectable

### `test_connectable_initial_state`: To verify the default state of a newly created `Connectable` object.
- Device starts disconnected (`connected == False`)
- IP address is `None`

### `test_connectable_connect`: To ensure that calling `connect(ip)` sets the correct state.
- `connected`becomes `True`
- IP address is updated correctly

### `test_connectable_disconnect`: To check that the device can disconnect properly.
- `connected` becomes `False`
- IP address is remembered by the device as the last assigned IP

### `test_connectable_reconnect`: To verify reconnection behavior.
- Device can be connected again after disconnecting
- New IP address replaces the old one
- `connected` is updated correctly

### `test_connectable_is_connected_method`: To validate the `is_connected()` method is correct.
- Returns `False` when not connected
- Returns `True` after a successful connection

### `test_connectable_disconnect_without_connect`: To test disconnecting a device that has never been connected (edge case).
- No errors are thrown
- `connected` remains `False`
- IP remains `None`

### `test_connectable_connect_twice`: To check system stability when connecting multiple times with the same IP.
- Reconnecting to the same IP does not cause errors
- Connection state remains valid
- IP remains unchanged

### `test_connectable_on_light`: To ensure that devices like `Light`, which should not support networking, behave correctly.
- Calling `connect`, `disconnect`, or `is_connected` on a `Light` raises a `NotImplementedError`
- Ensures correct use of inheritance 

### `test_connectable_invalid_ip`: To verify error handling when invalid IPs are passed.
- Passing an invalid data type raises a `TypeError`
Passing an incorrectly formatted string (e.g. `"a.b.c.d"`) raises a `ValueError`
- Confirms that the system validates IP addresses properly before connecting

---

## Testing of Light

### `test_light_new`: To ensure that `Light` objects can be correctly created and validated during instantiation.
- Creation with valid parameters sets all attributes correctly
- Duplicate names raise a `ValueError`
- Invalid data types for attributes (example, integer for location) raise `TypeError`
- Invalid values (example, negative basepower or brightness, invalid status string) raise `ValueError`

### `test_light_power_consumption`: To verify that power consumption is calculated correctly based on status and brightness.

- When light is `on`, power is calculated as `basepower * brightness / 100`, rounded
- When light is `off`, power consumption is `0`, regardless of brightness
- Brightness of `0` is treated as off (power = 0)

### `test_light_describe_device`: To check the correctness of the `describe_device()` method output.
- Returns a string in the correct format including the name, location, status (`on`/`off`), and brightness percentage

### `Toggle Status`: This functionality is inherited from the `Device` class and doesn't require separate testing here.
- Toggling changes the status between `on` and `off`
- Power consumption updates accordingly

### `No Brightness Setter`:
- According to the exercise specification, there is **no method to change brightness after creation**

---

## Testing of Thermostat 

### `test_thermostat_new`: To verify that Thermostat objects are created correctly with valid attributes and handle invalid inputs properly.
- Valid creation assigns correct attributes including `name`, `location`, `basepower`, `status`, `room_temperature`, and `target_temperature`
- Duplicate or invalid attribute values (example, temperatures outside 0-40°C) raise `ValueError`
- Thermostats are registered in global `AllDevices` and `AllConnectables` dictionaries upon creation

### `test_thermostat_set_target_temperature`: To validate the `set_target_temperature()` method.
- Accepts target temperatures within 0-40°C
- Raises `ValueError` when target temperatures are out of bounds (<0 or >40)

### `test_thermostat_attributes`: To ensure all thermostat attributes are correctly set and inherited
- Inherits from `Device` and `Connectable`, having expected attributes such as `status` and connection status
- Attributes like `room_temperature` and `target_temperature` are correctly assigned

### `test_thermostat_get_power_consumption`: To confirm accurate power consumption calculation.
- When thermostat is `on`, power consumption equals `basepower * (target_temperature - room_temperature)`
- When thermostat is `off`, power consumption is zero
- Tested with both positive and negative temperature differences

### Connection Handling (implicit in tests):
- Starting disconnected with no IP
- Connecting assigns IP and sets connected status
- Reconnecting to the same or different IP updates connection without error
- Disconnecting sets connected status to false but retains last IP

### `test_connect_same_ip`: To verify robustness when connecting multiple times to the same IP.
- Multiple connects to the same IP do not raise errors
- IP and connection status remain consistent

---

## Testing of Camera

### `test_camera_new_and_attributes`: To validate creation and attribute correctness of Camera objects.
- Cameras are created with valid attributes including `name`, `location`, `basepower`, `status`, and `resolution_factor`
- Invalid `resolution_factor` values (< 0 or > 20) raise `ValueError`

### `test_camera_power_consumption_behavior`: To verify power consumption calculations based on status and connection.
- Power consumption is zero when the camera is off or disconnected
- When camera is on and connected, power consumption = `basepower * resolution_factor`
- Toggling status on/off updates power consumption correctly

### `test_camera_connect_disconnect_logic`: To ensure connection and IP handling works as expected.
- Cameras start disconnected with no IP
- Connecting assigns IP and marks device connected
- Reconnecting with a different IP updates the IP
- Disconnecting sets device as disconnected but retains last IP

### `test_camera_describe_device_quality_and_connection`: To check the correctness of `describe_device()` output.
- Descriptions reflect resolution quality levels: low (<=5), medium (6–10), high (>10)
- Connection status and IP address (when connected) are included in the description string

### `test_camera_resolution_factor_limits`: To verify cameras handle boundary resolution factors correctly.
- Cameras with minimum resolution factor (1) and maximum (20) are created and validated

---

## Testing of Smart House Management

### `test_smartHouseManagement_new`: To verify the creation of `SmartHouseManagement` objects with valid and invalid parameters.
- Valid creation works with or without specifying `search_type` and `search_room`
- When provided, `search_type` must be a valid class (e.g. `Light`, `Camera`) or `None`
- When provided, `search_room` must be a `str` or `None`
- Invalid types for `search_type` or `search_room` raise `TypeError`

### `test_smartHouseManagement_get_all_connected_devices`: To ensure correct behavior of retrieving connected devices.
- Returns an empty list when no devices are connected
- Returns all connected devices when no IP is specified
- Filters connected devices by IP address when specified
- Devices that are disconnected or turned off are excluded from results
- Verifies that non-connectable devices (e.g. `Light`) are never included

### `test_smartHouseManagement_get_all_device_description`: To test filtering and retrieval of device descriptions.
- Returns description strings for **all** registered devices by default
- Can filter results by:
  - `search_type` (example, only `Camera`)
  - `search_room` (example., only devices in `"Bathroom"`)
  - Both filters simultaneously (example, only `Camera`s in `"Bedroom"`)
- Properly handles empty result sets (example, no `Light` in `"Bedroom"`)

### `test_smartHouseManagement_calculate_total_power_consumption`: To validate correct total power consumption calculations.
- Sums the power consumption of all devices currently `on`
- Can filter results by:
  - `search_type` (example, total for all `Thermostat`s)
  - `search_room` (example, total for all devices in `"Bedroom"`)
  - Both `search_type` and `search_room` together
- Devices that are `off` or disconnected contribute zero to the total

---

## Use of AI

We used AI (Chat GPT) for:

- inspiration on how to make and write a README.md file
- understanding what `--select` and `--verbose` are and how to use them