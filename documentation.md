# EagleEye  
## Design and Implementation of a Top-Down Vision-Based People Counting System for Real-Time Occupancy Analysis in a College Mess

---

## 1. Problem Statement

In large institutional environments such as college mess halls, understanding student dining patterns is crucial for efficient resource planning, food quality assessment, and waste reduction. Currently, most mess facilities rely on **manual estimation**, **static attendance logs**, or **billing-based assumptions** to infer student footfall. These methods are often inaccurate, delayed, and incapable of providing real-time or fine-grained insights.

Manual counting is impractical during peak hours, while access-card or token-based systems fail to capture actual dining behavior, as they do not account for students entering without eating, exiting midway, or repeated movement patterns. As a result, mess administrators lack reliable data to correlate **food quality, timing, and menu choices** with student participation.

There is a need for an **automated, non-intrusive, real-time system** that can accurately count the number of people entering and exiting the mess hall, track occupancy over time, and store structured data for analysis—without violating privacy or requiring changes to existing student workflows.

**EagleEye** aims to address this gap by leveraging **computer vision techniques** with a **top-down camera perspective** and **direction-aware line-crossing logic**, enabling accurate estimation of mess occupancy and dining trends.

---

## 2. Objectives

### 2.1 Primary Objectives

- To design and implement **EagleEye**, a vision-based people counting system using a top-down camera view.
- To accurately classify movement across an entrance as **IN** or **OUT** based on direction of motion.
- To maintain a **real-time count of current occupancy** inside the mess hall.
- To store all entry and exit events with **timestamps and dates** in a structured database for further analysis.

### 2.2 Secondary Objectives

- To develop a **hardware-light prototype** using an ESP32-CAM for video capture and an external processing unit for analytics.
- To ensure the system operates **without collecting personally identifiable information**, thereby preserving privacy.
- To enable **time-based analytics** such as hourly, daily, and weekly footfall trends.
- To design EagleEye in a **modular and scalable manner**, allowing future upgrades to edge devices or multiple entrances.

---

## 3. Scope of the Project

- EagleEye focuses solely on **counting people**, not identifying individuals.
- The camera is installed in a **top-down orientation** at the entrance to minimize occlusion and tracking ambiguity.
- The initial implementation supports **single-entrance monitoring**.
- The system is designed for **indoor environments** with relatively controlled lighting conditions.
- The generated data is intended for **trend and pattern analysis**, not biometric accuracy.

### Out of Scope

- Facial recognition or identity verification  
- Multi-camera person re-identification  
- Integration with billing or payment systems  

---

## 4. Methodology

1. **Video Acquisition**  
   A camera module mounted above the entrance captures a continuous video stream.

2. **Person Detection**  
   Each video frame is processed using a deep learning–based object detection model trained to detect humans.

3. **Multi-Object Tracking**  
   Detected individuals are assigned persistent IDs across consecutive frames to prevent duplicate counting.

4. **Line-Crossing Analysis**  
   A virtual horizontal line is defined in the video frame. The direction of centroid movement across this line determines whether a person is entering or exiting.

5. **Event Logging**  
   Each IN or OUT event is recorded along with a timestamp and current occupancy value in a database.

6. **Data Analysis**  
   Logged data is analyzed to identify trends such as peak dining hours, low turnout periods, and long-term usage patterns.

---

## 5. Significance of the Project

### 5.1 Operational Significance
- Enables data-driven decision-making for mess administration.
- Helps identify periods of low participation potentially linked to food quality or menu choices.
- Assists in optimizing staff deployment and food preparation volumes.

### 5.2 Technical Significance
- Demonstrates a practical application of computer vision and object tracking techniques.
- Integrates hardware, software, and data analytics into a unified pipeline.
- Emphasizes system reliability and robustness over unnecessary algorithmic complexity.

### 5.3 Academic Significance
- Covers core domains including:
  - Computer Vision
  - Machine Learning
  - Embedded Systems
  - Database Management Systems
- Suitable for:
  - Final-year major project
  - Research-oriented extension
  - Real-world campus deployment

---

## 6. Expected Outcomes

- A functional EagleEye prototype capable of counting people entering and exiting the mess hall in real time.
- A structured dataset containing time-stamped entry and exit records.
- Analytical insights highlighting peak hours, daily trends, and variations in mess usage.
- A scalable system architecture that can be extended to other campus facilities.

---

## 7. Ethical and Privacy Considerations

- No video footage is stored.
- No facial or biometric data is collected.
- The system relies solely on anonymous motion and positional information.
- EagleEye adheres to basic privacy principles suitable for public institutional environments.

---

## 8. Future Enhancements

- Deployment on edge devices such as Raspberry Pi or AI-enabled embedded platforms.
- Support for multiple entrances with synchronized counting.
- Correlation of occupancy trends with mess menu schedules.
- Development of a web-based dashboard for visualization and reporting.
- Alert mechanisms for overcrowding or unusually low attendance patterns.

---
