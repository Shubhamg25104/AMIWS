import socket

class AMIClient:
    def __init__(self, host="172.16.2.18", port=5038, username="tvtroot", secret="root@tvt#123"):
        self.host = host
        self.port = port
        self.username = username
        self.secret = secret
        self.sock = None

    def connect(self):
        """Connect to AMI"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        
        # Read initial Asterisk banner
        banner = self._recv_response()
        print("Connected:\n", banner)

        self.login()

    def login(self):
        """Login to AMI"""
        action = (
            f"Action: Login\r\n"
            f"Username: {self.username}\r\n"
            f"Secret: {self.secret}\r\n"
            f"\r\n"
        )
        response = self.send_action(action)
        print("Login Response:\n", response)

    def send_action(self, action):
        """Send AMI action and return response"""
        if not self.sock:
            raise Exception("Not connected")

        self.sock.sendall(action.encode())
        return self._recv_response()

    def _recv_response(self):
        """Receive full AMI response"""
        data = b""
        while True:
            chunk = self.sock.recv(4096)
            data += chunk
            if b"\r\n\r\n" in data:
                break
        return data.decode()

    def ping(self):
        action = "Action: Ping\r\n\r\n"
        return self.send_action(action)

    def show_channels(self):
        action = "Action: CoreShowChannels\r\n\r\n"
        return self.send_action(action)

    def originate_call(self, channel, exten, context="default", priority=1):
        action = (
            f"Action: Originate\r\n"
            f"Channel: {channel}\r\n"
            f"Exten: {exten}\r\n"
            f"Context: {context}\r\n"
            f"Priority: {priority}\r\n"
            f"Async: true\r\n"
            f"\r\n"
        )
        return self.send_action(action)

    def close(self):
        if self.sock:
            self.sock.close()
            print("Connection closed")


# ✅ Usage
if __name__ == "__main__":
    ami = AMIClient()

    try:
        ami.connect()

        print("\n--- PING ---")
        print(ami.ping())

        print("\n--- CHANNELS ---")
        print(ami.show_channels())

        # Example call (optional)
        # print("\n--- ORIGINATE ---")
        # print(ami.originate_call("PJSIP/1001", "1002"))

    except Exception as e:
        print("Error:", e)

    finally:
        ami.close()