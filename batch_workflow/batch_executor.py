"""
Handles the complete workflow: folder creation, file generation, and incostem execution in params/xyz files
for
-->
1-Stem Images
2-Label Maps 
--> 
3-pre_Processing 
"""
import os
import platform
import subprocess
import shutil
from pathlib import Path
import numpy as np
import tifffile
# Use absolute import since main.py runs from project root
from _2_pre_processing.post_process_stem import post_process



########################      #-1 Create Batch_Folders   ##########################################


def create_batch_folders(base_path, batch_num):
    """
    Creates the batch folder structure:
    batch_X/
        inputs/
            main/
            labels/
        outputs/
            main/
            labels/
        Training_Ready/
            main/
            labels/
            labels_npy/
    """
    
    batch_folder = os.path.join(base_path, f"batch_{batch_num}") # This is the batch_X folder
    
                #Define all the required folder, ones specified in the graphical workflow
    folders = {
        'batch': batch_folder, # Main Folder Holding Everything
        
        'inputs': os.path.join(batch_folder, 'inputs'), # Inputs Folder Holding STEM and Labels XYZ/Params
        'inputs_main': os.path.join(batch_folder, 'inputs', 'main'),
        'inputs_labels': os.path.join(batch_folder, 'inputs', 'labels'),
        
        'outputs': os.path.join(batch_folder, 'outputs'), # Outputs Folder Holding STEM and Labels TiFs
        'outputs_main': os.path.join(batch_folder, 'outputs', 'main'),
        'outputs_labels': os.path.join(batch_folder, 'outputs', 'labels'),
        
        'training_ready': os.path.join(batch_folder, 'Training_Ready'), # Training Ready Folder for Pre-Processing
        'training_ready_main': os.path.join(batch_folder, 'Training_Ready', 'main'),
        'training_ready_labels': os.path.join(batch_folder, 'Training_Ready', 'labels'),
        'training_ready_labels_npy': os.path.join(batch_folder, 'Training_Ready', 'labels_npy')
    }
    
                #Create all folders with its path 
    for folder in folders.values():
        os.makedirs(folder, exist_ok=True)
    
    return folders



 ################   #2- Copy the executable files to the batch   #################################


def copy_incostem_files(batch_folder):
    """
    Copies incostem.exe and libfftw3f-3.dll to the batch folder
    """
    #1-Get the batch_workflow directory (where this script is located)
    workflow_dir = Path(__file__).parent.resolve()
    
    #2- Define source and destination paths of the files to copy 
    incostem_src = workflow_dir / "incostem.exe"
    dll_src = workflow_dir / "libfftw3f-3.dll"
    
    #3- Define destination paths in the batch folder
    incostem_dest = os.path.join(batch_folder, "incostem.exe") # Destination path for incostem.exe
    dll_dest = os.path.join(batch_folder, "libfftw3f-3.dll")   # Destination path for DLL
    
    #4- Try and except for the copy process(Exception for possible later errors in the future)
    try:
        if not incostem_src.exists():
            raise FileNotFoundError(f"incostem.exe not found at {incostem_src}")
    
        if not dll_src.exists():
            raise FileNotFoundError(f"libfftw3f-3.dll not found at {dll_src}")
        shutil.copy2(str(incostem_src), incostem_dest)
        shutil.copy2(str(dll_src), dll_dest)
        return True
    
    except Exception as e:
        print(f"Failed to copy files: {e}")
        return False





############## 3- Execute incostem for a single param File ###########################

