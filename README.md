#Android packaging
This tutorial demonstrates how to build and deploy an android app to your smartphone. The app was programmed with python and the kivy framework. Buildozer, the android debug bridge and the ubuntu subsystem were used to build, deploy and debug the android app. This tutorial works also perfectly fine for Ubuntu.

If anything is unclear, feel free to ask and write a comment.

▬ Links ► ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

ADB for Windows:
https://dl.google.com/android/reposit...

▬ Commands ► ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

►  Download project
https://github.com/adisa39/conversationAI-App.git

► Install buildozer:
git clone https://github.com/kivy/buildozer.git
cd buildozer
sudo python3 setup.py install

► Required libraries and tools:
- sudo apt-get update
- sudo apt-get install openjdk-8-jdk unzip python3 python3-pip ipython3 cython

- sudo apt-get install autoconf
- sudo apt install build-essential libltdl-dev libffi-dev libssl-dev python-dev
- sudo pip3 install --upgrade cython
- sudo apt-get install zip

► Build & Deployment
- To build, deploy and run the app run -> *buildozer android debug deploy run logcat*
- To display error message during the app testing on android device run -> adb -s [DEVICE_ID] logcat *:S python:D
- To deploy the app on connected android device run -> *adb -s [DEVICE_ID] install [app_name.apk]*

► Connection to phone

- Connect your android device to the system via USB
- go to settings, about phone and click on "Build Number" 7x to activate developer option.
- got to and enable USB DEBUG option.
- on your system powershell in adb directory, run -> *adb devices*

cmd:
- To start adb server at port 5555 run -> *adb tcpip 5555*

wsl2 Ubuntu terminal (ubuntu subsystem):
- To connect the terminal to your connected device run -> *adb connect [PHONE_IP_address]:5555* 