# 01 #################################### Classes and Objects for smart house  #################################### 


# region ############## methods for calling functions ###########################
def make(cls, *args):                               # creates new objects manually via _new constructor function
    return cls["_new"](*args)
                                                    #calls a method on that object
def call(obj, method_name, *args, **kwargs):        # finds method in class or parent and calls it with object as its first argument 
    method = find(obj["_class"], method_name)       # search class or parent for method 
    return method(obj, *args, **kwargs)             # obj is like the self in a class in py 

def find(cls, method_name):                         # find to search in inheritance chain 
    while cls is not None:
        # CASE 1: if cls is a single class dict
        if isinstance(cls, dict):
            if method_name in cls:
                return cls[method_name]
            cls = cls["_parent"]

        # CASE 2: if cls is a list of parent classes (multiple inheritance)
        elif isinstance(cls, list):
            for parent in cls:
                try:
                    return find(parent, method_name)
                except NotImplementedError:
                    continue
            # if not found in any parent, stop
            cls = None
        else:
            break
    raise NotImplementedError(f"Method {method_name} is not implemented")
#endregion

AllDevices = {}             # global dict to keep track of devices that got created 
AllConnectables = {}        # global dict to keep track of connectables that got created 

def reset_globals():        # Reset all global device registries (for clean test setup, used in test.py).
    AllDevices.clear()
    AllConnectables.clear()


# region ############## DEVICE CLASS Parent #####################################

# Abstract Methods for Device , child classes must implement
def get_power_consumption(obj):
    raise NotImplementedError( f"{obj['_class']['_classname']} must implement get_power_consumption().")

def describe_device(obj):
    raise NotImplementedError( f"{obj['_class']['_classname']} must implement describe_device().")


# Method for Device 
def toggle_status(obj): # changes status to on if device is off and other way around
    if obj["status"] == "off":
        obj["status"] = "on"
    else: obj["status"] = "off"


# init Device object, returning device attributes
def device_name(obj):
    return obj["name"]

def device_location(obj):
    return obj["location"]

def device_basepower(obj):
    return obj["basepower"]

def device_status(obj):
    return obj["status"]

def device_new(name, location, basepower, status= "off"):   # new device is always off 
    if not isinstance(name, str):
        raise TypeError("name should be a string")
    if not isinstance(location, str):
        raise TypeError("location should be a string")
    if len(name) < 1:
        raise ValueError("name should have least one character")
    if name in AllDevices:
        raise ValueError("name is already taken")
    if status not in ("off", "on"):
        raise ValueError("status given when creating device is not valid")
    if basepower < 0:
        raise ValueError("basepower given when creating device is not valid")
    new_device = {
        "name": name,
        "location": location,
        "basepower": basepower,
        "status": status,
        "_class": Device                #links to class Device
    }
    AllDevices[name] = new_device
    return new_device


# Device class implemented using dict
Device = {                              # device class with attributes name, location, base power, status 
    "name": device_name,
    "location": device_location,
    "basepower": device_basepower,
    "status": device_status,
    "_classname": "Device",             # class for inheritance, but device is parent class 
    "_parent": None,
    "_new": device_new,                 # points to it's constructor, create new device with attributes 
    "toggle_status": toggle_status,     # method to change status on and off 
    "describe_device": describe_device, # abstract methods describe device and get power cons. 
    "get_power_consumption": get_power_consumption
}
#endregion


# region ############## CONNECTABLE CLASS Parent ################################

# attributes for connectable 
def connectable_connected(obj):     # is it connected or not 
    return obj["connected"]

def connectable_ip(obj):            # what ip address it is connected to 
    return obj["ip"]

# Methods for connectable 
def connectable_connect(obj, ip):   # connect and set ip
    if not isinstance(ip, str):
        raise TypeError("ip should be a str")
    if not all(c.isdigit() or c == '.' for c in ip):
        raise ValueError("ip should be numbers and dots")
    obj["connected"] = True
    obj["ip"] = ip

