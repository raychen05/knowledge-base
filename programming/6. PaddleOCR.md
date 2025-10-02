### PaddleOCR
---

#### links

https://paddlepaddle.github.io/PaddleOCR/latest/index.html#_1
https://paddlepaddle.github.io/PaddleX/latest/pipeline_usage/tutorials/ocr_pipelines/table_recognition.html#42

---


#### 1. To improve OCR accuracy 


To improve OCR accuracy for skewed text on bottle labels using PaddleOCR, consider the following list of parameters:

Suggested Parameters for Skewed Text:
1.	use_angle_cls=True:
- Enables angle classification to handle skewed text orientations.
2.	det_limit_side_len:
- Adjusts the image size limit for detection. Useful for handling distorted or skewed text.
3.	det_db_box_thresh:
- Sets the threshold for box detection confidence score, helping filter out less confident detections.
4.	det_db_score_mode:
- Controls how the score is computed for boxes (can improve detection accuracy on skewed text).
5.	det_db_unclip_ratio:
- Improves the un-clipping of skewed text boxes.
6.	use_pdserving=True:
- Enables model serving for faster inference on skewed text detection.
7.	det_db_max_candidates:
- Limits the number of candidate boxes to improve efficiency and reduce noise.
8.	rec_algorithm:
- Selects different algorithms like CRNN, SRN, or DetSRN for better recognition accuracy on skewed text.
9.	rec_algorithm_confidence:
- Sets confidence thresholds for the recognition algorithm, improving accuracy on lower-quality or skewed text.
10.	use_gpu=True:
- Utilizing GPU acceleration can improve processing speed for images with skewed text.
11.	use_dilation=True:
- Helps expand the bounding boxes for text regions, improving OCR accuracy in cases of skewed text.

**Example Usage:**

```python
    ocr = PaddleOCR(use_angle_cls=True, 
                    det_limit_side_len=1024, 
                    det_db_box_thresh=0.5, 
                    det_db_unclip_ratio=2.0, 
                    use_pdserving=True, 
                    rec_algorithm='SRN',
                    use_gpu=True)
```

These parameters can significantly enhance OCR performance for images with skewed or distorted text, such as bottle labels.

---

#### 2. Reading Binary Image Data with OpenCV

If you want to read binary image data (e.g., an image uploaded as binary content in a web request), you can use cv2.imdecode instead of cv2.imread. The imdecode function decodes an image from a byte buffer (binary data).

```python
    import cv2
    import numpy as np

    # Simulated binary image data (e.g., from a web request)
    with open("your_image.jpg", "rb") as f:
        binary_image_data = f.read()

    # Convert binary data to a NumPy array
    np_arr = np.frombuffer(binary_image_data, np.uint8)

    # Decode the NumPy array into an OpenCV image
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Check if the image was loaded successfully
    if image is not None:
        print("Image loaded successfully!")
    else:
        print("Failed to load image.")

    # Display the image dimensions
    print("Image dimensions:", image.shape)
```

**Explanation**

1.	np.frombuffer:
- Converts the binary image data into a NumPy array of type uint8.
2.	cv2.imdecode:
- Decodes the NumPy array into an OpenCV image. The cv2.IMREAD_COLOR flag ensures the image is loaded in color mode.
3.	Output:
- The image variable now holds the OpenCV image, which can be further processed or displayed.

**Notes**

	•	Ensure the binary data is in the correct format (e.g., JPEG, PNG) for OpenCV to decode.
	•	You can use cv2.IMREAD_GRAYSCALE if you want to load the image in grayscale.

This approach is ideal for handling image uploads or working with binary image data in applications like APIs or OCR systems.

---

#### 3. To process only a specific region of the input image

you can configure PaddleOCR to process only a specific region of the input image, such as the top, middle, or bottom third of the image, by cropping the image before passing it to the OCR function. PaddleOCR itself does not provide a direct parameter to restrict processing to a specific portion of the image, but you can achieve this using image preprocessing techniques.

