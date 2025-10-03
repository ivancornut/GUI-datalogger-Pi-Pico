# Datalogger Graphical User Interface for micropython devices

- [Datalogger GUI](#datalogger-graphical-user-interface-for-micropython-devices)
  * [General presentation](#general-presentation)
  * [Installation on a debian system](#installation-on-a-debian-system)
    + [Creation of desktop icon](#creation-of-a-desktop-icon)
  * [Installation on a macos system](#installation-on-a-mac)

## General presentation
<img width="758" height="644" alt="image" src="https://github.com/user-attachments/assets/6f7a00f6-389b-4f43-8199-4f0c8f5063ab" />


## Installation on a debian system
The best for this datalogger GUI is to use a debian system. 
To install the mpremote tool (the tool that allows your computer to communicate with your micropython device.
```
pip install mpremote
```
### Creation of a desktop icon
To make it easier for non technical people to use the tool you can install a clickable icon on the desktop that will launch the application.
To do this create a file: 
```
nano ~/Desktop/datalog_manag.desktop
```
If your on a French system replace Dekstop with Bureau in the filepath
Then inside the file:
```
[Desktop Entry]
Version=1.0
Exec=python /home/user/<your filepath>/GUI-datalogger-Pi-Pico/full_datalogger_management_gui.py
Icon= /home/user/<your filepath>/GUI-datalogger-Pi-Pico/icon.png
Name=GUI Datalogger
Comment= User interface for datalogger management
Encoding=UTF-8
Terminal=true
Type=Application
Categories=Application;Network;
```
Then an icon like this should appear on your desktop:

<img width="121" height="131" alt="image" src="https://github.com/user-attachments/assets/1898767e-f76d-4ce0-b9a7-0ce83e580162" />

## Installation on a mac
On MacOS: 
```
brew install python-tk
```