def connectable_disconnect(obj):    # disconnect device 
    obj["connected"] = False        # remember ip for further connections   

def connectable_is_connected(obj):  # tell if its connected 
    return obj["connected"]

def connectable_new():
    return {
        "connected": False,     # by default: not connected ; all new devices are not connected 
        "ip": None,             # no IP address # WHEN CREATING A NEW CONN. IT ISN'T CONNECTED TO ANY IP?
        "_class": Connectable   # points to its class
    }

# Connectable class implemented using dict 
Connectable = {
    "connected": connectable_connected,
    "ip": connectable_ip,
    "_classname": "Connectable",            # just for identification
    "_parent": None,                        # no parent (this is a base class)
    "_new": connectable_new,                # constructor function
    "connect": connectable_connect,         # method to connect
    "disconnect": connectable_disconnect,   # method to disconnect
    "is_connected": connectable_is_connected  # method to check status
}
#endregion


# region ############## LIGHT CHILD CLASS subclass ##############################
# inherits from Device not Connectable

def light_brightness(obj):
    return obj["brightness"]

def light_get_power_consumption(obj):
    if obj["status"] == "off":
        return 0
    return round(obj["basepower"]*obj["brightness"]/100)        # Returns the total power consumed by the smart light using the fol-
                                                                # lowing formula (rounded to the closest integer):

def light_describe_device(obj):                                 #rename to light_ - avoid confusion with device class      # string to identify name, type, location, status, brightness in % 
    return (f"The {obj['name']} is located in the {obj['location']}, "
            f"is currently {obj['status']}, "
            f"and is currently set to {obj['brightness']}% brightness.")


def light_new(name, location="not defined", basepower=0, status="off", brightness=0): # creates a new Light object
    if brightness < 0 or brightness > 100:
        raise ValueError("brightness should be a number between 0 and 100")
    new_light = make(Device, name, location, basepower, status) | {                        # makes new light object by using parent class Device 
        "brightness":brightness,
        "_class": Light
    }
    AllDevices[name] = new_light                                                            # added light to all devices as well 
    return new_light

# Light class implemented using dict
Light = {
    "brightness": light_brightness,         # inherits from Device with additional attribute brightness  
    "get_power_consumption": light_get_power_consumption,
    "describe_device": light_describe_device,
    "_classname": "Light",
    "_parent": Device,
    "_new": light_new
}
#endregion


# region ############## THERMOSTAT CHILD CLASS subclass #########################
# inherits from Device and Connectable, multiple inheritance 

def set_target_temperature(obj, temp): # user configurable
    if temp>40 or temp<0:
        raise ValueError("temperature should be between 0 and 40 degrees celsius")
    obj["target_temperature"] = temp

def get_target_temperature(obj):
    return obj["target_temperature"]

def room_temperature(obj): # not user configurable!!!
    return obj["room_temperature"]

def target_temperature(obj):
    return obj["target_temperature"]

def thermostat_get_power_consumption(obj):
    if obj["status"] == "off":
        return 0
    return obj["basepower"] * abs(obj["target_temperature"] - obj["room_temperature"])

def thermostat_describe_device(obj):                                                    # first check if ip is connected or not, if not connected tell its not, otherwise return ip 
    connection_info = (f"connected to server {obj['ip']}" if obj["connected"]
                       else "not connected to any server")
    return (f"The {obj['name']} is located in the {obj['location']}, is currently {obj['status']}, "
            f"and is currently set to {obj['target_temperature']} degrees Celsius in a {obj['room_temperature']} degree room. "
            f"It is currently {connection_info}.")                                      # use connection info to check if ip is really connected or not 