Here’s how you can configure PaddleOCR to OCR only one-third of the image:

**Step-by-Step Solution**

1.	Load the Image
- Use a library like OpenCV or PIL to load the image.
2.	Determine the Region to Process
- Calculate the dimensions of the specific portion (e.g., the top, middle, or bottom third).
3.	Crop the Image
- Use slicing or cropping functions to extract the desired portion.
4.	Pass the Cropped Image to PaddleOCR
- Feed the cropped region to the PaddleOCR function.

**Example Code**

Here’s an example where we process only the middle third of the image:

```python
    import cv2
    from paddleocr import PaddleOCR

    # Load the image
    image_path = "your_image.jpg"
    image = cv2.imread(image_path)

    # Get image dimensions
    height, width, _ = image.shape

    # Calculate the middle third region
    start_y = height // 3  # Starting point (1/3 height)
    end_y = 2 * (height // 3)  # Ending point (2/3 height)

    # Crop the middle third of the image
    cropped_image = image[start_y:end_y, 0:width]

    # Initialize PaddleOCR
    ocr = PaddleOCR(use_angle_cls=True, lang='en')

    # Convert the cropped image to the required format
    image_data = cv2.imencode('.jpg', cropped_image)[1].tobytes()

    # Perform OCR on the cropped region
    result = ocr.ocr(image_data)

    # Print results
    print(result)
```

**Explanation**
- start_y and end_y: Define the vertical bounds of the region to crop.
- cv2.imread: Loads the image.
- cv2.imencode: Converts the cropped region into bytes for PaddleOCR.
- ocr.ocr: Processes the cropped image region.

