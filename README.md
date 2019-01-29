# Statics-simulation-python_2017

This was a project for class in numerical methods. I wrote a program in which user specifies a beam with supports. On that user can then place either continuous loads or point loads. The program then calculates internal forces in the beam as well as its displacement.

<image src="/program_example.jpg">

To run the program Gui.py has to be run. Program has to take user input in specific order otherwise it does not work as very little error handling is implemented. In the file bg.py the calculations for the struts are executed. In the file numericne_metode.py functions for numerical methods are written. It uses tkinter for graphics while calculations are mostly done with numpy and scipy.