def thermostat_new(name, location="not defined", basepower=0, status="off", room_temperature = 10, target_temperature=10): # creates a new Thermostat object using device and connectable class 
    # check temperatures are valid
    if room_temperature > 40 or room_temperature < 0:
        raise ValueError("room_temperature should be between 0 and 40 degrees celsius")
    if target_temperature > 40 or target_temperature < 0:
        raise ValueError("target_temperature should be between 0 and 40 degrees celsius")
     
    new_thermostat = make(Device, name, location, basepower, status) | make(Connectable)| {
        "room_temperature":room_temperature,
        "target_temperature":target_temperature,
        "_class": Thermostat
    }
    AllDevices[name] = new_thermostat
    AllConnectables[name] = new_thermostat
    return new_thermostat

# Thermostat class implemented using dict
Thermostat = {
    "set_target_temperature": set_target_temperature,
    "get_target_temperature": get_target_temperature,
    "room_temperature": room_temperature,                       # room and target temp as attributes 
    "target_temperature": target_temperature,
    "get_power_consumption": thermostat_get_power_consumption,  # returns total power consumed by smart thermo 
    "describe_device": thermostat_describe_device,
    "_classname": "Thermostat",
    "_parent": [Device, Connectable],                           # multiple inheritance
    "_new": thermostat_new
}
# endregion


# region ############## CAMERA CHILD CLASS subclass #############################
# inherits from Device and Connectable, multiple inheritance 

def camera_resolution_factor(obj):
    return obj["resolution_factor"]


def camera_get_power_consumption(obj):
    if obj["status"] == "off":
        return 0
    return obj["basepower"] * obj["resolution_factor"]


def camera_describe_device(obj):
    if obj["resolution_factor"] < 5:
        quality = "low"
    elif obj["resolution_factor"] < 10:
        quality = "medium"
    else:
        quality = "high"

    if obj["connected"]:
        connection_status = f"connected to server {obj['ip']}"
    else:
        connection_status = "disconnected"

    return (f"The {obj['name']} is located in the {obj['location']}," 
            f" is currently {obj['status']}, and is a {quality} resolution sensor."
            f" It is currently {connection_status}.")

def camera_new(name, location = "not defined", basepower = 0, status = "off", resolution_factor = 1):
    if resolution_factor < 0 or resolution_factor > 20:
        raise ValueError("resolution_factor should be between 0 and 20")
    
    device_part = make(Device, name, location, basepower, status)                                       # create new camera with device class 
    connectable_part = make(Connectable)
    device_attrs = {k: v for k, v in device_part.items() if k !="_class"}
    connectable_attrs = {k: v for k, v in connectable_part.items() if k != "_class"}

    new_camera = device_attrs | connectable_attrs | {
        "resolution_factor": resolution_factor,
        "_class": Camera
    }

    AllDevices[name] = new_camera                       # added this to also add camera in all devices like thermo 
    AllConnectables[name] = new_camera

    return new_camera


# Camera class implemented using dict
Camera = {
    "resolution_factor": camera_resolution_factor,
    "get_power_consumption": camera_get_power_consumption, 
    "describe_device": camera_describe_device, 
    "_classname": "Camera",
    "_parent": [Device, Connectable],
    "_new": camera_new
}
#endregion


# region ############## instances of Device objects #############################

