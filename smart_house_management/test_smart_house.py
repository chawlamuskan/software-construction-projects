# 03 #################################### Testing for smart house #################################### 


import smart_house             # you need to call smart_house.METHOD/OBJECT for anything that you want to import from smart_house
import pprint
import time
import sys 

# some test_ variable for the verbose test
test_variable = 1                                   
test_other_var = "var"


#region ######################## Test DEVICE CLASS parent #########################
# correct setup / attribute initialization  DONE
# status argument on or off valid status    DONE
# name uniqueness, non - empty name         DONE
# name type should be string                DONE          
# basepower not negative                    DONE
# toggle_status method                      DONE

def test_device_attributes():
    smart_house.reset_globals() # delete all objects created before
    d = smart_house.make(smart_house.Device,"Stove", "Kitchen", 100) #using Device class
    
    #testing if attributes are correct
    assert smart_house.call(d, "name") == "Stove"  #using d as device object
    assert smart_house.call(d, "location") == "Kitchen"
    assert smart_house.call(d,"basepower") == 100
    assert smart_house.call(d, "status") == "off"
    
    d1= smart_house.make(smart_house.Device, "Light", "Room", 201, "on")        # create another device with status on 
    
    assert smart_house.call(d1, "status") == "on"
    
    # Test: Empty name should raise ValueError
    try:
        smart_house.make(smart_house.Device, "", "Room", 201)
        assert False, "Empty name should raise ValueError"
        
    except ValueError:
        assert True

def test_device_valid_status():  
    smart_house.reset_globals()
    d_off = smart_house.make(smart_house.Device, "Stove0", "Kitchen0", 105, "off")   #default is off
    d_on = smart_house.make(smart_house.Device, "Stove2", "Kitchen2", 120, "on")    #change to on
    
    assert smart_house.device_status(d_off) == "off"
    assert smart_house.device_status(d_on) == "on"

def test_device_name_uniqueness():
    # Test: name already taken should raise ValueError
    smart_house.reset_globals()
    smart_house.make(smart_house.Device, "UniqueLight", "Room", 400)   #stored in all Devices, so then we have two names ==> Error
    try:
        smart_house.make(smart_house.Device, "UniqueLight", "Room", 400)
        assert False, "Duplicate name should raise ValueError"
        
    except ValueError:
        assert True

def test_device_wrong_name_type():
    smart_house.reset_globals()
    try:
        smart_house.make(smart_house.Device, 123, "Room", 100)
        assert False, "Non-string name should raise TypeError"
        
    except TypeError:
        assert True

def test_device_negative_basepower():
    smart_house.reset_globals()
    try:
        smart_house.make(smart_house.Device, "Test", "Room", -50)
        assert False, "Negative basepower should raise ValueError"
        
    except ValueError:
        assert True

def test_device_toggle_status():
    smart_house.reset_globals()
    device = smart_house.make(smart_house.Device, "Test Device", "Test Room", 100, "off")
    light = smart_house.make(smart_house.Light, "Test Light", "Test Room", 100, "off", 50)
    thermostat = smart_house.make(smart_house.Thermostat, "Test Thermostat", "Test Room", 100, "on", 15, 15)
    camera = smart_house.make(smart_house.Camera, "Test Camera", "Test Room", 100, "off", 10)
    
    # Test 1 device
    assert smart_house.call(device, "status") == "off"  # off
    smart_house.call(device, "toggle_status")           
    assert smart_house.call(device, "status") == "on"   # on

    # Test 2 light
    assert smart_house.call(light, "status") == "off"  # off
    smart_house.call(light, "toggle_status")           
    assert smart_house.call(light, "status") == "on"   # on
    
    # Test 3 light
    smart_house.call(light, "toggle_status")           
    assert smart_house.call(light, "status") == "off"  # off 
    
    # Test 4 light
    smart_house.call(light, "toggle_status")           
    assert smart_house.call(light, "status") == "on"   # Should be on 

    # Test 5 thermostat
    assert smart_house.call(thermostat, "status") == "on"  # on
    smart_house.call(thermostat, "toggle_status")           
    assert smart_house.call(thermostat, "status") == "off"   # off

    # Test 6 thermostat
    smart_house.call(thermostat, "toggle_status")           
    assert smart_house.call(thermostat, "status") == "on"   # on

    # Test 7 camera
    assert smart_house.call(camera, "status") == "off"  # off
    smart_house.call(camera, "toggle_status")           
    assert smart_house.call(camera, "status") == "on"   # on

    # Test 8 camera
    smart_house.call(camera, "toggle_status")           
    assert smart_house.call(camera, "status") == "off"   # off

