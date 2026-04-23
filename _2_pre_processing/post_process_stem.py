"""
Post Process On simulate ADF_STEM images and defects maps
Chuqiao Shi & Chia-hao Lee 20190827
Modified: 2026 - Added error handling and updated API calls
"""

import numpy as np
import matplotlib.pyplot as plt
import os
from skimage import transform
import tifffile

plt.rcParams['figure.figsize'] = (16, 9)


class post_process():
    
    #Two gloabal helper functions#
    global _get_normal_distribution
    global _generate_random_bkg
    
    
    def __init__(self, image_path, file_num, defect_list):
        
        #Input parameters of this class:
        #string: image_path, the path of you images and labels
        #int: file_num
        #list: defect_list, list of str, includes the defect labels you need
        
        self.image_path = image_path
        self.file_num = file_num
        self.defect_list = defect_list
        
        
    def _get_normal_distribution(param):
        '''
        Get positive/negative normal distribution from a tuple
        Imput: tuple: (mean, std)
        return: float: normal_distribution_number
        '''
        num = np.random.normal(param[0],param[1])
        pos = np.random.rand()
        
        if pos>0.5:
            return num
        else:
            return -num
    
    
    def read_image_and_label(self):
        
        '''
        Put image and its defect into one image stack for following process
        self.image_stack: np.array shape = (num_image, x,y,num_defects+1)
        '''
        
        all_files = os.listdir(self.image_path)
        image_list = []
        for image_file in all_files:
            if image_file[:5] == 'Image':
                image_list.append(image_file)
        
        # Adjust file_num to actual number of available images
        actual_num = len(image_list)
        if actual_num < self.file_num:  # MODIFIED FROM ORIGINAL : Added this check to prevent IndexError
            self.file_num = actual_num  # MODIFIED FROM ORIGINAL : Auto-adjust to available images
        
        img = plt.imread(self.image_path+image_list[0])
        #get image size
        x,y = np.shape(img)
        image_stacks = np.zeros((self.file_num,x,y,len(self.defect_list)+1))
        for i in range(self.file_num):
            image_name = image_list[i]
            temp_image = plt.imread(self.image_path+image_name)
            image_stacks[i,:,:,0] = temp_image
            for j in range(len(self.defect_list)):
                temp_defect_name = self.defect_list[j]+'_'+image_name[5:]
                defect_path = self.image_path+temp_defect_name            # MODIFIED FROM ORIGINAL : Store path for existence chek
                if os.path.exists(defect_path):                           # MODIFIED FROM ORIGINAL : Check if file exists before loading
                    temp_defect_image = plt.imread(defect_path)
                    image_stacks[i,:,:,j+1] = temp_defect_image
                else:                                                     # MODIFIED FROM ORIGINAL : Skip missing files instead of crashing
                    print(f"Skipping missing label: {temp_defect_name}")  # MODIFIED FROM ORIGINAL : Print warning
        self.image_stacks = image_stacks.copy()
    
    def add_horizental_sheer(self, sheer_rate):
        
        """
        Add horizental sheer to simulate horizental sample draft during taking the image in STEM
        sheer_rate = (sheer_mean,sheer_std) in gaussian distribution
        single image has a linear sheer, while in different images, sheer rates are different
        """
        num_image, x, y, num_defects = np.shape(self.image_stacks)
        for i in range(num_image):
            temp_stack = self.image_stacks[i,:,:,:]
            shear = _get_normal_distribution(sheer_rate)
            afine_tf = transform.AffineTransform(shear = shear)
            modified = transform.warp(temp_stack, inverse_map=afine_tf)
            self.image_stacks[i,:,:,:] = modified
        
        
        
    def add_vertical_constrain(self, constrain_rate):
        '''
        Add vertical constrain to simulate vertical sample draft during taking the image in STEM
        constrain_rate = (constrain_mean,constrain_std) in guassian distribution
        single image has a constant constrain rate, while in different images, constrain rate are different
        '''
        
        num_image, x, y, num_defects = np.shape(self.image_stacks)
        for i in range(num_image):
            temp_stack = self.image_stacks[i,:,:,:]
            constrain = _get_normal_distribution(constrain_rate)+1
            afine_tf = transform.AffineTransform(scale = (1,constrain))
            modified = transform.warp(temp_stack, inverse_map=afine_tf)
            self.image_stacks[i,:,:,:] = modified
    
    
    def rotate(self, degree):
        
        '''
        rotate the images into the same degree of real images, if there are multiple orientations in real images, 
        you can genreate different degrees in training set
        '''
        
        num_images,x,y,num_defects = np.shape(self.image_stacks)
        for i in range(num_images):
            for j in range(num_defects):
                 self.image_stacks[i,:,:,j] = transform.rotate(self.image_stacks[i,:,:,j],degree)
        pass
    
    def crop(self, target_x, target_y):
        
        '''
        The raw images is a bit larger because the sheer and rotation will cause some blank in the image 
        Crop the center image to shape(target_x, target_y) and avoid the blank
        '''
        
        num_image, x, y, num_defects = np.shape(self.image_stacks)
        cropped_x = abs(x-target_x)//2
        cropped_y = abs(y-target_y)//2
        self.image_stacks = self.image_stacks[:,cropped_x:-cropped_x,cropped_y:-cropped_y,:]
        pass
    
    def change_brightness_and_contrast(self, target_mean, target_std):
        
        '''
        Change the B/C of simulate images to the real image
        You can get the target_mean and target_std from a real image
        
        '''
        
        num_images,x,y,num_defects = np.shape(self.image_stacks)
        for i in range(num_images):
            temp_image = self.image_stacks[i,:,:,0]
            temp_std = np.std(temp_image)
            temp_image *= target_std/temp_std
            temp_mean = np.mean(temp_image)
            temp_image += target_mean-temp_mean
            self.image_stacks[i,:,:,0] = temp_image
        sel = self.image_stacks<0
        self.image_stacks[sel] = 0
        sel1 = self.image_stacks>255
        self.image_stacks[sel1] = 255

    def add_gaussian_noise(self, gaussian_rate):
        
        '''
        add gaussian noise in the image
        '''
        
        for i in range(self.file_num):
            self.image_stacks[i,:,:,0] += np.random.normal(gaussian_rate[0],gaussian_rate[1],np.shape(self.image_stacks[i,:,:,0]))
            
        sel = self.image_stacks<0
        self.image_stacks[sel] = 0
        sel1 = self.image_stacks>255
        self.image_stacks[sel1] = 255
        
    def _generate_random_bkg(bkg_stack):
        
        num, x, y = np.shape(bkg_stack)
        random_weight = np.random.rand(9)
        random_weight = random_weight/np.sum(random_weight)
        bkg_image = np.zeros((x,y))
        for i in range(num):
            bkg_image += random_weight[i]*bkg_stack[i,:,:]
        return bkg_image
            
    
    
    def add_bkg(self, bkg_stack):
        
        '''
        Add random, ununiform background on the images,
        you can extract bkg through high pass filter of STEM image
        '''
        
        _,x,y,_ = np.shape(self.image_stacks)
        for i in range(self.file_num):
            bkg_image = _generate_random_bkg(bkg_stack)
            self.image_stacks[i,:,:,0] += bkg_image[:x,:y]
        pass
    
    def save_as_image(self, save_path):
        
        '''
        Save images stacks as image
        '''
        if os.path.exists(save_path) == False:
            os.makedirs(save_path)
        num_images,x,y,num_defects = np.shape(self.image_stacks)
        for i in range(num_images):
            temp_path = save_path+'image{}/'.format(i)
            os.makedirs(temp_path, exist_ok=True)  # MODIFIED From Original: Added exist_ok=True to avoid FileExistsError on re-run
            tifffile.imwrite(temp_path+'training_image{}'.format(i)+'.tiff',self.image_stacks[i,:,:,0].astype('uint8'))  # MODIFIED: Changed imsave to imwrite
            for j in range(len(self.defect_list)):
                tifffile.imwrite(temp_path+'image{}_label'.format(i)+self.defect_list[j]+'.tiff',  # MODIFIED From Original: Changed imsave to imwrite
                                self.image_stacks[i,:,:,j+1].astype('uint8'))
    
    
    def save_as_npy_files(self, save_path):
        
        '''
        Save images files as .npy files, it is easy to load into deep learning code
        '''
        
        if os.path.exists(save_path) == False:
            os.makedirs(save_path)
        
        np.save(save_path+'images_files.npy',self.image_stacks[:,:,:,0])
        for i in range(len(self.defect_list)):
            np.save(save_path+self.defect_list[i]+'_files.npy',self.image_stacks[:,:,:,i+1])


'''
From The Jupyter Notebook Test Code
if __name__ == "__main__":
    # Define defect list
    defect_list = ['1Doped','2Doped','1vacancy','2vacancy','metal_vacancy','metal_Doped']
    
    # Create processor instance
    Mypostprocess = post_process(image_path='image/', file_num=10, defect_list=defect_list)
    
    # Read images and labels
    Mypostprocess.read_image_and_label()
    
    # Apply transformations
    Mypostprocess.add_horizental_sheer((0.05,0.025))
    Mypostprocess.add_vertical_constrain((0.05,0.025))
    Mypostprocess.rotate(45)
    Mypostprocess.crop(256,256)
    Mypostprocess.add_gaussian_noise((0,20))
    
    # Save results
    Mypostprocess.save_as_image('./saved_image/')
    Mypostprocess.save_as_npy_files('./saved_npy_files/')
    
    print("Processing complete!")
'''