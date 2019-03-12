# ########################################################################
#                                                                        #
#  ____   _         _      ____         _             _    _             #
# |  _ \ (_) _ __  | | __ |  _ \  ___  | |__    ___  | |_ (_)  ___  ___  #
# | |_) || || '_ \ | |/ / | |_) |/ _ \ | '_ \  / _ \ | __|| | / __|/ __| #
# |  __/ | || | | ||   <  |  _ <| (_) || |_) || (_) || |_ | || (__ \__ \ #
# |_|    |_||_| |_||_|\_\ |_| \_\\___/ |_.__/  \___/  \__||_| \___||___/ #
#                                                                        #
# ########################################################################

# Simple swarm control for Tello EDU (SDK 2.0) drones by Ryzn/DJI
# https://github.com/PinkRobotics/Simple_Tello_Swarm

# This software comes with no promises. Use at your own risk.


class Tello:

    def __init__(self, ip_address, socket):
        #The communication socket
        self.socket = socket

        #Set address and name information
        self.name = ''
        self.address = ip_address

        #List of commands for this Tello
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
        trigger = ''
        if command.find(',') != -1:
            command,trigger = command.split(',')

        self.socket.sendto(command.encode('utf-8'), (self.address,8889))
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

        next_command = self.commands[0]
        self.send_command(next_command)

    #The default 'start drone' action
    def start_default(self):
        self.commands.insert(0,'command')
        self.commands.insert(1,'battery?')
        self.commands.insert(2,'mon')
        self.commands.insert(3,'mdirection 0')
        self.commands.insert(4,'speed 50')
        self.commands.append('land')
        self.send_command(self.commands[0])