# endregion


# region ######################## Test CONNECTABLE CLASS parent ###################
# connectable setup                             DONE
# connecting a connectable object               DONE
# disconnecting a connectable object            DONE
# reconnecting a connectable object             DONE
# check is connected                            DONE
# try disconnecting without beeing connected    DONE
# try connecting twice to same ip               DONE
# try connecting a light                        DONE
# TEST INVALID IP!!

def test_connectable_initial_state():
    c = smart_house.connectable_new()                     # Create a new Connectable object
    assert c["connected"] == False                        # Should start disconnected
    assert c["ip"] == None                                # IP should be None initially

def test_connectable_connect():
    c = smart_house.connectable_new()                     # Create a new Connectable object
    smart_house.call(c, "connect", "192.123.1.4")         # Use the connect method to assign an IP
    assert c["connected"] == True                         # Should now be marked as connected
    assert c["ip"] == "192.123.1.4"                       # IP should be correctly set

def test_connectable_disconnect():
    c = smart_house.connectable_new()                     # Create a new Connectable object
    smart_house.call(c, "connect", "192.168.1.1")         # Connect to an IP first
    smart_house.call(c, "disconnect")                     # Then disconnect the object
    assert c["connected"] == False                        # Should be marked as disconnected
    assert c["ip"] == "192.168.1.1"                       # IP should still be there because we dont reset it to None 

def test_connectable_reconnect():
    c = smart_house.connectable_new()                     # Create a new Connectable object
    smart_house.call(c, "connect", "10.0.0.1")            # First connect to one IP
    smart_house.call(c, "disconnect")                     # Then disconnect
    smart_house.call(c, "connect", "10.5.6.2")            # Reconnect to another IP
    assert c["connected"] == True                         # Should be connected again
    assert c["ip"] == "10.5.6.2"                          # IP should be the new second one now 

def test_connectable_is_connected_method():
    c = smart_house.connectable_new()                     # Create a new Connectable object
    assert smart_house.call(c, "is_connected") == False   # Should return False initially
    smart_house.call(c, "connect", "1.1.1.1")             # Connect it
    assert smart_house.call(c, "is_connected") == True    # Should now return True because i just connected it 

def test_connectable_disconnect_without_connect():        # EDGE CASE CALLING DISCONNECT BEFORE CONNECT 
    c = smart_house.connectable_new()                     # New object, not connected
    smart_house.call(c, "disconnect")                     # Try disconnecting it anyway
    assert c["connected"] == False                        # Should remain False because i never connected before so how can it disconnect 
    assert c["ip"] == None                                # Should still be None because i didnt set any ip 

def test_connectable_connect_twice():                     # EDGE CASE CONNECTING TWICE TO SAME IP 
    c = smart_house.connectable_new()                     # New object, not connected
    smart_house.call(c, "connect", "1.1.1.1")             # Connect it
    smart_house.call(c, "connect", "1.1.1.1")             # Connect it again
    assert c["connected"] == True                         # Should not raise an error and connect is true 
    assert c["ip"] == "1.1.1.1"

def test_connectable_on_light():                          # EDGE CASE CONNECTING A LIGHT THAT IS NOT A CONNECTABLE
    l = smart_house.make(smart_house.Light, "l", "Test Room", 100, "on", 50)
    try:
        smart_house.call(l, "connect")   # Should raise NotImplementedError
        assert False, "connect should raise NotImplementedError on light"
    except NotImplementedError: pass