if __name__ == "__main__": # this ensures that all this code doesn't get printed to the terminal when running test_smart_house.py
    L1 = make(Light, "Bedtable Light", "Bedroom", 250, "on", 50)
    L2 = make(Light, "Bathroom Light", "Bathroom", 300, "off", 80)
    L3 = make(Light, "Living Room Light", "Living Room", 400, "on", 100)
    T1 = make(Thermostat, "Towel Thermostat", "Bathroom", 1200, "on", 18, 24)
    T2 = make(Thermostat, "Bedroom Thermostat", "Bedroom", 3100, "off", 19, 21)         # room should be warmer
    T3 = make(Thermostat, "Living Room Thermostat", "Living Room", 5800, "on", 24, 21)  # room should be colder
    C1 = make(Camera, "New RGB Camera", "Living Room", 500, "on", 12)                   # high resolution
    C2 = make(Camera, "Surveilance Camera", "Front Door", 200, "on", 2)                 # low resolution
    C3 = make(Camera, "Bedroom Camera", "Bedroom", 200, "off", 7)                       # medium resolution

    lights_list = [L1, L2, L3]
    thermostats_list = [T1, T2, T3]
    cameras_list = [C1, C2, C3]

    for element in lights_list:
        name = element["name"]
        brightness = call(element, "brightness")
        location = call(element, "location")
        basepower = call(element, "basepower")
        status = call(element, "status")
        class_name = element["_class"]["_classname"]

        print(f"{name} has brightness {brightness}%, located in {location}, base power {basepower}W, status {status}, and is of class {class_name}.")
        print("Description:", call(element, "describe_device"))
        print("Power Consumption:", call(element, "get_power_consumption"))
        print("-" * 60)


    for element in thermostats_list:
        name = element["name"]
        room_temp = call(element, "room_temperature")
        target = call(element, "target_temperature")
        basepower = call(element, "basepower")
        class_name = element["_class"]["_classname"]

        print(f"{name} has base power {basepower}W and is of class {class_name}. The room temperature is {room_temp}, the target temperature is {target} ")
        print("Description:", call(element, "describe_device"))
        print("Power Consumption:", call(element, "get_power_consumption"))
        print("-" * 60)


    for element in cameras_list:
        name = element["name"]
        resolution = call(element, "resolution_factor")
        basepower = call(element, "basepower")
        class_name = element["_class"]["_classname"]

        print(f"{name} has base power {basepower}W, has resolution factor {resolution} and is of class {class_name}.")
        print("Description:", call(element, "describe_device"))
        print("Power Consumption:", call(element, "get_power_consumption"))
        print("-" * 60)

    # Test Thermostat
    call(T1, "toggle_status")  # Turn it OFF
    print(f"T1 has status {call(T1, 'status')}.")

    # Set new temperature
    call(T1, "set_target_temperature", 22)

    # Print description
    print("Thermostat description:")
    print(call(T1, "describe_device"))

    # Print power consumption
    print("Thermostat power consumption:", call(T1, "get_power_consumption"))

    # Change camera connection and print description
    call(C1, "connect", "10.10.10.4")
    print("Connecting camera:", call(C1, "describe_device"))

    # Print camera after disconnecting and turning off
    call(C1, "disconnect")
    call(C1, "toggle_status")
    print("After disconnecting:", call(C1, "describe_device"))
    print("After disconnecting: power consumption is ", call(C1, "get_power_consumption"))
# endregion



# 02 #################################### Management of smart house  #################################### 


# region ############## Smart House Management Class parent ##################### like Dashboard

def smart_house_man_search_type(obj):   
    return obj["search_type"]                       


def smart_house_man_search_room(obj):    
    return obj["search_room"]            
    

def smart_house_man_calculate_total_power_consumption(obj, search_type=None, search_room=None):

    total_power = 0

    for device in AllDevices.values():
        # Apply both filters if given
        type_match = (search_type is None or device["_class"]["_classname"] == search_type["_classname"])
        room_match = (search_room is None or device["location"] == search_room)

        if type_match and room_match:
            power = call(device, "get_power_consumption")
            total_power += power

    return total_power


def smart_house_man_get_all_device_description(obj, search_type=None, search_room=None):

    device_descriptions = []        # Create a list to store descriptions of devices that match the filters

    for device in AllDevices.values():                                              # Iterate through all devices that have been created and stored in AllDevices
        type_match = (search_type is None or device["_class"]["_classname"] == search_type["_classname"])       # Check if the device matches the given search_type (or allow all if not specified)
        room_match = (search_room is None or device["location"] == search_room)           # Check if the device is in the specified room (or allow all if not specified)

        if type_match and room_match:                                                           # If both filters match (or if no filters are applied), include the device
            description = call(device, "describe_device")                                       # Call the 'describe_device' method to get a string describing the device
            device_descriptions.append(description)                                             # Add the description to the list
    return device_descriptions                                                                  # Return the list of matching device descriptions


