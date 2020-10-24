from talon import Module, actions, ui, fs
import logging as log
import socket
import fcntl
import threading # this code isn't threaded, but maybe talon is?

logCommands = False
def toggleCommandLogging(*args):
    global logCommands
    logCommands = not logCommands

clientInst = None

allCommandClients = {
    # "HOSTNAME" : PORT
}

class CommandClient(object):
    EMACS_TIMEOUT = 5

    def __init__(self, host, port):
        self.sock = None
        self.sock = self.makeSocket()
        self.host = host
        self.port = port
        if self.host == socket.gethostname():
            # necessary starting in emacs 26.1... seems to be a distinction between
            # localhost and 127.0.0.1
            self.host = "127.0.0.1"
        else:
            log.info("Requested emacs foreign host: {}:{}".format(self.host, self.port))
            from os.path import expanduser
            home = expanduser("~")
            self.port = int(open(home + "/.emacs_ports/" + self.host).read())
            self.host = "localhost"
            log.info("Remapping through local tunnel: {}:{}".format(self.host, self.port))

    def makeSocket(self):
        if self.sock:
            self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        fd = self.sock.fileno()
        old_flags = fcntl.fcntl(fd, fcntl.F_GETFD)
        fcntl.fcntl(fd, fcntl.F_SETFD, old_flags | fcntl.FD_CLOEXEC)

    def tryConnect(self):
        if not self.sock:
            self.makeSocket()

        self.sock.settimeout(0.50)
        try:
            self.sock.connect((self.host, self.port))
            log.info("Connected to emacs!")
            return True
        except socket.error as e:
            log.error("Error connecting to emacs: %s" % e)
        except socket.timeout as e:
            log.error("Connection to emacs timed out.")
        return False

    def dumpOther(self):
        # This will prevent mandimus from hanging when emacs stops responding,
        # as long as emacs isn't given focus.
        # global clientInst
        # clientInst = None

        self.sock.close()
        self.sock = None

    def sendMsg(self, msg):
        try:
            self.sock.settimeout(self.EMACS_TIMEOUT)
            try:
                self.sock.sendall((msg + "\n").encode('utf-8'))
                return True
            except UnicodeDecodeError as e:
                log.error(str(e))
                return False
        except socket.error as e:
            log.info("Socket error while sending: %s" % e)
            if e.errno == errno.EPIPE or e.errno == errno.EBADF:
                self.dumpOther()
                return False
            else:
                raise
        except Exception as e:
            log.info("Unknown error while sending: %s" % e)
            self.dumpOther()
            raise

    def recvMsg(self):
        self.sock.settimeout(self.EMACS_TIMEOUT)
        out = b""

        newData = None
        try:
            while b"\n" not in out:
                # print "in recv loop"
                newData = self.sock.recv(4096)
                out += newData
                # out += unicode(self.sock.recv(4096), 'utf-8')
        except socket.timeout as e:
            log.info("Emacs socket timeout.")
            self.dumpOther()
            return None
        except socket.error as e:
            log.info("Emacs socket error while receiving: %s" % e)
            if e.errno == errno.EPIPE or e.errno == errno.EBADF:
                self.dumpOther()
                return None
            else:
                raise
        except Exception as e:
            log.info("Unknown error while receiving: %s" % e)
            log.info("New data dump: [%s]" % newData)
            self.dumpOther()
            raise

        out = out.decode('utf-8')
        return out

    def runCmd(self, command, inFrame=True, dolog=False, allowError=False, queryOnly=True):
        """Run command optionally in particular frame,
        set True for active frame."""

        if command is None:
            raise Exception("Command must be a string.")

        if not self.sock:
            if not self.tryConnect():
                log.error("Can't run command, not connected: [%s]" % command)
                return "nil"

        wrapper = [u"{}"]

        if allowError:
            wrapper += [u'(condition-case err {} (error nil))']

        if inFrame:
            wrapper += [u'(with-current-buffer (window-buffer (if (window-minibuffer-p) (active-minibuffer-window) (selected-window))) {})']

        # See elisp function's documentation
        if not queryOnly:
            wrapper += [u'(let ((result {})) (md-generate-noop-input-event) result)']

        for w in reversed(wrapper):
            command = w.format(command)

        # have to delete newlines since they're the protocol delimeter
        command = command.replace("\n", "")

        if dolog or logCommands:
            log.info('emacs cmd: ' + command)

        self.sock.settimeout(None)
        if not self.sendMsg(command):
            log.info("Couldn't send message: [%s]" % command)
            return "nil"

        out = self.recvMsg()
        if out is None:
            log.error("Error getting result of command: [%s]" % command)
            return "nil"

        out = out.rstrip()

        if dolog or logCommands:
            log.info('emacs output: [%s]' % out)
        return out


EMACS_LOCK = threading.Lock()

def _choose_command_client(win):
    with EMACS_LOCK:
        global allCommandClients
        global clientInst

        key = None
        try:
            window_name = win.title
            host_and_port_string = window_name.rsplit("mandimus[")[1]
            host_and_port_string = host_and_port_string.split("]")[0]
            key = host_and_port_string.split(":")
            key[1] = int(key[1])
            key = tuple(key)
        except IndexError:
            # "emacs" not always in window title, this may just not be an emacs window
            #log.error(f"Couldn't get host and port from emacs window: {win.title}")
            return

        if key is None:
            return

        if key not in allCommandClients:
            allCommandClients[key] = CommandClient(key[0], key[1])

        if clientInst is not allCommandClients[key]:
            log.info("Switching to emacs: {}".format(key))
            clientInst = allCommandClients[key]

loggedNoEmacs=False
def runEmacsCmd(command, inFrame=True, dolog=False, allowError=False, queryOnly=True):
    with EMACS_LOCK:
        global clientInst
        global loggedNoEmacs
        if clientInst is None:
            if not loggedNoEmacs:
                log.info("Can't run command because not attached to any emacs: {}".format(command))
                loggedNoEmacs = True
            return ""
        return clientInst.runCmd(command, inFrame, dolog, allowError, queryOnly)

ui.register('win_focus', _choose_command_client)
ui.register('win_title', _choose_command_client)
