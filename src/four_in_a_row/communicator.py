import socket


def get_local_ip():
    """best-effort LAN ip address of this machine (what a friend on the same
    network should connect to)"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


class Communicator:
    """
    Implements a non-blocking socket interface, where a message can be sent
    (immediately, after an initial connection has been created) and a message
    can be anticipated (after an initial connection has been created) and
    acted upon. The initial connection needs to be explicitly created by
    invoking connect(), which attempts establishment in a non blocking way.
    """

    WAIT_PERIOD = 100  # The wait period between two read attempts.
    BUFFER_SIZE = 1024  # The socket read / write buffer size (in bytes).
    CONNECT_TIMEOUT = 0.1  # The (client) connection timeout, set as a very

    # low value to create a connection "chance" (will
    # not happen if simply set to non blocking), but
    # without interfering the mainloop flow.

    def __init__(self, root, port, ip=None):
        """
        Constructor.
        :param root: the tkinter root (used for accessing the main loop).
        :param ip: the ip to connect to (client) or listen on (server).
        :param port: the port to connect to (client or listen on (server).
        :param server: true if the communicator is started in server mode,
                       otherwise false.
        """
        self.__root = root
        self.__port = port
        self.__ip = ip
        self.__socket = None
        self.__bound_func = None
        self.__server_socket = None
        self.closed = False
        self.__buffer = ""
        self.on_connected = None  # called once a connection is made
        self.on_disconnected = None  # called if the other side goes away
        # This means this communicator is a server communicator and is
        # responsible for trying and listening for an incoming connection.
        if self.__ip is None:
            self.__ip = get_local_ip()
            self.__server_socket = socket.socket()
            self.__server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__server_socket.bind(("", self.__port))
            self.__server_socket.listen(1)
            self.__server_socket.setblocking(0)  # non blocking.

    @property
    def address(self):
        return "%s:%s" % (self.__ip, self.__port)

    def close(self):
        """stops all polling and closes the sockets"""
        self.closed = True
        for sock in (self.__socket, self.__server_socket):
            if sock:
                try:
                    sock.close()
                except OSError:
                    pass
        self.__socket = self.__server_socket = None

    def connect(self):
        """
        Has to be invoked before any message sending and receiving can be
        accomplished. Uses the tkinter main loop to constantly listen on a
        given port for an incoming connection (server) or attempt and connect
        to a remote host via an IP and a port number.
        :return: None.
        """
        if self.__socket or self.closed:
            return
        try:
            # This is the server communicator, try and accept connections.
            if self.__server_socket is not None:
                self.__socket, _ = self.__server_socket.accept()
                self.__socket.setblocking(0)
                self.__server_socket.close()
            # This is the client communicator, try and connect (quickly).
            else:
                self.__socket = socket.socket()
                self.__socket.settimeout(self.CONNECT_TIMEOUT)
                self.__socket.connect((self.__ip, self.__port))
                self.__socket.setblocking(0)
            if self.on_connected:
                self.on_connected()
            self.__get_message()
        except socket.error:
            # Always close the socket if created, then make it none (this
            # way it is evident that a connection was not yet established).
            if self.__socket:
                self.__socket.close()
                self.__socket = None
            # Try again in a given interval.
            self.__root.after(self.WAIT_PERIOD, self.connect)

    def bind_action_to_message(self, func):
        """
        Binds a specific function to the event of receiving a message.
        :param func: the function.
        :return: None.
        """
        self.__bound_func = func

    def send_message(self, message):
        """
        Sends a message via the socket (if a connection is established).
        If the socket is not yet connected, does nothing (no retry).
        :param message: the message to be sent.
        :return: None.
        """
        if self.closed:
            return
        if not self.is_connected():
            self.__root.after(self.WAIT_PERIOD, lambda: self.send_message(message))
            return
        try:
            self.__socket.send((str(message) + "\n").encode())
        except OSError:
            pass

    def is_connected(self):
        """
        Returns true once a connection has been established.
        :return: true if a connection is established, else false.
        """
        return self.__socket is not None

    def __get_message(self):
        """
        Upon regular intervals, try and receive a message from the connection
        socket (if established). If the message is empty, it means the remote
        host was abruptly closed, so do nothing. Otherwise invoke a given 2nd
        order function on the received message. If no message was made
        available, the method re-tries after a fixed interval.
        :return: None.
        """
        if self.closed:
            return
        if self.is_connected():
            try:
                message = self.__socket.recv(Communicator.BUFFER_SIZE).decode()
                # Don't register again - the remote host is closed.
                if len(message) == 0:
                    self.__disconnected()
                    return
                self.__buffer += message
                while "\n" in self.__buffer:
                    msg, self.__buffer = self.__buffer.split("\n", 1)
                    if msg and self.__bound_func is not None:
                        self.__bound_func(msg)
            except BlockingIOError:
                pass
            except OSError:
                self.__disconnected()
                return
        self.__root.after(self.WAIT_PERIOD, self.__get_message)

    def __disconnected(self):
        self.close()
        if self.on_disconnected:
            self.on_disconnected()
        else:
            self.__root.destroy()