def execute_incostem_file(batch_folder, param_file_path):
    """
    Case 1: 
    Executes incostem.exe for a single param file
    """
    
    #1-Get the path to incostem.exe and  handle missing file
    incostem_path = os.path.join(batch_folder, "incostem.exe")
    
    if not os.path.exists(incostem_path):
        return {
            "success": False,
            "message": f"incostem.exe not found in {batch_folder}",
            "file": param_file_path
        }
        
        
    #2- Execute incostem with the param file content piped in
    try:
        # Read the param file content
        with open(param_file_path, 'rb') as f:
            params_content = f.read()
        
        # On Linux (Docker) incostem.exe is a Windows binary, so run it through Wine.
        # On Windows run it directly.
        if platform.system() == "Linux":
            cmd = ["wine", incostem_path]
        else:
            cmd = [incostem_path]

        result = subprocess.run(
            cmd,
            input=params_content,  # Pipe the content of the param file
            capture_output=True,   # Capture stdout and stderr
            cwd=batch_folder,      # Run in batch folder
            timeout=300,           # 5 minute timeout
            shell=False            # No shell needed
        )
        
    #3- Handle the result, returns a dictionary with success status and message
        if result.returncode == 0:
            return {
                "success": True,
                "message": f"Successfully generated STEM image",
                "file": os.path.basename(param_file_path)
            }
        else:
            error_msg = result.stderr.decode('utf-8', errors='ignore') if result.stderr else "Unknown error"
            return {
                "success": False,
                "message": f"Execution failed: {error_msg}",
                "file": os.path.basename(param_file_path)
            }
            
    # - This except handles if the procces time exceeds the timeout limit 
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "message": "Execution timeout (exceeded 5 minutes)",
            "file": os.path.basename(param_file_path)
        }
    # - This except handles if the param file is not found
    except PermissionError as e:
        return {
            "success": False,
            "message": f"Permission error: {str(e)}",
            "file": os.path.basename(param_file_path)
        }
    # - This except handles any other general exception
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "file": os.path.basename(param_file_path)
        }
    #- Finally block to ensure cleanup
    finally:
        import gc
        gc.collect()



############## #4-Main Function to Execute Incostem For All Param Files in an Folder #######################

def _execute_param_files(batch_folder, input_folder, file_type="images"):
    """
    Args:
        batch_folder: Path to batch folder containing incostem.exe
        input_folder: Path to folder containing .param files
        file_type: Description for return message (e.g., "images", "label images")
    
    Returns:
        dict: Execution results with success status and statistics
    """
    
    
    #1-Find all .param files + handle no files found
    param_files = []
    for f in os.listdir(input_folder):
        if f.endswith('.param'):
            param_files.append(f)
    
    if not param_files:
        return {
            "success": False,
            "message": f"No .param files found in {os.path.basename(input_folder)}/",
            "results": []
        }
    
    #2-Verify incostem.exe exists before execution
    incostem_exe = os.path.join(batch_folder, 'incostem.exe')
    if not os.path.exists(incostem_exe):
        return {
            "success": False,
            "message": "incostem.exe not found in batch folder",
            "results": []
        }
    
    #3-Execute incostem for each param file
    results = []
    for param_file in param_files:
        param_path = os.path.join(input_folder, param_file) # Full path to param file
        result = execute_incostem_file(batch_folder, param_path) # Execute incostem
        results.append(result) # Collect result
    
    successful = sum(1 for r in results if r['success']) # Count successful executions
    total = len(param_files) # Total number of param files
    
    #4-Return summary of execution results
    return {
        "success": successful > 0,
        "message": f"Completed {successful}/{total} {file_type}",
        "results": results,
        "successful": successful,
        "total": total
    }

#4.1-Execute for Input Folder
def execute_batch(folders):
    """
    Executes incostem for all main image param files in the batch
    """
    return _execute_param_files(folders['batch'], folders['inputs_main'], "images")


#4.2-Execute for Label Folder
def execute_labels(folders):
    """
    Executes incostem for all label param files in the batch
    """
    return _execute_param_files(folders['batch'], folders['inputs_labels'], "label images")



################   5- Organize output files into appropriate folders  ###########################

