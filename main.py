# ##############################################################################
#                                                                              #
#    ____   _         _        ____         _             _    _               #
#   |  _ \ (_) _ __  | | __   |  _ \  ___  | |__    ___  | |_ (_)  ___  ___    #
#   | |_) || || '_ \ | |/ /   | |_) |/ _ \ | '_ \  / _ \ | __|| | / __|/ __|   #
#   |  __/ | || | | ||   <    |  _ <| (_) || |_) || (_) || |_ | || (__ \__ \   #
#   |_|    |_||_| |_||_|\_\   |_| \_\\___/ |_.__/  \___/  \__||_| \___||___/   #
#                                                                              #
# ##############################################################################
# This software comes with no promises. Use at your own risk.


# Simple swarm control for Tello EDU (SDK 2.0) drones by Ryzn/DJI
#   https://github.com/PinkRobotics/Simple_Tello_Swarm
#
# Features:
#   - Control variable number of drones simultaneously
#   - Drones don't block each other (commands of one drone will not stop
#     commands of the others to be sent)
#   - Drones now have a command and can be triggered to continue by
#     another drone
#   - Ctrl-C sends emergency to all drones
#
# Limitations:
#   - All drones need to be on the same network so video streaming is not
#     available.


import sys
import time
import signal
import socket
import threading
from tello import Tello

#The set of Tello drones
tellos = []

#The socket for handling commands and acknowledgements
socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.bind(('',8889))


#Create the signal handler to capture Ctrl-C and stop drones
def signal_handler(sig, frame):
    print('You pressed Ctrl-C! - Emergency stop sent to all drones')
    for tello in tellos:
        tello.send_command('emergency')
    socket.close()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


#The thread that will read the acknowledgements and trigger commands
def _receive_thread():
    while True:

        #Listen to the socket
        response, (ip, port) = socket.recvfrom(1024)
        response = response.rstrip()

        #Find the tello that this response came from
        for tello in tellos:
            if ip != tello.address:
                continue

            #Each tello stores the command that was just executed, last_command
            if tello.last_command == 'command' and response == 'ok':
                print 'Tello %s (%s) has connected' % (tello.name,ip)
                tello.online = True

            elif tello.last_command == 'battery?':
                tello.battery = int(response)
                if tello.battery <= 10:
                    print 'Tello %s (%s) LOW BATTERY: %s' % (tello.name, ip, response)
                    tello.online = False
                    tello.error = True
                else:
                    print 'Tello %s (%s) Battery: %s' % (tello.name, ip, response)

            elif response == 'error':
                print 'Tello %s (%s) ERROR on %s : %s' % \
                    (tello.name, ip, tello.last_command, response)
                tello.error = True

            else:
                print 'Tello %s (%s) %s: %s' % \
                    (tello.name, ip, tello.last_command, response)

            #Check if there was a trigger in the previous command
            if tello.last_trigger != '':

                #If there was, find which tello it was referring to
                trigger_num = int(tello.last_trigger[1:]) - 1 #ignore the 't' and adjust

                #Set that tello up to be triggered
                tellos[trigger_num].wait = False
                tello.last_trigger = ''

                #Trigger the tello
                print 'Tello %s is triggering Tello %s' % (tello.name,trigger_num)
                tellos[trigger_num].ready_next_command();

            #Prepare and (possibly) send the next command
            tello.ready_next_command()


#Start the receiving thread
receive_thread = threading.Thread(target=_receive_thread)
receive_thread.daemon = True
receive_thread.start()

#Read in the tello ip addresses from a file
tello_addresses_filename = sys.argv[1]
tello_addresses_file = open(tello_addresses_filename, "r")
tello_addresses = tello_addresses_file.readlines()

#Create the tello drone objects
tello_counter = 1
for tello_address in tello_addresses:
    t = Tello(tello_address.rstrip(),socket)
    t.name = tello_counter
    tello_counter += 1
    tellos.append(t)
tello_addresses_file.close()

#Read in the command file
commands_filename = sys.argv[2]
commands_file = open(commands_filename, "r")
commands = commands_file.readlines()

#Add the commands to each tello
for command in commands:

    #Ignore commented lines (shown with hash), empty lines or white space
    command = command.rstrip()
    if command == '' or command.find('#') != -1:
        continue

    #Parse the command string to determine drone number
    #Command string format: t<drone number>,<command>, for example: t1,takeoff
    command_list = command.split(',')
    tello_num_str = 't1' #default if unspecified
    triggers = ''
    if len(command_list) == 1:
        command = command_list[0]
    elif len(command_list) == 2:
        tello_num_str = command_list[0]
        command = command_list[1]
    else:
        tello_num_str = command_list[0]
        command = command_list[1]
        triggers = command_list[2]
    tello_num = int(tello_num_str[1:]) - 1 #ignore the 't' and adjust for 0-index

    #Add the full command string to the drones command list
    if triggers == '':
        tellos[tello_num].commands.append(command)
    else:
        tellos[tello_num].commands.append(command + ',' + triggers)
        #print 'Test: %s %s' % (tello_num,command)
commands_file.close()

#Start each of the drones
for tello in tellos:
    if len(tello.commands) > 0:
        tello.start_default()

#Give the drones a moment to start
time.sleep(2)

#Wait for the other drones to finish
while tello_counter != 0:

    for tello in tellos:

        #Disconnect a tello that ran out of commands
        if tello.online == True and len(tello.commands) == 0:
            print 'Tello %s (%s) has disconnected' % (tello.name, tello.address)
            tello.online = False
            tello_counter = tello_counter - 1

        #Disconnect a tello that never started
        if tello.online == False and tello.battery == 0:
            print 'Tello %s (%s) is presumed offline' % (tello.name, tello.address)
            tello.battery = -1
            tello_counter = tello_counter - 1

    #If no more tellos are online
    if tello_counter <= 1:
        break

    #To slow the loop to save CPU
    time.sleep(.1)

print 'All tello\'s finished'
