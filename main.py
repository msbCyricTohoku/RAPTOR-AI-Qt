'''
 * RAPTOR-AI Qt version
 * Developed by: Mehrdad S. Beni and Hiroshi Watabe -- 2024

 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QLineEdit, QGridLayout
)
from PyQt6.QtGui import QPixmap, QIcon, QImage
from PyQt6.QtCore import Qt  #this version of the program uses PyQt6
from PIL import Image
from PIL.ImageQt import ImageQt
import subprocess
import os
import csv
from pathlib import Path
from codegen import phantom  ##this calls the human phantom generator module

class InferenceApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RAPTOR-AI")
        self.setGeometry(100, 100, 1280, 800)  #change this to match your desired resolution and screen size

        icon_path = os.path.abspath("resources/icon.ico")  #load the icon for Raptor-AI
        self.setWindowIcon(QIcon(icon_path))

        self.input_image_path = None
        self.output_image_path = None

        #these are the user-controlled parameters from the GUI
        self.radioisotope = "Cs-137"
        self.particle = "photon"
        self.activity = "1000"
        self.tally = "photon"
        self.maxcas = "1000"
        self.maxbch = "10"
        self.scale = "1"
        self.sx = "0.0"
        self.sy = "0.0"
        self.sz = "10.0"

        #create the main widget here
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.main_layout = QVBoxLayout(self.main_widget)

        #create button frame here, pretty standard qt stuff
        self.button_layout = QHBoxLayout()

        self.upload_btn = QPushButton("Open")
        self.upload_btn.clicked.connect(self.upload_image)
        self.button_layout.addWidget(self.upload_btn)

        self.run_inference_btn = QPushButton("Run")
        self.run_inference_btn.clicked.connect(self.run_inference)
        self.run_inference_btn.setEnabled(False)
        self.button_layout.addWidget(self.run_inference_btn)

        self.about_btn = QPushButton("About")
        self.about_btn.clicked.connect(self.show_about)
        self.button_layout.addWidget(self.about_btn)

        self.quit_btn = QPushButton("Quit")
        self.quit_btn.clicked.connect(self.close)
        self.button_layout.addWidget(self.quit_btn)

        self.main_layout.addLayout(self.button_layout)

        #create image frame -- this store the uploaded user image and the detected/inferred image
        self.image_layout = QHBoxLayout()
        self.image_layout.setSpacing(20)  # Set spacing between images

        #the layout, to keep the buttons, frames and line edits in correct position
        #this also ensures that if the window size changes, the features will still be in a
        #correct position and not messed up
        self.user_features_layout = QVBoxLayout()
        self.original_label = QLabel("User Features")
        self.user_features_layout.addWidget(self.original_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.original_image_label = QLabel()
        self.user_features_layout.addWidget(self.original_image_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.image_dimensions_label = QLabel()
        self.user_features_layout.addWidget(self.image_dimensions_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.image_layout.addLayout(self.user_features_layout)

        #this is for the detected images
        self.detected_features_layout = QVBoxLayout()
        self.inferred_label = QLabel("Detected Features")
        self.detected_features_layout.addWidget(self.inferred_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.inferred_image_label = QLabel()
        self.detected_features_layout.addWidget(self.inferred_image_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.inferred_image_dimensions_label = QLabel()
        self.detected_features_layout.addWidget(self.inferred_image_dimensions_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.image_layout.addLayout(self.detected_features_layout)

        self.main_layout.addLayout(self.image_layout)
        self.entry_layout = QGridLayout()

        custom_labels = [
            ("Radioisotope:", self.radioisotope),
            ("Particle:", self.particle),
            ("Activity (Bq):", self.activity),
            ("Tally:", self.tally),
            ("maxcas:", self.maxcas),
            ("maxbch:", self.maxbch),
            ("Scale (> 1):", self.scale),
            ("SX (cm):", self.sx),
            ("SY (cm):", self.sy),
            ("SZ (cm):", self.sz)
        ]

        self.entries = []
        for i in range(5):
            label = QLabel(custom_labels[i][0])
            self.entry_layout.addWidget(label, i, 0)
            entry = QLineEdit()
            entry.setText(custom_labels[i][1])
            self.entry_layout.addWidget(entry, i, 1)
            self.entries.append(entry)

        for i in range(5, 10):
            label = QLabel(custom_labels[i][0])
            self.entry_layout.addWidget(label, i-5, 2)
            entry = QLineEdit()
            entry.setText(custom_labels[i][1])
            self.entry_layout.addWidget(entry, i-5, 3)
            self.entries.append(entry)

        self.main_layout.addLayout(self.entry_layout)

    def upload_image(self):
        options = QFileDialog.Option.ReadOnly
        self.input_image_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Image Files (*.png *.jpg *.bmp)", options=options)
        if self.input_image_path:
            img = Image.open(self.input_image_path)

            self.original_image_width, self.original_image_height = img.size

            #this reports the size of the image to the user which determine the simulation domain size in cm
            self.image_dimensions_label.setText(f"Domain dimensions: Width: {self.original_image_width} cm, Height: {self.original_image_height} cm")

            self.display_image(self.input_image_path, self.original_image_label)
            self.run_inference_btn.setEnabled(True)

    def run_inference(self):
        try:
            yolov5_path = 'yolov5'
            weights_path = 'trained_model/raptor-20240725.pt'
            source_dir = self.input_image_path
            output_dir = 'output'

            #change --conf value if you wish to tweak the confidence for detected marks
            subprocess.run([
                'python3', f'{yolov5_path}/detect.py',
                '--weights', weights_path,
                '--img', '640',
                '--conf', '0.7',
                '--source', source_dir,
                '--project', output_dir,
                '--name', 'results',
                '--save-csv'
            ], check=True)

            output_base_dir = Path(output_dir)
            all_dirs = [d for d in output_base_dir.iterdir() if d.is_dir() and d.name.startswith('results')]

            latest_dir = max(all_dirs, key=os.path.getmtime)
            csv_file = latest_dir / 'predictions.csv'
            center_coords_file = latest_dir / 'center_coordinates.txt'
            #this file saves the shield coordinate in a shield_coordinate.txt 
            shield_coords_file = latest_dir / 'shield_coordinates.txt'

            #the detected box center will be determined and used as the location of human phantom on the defined domain
            def compute_center(xmin, ymin, xmax, ymax):
                center_x = (xmin + xmax) / 2
                center_y = (ymin + ymax) / 2
                #flip y-axis -- phits consider different origin point this ensures a correct matching
                flipped_center_y = self.original_image_height - center_y
                return center_x, flipped_center_y

            #pass the variables for shield to the codegen module call
            def sheild_coordinate_pass(xmin, xmax, ymin, ymax):
                xmins = xmin
                xmaxs = xmax
                ymins = ymin
                ymaxs = ymax
                return xmins, xmaxs, ymins, ymaxs

            #this is to save the xmin, xmax, ymin, ymax of the shield, given the shield assumed to be a slab
            def save_shield_coordinates(coords):
                with open(shield_coords_file, 'w') as txtfile:
                    txtfile.write('xmin,xmax,ymin,ymax\n')
                    for item in coords:
                        image_name, prediction, confidence, xmin, xmax, ymin, ymax = item
                        txtfile.write(f'{xmin},{xmax},{ymin},{ymax}\n')

            #here the coordinate of the detected boxes will be saved into a csv file
            center_coords = []
            #here the coordinate of the detected shield box will be saved to a txt file
            shield_coords = []

            with open(csv_file, 'r') as csvfile:
                csvreader = csv.DictReader(csvfile)

                countx = 0
                shieldcount = 0  #initialize a counter for the shield since it can be many!
                for row in csvreader:
                    image_name = row['Image Name']
                    prediction = row['Prediction']
                    confidence = row['Confidence']
                    coordinates = row['Coordinates'].strip('"').split(',')

                    xmin, ymin, xmax, ymax = map(float, coordinates)

                    if prediction in ['lead', 'concrete', 'pe', 'custom']:
                        shieldcount += 1

                        xmins, xmaxs, ymins, ymaxs = sheild_coordinate_pass(xmin, xmax, ymin, ymax)

                        shield_coords.append((image_name, prediction, confidence, xmin, xmax, ymin, ymax))
                    else:
                        countx += 1
                        center_x, center_y = compute_center(xmin, ymin, xmax, ymax)
                        center_coords.append((image_name, prediction, confidence, center_x, center_y))

            print("Total number of positions detected and processed:", countx)
            print("Total number of shields detected and processed:", shieldcount)

            #here the center coordinate will be sorted by x and y
            center_coords.sort(key=lambda x: (x[3], x[4]))
            save_shield_coordinates(shield_coords)

            #here write the sorted center coordinates to the text file and generate a new file for each item
            with open(center_coords_file, 'w') as txtfile:
                txtfile.write('x,y\n')
                count = 0
                for item in center_coords:
                    count += 1
                    image_name, prediction, confidence, center_x, flipped_center_y = item
                    txtfile.write(f'{center_x},{flipped_center_y}\n')

                    phantom(countx, count, self.original_image_width, self.original_image_height, center_x, flipped_center_y,
                            self.radioisotope, self.particle,
                            self.activity, self.tally,
                            self.maxcas, self.maxbch,
                            self.scale, self.sx,
                            self.sy, self.sz, shieldcount, xmins, xmaxs, ymins, ymaxs, shield_coords)

            #inferred image path from the latest results directory
            inferred_image_path = latest_dir / Path(self.input_image_path).name
            #print(f"Inferred image path: {inferred_image_path}")
            if inferred_image_path.exists():
                self.display_image(inferred_image_path, self.inferred_image_label)
                #display the dimensions under the inferred image
                self.inferred_image_dimensions_label.setText(f"Domain dimensions: Width: {self.original_image_width} cm, Height: {self.original_image_height} cm")
            else:
                print("Inferred image does not exist.")
        except subprocess.CalledProcessError as e:
            print(f"Inference process failed: {e}")
            QMessageBox.critical(self, "Inference Error", f"Inference process failed: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def display_image(self, image_path, label):
        try:
            max_width, max_height = 400, 400
            img = Image.open(image_path)

            #determines the scaling factor while preserving aspect ratio -- note this preserves aspect ratio
            width_ratio = max_width / img.width
            height_ratio = max_height / img.height
            scaling_factor = min(width_ratio, height_ratio)

            #determines the new dimensions
            new_width = int(img.width * scaling_factor)
            new_height = int(img.height * scaling_factor)

            #resize the image here, given that images might have different resolutions
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            img = ImageQt(img).copy()  #convert Image to ImageQt and copy to avoid garbage collection
            qimage = QImage(img)  #convert ImageQt to QImage, got stuck here with PyQt5, just changed my code to PyQt6 and it worked so keep as it is
            pixmap = QPixmap.fromImage(qimage)
            label.setPixmap(pixmap)
            label.setFixedSize(new_width, new_height)
            #print(f"Displayed image: {image_path}")
        except Exception as e:
            print(f"Failed to display image: {e}")
            QMessageBox.critical(self, "Image Display Error", f"Failed to display image: {e}")

    def show_about(self):
        QMessageBox.information(self, "RAPTOR-AI", "RAPTOR-AI\nVersion 1.0\nDeveloped by:\nMehrdad S. Beni\nHiroshi Watabe\nTohoku University, 2024")

#run the raptor here and enjoy
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = InferenceApp()
    mainWin.show()
    sys.exit(app.exec())
