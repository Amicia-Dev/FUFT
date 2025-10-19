
# FU#T
[![CC_BY-NC-SA_4.0 License](https://img.shields.io/badge/License-CC_BY--NC--SA_4.0-purple)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

A fast simple P2P file transferring program.

![Screenshot](https://i.postimg.cc/4yk2VYfX/image-2025-10-19-050431667.png)


## Installation (Easy way)
1. Install python. (If you are here you probably already have python installed...)

2. Clone the repository and run the setup which corresponds to your OS. Done!

## (Not as easy way / manual)

1. Clone the repository
2. Setup a venv
3. Install dependencies ***urllib3*** & ***tqdm***
4. Set up a launch file or launch manually.
## Usage

1. Simply run the Launch file and it should delete the setup files and start the program.

2. Create a profile with ```profile create <SelectUserName>```. It will detect your public IP and select the default port as your options. You can specify an IP and port with options. See command options in help menu.

3. After you have created your profile, do ```profile show``` to see your user code, username, public ip and port.

4. You need to portforward the port for the program to be able to send files over separate networks. If you only want it for an internal network, you need to set the ip to your local ip manually. Use ```profile edit``` without any options to edit your profile.

5. Share your code with the person you want to be able to send or receive files with. The other person also needs to do the steps above and give you their code.

6. To add the other person as a contact, do ```contact add <TheirCodeHere>```. Then you can do ```contacts show``` to get a list of all your contacts. The other person needs to add your code as well.

7. To send/receive a file, tell the receiving person to do ```receive <SendersUsernameHere>``` so they can accept the file. Then run ```send <filenameAndPath> <ReceiversUserName>``` and the file should begin transfering.

8. Done! The transfered file should end up in the main directory.


## Disclaimer

This software is provided “as is” without any warranties, express or implied. The developer is not responsible for any data loss, corruption, security breaches, or other damages resulting from the use of this program. Users assume full responsibility for the safety and integrity of their files and systems when using this software.