def test_connectable_invalid_ip():
    c = smart_house.connectable_new()                     # Create a new Connectable object
    try: 
        smart_house.call(c, "connect", 999999)            # Connect to invalid IP
        assert False, "connect with invalid ip should raise  TypeError"
    except TypeError: pass 
    try: 
        smart_house.call(c, "connect", "a.b.c.d,")        # Connect to invalid IP
        assert False, "connect with invalid ip should raise  ValueError"
    except ValueError: pass 

#endregion


# region ########################## Test LIGHT CLASS child ########################
# Instantiation (light_new)                 DONE
# Toggle status (on/off)                    DONE in device       
# Power consumption based on brightness     DONE
# decribe device                            DONE

def test_light_new(): 
    L1 = smart_house.make(smart_house.Light, "Bedtable Light1", "Bedroom", 250, "on", 50) # valid light
    assert  L1["name"] == "Bedtable Light1"
    assert  L1["location"] == "Bedroom"
    assert  L1["basepower"] == 250
    assert  L1["status"] == "on"
    assert  L1["brightness"] == 50
    assert  L1['_class']['_classname'] == "Light"
    assert  L1['_class']["_parent"] == smart_house.Device

    # testing invalid lights
    try: # creating light with same name twice
        L1 = smart_house.make(smart_house.Light, "Bedtable Light2", "Bedroom", 250, "on", 50)
        L1same = smart_house.make(smart_house.Light, "Bedtable Light2", "Other Room", 100, "on", 10)
        assert False, "Expected ValueError for invalid name"
    except ValueError: pass

    try: # creating light with wrong type for location - used int 000 instead of str 
        smart_house.make(smart_house.Light, "wrong location", 000, 250, "on", 50)
        assert False, "Expected TypeError for invalid location"
    except TypeError: pass

    try: # creating light with invalid basepower - negative 
        smart_house.make(smart_house.Light, "Bathroom Light", "Bathroom", -1000, "off", 80)
        assert False, "Expected ValueError for invalid basepower"
    except ValueError: pass

    try: # creating light with invalid brightness - negative 
        smart_house.make(smart_house.Light, "Bathroom Light2", "Bathroom", 300, "off", -20)
        assert False, "Expected ValueError for invalid brightness"
    except ValueError: pass

    try: # creating light with invalid status - not on or off
        smart_house.make(smart_house.Light, "Living Room Light", "Living Room", 400, "invalid", 100)
        assert False, "Expected ValueError for invalid status"
    except ValueError: pass
 

def test_light_power_consumption():
    light1 = smart_house.make(smart_house.Light, "light1", "Test Room", 100, "on", 50)      # light on brightness 50 %
    light2 = smart_house.make(smart_house.Light, "light2", "Test Room", 100, "on", 15)      # light on brightness 15 %
    light3 = smart_house.make(smart_house.Light, "light3", "Test Room", 100, "on", 100)     # light on brightness 100 %
    light4 = smart_house.make(smart_house.Light, "light4", "Test Room", 100, "off", 100)    # light is off
    light5 = smart_house.make(smart_house.Light, "light5", "Test Room", 100, "on", 0)       # brightness is 0 == light is off
    
    # Test light1
    res = round(light1["basepower"]*light1["brightness"]/100)
    assert smart_house.call(light1, "get_power_consumption") == res  
    # Test light2
    res = round(light2["basepower"]*light2["brightness"]/100)
    assert smart_house.call(light2, "get_power_consumption") == res  
    # Test light3
    res = round(light3["basepower"]*light3["brightness"]/100)
    assert smart_house.call(light3, "get_power_consumption") == res  
    # Test light4
    res = round(light4["basepower"]*light4["brightness"]/100)
    assert smart_house.call(light4, "get_power_consumption") == 0  
    # Test light5
    res = round(light5["basepower"]*light5["brightness"]/100)
    assert smart_house.call(light5, "get_power_consumption") == 0  

   
