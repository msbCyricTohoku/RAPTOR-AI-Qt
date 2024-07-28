* RAPTOR-AI Qt version -- Draw/Track/Model
* Developed by: Mehrdad S. Beni and Hiroshi Watabe, 2024

RAPTOR-AI model Qt version that takes user input images marked with "x" (note must be drawn) locations on the uploaded image. The program is coupled with a custom-trained AI model that automatically detects and track these drawn locations. Based on these locations, the program then generates anthropomorphic phantom with that respective drawn and tracked locations. 

The model was developed on and for GNU/Linux operating systems ONLY. 

How to:

1. sudo apt update
2. sudo apt upgrade
3. sudo apt install python3 python3-pip python3-tk python3-pil python3-pil.imagetk python3-venv
4. python3 -m venv .venv
5. source .venv/bin/activate
6. python3 -m pip install PyQt6  or  pip install PyQt6
7. pip install PySide6   -- in case you need to use it only

Should you encounter any bugs or issues, please do not hesitate to contact me via email at: ben.sh@tohoku.ac.jp or ben.sh@my.cityu.edu.hk

enjoy!
20240725
