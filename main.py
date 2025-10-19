import os
import sys
import tqdm
import json
import base64
import codecs
import socket
import urllib3
import hashlib



def logoAsciiArt():
    return """
███████╗██╗   ██╗ ██╗ ██╗ ████████╗
██╔════╝██║   ██║████████╗╚══██╔══╝
█████╗  ██║   ██║╚██╔═██╔╝   ██║   
██╔══╝  ██║   ██║████████╗   ██║   
██║     ╚██████╔╝╚██╔═██╔╝   ██║   
╚═╝      ╚═════╝  ╚═╝ ╚═╝    ╚═╝   
Fast Unlimited File Transfer
https://amicia-dev.github.io
Made by Amicia-Dev
    """

def clearTerminal():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(logoAsciiArt())


def showHelp():
    return """
    help        Shows this help menu

    receive     Receive files: receive <fromContactName>

    send        Send files: send <filenameAndPath> <toUserName>

    contacts    Shows your contacts / allows you to add a contact by their code. Options for contacts: show, add, delete.
        show
        add <otherUsersCode>
        delete <userName>

    profile     Shows your profile and code / allows you to create your profile/code. Options for profile: show, create, edit.
        show
        create <selectAUserName> <yourPublicIPOrLeaveBlankForAuto> <portOrLeaveBlankForDefault>
        edit

    clear       Clears the terminal screen

    exit        Exits the program
    """




# File Integrity Checker
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def getFileHash(filePath):
    
    sha256 = hashlib.sha256()
    with open(filePath, "rb") as f:
        while chunk := f.read(8192):  # use larger buffer for hashing
            sha256.update(chunk)
    return sha256.hexdigest()




# File Receiver Stuff
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def receiveFiles(username):

    if not os.path.exists("contacts.json"):
        print("No contacts found. Please add a contact first.")
        return
    
    loadData = json.load(open("contacts.json", "r"))
    contact = next((c for c in loadData if c['username'] == username), None)
    if not contact:
        print(f"Contact '{username}' not found. Contact names are case sensitive.")
        return

    contactCode = contact['code']
        
    DemagicCode = codecs.decode(contactCode, 'rot_13')
    DemagicCode = base64.b64decode(DemagicCode).decode()

    codeArray = DemagicCode.split(":")

    uname, publicIP, port = codeArray

    print(f"\nLoaded profile data from {uname}\n")



    bufferSize = 8192

    receiverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiverSocket.bind(("0.0.0.0", int(port)))
    receiverSocket.listen(1)
    print(f"Waiting for incoming files...")
    
    conn, addr = receiverSocket.accept()
    if addr[0] != publicIP:
        print(f"Rejected connection from {addr[0]}!")
        conn.close()
        return

    clearTerminal()
    print(f"Connection established with {uname}")

    filename = conn.recv(bufferSize).decode()
    print(f"\nReceiving file: {filename}")

    conn.send(b"ACK")

    filesize = int(conn.recv(bufferSize).decode())
    bToMB = filesize / (1024 * 1024)
    shortSize = f"{bToMB:.2f}"
    print(f"File size: {shortSize} MB\n")



    progress = tqdm.tqdm(total=filesize, desc=f"Receiving {filename}", unit="B", unit_scale=True)
    remaining = filesize
    with open(filename, "wb") as f:
        while remaining > 0:
            data = conn.recv(min(bufferSize, remaining))
            if not data:
                raise ConnectionError("Connection lost during file transfer")
            f.write(data)
            remaining -= len(data)
            progress.update(len(data))
    progress.close()
    print(f"\n{filename} received!")

    receivedHash = b""
    while len(receivedHash) < 64:  # if SHA256 hash
        receivedHash += conn.recv(64 - len(receivedHash))
    receivedHash = receivedHash.decode("utf-8")

    localHash = getFileHash(filename)

    print("\nVerifying file integrity...")
    if receivedHash == localHash:
        print(f"[✓] {filename} transferred correctly!")
    else:
        print(f"[✗] WARNING!!!: {filename} corrupted during transfer!")

    conn.close()
    receiverSocket.close()