def test_light_describe_device():   
    light = smart_house.make(smart_house.Light, "light_desc", "Test Room", 100, "on", 50)                                             
    assert smart_house.call(light, "describe_device") == f"The light_desc is located in the Test Room, is currently on, and is currently set to 50% brightness."
    
#endregion


# region ########################## Test THERMOSTAT CLASS child ###################
# Toggle status                                         DONE in device 
# Create new thermostat                                 DONE
# Set target temp                                       DONE
# Test attributes                                       DONE
# Power consumption based on temperature difference     DONE
#  and only consumes power when "on" (all in same)      DONE
# connect to same ip address                            DONE in connectable


def test_thermostat_new():
    smart_house.reset_globals()
    
    # Valid creation and check global registration
    therm2 = smart_house.make(smart_house.Thermostat, "Testing", "R", 1000, "on", 27, 28)
    assert smart_house.call(therm2, "name") == "Testing"
    assert smart_house.call(therm2, "room_temperature") == 27
    assert smart_house.call(therm2, "target_temperature") == 28
    
    # Check it's registered in global dictionaries
    assert "Testing" in smart_house.AllDevices
    assert "Testing" in smart_house.AllConnectables
    assert smart_house.AllDevices["Testing"] == therm2
    assert smart_house.AllConnectables["Testing"] == therm2
    
    # Invalid room temperature
    try:
        smart_house.make(smart_house.Thermostat, "B", "R", 1000, "on", 45, 28)
        assert False
    except ValueError: 
        pass
    
    # Invalid target temperature  
    try:
        smart_house.make(smart_house.Thermostat, "B", "R", 1000, "on", 27, -1)
        assert False
    except ValueError: 
        pass


def test_thermostat_set_target_temperature():
    smart_house.reset_globals()

    thermo = smart_house.make(smart_house.Thermostat, "Test Thermo", "Living Room", 1000, "on", 20, 22)
    
    smart_house.call(thermo, "set_target_temperature", 25)
    assert smart_house.call(thermo, "get_target_temperature") == 25
    
    # Test: Set to minimum boundary (0 degrees)
    smart_house.call(thermo, "set_target_temperature", 0)
    assert smart_house.call(thermo, "get_target_temperature") == 0
    
    # Test Set to maximum boundary (40 degrees)  
    smart_house.call(thermo, "set_target_temperature", 40)
    assert smart_house.call(thermo, "get_target_temperature") == 40
    
    # Test: Try to high temperature > invalid
    try:
        smart_house.call(thermo, "set_target_temperature", 41)
        assert False, "Should raise ValueError for temperature 41"
    except ValueError:
        pass                            # Expected
    
    # Test: Try to set invalid temperature (too low)
    try:
        smart_house.call(thermo, "set_target_temperature", -1)
        assert False, "Should have raised ValueError for temperature -1"
    except ValueError:
        pass                             # Expected


def test_thermostat_attributes():              #Test that thermostat has all the correct attributes
    smart_house.reset_globals()                #reset 
    
    thermo1 = smart_house.make(smart_house.Thermostat, "Bedroom Thermo", "Bedroom", 1500, "on", 22, 24)  # Create thermostat object for testing
    
    # Test Device attributes, checking again from parent class
    assert smart_house.call(thermo1, "name") == "Bedroom Thermo"
    assert smart_house.call(thermo1, "location") == "Bedroom" 
    assert smart_house.call(thermo1, "basepower") == 1500
    assert smart_house.call(thermo1, "status") == "on"
    
    # Test Thermostat specific attributes
    assert smart_house.call(thermo1, "room_temperature") == 22
    assert smart_house.call(thermo1, "target_temperature") == 24
    
    # Test Connectable attributes
    assert smart_house.call(thermo1, "is_connected") == False    # should start disconnected
    
    
