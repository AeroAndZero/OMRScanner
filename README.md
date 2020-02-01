# AOS - Advance OMR Scanner
Check [release](https://github.com/AeroAndZero/OMRScanner/releases) of the repository for the latest version.
## How To Use ?
To use aos first you need to create preset for specific type of OMR sheet
### 1. Create A Preset
![Preset Window](/images/presetWindow.png)
- click on the plus button
- Open a blank omr sheet
- **If your OMR is not showing up in the "Detected OMR" panel, try tweaking the Edge Detection Settings. Make sure you hit apply to see and apply changes as shown below :**
\
![Edge Detection Settings](/images/edgeDetectionSettings.gif)
\
### 1.1 Add A Batch
![Add A Batch](/images/addBatch.png)\
**Batches are basically a way to tell the software where the MCQ is.**\
*Batches are important for scanning. Every preset should've atleast 1 batch.*
- After you add a batch you need to Pick the place of following questions
  1. First Option of First question
  2. Second Option of **First question**
  3. First Option of Second Question
- Hit the Pick Button And Click on the option place on Detected OMR panel's image as shown below :\
\
![batchPicking](/images/batch1Picking.gif)\
**After you specify all the parameters you will get an immediate preview of how your MCQs will be scanned.**
- Make Sure All The circles are in purple color. Otherwise your scan will not perform well and will get wrong results.
**In Above Preview all of the circles are not purple colored. Adjust them as shown below :**\
\
![Adjustin Batch](/images/adjustingBatch1.gif)
- If you have 2 parts of mcqs just like above omr sheet then you should another batch for that part of the omr sheet. Just like this :\
\
![Batch 2 Picking](/images/batch2Picking.gif)
#### {!} Make Sure the number of batches is in order with the order of the mcqs. Scanner will go through Batch 1 and then batch 2 and so on.. So make sure your batches are in ascending order
### 1.2 Save The Preset
- Make sure you save the preset in order to use it. To save a preset got to Preset Menu -> Save Preset Then enter name and description.

### 2. Use Preset To Scan OMR
Now that you have made presets you can use them to scan the same type of OMR sheet. Press on **Use** button to use the preset.
- When you click on Use Button you will be provided with a window for choosing the scanning method.
![Method Choosing](/images/methodWindow.png)
\
**Simple Scanning :** The Simple scanning method will scan the omr as same as Preset preview. If the OMR is not provided with same orientation/cropping as Preset the Scanning will not be accurate and will output wrong result. Make sure you maintain the image quality.\
**AI Method :** The AI Method scanning is very unstable currently. It uses OpenCV circle detection and Dynamic Difference between two circles. This method will improve with the developement.

- File Choosing scanning method. Open/Load an OMR by clicking on **File -> Open**
  - Yellow Circle : Shows the ticked MCQ option.
  - Purple circle : Shows Where the scanning has been through.
  
- Add Answer Key For Result Calculation by Click on **Open Answer Key** button. Hit re-scan when you add an Answer key.\
![Attaching Answer Key](/images/attachingAnswerkey.gif)

### 2.1 Creating Answer Key
Creating Answer key is very simple. The answer fo the question number is same as the number of the line in .txt file.\
For Example : Line number 1 is the Answer of Question number 1, Line number 2 is the Answer of Question number 2...\
\
For creating answer key don't use option name like 'a','b','c' etc. but Use answer number like this :
  - 1 : A,  2 : B,  3 : C, 4 : D ...
- Look at below image for reference :
\
![Reference Answer Key](/images/refAnswerKey.png)
#### InkThreshold : Its stands for how dark the ink of the pen is. If student's pen Ink is too bright and aos cannot detect circles, Try increasing the Ink Threshold value. (Make sure you hit Re-scan to see changes.)


## About Code
***Created in Python 2.7***
### Dependencies
- Tkinter
- OpenCV
- os
- shutil
- Pillow

I am not a professional coder and this was my first "Big" project. Good luck understanding it :)
