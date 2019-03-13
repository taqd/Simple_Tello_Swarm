 ##############################################################################
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

#Object that holds all per-tello information
#One tello object is created for each IP in the address file
class Tello:

    def __init__(self, ip_address, socket):
        #The communication socket
        self.socket = socket

        #Address and name information
        self.name = ''
        self.address = ip_address

        #List of commands and triggers for this Tello
        self.commands = []
        self.last_command = ''
        self.last_trigger = ''

        #Tello state information
        self.online = False
        self.battery = 0
        self.error = False
        self.wait = False

    #Send a command to the drone
    def send_command(self, command):

        #Check if there is a trigger in the command
        trigger = ''
        if command.find(',') != -1:
            command,trigger = command.split(',')

        #Send the command (this doesn't wait for the response)
        self.socket.sendto(command.encode('utf-8'), (self.address,8889))

        #Set the last_ stuff, and remove the command from the list
        self.last_command = command
        self.last_trigger = trigger
        if len(self.commands) > 0:
            self.commands.pop(0)

    #Prepare the next command
    def ready_next_command(self):
        if len(self.commands) == 0:
            print 'Tello %s (%s) has no more instructions' % (self.name, self.address)
            return

        if self.commands[0].find('wait') != -1 and self.wait == False:
            self.commands.pop(0)
            self.wait = True
            return

        #Send the next command
        self.send_command(self.commands[0])

    #The default 'start drone' action (simplifies command files)
    def start_default(self):
        self.commands.insert(0,'command')
        self.commands.insert(1,'battery?')
        self.commands.insert(2,'mon')
        self.commands.insert(3,'mdirection 0')
        self.commands.insert(4,'speed 50')

        self.send_command(self.commands[0])