def test_thermostat_get_power_consumption():
    smart_house.reset_globals()                #reset 
    # positive change in temp: room is 21 target is 23
    ther1 = smart_house.make(smart_house.Thermostat, "Test1", "Room", 200, "on", 21, 23)
    expected = 200 * abs(23-21)
    result = smart_house.call(ther1, "get_power_consumption")
    assert result == expected, f"Expected {expected} but got {result} instead."
    # negative change in temp: room is 21 target is 19
    ther2 = smart_house.make(smart_house.Thermostat, "Test2", "Room", 200, "on", 21, 19)
    expected = 200 * abs(19-21)
    result = smart_house.call(ther2, "get_power_consumption")
    assert result == expected, f"Expected {expected} but got {result} instead."
    # device is off power cons = 0
    ther3 = smart_house.make(smart_house.Thermostat, "Test3", "Room", 200, "off", 21, 19)
    expected = 0
    result = smart_house.call(ther3, "get_power_consumption")
    assert result == expected, f"Expected {expected} but got {result} instead."
    

def test_connect_same_ip():
    smart_house.reset_globals()
    c = smart_house.connectable_new()
    smart_house.call(c, "connect", "192.168.1.1")
    smart_house.call(c, "connect", "192.168.1.1")  # should just override/reconnect, not error
    assert c["ip"] == "192.168.1.1"


def test_thermostat_new():
    smart_house.reset_globals()
    
    # Valid creation and check global registration
    therm2 = smart_house.make(smart_house.Thermostat, "Testing", "R", 1000, "on", 27, 28)
    assert smart_house.call(therm2, "name") == "Testing"
    assert smart_house.call(therm2, "room_temperature") == 27
    assert smart_house.call(therm2, "target_temperature") == 28
    
    # Check it's registered in global dictionaries
    assert "Testing" in smart_house.AllDevices
    assert "Testing" in smart_house.AllConnectables
    assert smart_house.AllDevices["Testing"] == therm2
    assert smart_house.AllConnectables["Testing"] == therm2
    
    # Invalid room temperature
    try:
        smart_house.make(smart_house.Thermostat, "B", "R", 1000, "on", 45, 28)
        assert False
    except ValueError: 
        pass
    
    # Invalid target temperature  
    try:
        smart_house.make(smart_house.Thermostat, "B", "R", 1000, "on", 27, -1)
        assert False
        
    except ValueError: 
        pass
#endregion

# region ########################## Test CAMERA CLASS child #######################
# valid camera creation and attributes          DONE
#   and invalid resolution factor               DONE
# power consumption                             DONE
# connection - connect, disconnect, change ip   DONE
# resolution quality                            DONE
# description with connection status            DONE

def test_camera_new_and_attributes():
    smart_house.reset_globals()         # reset all global device states
    # Valid camera
    cam = smart_house.make(smart_house.Camera, "Cam1", "Hall", 100, "on", 7)
    # Basic attribute checks
    assert cam["name"] == "Cam1"
    assert cam["location"] == "Hall"
    assert cam["basepower"] == 100
    assert cam["status"] == "on"
    assert cam["resolution_factor"] == 7
    assert cam["_class"]["_classname"] == "Camera"
    # Invalid resolution_factor too high
    try:
        smart_house.make(smart_house.Camera, "CamBad1", "Hall", 50, "on", 21)
        assert False, "Expected ValueError for resolution_factor > 20"
    except ValueError:
        pass
    # Invalid resolution_factor negative
    try:
        smart_house.make(smart_house.Camera, "CamBad2", "Hall", 50, "on", -1)
        assert False, "Expected ValueError for resolution_factor < 0"
    except ValueError:
        pass

def test_camera_power_consumption_behavior():
    smart_house.reset_globals()
    cam = smart_house.make(smart_house.Camera, "Cam2", "Garage", 200, "off", 5)     # off and disconnected
    # Off initially - zero
    assert smart_house.call(cam, "get_power_consumption") == 0
    # Turn on and connect
    smart_house.call(cam, "toggle_status")
    smart_house.call(cam, "connect", "10.0.0.5")
    expected = 200 * 5
    assert smart_house.call(cam, "get_power_consumption") == expected
    # Turn off - power zero
    smart_house.call(cam, "toggle_status")
    assert smart_house.call(cam, "get_power_consumption") == 0