Adjusting for Different Regions
- Top third: Set start_y = 0 and end_y = height // 3.
- Bottom third: Set start_y = 2 * (height // 3) and end_y = height.

**Benefit**

By focusing on specific regions, you reduce the computational cost and target only the area of interest for OCR.

---

#### 4. Key Parameters for Preprocessing in PaddleOCR

1.	Gray-Scale Conversion:
- Convert the image to grayscale to reduce noise and focus on text content.

```python
from PIL import Image
img = Image.open('image_path').convert('L')   # Convert to grayscale
```

2.	Image Resizing:
- Resize the image to fit within PaddleOCR’s detection model’s limits.
- Use det_limit_side_len and det_limit_type parameters.

```python
det_limit_side_len=1024
det_limit_type='min'  # Resize based on the shorter side
```

3.	Image Denoising:
- Apply techniques such as median or Gaussian blur to remove noise while preserving edges.

4.	Binarization (Thresholding):
- Use thresholding to create a binary image for clearer text segmentation.

```python
import cv2
_, binary_img = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
```

5.	Rotation Correction:
- Skewed images can be corrected by detecting and adjusting the angle of rotation.
- Use use_angle_cls=True in PaddleOCR for automatic angle correction.

6.	Contrast Enhancement:
- Adjust contrast to make text more distinguishable.


```python
import cv2
adjusted_img = cv2.convertScaleAbs(image, alpha=1.5, beta=0)  # Increase contrast
```

7.	Padding:
- Add padding around the text to ensure no parts are cut off during processing.
8.	Sharpening:
- Apply image sharpening to enhance text clarity.

```python
kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
sharpened_img = cv2.filter2D(image, -1, kernel)
```

9.	Morphological Transformations:
- Use operations like dilation or erosion to enhance or suppress specific text features.

```python
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
dilated_img = cv2.dilate(binary_img, kernel, iterations=1)
```

10.	Gamma Correction:
- Correct lighting conditions in the image.

```python
corrected_img = np.power(image/255.0, gamma)
```
11.	Use of Pre-trained Models:
- Use det_db_box_thresh, det_db_unclip_ratio, and rec_algorithm parameters to fine-tune detection and recognition.

```python
det_db_box_thresh=0.6
det_db_unclip_ratio=1.5
rec_algorithm='CRNN'  # or 'SRN' for more complex text
```

12.	Crop to Region of Interest (ROI):
- Crop the image to focus only on the area containing text.

**Example of Preprocessing Workflow**

```python
import cv2
from PIL import Image
import numpy as np

# Load image
image = cv2.imread('image_path')

# Convert to grayscale
gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply thresholding
_, binary_img = cv2.threshold(gray_img, 127, 255, cv2.THRESH_BINARY)

# Correct skew (optional)
# Apply morphological operations
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
processed_img = cv2.dilate(binary_img, kernel, iterations=1)

# Resize
resized_img = cv2.resize(processed_img, (1024, 1024))

# Save preprocessed image
cv2.imwrite('processed_image.jpg', resized_img)
```

These preprocessing steps can be fine-tuned based on the characteristics of your dataset (e.g., font size, skew, noise level, etc.) to achieve optimal OCR performance.

By applying these preprocessing steps, you can significantly improve the quality of input images and achieve more accurate OCR results tailored to your dataset. Adjust the parameters based on the specific text and background characteristics for optimal performance.

---

#### 5. Correct Way to Handle Grayscale Images


When loading an image with cv2.IMREAD_GRAYSCALE, OpenCV reads it as a single-channel image, so the resulting image.shape will have two values: (height, width).
When loading an image with cv2.IMREAD_COLOR, OpenCV reads it as a 3,4-channels image, so the resulting image.shape will have three values:  (height, width, channels).


**Key Notes**

- Grayscale Image (IMREAD_GRAYSCALE): Shape is (height, width). There is no third dimension for channels because it’s a single-channel image.
- Color Image (IMREAD_COLOR): Shape is (height, width, channels), with channels typically being 3 for RGB or 4 for RGBA.

**Solution for Dynamic Unpacking**

If the image can be either grayscale or color, you can handle it dynamically:

```python
if len(image.shape) == 2:  # Grayscale image
    height, width = image.shape
    channels = 1  # Single channel for grayscale
elif len(image.shape) == 3:  # Color image
    height, width, channels = image.shape

print(f"Height: {height}, Width: {width}, Channels: {channels}")
```

This approach ensures you handle images of both types without errors.

---

#### 6.  PaddleOCR: Parameters to Optimize Processing Speed

To enhance the speed and reduce processing time in PaddleOCR, the following parameters and configurations can be adjusted:

---

###### 1. General Optimization Parameters

| **Parameter**        | **Description**                                                                                     | **Recommendation**                        |
|-----------------------|-----------------------------------------------------------------------------------------------------|-------------------------------------------|
| `use_gpu`            | Enable GPU processing for OCR.                                                                      | Set to `True` if a GPU is available.      |
| `gpu_mem`            | Limits the GPU memory usage to prevent overloading.                                                 | Adjust based on available memory (e.g., `500`). |
| `enable_mkldnn`      | Enables Intel MKL-DNN for CPU acceleration.                                                         | Set to `True` for CPU-based systems.      |
| `use_angle_cls`      | Enables angle classification, which may slow down the process.                                       | Set to `False` if text is horizontal.     |
| `det_db_box_thresh`  | Filters detection boxes with low confidence scores. Lowering this reduces post-processing overhead. | Default is `0.5`; adjust if necessary.    |
| `det_db_unclip_ratio`| Controls the expansion of detected boxes.                                                           | Set closer to `1.0` for faster detection. |

---

###### 2. Model Selection

| **Model Type**              | **Description**                                                         | **Recommendation**                       |
|------------------------------|-------------------------------------------------------------------------|------------------------------------------|
| `det_model_dir`             | Path to the detection model. Use lightweight models for faster inference.| Use a lightweight model (e.g., `mobile`).|
| `rec_model_dir`             | Path to the recognition model.                                           | Use `ch_ppocr_mobile_v2.0` for speed.    |
| `cls_model_dir`             | Path to the classification model.                                        | Avoid if angle classification is not needed. |
| `use_tensorrt`              | Enable TensorRT for optimized inference on supported GPUs.               | Use `True` if TensorRT is supported.     |

---

###### 3. Batch Processing

| **Parameter**                | **Description**                                                     | **Recommendation**                       |
|-------------------------------|---------------------------------------------------------------------|------------------------------------------|
| `max_batch_size`             | Number of images processed in a batch.                             | Increase to utilize GPU/CPU resources.   |
| `rec_batch_num`              | Number of recognition tasks processed in parallel.                  | Set based on available compute power.    |

---

###### 4. Image Preprocessing

| **Parameter**                | **Description**                                                     | **Recommendation**                       |
|-------------------------------|---------------------------------------------------------------------|------------------------------------------|
| `image_shape`                | Resize images before processing.                                   | Use a smaller resolution (e.g., `3, 32, 100`). |
| `scale`                      | Downscale input images for faster processing.                      | Balance resolution and speed.            |
| `use_mp`                     | Enable multi-process for preprocessing.                            | Set to `True` if the system has multiple cores. |

---

###### 5. Post-Processing

| **Parameter**                | **Description**                                                     | **Recommendation**                       |
|-------------------------------|---------------------------------------------------------------------|------------------------------------------|
| `det_db_thresh`              | Confidence threshold for text box detection.                       | Adjust to skip low-confidence regions.   |
| `rec_char_dict_path`         | Use smaller character dictionaries for recognition.                | Use an appropriate dictionary for your language. |
| `rec_algorithm`              | Recognition algorithm to use.                                      | Use `CRNN` or `RARE` for faster results. |

---

###### 6. Concurrency Settings

| **Setting**                  | **Description**                                                     | **Recommendation**                       |
|-------------------------------|---------------------------------------------------------------------|------------------------------------------|
| `num_workers`                | Number of worker threads.                                          | Increase based on CPU cores.             |
| `use_mp`                     | Multi-processing.                                                  | Use `True` for CPU-heavy tasks.          |
| `enable_benchmark`           | Enables benchmarking to optimize parameters dynamically.           | Set to `True` for one-time configuration.|

---


**Example Configuration for Speed Optimization:**

```python
ocr = PaddleOCR(
    use_gpu=True,
    enable_mkldnn=True,
    det_model_dir="path/to/lightweight/detection/model",
    rec_model_dir="path/to/lightweight/recognition/model",
    use_angle_cls=False,
    det_db_box_thresh=0.5,
    det_db_unclip_ratio=1.5,
    image_shape="3,32,100",
    rec_batch_num=16,
    num_workers=4,
    enable_benchmark=True
)
```
To optimize the processing speed and reduce processing time in PaddleOCR, you can adjust various parameters and settings. Here’s a list of options to consider:



---

#### 7.  How to Set Timeout for PaddleOCR

**Using requests to Add Timeout for PaddleOCR**

As of now, PaddleOCR does not support a timeout parameter directly. However, you can achieve this by using Python’s requests library in combination with PaddleOCR. Here’s an alternative approach:

```python
import requests
from paddleocr import PaddleOCR

# Define a timeout in seconds (e.g., 10 seconds)
timeout = 10  

# Initialize PaddleOCR
ocr = PaddleOCR()

# Wrapper function to handle timeout
def ocr_with_timeout(image_data, timeout):
    try:
        result = ocr.ocr(image_data)
        return result
    except requests.exceptions.Timeout:
        raise Exception(f"OCR process timed out after {timeout} seconds.")

# Process the image with a timeout
result = ocr_with_timeout(image_data, timeout)
print(result)
```

**Explanation:**
- ocr_with_timeout(image_data, timeout) is a wrapper function that handles the timeout.
- Inside the wrapper, ocr.ocr(image_data) processes the image.
- If the OCR process exceeds the specified timeout, a Timeout exception is raised.

This method ensures that PaddleOCR completes the OCR process within the specified time limit.

