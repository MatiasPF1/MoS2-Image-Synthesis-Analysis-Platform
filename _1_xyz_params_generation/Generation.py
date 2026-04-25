import os 
import time
import numpy as np
from batch_workflow import batch_executor 


#All Credits to Chuqiao Shi & Chia-hao Lee 20190310, Almost most  of this work is based on their previous MoS2 dopant STEM simulation code 
'''
The original Implementation is same as previous code , but now integrated into the workflow structure.
'''

                                # XYZ/Parameters Generation
#Inputs By the User, this is just for initialization
file_name = 0
pixel_size = 0
image_size = 0
metal_atom = 0
chalcogen_atom = 0
lattice_constant_a = 0
doped_metal_atom = 0
metal_atom_concentration = 0.0
metal_atom_vacancy_concentration = 0.0
doped_chalcogen_atom = 0
chalcogen_atom_concentration_two_subsititution = 0.0
chalcogen_atom_concentration_one_subsititution = 0.0
chalcogen_atom_concentration_one_vacancy = 0.0
chalcogen_atom_concentration_two_vacancy = 0.0


voltage = 0
Cs3_param_mean = 0
Cs3_param_std  = 0
Cs5_param_mean = 0
Cs5_param_std  = 0
df = 0
aperture = 0
ADF_angle_min = 0
ADF_angle_max = 0
Source_size_param_mean = 0
Source_size_param_std  = 0
defocus_spread_param_mean = 0
defocus_spread_param_std  = 0
probe_current_param_mean = 0
probe_current_param_std  = 0
dwell_time = 0

# Dictionaries (initialized in run_generation)
sample_param_dic = {}
EM_param_dic = {}


def run_generation(file_num):
    """
    Main generation function to be called after all parameters are set.
    Args:
        file_num (int): Number of files to generate
    """
    
     # Update dictionaries with current variable values
    sample_param_dic['file_name'] = file_name
    sample_param_dic['pixel_size'] = pixel_size
    sample_param_dic['image_size'] = image_size
    sample_param_dic['metal_atom'] = metal_atom
    sample_param_dic['chalcogen_atom'] = chalcogen_atom
    sample_param_dic['lattice_constant_a'] = lattice_constant_a
    sample_param_dic['doped_metal_atom'] = doped_metal_atom
    sample_param_dic['metal_atom_concentration'] = metal_atom_concentration
    sample_param_dic['metal_atom_vacancy_concentration'] = metal_atom_vacancy_concentration
    sample_param_dic['doped_chalcogen_atom'] = doped_chalcogen_atom
    sample_param_dic['chalcogen_atom_concentration_two_subsititution'] = chalcogen_atom_concentration_two_subsititution
    sample_param_dic['chalcogen_atom_concentration_one_subsititution'] = chalcogen_atom_concentration_one_subsititution
    sample_param_dic['chalcogen_atom_concentration_one_vacancy'] = chalcogen_atom_concentration_one_vacancy
    sample_param_dic['chalcogen_atom_concentration_two_vacancy'] = chalcogen_atom_concentration_two_vacancy
    
    # Recalculate derived values
    sample_param_dic['lattice_constant_b'] = sample_param_dic['lattice_constant_a']*np.sqrt(3)
    sample_param_dic['lattice_constant_c'] = 1
    sample_param_dic['rep_x'] = int(sample_param_dic['image_size']*sample_param_dic['pixel_size']/sample_param_dic['lattice_constant_a'])
    sample_param_dic['rep_y'] = int(sample_param_dic['image_size']*sample_param_dic['pixel_size']/sample_param_dic['lattice_constant_b'])
    sample_param_dic['rep_z'] = 1
    sample_param_dic['metal_dopant_different'] = sample_param_dic['doped_metal_atom'] - sample_param_dic['metal_atom']
    sample_param_dic['chalcogen_dopant_different'] = sample_param_dic['doped_chalcogen_atom'] - sample_param_dic['chalcogen_atom']
    sample_param_dic['dopant_conc_two_subsitutions_high'] = sample_param_dic['chalcogen_atom_concentration_two_subsititution']
    sample_param_dic['dopant_conc_one_subsitution_high'] = sample_param_dic['chalcogen_atom_concentration_one_subsititution']+sample_param_dic['dopant_conc_two_subsitutions_high']
    sample_param_dic['dopant_conc_one_vacancy_high'] = sample_param_dic['dopant_conc_one_subsitution_high']+sample_param_dic['chalcogen_atom_concentration_one_vacancy']
    sample_param_dic['dopant_conc_two_vacancies_high'] = sample_param_dic['dopant_conc_one_vacancy_high'] + sample_param_dic['chalcogen_atom_concentration_two_vacancy']
    sample_param_dic['supercell_a'] = sample_param_dic['lattice_constant_a'] * sample_param_dic['rep_x']
    sample_param_dic['supercell_b'] = sample_param_dic['lattice_constant_b'] * sample_param_dic['rep_y']
    sample_param_dic['supercell_c'] = sample_param_dic['lattice_constant_c'] * sample_param_dic['rep_z']
    
    # Update EM parameters
    EM_param_dic['voltage'] = voltage
    EM_param_dic['Cs3_param'] = (Cs3_param_mean, Cs3_param_std)
    EM_param_dic['Cs5_param'] = (Cs5_param_mean, Cs5_param_std)
    EM_param_dic['df'] = df
    EM_param_dic['aperture'] = aperture
    EM_param_dic['ADF_angle_min'] = ADF_angle_min
    EM_param_dic['ADF_angle_max'] = ADF_angle_max
    EM_param_dic["Higher_order"] = 'END'
    EM_param_dic['Source_size_param'] = (Source_size_param_mean, Source_size_param_std)
    EM_param_dic['defocus_spread_param'] = (defocus_spread_param_mean, defocus_spread_param_std)
    EM_param_dic['counting_noise'] = 'y'
    EM_param_dic['probe_current_param'] = (probe_current_param_mean, probe_current_param_std)
    EM_param_dic['dwell_time'] = dwell_time
    return generate_files(sample_param_dic, EM_param_dic, file_num)
    

