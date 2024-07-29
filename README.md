* RAPTOR-AI Qt version -- Draw/Track/Model
* Developed by: Mehrdad S. Beni and Hiroshi Watabe, 2024

RAPTOR-AI model Qt version that takes user input images marked locations on the uploaded image. The program is coupled with a custom-trained AI model that automatically detects and track these drawn locations. Based on these locations, the program then generates anthropomorphic phantom with that respective drawn and tracked locations. In addition, users have the ability to model shielding mateirlas. 

The model was developed on and for GNU/Linux operating systems ONLY. 

How to:

1. sudo apt update
2. sudo apt upgrade
3. sudo apt install python3 python3-pip python3-tk python3-pil python3-pil.imagetk python3-venv
4. python3 -m venv .venv (optional)
5. source .venv/bin/activate (optional)
6. python3 -m pip install PyQt6  or  pip install PyQt6
7. pip install pyqt6==6.4.2
8. pip install pyqt6-qt6==6.4.2
9. pip install PySide6   -- in case you need to use it only

Note: for the Qt version, we have noticed it will work with Wayland rather than xorg. Please switch if needed. 

Should you encounter any bugs or issues, please do not hesitate to contact me via email.

enjoy!
20240729