def test_camera_connect_disconnect_logic():
    smart_house.reset_globals()
    cam = smart_house.make(smart_house.Camera, "Cam3", "Lobby", 150, "on", 3)
    # Initially disconnected
    assert cam.get("connected", False) == False
    # Connect
    smart_house.call(cam, "connect", "192.168.1.100")
    assert cam["connected"] == True
    assert cam["ip"] == "192.168.1.100"
    # Connect again to different ip should override
    smart_house.call(cam, "connect", "172.16.0.1")
    assert cam["ip"] == "172.16.0.1"
    # Disconnect
    smart_house.call(cam, "disconnect")
    assert cam["connected"] == False

def test_camera_describe_device_quality_and_connection():
    smart_house.reset_globals()
    # Low quality, disconnected
    cam_low = smart_house.make(smart_house.Camera, "CamL", "Room1", 100, "off", 3)
    desc_low = smart_house.call(cam_low, "describe_device")
    assert "low resolution" in desc_low
    assert "disconnected" in desc_low

    # Medium quality, connect
    cam_med = smart_house.make(smart_house.Camera, "CamM", "Room2", 120, "on", 7)
    smart_house.call(cam_med, "connect", "10.1.2.3")
    desc_med = smart_house.call(cam_med, "describe_device")
    assert "medium resolution" in desc_med
    assert "connected to server 10.1.2.3" in desc_med

    # High quality
    cam_high = smart_house.make(smart_house.Camera, "CamH", "Roof", 200, "on", 12)
    smart_house.call(cam_high, "connect", "192.0.2.1")
    desc_high = smart_house.call(cam_high, "describe_device")
    assert "high resolution" in desc_high
    assert "connected to server 192.0.2.1" in desc_high

def test_camera_resolution_factor_limits():
    cam_min = smart_house.make(smart_house.Camera, "CamMin", "Hall", 100, "on", 1)
    cam_max = smart_house.make(smart_house.Camera, "CamMax", "Hall", 100, "on", 20)
    
    assert cam_min["resolution_factor"] == 1
    assert cam_max["resolution_factor"] == 20
    
# endregion 


# region ########################## Test SMART HOUSE MANAGEMENT parent ############
# smart house management setup                                          DONE
# get_all_connected_devices test with and without ip                    DONE
# get_all_device_description test with and without                      DONE
#   specifications of room and type                                     DONE
# calculate_total_power_consumption test with and                       DONE
#   without specifications of room and type and devices on or off       DONE

def test_smartHouseManagement_new():
    smart_house.reset_globals() # delete all objects created

    SHM = smart_house.make(smart_house.SmartHouseManagement, smart_house.Light, "Bedroom") 
    assert  SHM["search_type"] == smart_house.Light
    assert  SHM["search_room"] == "Bedroom"
    assert  SHM['_class']['_classname'] == "SmartHouseManagement"
    assert  SHM['_class']["_parent"] == None

    SHMnone = smart_house.make(smart_house.SmartHouseManagement) 
    assert  SHMnone["search_type"] == None
    assert  SHMnone["search_room"] == None
    assert  SHMnone['_class']['_classname'] == "SmartHouseManagement"
    assert  SHMnone['_class']["_parent"] == None

    try: # creating shm with wrong search_type
        smart_house.make(smart_house.SmartHouseManagement, "wrong type for search_type") 
        assert False, "Expected TypeError for invalid search_type"
    except TypeError: pass

    try: # creating shm with wrong search_room
        smart_house.make(smart_house.SmartHouseManagement, None, 000) 
        assert False, "Expected TypeError for invalid search_room"
    except TypeError: pass

