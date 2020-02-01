# AOS - Advance OMR Scanner
Check [release](https://github.com/AeroAndZero/OMRScanner/releases) of the repository for the latest version.
## How To Use ?
To use aos first you need to create preset for specific type of OMR sheet
### 1. Create A Preset
![Preset Window](/images/presetWindow.png)
- click on the plus button
- Open a blank omr sheet
- **If your OMR is not showing up in the "Detected OMR" panel, try tweaking the Edge Detection Settings. Make sure you hit apply to see and apply changes**

#### 1.1 Add A Batch
![Add A Batch](/images/addBatch.png)
**Batches are basically a way to tell the software where the MCQ is.**
*Batches are important for scanning. Every preset should've atleast 1 batch.*
- After you add a batch you need to Pick the place of following questions
  1. First Option of First question
  1. Second Option of **First question**
  1. First Option of Second Question
- Hit the Pick Button And Click on the option place on Detected OMR panel's image as shown below :
![batchPicking](/images/batch1Picking.gif)
**After you specify all the parameters you will get an immediate preview of how your MCQs will be scanned.**
- Make Sure All The circles are in purple color. Otherwise your scan will not perform well and will get wrong results.
**In Above Preview all of the circles are not purple colored. Adjust them as shown below :**
![Adjustin Batch](/images/adjustingBatch1.gif)
- If you have 2 parts of mcqs just like above omr sheet then you should another batch for that part of the omr sheet.
##### Make Sure the number of batches is in order with the order of the mcqs. Scanner will go through Batch 1 and then batch 2 and so on.. So  make sure your batches are in ascending order
