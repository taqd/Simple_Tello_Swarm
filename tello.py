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

        #Tello state information
        self.online = False
        self.battery = 0
        self.error = False

    #Send a command to the drone
    def send_command(self, command):
        self.socket.sendto(command.encode('utf-8'), (self.address,8889))
        self.last_command = command

    #Prepare the next command
    def ready_next_command(self):
        self.commands.pop(0)
        if len(self.commands) == 0:
            print 'Tello %s (%s) has no more instructions' % (self.name, self.address)
            return

        next_command = self.commands[0]
        self.send_command(next_command)

    #The default 'start drone' action
    def start_default(self):
        self.commands.insert(0,'command')
        self.commands.insert(1,'battery?')
        self.commands.insert(2,'takeoff')
        self.commands.append('land')
        self.send_command(self.commands[0])