def test_smartHouseManagement_get_all_connected_devices():
    smart_house.reset_globals()
    L1 = smart_house.make(smart_house.Light, "Bedtable Light", "Bedroom", 250, "on", 50)
    T1 = smart_house.make(smart_house.Thermostat, "Towel Thermostat", "Bathroom", 1200, "on", 18, 24)
    C1 = smart_house.make(smart_house.Camera, "New RGB Camera", "Living Room", 500, "on", 12)
    SHM = smart_house.make(smart_house.SmartHouseManagement)

    assert smart_house.call(SHM, "get_all_connected_devices") == []

    # connecting C1 and T1
    smart_house.call(T1, "connect", "10.10.10.4")
    smart_house.call(C1, "connect", "11.11.11.4")

    # searching without ip
    res = smart_house.call(SHM, "get_all_connected_devices")  # T1 C1
    true_ans = [
        (smart_house.call(T1, "get_power_consumption"), smart_house.call(T1, "describe_device")),
        (smart_house.call(C1, "get_power_consumption"), smart_house.call(C1, "describe_device"))
    ]
    assert true_ans == res

    # searching with ip
    res = smart_house.call(SHM, "get_all_connected_devices", "10.10.10.4")  # T1
    true_ans = [
        (smart_house.call(T1, "get_power_consumption"), smart_house.call(T1, "describe_device"))
    ]
    assert true_ans == res

    # searching with ip that doesn’t have anything connected to
    res = smart_house.call(SHM, "get_all_connected_devices", "09.10.10.4")
    assert res == []

    # turn T1 off and connect C1 to ip 10.10.10.4
    smart_house.call(T1, "toggle_status")
    smart_house.call(C1, "connect", "10.10.10.4")

    res = smart_house.call(SHM, "get_all_connected_devices", "10.10.10.4")  # C1
    true_ans = [
        (smart_house.call(C1, "get_power_consumption"), smart_house.call(C1, "describe_device"))
    ]
    assert true_ans == res

    # disconnect C1
    smart_house.call(C1, "disconnect")
    res = smart_house.call(SHM, "get_all_connected_devices")  # none
    assert res == []

def test_smartHouseManagement_get_all_device_description():
    smart_house.reset_globals()
    L1 = smart_house.make(smart_house.Light, "Bathroom Light", "Bathroom", 300, "off", 80)
    L2 = smart_house.make(smart_house.Light, "Living Room Light", "Living Room", 400, "on", 100)
    T1 = smart_house.make(smart_house.Thermostat, "Towel Thermostat", "Bathroom", 1200, "on", 18, 24)
    T2 = smart_house.make(smart_house.Thermostat, "Bedroom Thermostat", "Bedroom", 3100, "off", 19, 21)      
    C1 = smart_house.make(smart_house.Camera, "New RGB Camera", "Living Room", 500, "on", 12)                   
    C2 = smart_house.make(smart_house.Camera, "Bedroom Camera", "Bedroom", 200, "off", 7)  
    SHM = smart_house.make(smart_house.SmartHouseManagement)             

    # all descriptions
    res = smart_house.call(SHM, "get_all_device_description")
    true_ans = [smart_house.call(L1, "describe_device"), smart_house.call(L2, "describe_device"),
        smart_house.call(T1, "describe_device"), smart_house.call(T2, "describe_device"),
        smart_house.call(C1, "describe_device"), smart_house.call(C2, "describe_device"),
    ]
    assert true_ans == res

    # only thermostats 
    res = smart_house.call(SHM, "get_all_device_description", smart_house.Thermostat)
    true_ans = [smart_house.call(T1, "describe_device"), smart_house.call(T2, "describe_device")]
    assert true_ans == res

    # only devices in Bathroom
    res = smart_house.call(SHM, "get_all_device_description", None, "Bathroom")
    true_ans = [smart_house.call(L1, "describe_device"), smart_house.call(T1, "describe_device")]
    assert true_ans == res

    # only cameras in bedroom
    res = smart_house.call(SHM, "get_all_device_description", smart_house.Camera, "Bedroom")
    true_ans = [smart_house.call(C2, "describe_device")]
    assert true_ans == res

    # only light in bedroom -- none
    res = smart_house.call(SHM, "get_all_device_description", smart_house.Light, "Bedroom")
    true_ans = []
    assert true_ans == res