def organize_output_files(folders):
    """
    Moves generated TIF files to appropriate output folders
    Main images → outputs/main/
    Label maps → outputs/labels/
    
    Args:
        folders: Dictionary of folder paths from create_batch_folders
    """
    batch_folder = folders['batch']
    outputs_main = folders['outputs_main']
    outputs_labels = folders['outputs_labels']
    
    #1-Find all .tif files in batch folder
    tif_files = [f for f in os.listdir(batch_folder) if f.endswith('.tif')]
    
    #2-Move files to appropriate output folders
    label_keywords = ['metal_Doped', 'metal_vacancy', '1Doped', '2Doped', '1vacancy', '2vacancy']
    
    for tif_file in tif_files:
        src = os.path.join(batch_folder, tif_file)
        
        # Check if it's a label map (contains keywords)
        is_label = any(keyword in tif_file for keyword in label_keywords)
        
        # Determine destination folder and move file
        dest_folder = outputs_labels if is_label else outputs_main
        dest = os.path.join(dest_folder, tif_file)
        
        try:
            shutil.move(src, dest)
        except Exception:
            pass



################   6- Match Image-Label Pairs for Pre-Processing  ###########################

def match_image_label_pairs(folders):
    """
    Pairs each main STEM image with its corresponding label maps
    Returns:
        List of dictionaries: [{'main': 'path/to/Image_001.tif', 
                               'labels': {'metal_vacancy': 'path/...', ...}}, ...]
    """
    
    outputs_main = folders['outputs_main']
    outputs_labels = folders['outputs_labels']
    
    # 1- Get all main STEM images (files starting with 'Image' and ending with .tif)
    main_images = []
    try:
        for f in os.listdir(outputs_main):
            if f.startswith('Image') and f.endswith('.tif'): 
                main_images.append(f)
    except FileNotFoundError:
        return []
    
    if not main_images:
        return []
    
    # 2- Define defect types to match
    defect_types = [
        'metal_vacancy',
        'chalcogen_vacancy', 
        'metal_Doped',
        'chalcogen_Doped',
        '1Doped',
        '2Doped',
        '1vacancy',
        '2vacancy'
    ]
    
    # 3- Match each main image with its corresponding label maps
    matched_pairs = []
    
    for main_image in main_images:
        # Full path to main image
        main_path = os.path.join(outputs_main, main_image)
        
        # Initialize labels dictionary for this main image
        labels_dict = {}
        
        # Strip 'Image' prefix to match actual label naming convention
        # Main: ImageMoS2_incostem_16_9_1_4.tif → MoS2_incostem_16_9_1_4.tif
        base_filename = main_image.replace('Image', '', 1)  # Remove first 'Image' only
        
        # 4- Search for corresponding label maps
        try:
            label_files = os.listdir(outputs_labels)
            for defect_type in defect_types:
                # Look for pattern: defect_type_MoS2_incostem_16_9_1_4.tif
                expected_label = f"{defect_type}_{base_filename}"
                
                if expected_label in label_files:
                    label_path = os.path.join(outputs_labels, expected_label)
                    labels_dict[defect_type] = label_path
                    
        except FileNotFoundError:
            pass
        
        # 5- Add to matched pairs (even if no labels found, to track all images)
        matched_pairs.append({
            'main': main_path,
            'main_filename': main_image,
            'labels': labels_dict
        })
    
    return matched_pairs



################   7- Process Individual Image-Label Pair Using post_process Class  ###########################