# File Sender Stuff
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def sendFiles(filenameAndPath, username):

    if not os.path.exists("contacts.json"):
        print("No contacts found. Please add a contact first.")
        return
    
    loadData = json.load(open("contacts.json", "r"))
    contact = next((c for c in loadData if c['username'] == username), None)
    if not contact:
        print(f"Contact '{username}' not found. Contact names are case sensitive.")
        return
    
    contactCode = contact['code']
        
    DemagicCode = codecs.decode(contactCode, 'rot_13')
    DemagicCode = base64.b64decode(DemagicCode).decode()

    codeArray = DemagicCode.split(":")

    uname, publicIP, port = codeArray

    print(f"\nLoaded profile data from {uname}\n")


    if not os.path.isfile(filenameAndPath):
        print(f"File '{filenameAndPath}' does not exist.")
        return

    FormattedFileName = os.path.basename(filenameAndPath)
    FormattedPath = os.path.abspath(filenameAndPath)

    print(f"Preparing to send file: {FormattedFileName} to {username}")




    bufferSize = 8192

    senderSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    senderSocket.connect((publicIP, int(port)))
    print(f"Connected to {uname}")

    senderSocket.send(FormattedFileName.encode())
    ack = senderSocket.recv(bufferSize)
    if ack != b"ACK":
        print("Failed to sync with server.")
        senderSocket.close()
        exit()
    
    filesize = os.path.getsize(FormattedPath)
    senderSocket.sendall(str(filesize).encode())

    progress = tqdm.tqdm(total=filesize, desc=f"Sending {FormattedFileName}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(FormattedPath, "rb") as f:
        while True:
            data = f.read(bufferSize)
            if not data:
                break
            senderSocket.sendall(data)
            progress.update(len(data))
    progress.close()
    print(f"File {FormattedFileName} sent successfully!")


    FileHash = getFileHash(FormattedPath)
    senderSocket.sendall(FileHash.encode("utf-8"))

    senderSocket.close()




# Contacts Stuff
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def addNewContact(codeInput):
    DemagicCode = codecs.decode(codeInput, 'rot_13')
    DemagicCode = base64.b64decode(DemagicCode).decode()
    try:
        userName, _ = DemagicCode.split(":", 1)
        contact = {
            "username": userName,
            "code": codeInput
        }
        if os.path.exists("contacts.json"):
            with open("contacts.json", "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        else:
            data = []

        data.append(contact)

        with open("contacts.json", "w") as f:
            json.dump(data, f, indent=4)
        print(f"Contact {userName} added successfully.")
    except ValueError:
        print("Invalid code. Please try again.")
        return
    
def viewContacts():
    if os.path.exists("contacts.json"):
        with open("contacts.json", "r") as f:
            try:
                data = json.load(f)
                if not data:
                    print("No contacts found.")
                    return
                print("Your Contacts:")
                for contact in data:
                    print(f"{contact['username']}")
            except json.JSONDecodeError:
                print("No contacts found.")
    else:
        print("No contacts found.")

def deleteContact(chosenContact):
    if os.path.exists("contacts.json"):
        with open("contacts.json", "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print("No contacts found.")
                return
        updatedData = [contact for contact in data if contact['username'] != chosenContact]
        if len(updatedData) == len(data):
            print(f"No contact named {chosenContact} found.")
            return
        with open("contacts.json", "w") as f:
            json.dump(updatedData, f, indent=4)
        print(f"Contact {chosenContact} deleted successfully.")
    else:
        print("No contacts found.")






# Profile Stuff
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def profileCreate(userName, publicIP, port):
    setUserName = userName
    setPublicIP = publicIP if publicIP else getPublicIP()
    setPort = port if port else "20847"
    codeMagic = base64.b64encode(f"{setUserName}:{setPublicIP}:{setPort}".encode()).decode()
    codeMagic = codecs.encode(codeMagic, 'rot_13')
    profile = {
        "username": setUserName,
        "publicIP": setPublicIP,
        "port": setPort,
        "code": codeMagic,
    }
    with open("profile.json", "w") as f:
        json.dump(profile, f)
    print("Profile created successfully. Use ´profile show´ to view your profile and code.")
    
def getPublicIP():
    http = urllib3.PoolManager()
    resp = http.request("GET", "ifconfig.me/ip")
    if resp.status == 200:
        return resp.data.decode('utf-8').strip()
    else:
        return "Could not automatically fetch IP, please enter manually."

def profileEdit():
    if not os.path.exists("profile.json"):
        print("No profile found. Please create a profile first using 'profile create <username> <publicIPOrLeaveBlankForAuto> <portOrLeaveBlankForDefault>'.")
        return
    with open("profile.json", "r") as f:
        try:
            profile = json.load(f)
        except json.JSONDecodeError:
            print("Profile data is corrupted. Please delete the profile and create a new one.")
            return
    newUserName = input(f"Enter new username (current: {profile['username']}): ").strip()
    newPublicIP = input(f"Enter new public IP (current: {profile['publicIP']}, leave blank for auto): ").strip()
    newPort = input(f"Enter new port (current: {profile['port']}, leave blank for default): ").strip()
    if newPublicIP == "":
        newPublicIP = getPublicIP()
    if newUserName:
        profile['username'] = newUserName
    if newPublicIP:
        profile['publicIP'] = newPublicIP
    if newPort:
        profile['port'] = newPort
    codeMagic = base64.b64encode(f"{profile['username']}:{profile['publicIP']}:{profile['port']}".encode()).decode()
    codeMagic = codecs.encode(codeMagic, 'rot_13')
    profile['code'] = codeMagic
    with open("profile.json", "w") as f:
        json.dump(profile, f)
    print("Profile updated successfully.")

def profileShow():
    if not os.path.exists("profile.json"):
        print("No profile found. Please create a profile first using 'profile create <username> <publicIPOrLeaveBlankForAuto> <portOrLeaveBlankForDefault>'.")
        return
    with open("profile.json", "r") as f:
        try:
            profile = json.load(f)
        except json.JSONDecodeError:
            print("Profile data is corrupted. Please delete the profile and create a new one.")
            return
    print("Your Profile:")
    print(f"Username: {profile['username']}")
    print(f"Public IP: {profile['publicIP']}")
    print(f"Port: {profile['port']}")
    print(f"Code: {profile['code']}")






# Main Command Loop
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


def main():
    clearTerminal()

    while True:
        userInput = input("FU#T > ").strip().split()

        if len(userInput) == 0:
            continue

        command = userInput[0].lower()



        if command == "help":
            print(showHelp())




        elif command == "receive":
            if len(userInput) < 2:
                print("Please specify a username (Case Sensitive) to receive files from. 'receive <fromContactName>'")
                continue
            username = userInput[1]
            receiveFiles(username)




        elif command == "send":
            if len(userInput) < 3:
                print("Please specify a filename/path and a username(Case Sensitive) to send files to. send <filenameAndPath> <toUserName>")
                continue
            filenameAndPath = userInput[1]
            username = userInput[2]
            sendFiles(filenameAndPath, username)




        elif command == "contacts" or command == "contact":
            if len(userInput) < 2:
                print("Please specify a contacts option: add, show, delete.")
                continue
            contactOption = userInput[1].lower()
            if contactOption == "add":
                if len(userInput) < 3:
                    print("Please specify a contact code. 'contacts add <otherUsersCode>'")
                    continue
                addNewContact(userInput[2])

            elif contactOption == "show":
                viewContacts()

            elif contactOption == "delete":
                if len(userInput) < 3:
                    print("Please specify a username(Case Sensitive) to delete. 'contacts delete <userName>'")
                    continue
                deleteContact(userInput[2])
            else:
                print("Unknown contacts option. Use: add, show, delete.")



        elif command == "profile":
            if len(userInput) < 2:
                print("Please specify a profile option: create, edit, show.")
                continue
            profileOption = userInput[1].lower()
            if profileOption == "create":
                if len(userInput) < 3:
                    print("Please specify a username and your public IP or leave IP blank for auto.")
                    continue
                if len(userInput) == 3:
                    userInput.append("")  # Append empty string for public IP if not provided
                if len(userInput) == 4:
                    userInput.append("")  # Append empty string for port if not provided
                profileCreate(userInput[2], userInput[3], userInput[4])
            elif profileOption == "edit":
                profileEdit()
            elif profileOption == "show":
                profileShow()
            else:
                print("Unknown profile option. Use: create, edit, show.")




        elif command == "clear":
            clearTerminal()

        elif command == "exit":
            sys.exit(0)

        else:
            print("Unknown command. Type 'help' for a list of commands.")

if __name__ == "__main__":
    main()


