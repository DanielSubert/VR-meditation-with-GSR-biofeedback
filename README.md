# VR-meditation-with-GSR-biofeedback
This prototype VR environment integrates a Galvanic Skin Response (GSR) sensor via a Raspberry Pi Pico to deliver real-time biofeedback during meditation. The system records a user's baseline skin conductivity and triggers rainfall in the VR environment when current GSR levels rise above this baseline, indicating ineffective meditation to the user. When the user's GSR remains at or below baseline, the environment stays calm, reinforcing successful meditation. While the core functionality is implemented, this prototype still requires refinement of the baseline calculation to ensure accurate and meaningful feedback. 

The original Unity environment was developed by @BerkcanAltungoz. The integration of the meditation task, user controls, and GSR sensor was carried out by the project author with some assistance from Matteo R. Teagno. The work was supervised by Dr. Martin Schmettow (@schmettow) and Dr. Funda Yildirim, and completed as part of the "Training, Sensors and Simulation" course in the Human Factors and Engineering Psychology Master’s program at the University of Twente.

The following is a list of all included files and scripts, along with their descriptions.

**Report.pdf** - written report about the full development, current state of the system, the data analysis conducted and the limitations and future improvements of the project. 

**GSR-UNITY Feedback - Set.up.pdf** - instructional document on how to recreate the exact set-up of this project.

**Main.py** - CircuitPython code meant to be saved onto the Pico board as main.py to record and send the GSR data via the serial port.

**File_Maker.py** - Python code running in Visual Studio Code to read the serial port, compute the baseline and the normalised percentage change to output either a 0 or 1 into a text file saved in the Unity Directory.

**RelaxAndMeditationVR-main 2** - The entire Unity project; contains the project scene called GSR Feedback (Assets/Scenes/GSR Feedback); Contains the RainScript.cs code which is the code responsible for changing the weather according to the text file output.