def test_smartHouseManagement_calculate_total_power_consumption():
    smart_house.reset_globals() # delete all objects created
    L1 = smart_house.make(smart_house.Light, "Bedtable Light", "Bedroom", 250, "on", 50)
    L1_power_cons = smart_house.call(L1, "get_power_consumption")
    T1 = smart_house.make(smart_house.Thermostat, "Towel Thermostat", "Bathroom", 1200, "on", 18, 24) 
    T1_power_cons = smart_house.call(T1, "get_power_consumption") 
    T2 = smart_house.make(smart_house.Thermostat, "Bedroom Thermostat", "Bedroom", 3100, "off", 19, 21) 
    T2_power_cons = smart_house.call(T2, "get_power_consumption") 
    C1 = smart_house.make(smart_house.Camera, "Surveillance Camera", "Front Door", 200, "on", 12) 
    C1_power_cons = smart_house.call(C1, "get_power_consumption")
    
    SHM = smart_house.make(smart_house.SmartHouseManagement)
    res = smart_house.call(SHM, "calculate_total_power_consumption")
    assert L1_power_cons + T1_power_cons + T2_power_cons + C1_power_cons == res

    # turn C1 off
    smart_house.call(C1, "toggle_status")
    res = smart_house.call(SHM, "calculate_total_power_consumption")
    assert L1_power_cons  + T1_power_cons + T2_power_cons == res

    # test with filter search_room
    res = smart_house.call(SHM, "calculate_total_power_consumption", None, "Bedroom")
    assert L1_power_cons  + T2_power_cons == res

    # test with filter search_type
    res = smart_house.call(SHM, "calculate_total_power_consumption", smart_house.Thermostat)
    assert T1_power_cons  + T2_power_cons == res

    # test with filter search_type, search_room but this object is off
    res = smart_house.call(SHM, "calculate_total_power_consumption", smart_house.Camera, "Front Door")
    assert res == 0

    # turn camera on and test with filter search_type, search_room
    smart_house.call(C1, "toggle_status")
    res = smart_house.call(SHM, "calculate_total_power_consumption", smart_house.Camera, "Front Door")
    assert C1_power_cons == res
    
# endregion


# region ############## run the tests ###########################

def run_tests():
    import time
    test_results = {"pass": 0, "fail": 0, "error": 0}

    # parse arguments
    select_pattern = None               # runs only tests that match this pattern ---- e.g -- select light will only run light tests and not all tests 
    verbose = False                     # controls if verbos output is shown  -- useful for debugging or checking test data
    for arg in sys.argv[1:]:            # loop through all command line argum excluding script name 
        if arg.startswith("--select"):
            next_index = sys.argv.index(arg) + 1        # find index of the pattern 
            pattern = sys.argv[next_index]              # get pattern string 
            select_pattern = pattern.lower()            # convert to lower case for case insensitive 
        if arg == "--verbose":
            verbose = True

    # verbose: print only test_ variables
    if verbose:                                         # if verbos mode is on, print all starting with test_
        print("Variables starting with 'test_':")
        for name, obj in globals().items():
            if name.startswith("test_") and not callable(obj):      # print only variables and not functions ! 
                print(f"  {name} = {obj}")                          # print variable name and value 

    # run test functions
    for name, test in globals().items():                                  # introspection with globals() -- loop through ALL items 
        if not name.startswith("test_"):
            continue              # skip non-test names
        if not callable(test):
            continue              # skip variables
        if select_pattern and select_pattern not in name.lower():
            continue              # skip non-matching tests -- doesnt match select pattern 

        start = time.time()                                                     # set start time to track time taken to test
        try:                                                                    # try testing --> PASS FAIL ERROR 
            test()
            print(f"[PASS]  {name} ({round(time.time() - start, 4)}s)")
            test_results["pass"] += 1
        except AssertionError:
            print(f"[FAIL]  {name} ({round(time.time() - start, 4)}s)")
            test_results["fail"] += 1
        except Exception as e:
            print(f"[ERROR] {name} ({round(time.time() - start, 4)}s) -> {e}")
            test_results["error"] += 1

    print("\n--- Test Summary ---")
    for key in test_results:
        print(f"{key}: {test_results[key]}")


if __name__ == "__main__":
    
    run_tests()
    
# endregion