def generate_files(sample_param_dic, EM_param_dic, file_num):
    filesuffix = '_incostem_'
    # Create batch folder structure using batch workflow
    
    # Use OUTPUT_DIR env var if set (Docker sets it to /output), otherwise use ~/Downloads/STEM_MOS2
    default_folder = os.path.join(os.path.expanduser("~"), "Downloads", "STEM_MOS2")
    base_folder = os.environ.get("OUTPUT_DIR", default_folder)
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)
    
    # Find next batch folder number
    batch_num = 1
    while os.path.exists(os.path.join(base_folder, f"batch_{batch_num}")):
        batch_num += 1
    
    # Create batch folders with inputs/outputs structure
    folders = batch_executor.create_batch_folders(base_folder, batch_num)
    
    # Copy incostem.exe and DLL to batch folder
    batch_executor.copy_incostem_files(folders['batch'])
    
    
   
    xtalnm     = sample_param_dic['file_name']
    image_size = sample_param_dic['image_size']
    rep_x      = sample_param_dic['rep_x']
    rep_y      = sample_param_dic['rep_y']
    rep_z      = sample_param_dic['rep_z']
    a          = sample_param_dic['lattice_constant_a']
    b          = sample_param_dic['lattice_constant_b']
    c          = sample_param_dic['lattice_constant_c']
    atomZ1     = sample_param_dic['metal_atom']
    atomZ2     = sample_param_dic['chalcogen_atom']
    
    atom1      = np.array([atomZ1, 0.000000, 0.000000, 1.797500, 1, 0.08])
    atom2      = np.array([atomZ2,      a/2,      b/6, 0.000000, 1, 0.08])
    atom3      = np.array([atomZ2,      a/2,      b/6, 3.595000, 1, 0.08])
    atom4      = np.array([atomZ1,      a/2,      b/2, 1.797500, 1, 0.08])
    atom5      = np.array([atomZ2,        a,    b*2/3, 0.000000, 1, 0.08])
    atom6      = np.array([atomZ2,        a,    b*2/3, 3.595000, 1, 0.08])

    supercell_a, supercell_b, supercell_c = sample_param_dic['supercell_a'], sample_param_dic['supercell_b'], sample_param_dic['supercell_c']
    
    metal_doped_prob                    = sample_param_dic['metal_atom_concentration']
    metal_vacancy_prob                  = sample_param_dic['metal_atom_vacancy_concentration']
    metal_dopant_different              = sample_param_dic['metal_dopant_different']
    chalcogen_dopant_different          = sample_param_dic['chalcogen_dopant_different']
    dopant_conc_two_subsitutions_high   = sample_param_dic['dopant_conc_two_subsitutions_high']
    dopant_conc_one_subsitution_high    = sample_param_dic['dopant_conc_one_subsitution_high']
    dopant_conc_one_vacancy_high        = sample_param_dic['dopant_conc_one_vacancy_high']
    dopant_conc_two_vacancies_high      = sample_param_dic['dopant_conc_two_vacancies_high']
    
    voltage                             = EM_param_dic['voltage']
    Cs3_param                           = EM_param_dic['Cs3_param']
    Cs5_param                           = EM_param_dic['Cs5_param']
    df                                  = EM_param_dic['df']
    aperture                            = EM_param_dic['aperture']
    ADF_angle_min                       = EM_param_dic['ADF_angle_min']
    ADF_angle_max                       = EM_param_dic['ADF_angle_max']
    Higher_order                        = 'END'
    Source_size_param                   = EM_param_dic['Source_size_param']
    defocus_spread_param                = EM_param_dic['defocus_spread_param']
    counting_noise                      = 'n'
    probe_current_param                 = EM_param_dic['probe_current_param']
    dwell_time                          = EM_param_dic['dwell_time']
    #---------------------------------------------------------------#
    inputs_main = folders['inputs_main']
    inputs_labels = folders['inputs_labels']
    
    for N in range(file_num):
        
    #1-Write .xyz file names for the images files and the labels files
        #images files - save to inputs/main/
        filename = xtalnm+filesuffix+str(rep_x)+'_'+str(rep_y)+'_'+str(rep_z)+'_'+str(N)
        fid      = open(os.path.join(inputs_main, filename+'.xyz'), 'w+')              #images files
        
        #Label files - save to inputs/labels/
        filename_metal_Doped    = xtalnm+'_metal_Doped'+filesuffix+str(rep_x)+'_'+str(rep_y)+'_'+str(rep_z)+'_'+str(N)
        fid_metal_Doped         = open(os.path.join(inputs_labels, filename_metal_Doped+'.xyz'), 'w+')
        filename_metal_vacancy  = xtalnm+'_metal_vacancy'+filesuffix+str(rep_x)+'_'+str(rep_y)+'_'+str(rep_z)+'_'+str(N)
        fid_metal_vacancy       = open(os.path.join(inputs_labels, filename_metal_vacancy+'.xyz'), 'w+')
        filename_2Doped         = xtalnm+'_2Doped'+filesuffix+str(rep_x)+'_'+str(rep_y)+'_'+str(rep_z)+'_'+str(N)
        fid_2Doped              = open(os.path.join(inputs_labels, filename_2Doped+'.xyz'), 'w+')
        filename_1Doped         = xtalnm+'_1Doped'+filesuffix+str(rep_x)+'_'+str(rep_y)+'_'+str(rep_z)+'_'+str(N)
        fid_1Doped              = open(os.path.join(inputs_labels, filename_1Doped+'.xyz'), 'w+')
        filename_1vacancy       = xtalnm+'_1vacancy'+filesuffix+str(rep_x)+'_'+str(rep_y)+'_'+str(rep_z)+'_'+str(N)
        fid_1vacancy            = open(os.path.join(inputs_labels, filename_1vacancy+'.xyz'), 'w+')
        filename_2vacancy       = xtalnm+'_2vacancy'+filesuffix+str(rep_x)+'_'+str(rep_y)+'_'+str(rep_z)+'_'+str(N)
        fid_2vacancy            = open(os.path.join(inputs_labels, filename_2vacancy+'.xyz'), 'w+')
        
        
    #2-Write the header into each xyz file
        DateString              = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        xyzheader               =xtalnm+filesuffix+str(rep_x)+'_'+str(rep_y)+'_'+str(rep_z)+'_Created_at_'+DateString+'\n'
        xyzheader_metal_Doped   =xtalnm+'_metal_Doped'+filesuffix+str(rep_x)+'_'+str(rep_y)+'_'+str(rep_z)+'_Created_at_'+DateString+'\n'
        xyzheader_metal_vacancy =xtalnm+'_metal_vacancy'+filesuffix+str(rep_x)+'_'+str(rep_y)+'_'+str(rep_z)+'_Created_at_'+DateString+'\n'
        xyzheader_2Doped        =xtalnm+'_2Doped'+filesuffix+str(rep_x)+'_'+str(rep_y)+'_'+str(rep_z)+'_Created_at_'+DateString+'\n'
        xyzheader_1Doped        =xtalnm+'_1Doped'+filesuffix+str(rep_x)+'_'+str(rep_y)+'_'+str(rep_z)+'_Created_at_'+DateString+'\n'
        xyzheader_1vacancy      =xtalnm+'_1vacancy'+filesuffix+str(rep_x)+'_'+str(rep_y)+'_'+str(rep_z)+'_Created_at_'+DateString+'\n'
        xyzheader_2vacancy      =xtalnm+'_2vacancy'+filesuffix+str(rep_x)+'_'+str(rep_y)+'_'+str(rep_z)+'_Created_at_'+DateString+'\n'
       
        fid.write(xyzheader)
        fid_metal_Doped.write(xyzheader_metal_Doped)
        fid_metal_vacancy.write(xyzheader_metal_vacancy)
        fid_2Doped.write(xyzheader_2Doped)
        fid_1Doped.write(xyzheader_1Doped)
        fid_1vacancy.write(xyzheader_1vacancy)
        fid_2vacancy.write(xyzheader_2vacancy)
        
        #2-Write the supercell dimensions into each xyz file
        fid.write('{:.4f} {:.4f} {:.4f} \n'.format(supercell_a,supercell_b,supercell_c))
        fid_metal_Doped.write('{:.4f} {:.4f} {:.4f} \n'.format(supercell_a,supercell_b,supercell_c))
        fid_metal_vacancy.write('{:.4f} {:.4f} {:.4f} \n'.format(supercell_a,supercell_b,supercell_c))
        fid_2Doped.write('{:.4f} {:.4f} {:.4f} \n'.format(supercell_a,supercell_b,supercell_c))
        fid_1Doped.write('{:.4f} {:.4f} {:.4f} \n'.format(supercell_a,supercell_b,supercell_c))
        fid_1vacancy.write('{:.4f} {:.4f} {:.4f} \n'.format(supercell_a,supercell_b,supercell_c))
        fid_2vacancy.write('{:.4f} {:.4f} {:.4f} \n'.format(supercell_a,supercell_b,supercell_c))
        #---------------------------------------------------------------#
        
        # Write atom positions in .xyz files 
        for i in range(rep_x):
            for j in range(rep_y):
                for k in range(rep_z):
                    
                    #---------------------------------------------------------------#
                
                    #In one unit lattice cell, atom1 and atom 4 are metal atoms
                    #If there is a metal doped atom, we change the atom number and 
                    #write the doped position in the "metal dope label map"
                    #If there is a metal vacancy, we just write the vacancy position
                    #in the "vacancy map" and we don't write it in the image file
                    #NOTICE: vacancy doesn't means atom number = 0, the computem program will
                    #be an error when atom number = 0, just skip it.
                    
                    #---------------------------------------------------------------#
                    prob_metal1 = np.random.rand() 
                    metal_vacancy1 = False
                    if prob_metal1<metal_doped_prob:
                        final_atom1 = atom1 + i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0]) + np.array([metal_dopant_different,0,0,0,0,0])
                        fid_metal_Doped.write('{:.0f} {:.6f} {:.6f} {:.6f} {:.0f} {:.2f} \n'.format(final_atom1[0],final_atom1[1],final_atom1[2],final_atom1[3],final_atom1[4],final_atom1[5]))
                    elif metal_doped_prob<prob_metal1<metal_doped_prob+metal_vacancy_prob:
                        final_atom1 = atom1 + i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0])
                        fid_metal_vacancy.write('{:.0f} {:.6f} {:.6f} {:.6f} {:.0f} {:.2f} \n'.format(final_atom1[0],final_atom1[1],final_atom1[2],final_atom1[3],final_atom1[4],final_atom1[5]))
                        metal_vacancy1 = True
                    else:
                        final_atom1 = atom1 + i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0])
                        
                    prob_metal2 = np.random.rand()
                    metal_vacancy2 = False
                    if prob_metal2<metal_doped_prob:
                        final_atom4 = atom4 + i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0]) + np.array([metal_dopant_different,0,0,0,0,0])
                        fid_metal_Doped.write('{:.0f} {:.6f} {:.6f} {:.6f} {:.0f} {:.2f} \n'.format(final_atom4[0],final_atom4[1],final_atom4[2],final_atom4[3],final_atom4[4],final_atom4[5]))
                    elif metal_doped_prob<prob_metal2<metal_doped_prob+metal_vacancy_prob:
                        final_atom4 = atom4 + i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0])
                        fid_metal_vacancy.write('{:.0f} {:.6f} {:.6f} {:.6f} {:.0f} {:.2f} \n'.format(final_atom4[0],final_atom4[1],final_atom4[2],final_atom4[3],final_atom4[4],final_atom4[5]))
                        metal_vacancy2 = True
                    else:
                        final_atom4 = atom4 + i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0])
                    #---------------------------------------------------------------#
                   
                
                    #---------------------------------------------------------------#
                    #In one unit lattice cell, atom2,3 and atom 5,6 are chalcegon atoms
                    #atom 2 and atom 3 have the same x, y position
                    #atom 4 and atom 5 have the same x, y position
                    #There are 4 types defects in chalcegon sites:
                    #Two doping atoms , one doping atom , one vacancy, two vacancies
                    #---------------------------------------------------------------#
                    
                    
                    #---------------------------------------------------------------#
                    prob_chalcegon1 = np.random.rand()
                    one_vacancy1, two_vacancy1 = False, False
                    if prob_chalcegon1<dopant_conc_two_subsitutions_high:
                        final_atom2 = atom2+ i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0])+np.array([chalcogen_dopant_different,0,0,0,0,0])
                        fid_2Doped.write('{:.0f} {:.6f} {:.6f} {:.6f} {:.0f} {:.2f} \n'.format(final_atom2[0],final_atom2[1],final_atom2[2],final_atom2[3],
                                                                                      final_atom2[4],final_atom2[5]))
                        final_atom3 = atom3+ i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0])+np.array([chalcogen_dopant_different,0,0,0,0,0])
                        fid_2Doped.write('{:.0f} {:.6f} {:.6f} {:.6f} {:.0f} {:.2f} \n'.format(final_atom3[0],final_atom3[1],final_atom3[2],final_atom3[3],
                                                                                      final_atom3[4],final_atom3[5]))
                    elif dopant_conc_two_subsitutions_high<prob_chalcegon1<dopant_conc_one_subsitution_high:
                        final_atom2 = atom2+ i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0])+np.array([chalcogen_dopant_different,0,0,0,0,0])
                        fid_1Doped.write('{:.0f} {:.6f} {:.6f} {:.6f} {:.0f} {:.2f} \n'.format(final_atom2[0],final_atom2[1],final_atom2[2],final_atom2[3],
                                                                                      final_atom2[4],final_atom2[5]))
                        final_atom3 = atom3+ i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0])
                        
                    elif dopant_conc_one_subsitution_high<prob_chalcegon1<dopant_conc_one_vacancy_high:
                        final_atom2 = atom2+ i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0])
                        fid_1vacancy.write('{:.0f} {:.6f} {:.6f} {:.6f} {:.0f} {:.2f} \n'.format(final_atom2[0],final_atom2[1],final_atom2[2],final_atom2[3],
                                                                                      final_atom2[4],final_atom2[5]))
                        final_atom3 = atom3+ i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0])
                        one_vacancy1 = True
                    elif dopant_conc_one_vacancy_high<prob_chalcegon1<dopant_conc_two_vacancies_high:
                        final_atom2 = atom2+ i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0])
                        fid_2vacancy.write('{:.0f} {:.6f} {:.6f} {:.6f} {:.0f} {:.2f} \n'.format(final_atom2[0],final_atom2[1],final_atom2[2],final_atom2[3],
                                                                                      final_atom2[4],final_atom2[5]))
                        final_atom3 = atom3+ i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0])
                        fid_2vacancy.write('{:.0f} {:.6f} {:.6f} {:.6f} {:.0f} {:.2f} \n'.format(final_atom3[0],final_atom3[1],final_atom3[2],final_atom3[3],
                                                                                      final_atom3[4],final_atom3[5]))
                        two_vacancy1 = True
                    else:
                        final_atom2 = atom2 + i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0])
                        final_atom3 = atom3 + i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0])
                    
                    prob_chalcegon2 = np.random.rand()
                    one_vacancy2, two_vacancy2 = False, False
                    if prob_chalcegon2<dopant_conc_two_subsitutions_high:
                        final_atom5 = atom5+ i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0])+np.array([chalcogen_dopant_different,0,0,0,0,0])
                        fid_2Doped.write('{:.0f} {:.6f} {:.6f} {:.6f} {:.0f} {:.2f} \n'.format(final_atom5[0],final_atom5[1],final_atom5[2],final_atom5[3],
                                                                                      final_atom5[4],final_atom5[5]))
                        final_atom6 = atom6+ i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0])+np.array([chalcogen_dopant_different,0,0,0,0,0])
                        fid_2Doped.write('{:.0f} {:.6f} {:.6f} {:.6f} {:.0f} {:.2f} \n'.format(final_atom6[0],final_atom6[1],final_atom6[2],final_atom6[3],
                                                                                      final_atom6[4],final_atom6[5]))
                    elif dopant_conc_two_subsitutions_high<prob_chalcegon2<dopant_conc_one_subsitution_high:
                        final_atom5 = atom5+ i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0])+np.array([chalcogen_dopant_different,0,0,0,0,0])
                        fid_1Doped.write('{:.0f} {:.6f} {:.6f} {:.6f} {:.0f} {:.2f} \n'.format(final_atom5[0],final_atom5[1],final_atom5[2],final_atom5[3],
                                                                                      final_atom5[4],final_atom5[5]))
                        final_atom6 = atom6+ i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0])
                        
                    elif dopant_conc_one_subsitution_high<prob_chalcegon2<dopant_conc_one_vacancy_high:
                        final_atom5 = atom5+ i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0])
                        fid_1vacancy.write('{:.0f} {:.6f} {:.6f} {:.6f} {:.0f} {:.2f} \n'.format(final_atom5[0],final_atom5[1],final_atom5[2],final_atom5[3],
                                                                                      final_atom5[4],final_atom5[5]))
                        final_atom6 = atom6+ i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0])
                        one_vacancy2 = True
                    elif dopant_conc_one_vacancy_high<prob_chalcegon2<dopant_conc_two_vacancies_high:
                        final_atom5 = atom5+ i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0])
                        fid_2vacancy.write('{:.0f} {:.6f} {:.6f} {:.6f} {:.0f} {:.2f} \n'.format(final_atom5[0],final_atom5[1],final_atom5[2],final_atom5[3],
                                                                                      final_atom5[4],final_atom5[5]))
                        final_atom6 = atom6+ i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0])
                        fid_2vacancy.write('{:.0f} {:.6f} {:.6f} {:.6f} {:.0f} {:.2f} \n'.format(final_atom6[0],final_atom6[1],final_atom6[2],final_atom6[3],
                                                                                      final_atom6[4],final_atom6[5]))
                        two_vacancy2 = True
                    else:
                        final_atom5 = atom5 + i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0])
                        final_atom6 = atom6 + i*np.array([0,a,0,0,0,0])+j*np.array([0,0,b,0,0,0])+k*np.array([0,0,0,c,0,0])
                    
                    if metal_vacancy1 == False:
                        fid.write('{:.0f} {:.6f} {:.6f} {:.6f} {:.0f} {:.2f} \n'.format(final_atom1[0],final_atom1[1],final_atom1[2],final_atom1[3],
                                                                                      final_atom1[4],final_atom1[5]))
                    
                        
                        
                    if one_vacancy1 == False and two_vacancy1 == False:
                        fid.write('{:.0f} {:.6f} {:.6f} {:.6f} {:.0f} {:.2f} \n'.format(final_atom2[0],final_atom2[1],final_atom2[2],final_atom2[3],
                                                                                          final_atom2[4],final_atom2[5]))
                        fid.write('{:.0f} {:.6f} {:.6f} {:.6f} {:.0f} {:.2f} \n'.format(final_atom3[0],final_atom3[1],final_atom3[2],final_atom3[3],
                                                                                          final_atom3[4],final_atom3[5]))
                    elif one_vacancy1 == True:
                        fid.write('{:.0f} {:.6f} {:.6f} {:.6f} {:.0f} {:.2f} \n'.format(final_atom2[0],final_atom2[1],final_atom2[2],final_atom2[3],
                                                                                          final_atom2[4],final_atom2[5]))

                    elif two_vacancy1 == True:
                        pass
                    
                    if metal_vacancy2 == False:
                        fid.write('{:.0f} {:.6f} {:.6f} {:.6f} {:.0f} {:.2f} \n'.format(final_atom4[0],final_atom4[1],final_atom4[2],final_atom4[3],
                                                                                      final_atom4[4],final_atom4[5]))

                    if one_vacancy2 == False and two_vacancy2 == False:
                        fid.write('{:.0f} {:.6f} {:.6f} {:.6f} {:.0f} {:.2f} \n'.format(final_atom5[0],final_atom5[1],final_atom5[2],final_atom5[3],
                                                                                          final_atom5[4],final_atom5[5]))
                        fid.write('{:.0f} {:.6f} {:.6f} {:.6f} {:.0f} {:.2f} \n'.format(final_atom6[0],final_atom6[1],final_atom6[2],final_atom6[3],
                                                                                          final_atom6[4],final_atom6[5]))
                    elif one_vacancy1 == True:
                        fid.write('{:.0f} {:.6f} {:.6f} {:.6f} {:.0f} {:.2f} \n'.format(final_atom5[0],final_atom5[1],final_atom5[2],final_atom5[3],
                                                                                          final_atom5[4],final_atom6[5]))
                    else:
                        pass
                    #---------------------------------------------------------------#
        
        # As End of the file and close all xyz files
        #---------------------------------------------------------------#
        fid.write('-1')
        fid_metal_Doped.write('-1')
        fid_metal_vacancy.write('-1')
        fid_2Doped.write('-1')
        fid_1Doped.write('-1')
        fid_1vacancy.write('-1')
        fid_2vacancy.write('-1')
        #---------------------------------------------------------------#
        
        # Close the files
        #---------------------------------------------------------------#
        fid.close()
        fid_metal_Doped.close()
        fid_metal_vacancy.close()
        fid_2Doped.close()
        fid_1Doped.close()
        fid_1vacancy.close()
        fid_2vacancy.close()
        #---------------------------------------------------------------#
        
        
        #Generate parameter files
        # Added by Matias: Join to inputs/main and inputs/labels folders(where they have to be saved)
        #---------------------------------------------------------------#
        fid_param                    = open(os.path.join(inputs_main, filename+'.param'),'w+')
        fid_metal_Doped_param        = open(os.path.join(inputs_labels, filename_metal_Doped+'.param'),'w+')
        fid_metal_vacancy_param      = open(os.path.join(inputs_labels, filename_metal_vacancy+'.param'),'w+')
        fid_2Doped_param             = open(os.path.join(inputs_labels, filename_2Doped+'.param'),'w+')
        fid_1Doped_param             = open(os.path.join(inputs_labels, filename_1Doped+'.param'),'w+')
        fid_1vacancy_param           = open(os.path.join(inputs_labels, filename_1vacancy+'.param'),'w+')
        fid_2vacancy_param           = open(os.path.join(inputs_labels, filename_2vacancy+'.param'),'w+')
        #---------------------------------------------------------------#
        
        #Generate the xyz filename 
        #Added by Matias: Join to inputs/main and inputs/labels folders(where they have to be saved)
        #---------------------------------------------------------------#
        fid_param.write('inputs/main/'+filename+'.xyz \n1 1 1\n')
        fid_metal_Doped_param.write('inputs/labels/'+filename_metal_Doped+'.xyz \n1 1 1\n')
        fid_metal_vacancy_param.write('inputs/labels/'+filename_metal_vacancy+'.xyz \n1 1 1\n')
        fid_2Doped_param.write('inputs/labels/'+filename_2Doped+'.xyz \n1 1 1\n')
        fid_1Doped_param.write('inputs/labels/'+filename_1Doped+'.xyz \n1 1 1\n')
        fid_1vacancy_param.write('inputs/labels/'+filename_1vacancy+'.xyz \n1 1 1\n')
        fid_2vacancy_param.write('inputs/labels/'+filename_2vacancy+'.xyz \n1 1 1\n')
        #---------------------------------------------------------------#
        
        #Save the image as .tif files with relative path to outputs folder
        #Added by Matias: Join to outputs/main and outputs/labels folders(where they have to be saved)
        #---------------------------------------------------------------#
        fid_param.write('outputs/main/Image'+filename+'.tif')
        fid_metal_Doped_param.write('outputs/labels/metal_Doped_'+filename+'.tif')
        fid_metal_vacancy_param.write('outputs/labels/metal_vacancy_'+filename+'.tif')
        fid_2Doped_param.write('outputs/labels/2Doped_'+filename+'.tif')
        fid_1Doped_param.write('outputs/labels/1Doped_'+filename+'.tif')
        fid_1vacancy_param.write('outputs/labels/1vacancy_'+filename+'.tif')
        fid_2vacancy_param.write('outputs/labels/2vacancy_'+filename+'.tif')
        #---------------------------------------------------------------#
        
        #Set parameters

        #get different str lines in .param files
        #Image and defect map have the same paramter file
        #except counting noise
        #---------------------------------------------------------------#
        image_size_str      = '\n'+str(int(image_size))+' '+str(int(image_size))
        Cs3                 = np.random.normal(Cs3_param[0],Cs3_param[1])
        Cs5                 = np.random.normal(Cs5_param[0],Cs5_param[1])
        STEM_Param_str      = '\n'+str(voltage)+' '+str(Cs3)+' '+str(Cs5)+' '+str(df)+' '+str(aperture)
        ADF_str             = '\n' + str(ADF_angle_min) + ' '+ str(ADF_angle_max)
        High_order_str      = '\nEND'  # Must be exactly 'END' on its own line
        Source_size         = np.random.normal(Source_size_param[0],Source_size_param[1])
        source_size_str     = '\n'+str(Source_size)
        defocus_spread      = np.random.normal(defocus_spread_param[0],defocus_spread_param[1])
        Defocus_str         = '\n'+str(defocus_spread)
        probe_current       = np.random.normal(probe_current_param[0],probe_current_param[1])
        noise_str           = '\n'+str(probe_current)+' '+str(dwell_time)
        
        # This section is wre-written by matias with help and analysis of Claude, before after trying again and again with incostem, files were not being written correctly, the last portion made incostem crash
        GeneralParam        = image_size_str+STEM_Param_str+ADF_str+High_order_str+source_size_str+Defocus_str+'\ny'+noise_str
        GeneralParam_defect = image_size_str+STEM_Param_str+ADF_str+High_order_str+source_size_str+Defocus_str+'\nn'
        #---------------------------------------------------------------#
        
        #Wirte Param str into files
        #---------------------------------------------------------------#
        fid_param.write(GeneralParam)
        fid_metal_Doped_param.write(GeneralParam_defect)
        fid_metal_vacancy_param.write(GeneralParam_defect)
        fid_2Doped_param.write(GeneralParam_defect)
        fid_1Doped_param.write(GeneralParam_defect)
        fid_1vacancy_param.write(GeneralParam_defect)
        fid_2vacancy_param.write(GeneralParam_defect)
        #---------------------------------------------------------------#
        
        #close param files
        #---------------------------------------------------------------#
        fid_param.close()
        fid_metal_Doped_param.close()
        fid_metal_vacancy_param.close()
        fid_2Doped_param.close()
        fid_1Doped_param.close()
        fid_1vacancy_param.close()
        fid_2vacancy_param.close()
        #---------------------------------------------------------------#
    
    



  
    ################################  New Code to Execute and Organize ####################
    # Execute incostem for all main image files
    execution_results = batch_executor.execute_batch(folders)

    # Execute incostem for all label files
    label_results = batch_executor.execute_labels(folders)

    # Organize ALL output files (main + labels)
    batch_executor.organize_output_files(folders)  
    
    # Pre-process training data (NEW: Step added after organizing)
    print("\n" + "="*60)
    print("Starting pre-processing for Training_Ready...")
    print("="*60)
    preprocessing_results = batch_executor.preprocess_training_data(folders)
    print(f"\n{preprocessing_results['message']}")
    print("="*60 + "\n")
    
    # Return the batch folder path and execution results
    return {
        'batch_folder': folders['batch'],
        'folders': folders,
        'execution_results': execution_results,
        'label_results': label_results,
        'preprocessing_results': preprocessing_results
    }
