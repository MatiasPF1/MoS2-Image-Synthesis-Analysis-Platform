# MoS2-Image-Synthesis-Platform

This tool facilitates STEM (Scanning Transmission Electron Microscopy) image simulation for Deep Learning and provides a general hub for working with atomic structures.

## 🐳 Run with Docker

```bash
git clone https://github.com/MatiasPF1/MoS2-Image-Synthesis-Analysis-Platform.git
cd MoS2-Image-Synthesis-Analysis-Platform
docker build -t mos2-platform .
docker run -p 8050:8050 mos2-platform
```

Then open `http://localhost:8050` in your browser. The only requirement is [Docker](https://www.docker.com/products/docker-desktop).

---


# 1. Generate Personalized XYZ and Params Files(100% Functional in current Version)

This module generates **custom atomic structure (XYZ)** files and corresponding **ComputeM parameter (params)** files for STEM image simulation of monolayer MoS₂, supporting both pristine and defective configurations.


### 📄 XYZ File (Atomic Structure)

The XYZ file contains the atomic coordinates and properties for the material structure.

**Example:**

```text
MoS2_incostem_10_17_1_Created_at_2024_12_26_15_30_45
31.5000 54.5660 1.0000
42 0.000000 0.000000 1.797500 1 0.08
16 1.575000 3.030889 0.000000 1 0.08
16 1.575000 3.030889 3.595000 1 0.08
42 1.575000 9.092667 1.797500 1 0.08
16 3.150000 12.123556 0.000000 1 0.08
16 3.150000 12.123556 3.595000 1 0.08
...
```

### ⚙️ Params File (STEM Simulation Parameters)

The params file contains the simulation parameters for ComputeM.

**Example:**

```text
MoS2_incostem_10_17_1_0.xyz
1 1 1
ImageMoS2_incostem_10_17_1_0.tif
512 512
300 -0.003 0.0 -50 21.4
70 200
END
0.45
30
y
12.5 1e-6
```

# 2. Generate STEM Images(100% Functional in current version)

<img width="300" height="500" alt="image" src="https://github.com/user-attachments/assets/ede06720-e61b-41aa-848c-28bc0b3c275c" />
<img width="300" height="501" alt="image" src="https://github.com/user-attachments/assets/e2583153-0428-4d3d-a34d-72ab2d8d032c" />


This step generates STEM `.tif` images by directly invoking **ComputeM** using the automatically generated XYZ and params files.

The resulting images are **equivalent** to those obtained when:
1. Manually creating the XYZ structure file  
2. Manually writing the corresponding params file  
3. Running both files independently through ComputeM  or in batches 
4. Getting the output STEM `.tif` with its correspondent Truth Labels `.tif`

# 3. Preprocessing(100% Functional in current version)

This stage applies **physics-informed preprocessing** to the generated STEM images and their corresponding defect label maps. The goal is to bridge the gap between ideal simulated images and experimentally acquired STEM data, while preserving pixel-wise alignment between images and labels.

All transformations are applied **consistently across the image and all defect channels**.

---

**Applied Operations**
- **Image & label stacking**  
  Combines each STEM image with its associated defect masks into a unified array  
  `(N, X, Y, num_defects + 1)`

- **Horizontal shear**  
  Simulates horizontal sample drift during STEM acquisition using a Gaussian-distributed shear rate

- **Vertical constraint (scaling)**  
  Models vertical scan distortion caused by sample or beam instabilities

- **Rotation**  
  Aligns simulated images with experimental orientations or generates multi-orientation training data

- **Center cropping**  
  Removes blank regions introduced by affine transformations and enforces a fixed image size

- **Brightness & contrast adjustment**  
  Matches simulated image intensity statistics to real experimental images

- **Gaussian noise injection**  
  Adds detector and shot noise to approximate experimental signal variability

- **Random background addition**  
  Superimposes spatially varying, non-uniform backgrounds generated from a background image stack

---

**Output Formats**
- `.tiff` images for direct inspection and visualization  
- `.npy` arrays for efficient loading into deep learning pipelines  

The preprocessing step preserves **exact pixel-wise correspondence** between images and defect labels, making the output suitable for supervised learning tasks such as defect detection and segmentation in STEM images.

# Folder Workflow and Platform Facilitation (For 1 , 2, 3)
- The platform safely interacts with the operating system to manage and organize output directories automatically, streamlining the large-scale, automated generation of STEM content.
   <img width="1273" height="687" alt="image" src="https://github.com/user-attachments/assets/0f528780-8c54-42a5-bd2d-f9e8e200c369" />




# 4. Deep Learning Models for Defect Detection(model was created as an prototype)

This stage implements **two ResUNet-based convolutional neural networks** designed for pixel-wise analysis of STEM images of MoS₂.

The models are trained to detect and segment:
- **Vacancy defects** 
- **Polymorphs**

Each model operates on the preprocessed STEM images generated in the previous stages and produces spatially resolved probability maps aligned with the input images.

---

**Model Architecture**
- Backbone: **Residual U-Net (ResUNet)**
- Encoder–decoder structure with skip connections
- Residual blocks improve gradient flow and stability for deep architectures
- Designed for high-resolution, low-SNR STEM data

<img width="502" height="432" alt="image" src="https://github.com/user-attachments/assets/7d4237f7-b840-4414-93cb-07f912ff0cf7" />


---

**Outputs**
- Pixel-wise defect probability maps
- Separate output channels for different defect or polymorph classes
- Preserves exact spatial correspondence with the input STEM image

<img width="508" height="342" alt="image" src="https://github.com/user-attachments/assets/5abf176f-b303-4809-adab-7e3f9a44dfc9" />


The two-model setup allows specialization: one network focuses on **vacancy-type defects**, while the other targets **structural polymorph identification**, improving robustness and interpretability.

---




### References

1. **ComputeM (STEM Simulation Software)**  
   ComputeM Development Team.  
   *ComputeM: Multislice STEM Simulation Toolbox.*  
   Page: https://sourceforge.net/projects/computem/ 
   
2. **Deep Learning of Vacancy Defects and Polymorphs in MoS₂**  
   Ziatdinov, M., Dyck, O., Maksov, A., Li, X., & Kalinin, S. V.  
   *Deep learning of atomically resolved scanning transmission electron microscopy images: identification of vacancy defects and polymorphs of MoS₂.*  
   **npj Computational Materials**, 3, 31 (2017).
   

3. **Deep Learning Enabled Measurements of Single-Atom Defects**  
   Lee, C.-H., Shi, C., Luo, D., Khan, A., Janicek, B. E., Kang, S., Zhu, W., Clark, B. K., & Huang, P. Y.  
   *Deep Learning Enabled Measurements of Single-Atom Defects in 2D Transition Metal Dichalcogenides with Sub-Picometer Precision.*  
   **Microscopy and Microanalysis**, 25(1), 172–181 (2019).  
   DOI: 10.1017/S1431927619001594
   <br>
   GitHub Repo:  https://github.com/Chuqiao2333/STEM-Simulation-Images/tree/master?tab=readme-ov-file