def preprocess_pair(image_data, folders, preprocessing_config):
    """
    Processes one main image + its labels using the existing post_process class
    
    Args:
        image_data: Dictionary from match_image_label_pairs {'main': 'path', 'main_filename': 'name', 'labels': {type: path}}
        folders: Dictionary containing all batch folder paths
        preprocessing_config: Dictionary with transformation parameters
    """
    try:
        # 1- Setup: Create temporary directory structure that post_process expects
        temp_dir = os.path.join(folders['batch'], '_temp_preprocess')
        os.makedirs(temp_dir, exist_ok=True)
        
        main_filename = image_data['main_filename']
        labels_dict = image_data['labels']
        
        # 2- Copy files to temp directory with expected naming convention
        shutil.copy2(image_data['main'], os.path.join(temp_dir, main_filename))
        defect_list = []
        for label_type, label_path in labels_dict.items():
            # post_process strips first 5 chars from image filename when looking for labels(specifically 'Image')
            if main_filename.startswith('Image'):
                base_name = main_filename[5:]
            else:
                base_name = main_filename
            expected_name = f"{label_type}_{base_name}"
            shutil.copy2(label_path, os.path.join(temp_dir, expected_name))
            defect_list.append(label_type)
        
        # 3- Create post_process instance
        processor = post_process(
            image_path=temp_dir + '/',  # post_process expects trailing slash
            file_num=1,  # Process one image at a time
            defect_list=defect_list
        )
        
        # 4- Read images and labels
        processor.read_image_and_label()
        
        # 5- Apply ALL transformations (as designed in original post_process class)
        processor.add_horizental_sheer(preprocessing_config['sheer_rate'])
        processor.add_vertical_constrain(preprocessing_config['constrain_rate'])
        processor.rotate(preprocessing_config['rotation_degree'])
        target_x, target_y = preprocessing_config['crop_size']
        processor.crop(target_x, target_y)
        processor.add_gaussian_noise(preprocessing_config['gaussian_noise'])
        
        # 6- Save processed files to Training_Ready folders
        # Save main image
        main_output = os.path.join(folders['training_ready_main'], main_filename)
        tifffile.imwrite(
            main_output,
            processor.image_stacks[0, :, :, 0].astype('uint8')
        )
        
        # Save labels (.tif and .npy)
        labels_processed = []
        for idx, label_type in enumerate(defect_list):
            
            # Save .tif version (exactly as original post_process class does)
            label_filename = f"{label_type}_{main_filename}"
            label_tif_path = os.path.join(folders['training_ready_labels'], label_filename)
            tifffile.imwrite(
                label_tif_path,
                processor.image_stacks[0, :, :, idx + 1].astype('uint8')
            )
            
            # Save .npy version
            npy_filename = label_filename.replace('.tif', '.npy')
            npy_path = os.path.join(folders['training_ready_labels_npy'], npy_filename)
            np.save(
                npy_path,
                processor.image_stacks[0, :, :, idx + 1]
            )
            
            labels_processed.append(label_type)
        
        # 7- Cleanup temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return {
            'success': True,
            'main_file': main_filename,
            'labels_processed': labels_processed,
            'error': None
        }
        
    except Exception as e:
        # Cleanup on error
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass
        
        return {
            'success': False,
            'main_file': image_data.get('main_filename', 'unknown'),
            'labels_processed': [],
            'error': str(e)
        }



################   8- Execute Batch Pre-Processing  ###########################

def preprocess_training_data(folders, preprocessing_config=None):
    """
    Main entry point for pre-processing all images in a batch
    """
    
    # Default configuration
    if preprocessing_config is None:
        preprocessing_config = {
            'sheer_rate': (0.05, 0.025),
            'constrain_rate': (0.05, 0.025),
            'rotation_degree': 45,
            'crop_size': (256, 256),
            'gaussian_noise': (0, 20)
        }
    
    # 1- Get all matched image-label pairs
    matched_pairs = match_image_label_pairs(folders)
    
    if not matched_pairs:
        return {
            'success': False,
            'message': 'No images found to process',
            'total_pairs': 0,
            'successful': 0,
            'failed': 0,
            'failed_files': [],
            'output_paths': {
                'main': folders['training_ready_main'],
                'labels': folders['training_ready_labels'],
                'labels_npy': folders['training_ready_labels_npy']
            }
        }
    
    # 2- Process each pair
    results = []
    successful = 0
    failed = 0
    failed_files = []
    
    for image_data in matched_pairs:
        result = preprocess_pair(image_data, folders, preprocessing_config)
        results.append(result)
        
        if result['success']:
            successful += 1
        else:
            failed += 1
            failed_files.append({
                'file': result['main_file'],
                'error': result['error']
            })
    
    # 3- Return summary
    total_pairs = len(matched_pairs)
    
    return {
        'success': successful > 0,
        'message': f"Pre-processed {successful}/{total_pairs} image pairs",
        'total_pairs': total_pairs,
        'successful': successful,
        'failed': failed,
        'failed_files': failed_files,
        'output_paths': {
            'main': folders['training_ready_main'],
            'labels': folders['training_ready_labels'],
            'labels_npy': folders['training_ready_labels_npy']
        },
        'results': results
    }