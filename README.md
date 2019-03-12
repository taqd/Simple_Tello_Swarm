# Tello EDU Swarm Control

This is a simple framework to control multiple Tello EDU drone’s simultaneously.

The code is largely based upon the [‘Single_Tello_Test’]
(https://github.com/dji-sdk/Tello-Python/tree/master/Single_Tello_Test)
code provided by DJI.

* Video demonstration:
* Source code: https://github.com/PinkRobotics/Simple_Tello_Swarm

### Features:
* The ability to control a variable number of drones simultaneously
* Drones don't block each other (commands of one drone will not stop
  commands of the others to be sent)
* Drones now have a ‘wait’ command and can be triggered to continue by another
  drone
* Ctrl-C sends ‘emergency’ to all drones

### Limitations:
* All drones need to be on the same network so video streaming is not available.

### The demo: Putting out a 'fire'
The primary challenge here was ensuring that the drones take turns and don’t run
into each other while over the 'fire'.
* In turn, a drone goes to the 'fire' (the pink middle mat)
* Drops water on the 'fire' (indicated by going down and up)
* Returns to a 'lake' (the blue mats)
* Picks up water (down and up again)
* Loops several times.

### Details:
* Drone hardware: Tello EDU by Ryze/DJI
* Drone SDK: Tello SDK 2.0
* Programming language: Python

### Files:
* main.py - The primary control code
* tello.py - Holds the tello object code
* addresses.txt - Holds the IP addresses of each drone

   Note: This requires all drones to be on the same network -- use the ‘ap’
   command to do this.

* commands.txt - Holds the list of commands to be run (currently set to the
commands that ran the demo)

   Note: All commands are read, distributed to each drone, and then sent out.
   The response from a command triggers the next one to be sent.

### Command format in commands.txt:
Note: Drone count starts at 1 and is the first address in the address file, and
the trigger is optional:
```
t<drone number>, command[, trigger]
```

### Example 1:
First drone in address file takes off and lands
```
t1,cmd
t1,takeoff
t1,land
```

### Example 2:
First drone (t1) takes off, and second drone (t2) waits. Then once t1 has
finished taking off, it triggers t2 to take off. Then t1 will land, and then t2
will land.
```
t1,cmd
t1,takeoff,t2
t1,land

t2,cmd
t2,wait
t2,takeoff
t2,land
```

### Execution command:
```
python main.py addresses.txt commands.txt
```