def smart_house_man_get_all_connected_devices(obj, ip=None):

    connected_device = [] # list of tuples containing: [ (power consumption, description), (..., ...)]
        
    for connectable in AllConnectables.values():            # only need to look through Cameras and Thermostats
        if call(connectable, "is_connected"):
            if ip is None or connectable["ip"] == ip:       # if ip filter is given, ensure it matches
                if connectable["status"] == "on":           # only include if the device is on
                    desc = call(connectable, "describe_device")
                    power = call(connectable, "get_power_consumption")
                    connected_device.append((power, desc))

    return connected_device


def smartHouseManagemement_new(search_type=None, search_room=None): # creates a new SmartHouseManagement object
    if not (isinstance(search_type, dict) or search_type is None):
        raise TypeError("search_type should be a Device or None")
    
    if not (isinstance(search_room, str) or search_room is None):
        raise TypeError("search_room should be a str or None")
    
    return {
        "search_type":search_type,
        "search_room":search_room,
        "_class": SmartHouseManagement
    }

# SmartHouseManagement class implemented using dict
SmartHouseManagement = {
    "_classname": "SmartHouseManagement",
    "_parent": None,
    "_new": smartHouseManagemement_new,
    "search_type": smart_house_man_search_type,
    "search_room": smart_house_man_search_room,
    "calculate_total_power_consumption": smart_house_man_calculate_total_power_consumption,
    "get_all_device_description": smart_house_man_get_all_device_description,
    "get_all_connected_devices": smart_house_man_get_all_connected_devices
}
# endregion


# region ############## instances of SmartHouseManagement objects ###############

if __name__ == "__main__": # this ensures that all this code doesn't get printed to the terminal when running test_smart_house.py
    reset_globals()
    # Create a SmartHouseManagement instance
    print("------------------ Testing SHM -------------------")
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

    # Initial total power
    print("Initial total power:", call(SHM, "calculate_total_power_consumption"))

    # Turn off a light
    call(L2, "toggle_status")
    print("After turning off L2:", call(SHM, "calculate_total_power_consumption"))

    # Change thermostat turn on and change target temperature
    call(T1, "set_target_temperature", 26)
    print("After increasing thermostat target temp:", call(SHM, "calculate_total_power_consumption"))

    # Dim a light
    L1["brightness"] = 40
    print("After dimming L1:", call(SHM, "calculate_total_power_consumption"))

    # Turn the camera off
    call(C2, "toggle_status")
    print("After turning off C2:", call(SHM, "calculate_total_power_consumption"))


    print("----------------- testing power consumption with search_room --------------------")
    e = call(SHM, "calculate_total_power_consumption", None, "Bedroom")
    print(f"total power Bedroom: {e}\n")

    print("----------------- testing power consumption with search_type --------------------") 
    e = call(SHM, "calculate_total_power_consumption", Camera)
    print(f"total power Camera: {e}\n")

    print("----------------- testing describe device --------------------") 
    e = call(SHM, "get_all_device_description")
    print(f"everything: {e} \n")

    e = call(SHM, "get_all_device_description", Camera, "Bedroom")
    print(f"search room: Bedroom & search type: Camera: {e}\n")

    print("----------------- testing connected device --------------------") 
    e = call(SHM, "get_all_connected_devices") # none
    print(e)

    call(T1, "connect", "10.10.10.4")
    call(C1, "connect", "11.11.11.4")
    e = call(SHM, "get_all_connected_devices") #t1 c1
    print(e)

    e = call(SHM, "get_all_connected_devices", "10.10.10.4") # t1
    print(e)

    call(T1, "disconnect")
    e = call(SHM, "get_all_connected_devices") # c1
    print(e)
#endregion
