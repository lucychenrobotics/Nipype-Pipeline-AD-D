###NOTES:
"""
DEPENDENCY ISSUES:
1. If you decide to use freesurfer, make sure FREESURFER_HOME is environment variable on your computer.
For macs it said to put it in .bhrc or something but for the lab mac, it's a different extension for some reason.
**look for where the variables on your computer are stored**
2. To draw the workflow graph, you have to make sure to have dot downloaded.

FORMAT ISSUES:
1. If it is a function where it would like all of the outputs of the previous node (it requests a list like sliceTiming),
make the previous node is a map node.
Refer to the bet node for example.
2. To unzip a file use gunzip
3. Here are some functions for converting formats so donut fret:
convert2nii = Node(MRIConvert(out_type='nii'), name='convert2nii')
4. DO REALIGN FIRST!!!!!!! FOR SOME REASON IT REQUIRES A LIST OF FILES BUT THEN IF YOU CREATE A MAP NODE THEN IT TURNS IT ALL INTO ONE RUN


FINDING FILES:
1.Freesurfer has a weird way of looking for files, this is the method they use. You will need this to pass in subject_id
and your folders will have to be in a certain format for it to work.
# FreeSurferSource - Data grabber specific for FreeSurfer data
fssource = Node(FreeSurferSource(subjects_dir=fs_dir),
                run_without_submitting=True,
                name='fssource')

2. There is a file grabber called datagrabber (kind of confusing), however 3. is another way to do it
3. 
###TRY NOT TO HAVE MORE THAN ONE SELECTFILES NODE, JUST ADD EXTRA FORMATS INTO TEMPLATES#####
#Sets up what you're iterating through
#Things to change: fields: ['first thing you want iterate through', 'second thing you want to iterate through']
infosource = Node(IdentityInterface(fields=['subject_id',
                                            'session_id']),
                  name="infosource")
#What each field name refers to
infosource.iterables = [('subject_id', subject_list),
                        ('session_id', session_list)]

#Describes what the file name looks like, but in {} if it should be replaced with a field. If you call func, it will give you what is right of func:
templates = {'func': 'data/{subject_id}/{session_id}.nii.gz',
             'struct': 'data/{subject_id}/Struct.nii.gz'}

#The node you actually call when you connect nodes, all of the above is just set up.
selectfiles = Node(SelectFiles(templates,
                               base_directory=experiment_dir),
                   name="selectfiles")



#Gunzip if you need to unzip, otherwise leave this part out
gunzip = Node(Gunzip(), name="gunzip")



#HOW TO CONNECT THEM
workflowname.connect([(infosource, selectfiles, [('subject_id', 'subject_id')]),
                      (selectfiles, gunzip, [('func', 'in_file')]),
                      (gunzip, coregister, [('out_file', 'source')]),
                      ])



FOR HELP:
1. Tutorials used: 
http://miykael.github.io/nipype-beginner-s-guide/firstLevel.html
http://nipype.readthedocs.io/en/latest/users/examples/fmri_spm.html
2. To get help on a function, type Function.help() for the mandatory and optional inputs and outputs 
EXAMPLE: BET.help()
3. To read pklz files (this is the file type for the crash files) go onto commandline and type:
nipypecli crash /filelocation/filename.pklz
To see what nipypecli can do, just type nipypecli
nipype_read_crash does not work! Do not use this.



"""
# Import modules
from os.path import join as opj
from nipype.interfaces.fsl import BET
from nipype.interfaces.afni import Despike
from nipype.interfaces.spm import (SliceTiming, Realign, Smooth, Level1Design,
                                   EstimateModel, EstimateContrast, Coregister, Normalize, Smooth)
from nipype.interfaces.utility import Function, IdentityInterface
from nipype.interfaces.io import FreeSurferSource, SelectFiles, DataSink, DataGrabber
from nipype.algorithms.rapidart import ArtifactDetect
from nipype.algorithms.misc import TSNR, Gunzip
from nipype.algorithms.modelgen import SpecifySPMModel
from nipype.pipeline.engine import Workflow, Node, MapNode
# MATLAB - Specify path to current SPM and the MATLAB's default mode
from nipype.interfaces.matlab import MatlabCommand

#change

##Edit as necessary
# preprocess(studyfile, startSubject, endSubject):

#Have to check this path
MatlabCommand.set_default_paths('/Users/lighthalllab/Documents/MATLAB/toolbox/spm12') 
MatlabCommand.set_default_matlab_cmd("/Applications/MATLAB_R2015a.app/bin/matlab -nodesktop -nosplash")

"""
# FreeSurfer - Specify the location of the freesurfer folder
fs_dir = '/Volumes/Research2/Lighthall_Lab/experiments/cjfmri-1/data/fmri/Lucy_testing/Copy/Func/freesurfer'
FSCommand.set_default_subjects_dir(fs_dir)"""



###
# Specify variables
experiment_dir = '/Volumes/Research2/Lighthall_Lab/experiments/cjfmri-1/data/fmri/Lucy_testing/Copy/Func'          # location of experiment folder
output_dir = 'output_fMRI_example_15rd'        # name of 1st-level output folder
working_dir = 'workingdir_fMRI_example_15rd'   # name of 1st-level working directory

subject_list = ["1002", "1003", "1004"]      # list of subject identifiers
session_list = ['Enc2']          # list of session identifiers





number_of_slices = 38                         # number of slices in volume
TR = 2.0                                      # time repetition of volume
smoothing_size = 6                        # size of FWHM in mm


TPMLocation = "/Applications/MATLAB_R2015a.app/toolbox/spm12/tpm/TPM.nii"

print("finish set up")
###
# Specify Preprocessing Nodes

# Infosource - a function free node to iterate over the list of subject names
infosource = Node(IdentityInterface(fields=['subject_id',
                                            'session_id']),
                  name="infosource")


infosource.iterables = [('subject_id', subject_list),
                        ('session_id', session_list)]

# SelectFiles
templates = {'func': 'data/{subject_id}/{session_id}.nii.gz',
             'struct': 'data/{subject_id}/Struct.nii.gz'}
selectfiles = Node(SelectFiles(templates,
                               base_directory=experiment_dir),
                   name="selectfiles")

"""

datasource = Node(interface=DataGrabber(infields=['subject_id'],
                                               outfields=['func', 'struct']),
                     name='datasource')
datasource.inputs.base_directory = experiment_dir

###Here set what the file name looks like
datasource.inputs.template = 'data/%s/%s.nii.gz'
datasource.inputs.template_args = info
datasource.inputs.sort_filelist = True
"""





# Despike - Removes 'spikes' from the 3D+time input dataset
skullstrip = Node(interface=BET(), name="skullstrip")
skullstrip.inputs.mask = True

"""

despike = MapNode(Despike(outputtype='NIFTI'),
                  name="despike", iterfield=['in_file'])
"""


# Slicetiming - correct for slice wise acquisition
interleaved_order = list(range(1,number_of_slices+1,2)) + list(range(2,number_of_slices+1,2))
sliceTiming = Node(SliceTiming(num_slices=number_of_slices,
                               time_repetition=TR,
                               time_acquisition=TR-TR/number_of_slices,
                               slice_order=interleaved_order,
                               ref_slice=number_of_slices//2),
                   name="sliceTiming")

# Realign - correct for motion
realign = Node(Realign(register_to_mean=True),
               name="realign")


#Gunzip - unzip anatomical
gunzip3 = Node(Gunzip(), name="gunzip3")

gunzip2 = Node(Gunzip(), name="gunzip2")

gunzip = Node(Gunzip(), name="gunzip")


"""# Artifact Detection - determine which of the images in the functional series
#   are outliers. This is based on deviation in intensity or movement.
art = Node(ArtifactDetect(norm_threshold=1,
                          zintensity_threshold=3,
                          mask_type='spm_global',
                          parameter_source='SPM'),
           name="art")
"""


coregister = Node(Coregister(), name='coregister')

#replaces volume transformation
normalize = Node(interface=Normalize(), name="normalize")
normalize.inputs.template = TPMLocation


# Smooth - to smooth the images with a given kernel
smooth = Node(Smooth(fwhm=smoothing_size),
              name="smooth")


print("finished nodes")
###
# Specify Preprocessing Workflow & Connect Nodes

# Create a preprocessing workflow
preproc = Workflow(name='preproc')

# Connect all components of the preprocessing workflow
# Coregister: source image is the anatomical image, mean_image is the functional image
preproc.connect([(infosource, selectfiles, [('subject_id', 'subject_id'),
                                            ('session_id', 'session_id')]),
                 (selectfiles, gunzip, [('func', 'in_file')]),
                 (gunzip, sliceTiming, [('out_file', 'in_files')]),
                 (sliceTiming, realign, [('timecorrected_files', 'in_files')]),
                 (selectfiles, gunzip2, [('struct', 'in_file')]),
                 (gunzip2, coregister, [('out_file', 'target')]),
                 (realign, coregister, [('mean_image', 'source'),
                                        ('realigned_files', 'apply_to_files')]),
                 (gunzip2, normalize, [('out_file', 'source')]),
                 (coregister, normalize, [('coregistered_files', 'apply_to_files')]),
                 (normalize, smooth, [('normalized_files', 'in_files')]),
                 (normalize, skullstrip, [('normalized_source', 'in_file')]),
                 ])


print("finish preprocess workflow")


# Specify Meta-Workflow & Connect Sub-Workflows
metaflow = Workflow(name='metaflow')
metaflow.base_dir = opj(experiment_dir, working_dir)


###
# Input & Output Stream

# Infosource - a function free node to iterate over the list of subject names
infosource = Node(IdentityInterface(fields=['subject_id']),
                  name="infosource")
infosource.iterables = [('subject_id', subject_list)]

# SelectFiles - to grab the data (alternativ to DataGrabber)
templates = {'func': 'data/{subject_id}/CJ*.nii.gz'}
selectfiles = Node(SelectFiles(templates,
                               base_directory=experiment_dir),
                   name="selectfiles")



# Datasink - creates output folder for important outputs
datasink = Node(DataSink(base_directory=experiment_dir,
                         container=output_dir),
                name="datasink")

# Use the following DataSink output substitutions
substitutions = [('_subject_id_', ''),
                 #('_despike', ''),
                 ('_detrended', ''),
                 ('_warped', '')]
datasink.inputs.substitutions = substitutions

# Connect Infosource, SelectFiles and DataSink to the main workflow
metaflow.connect([(preproc, datasink, [('sliceTiming.timecorrected_files',
                                        'preprocout.timecorrected.@timecorrect_files'),
                                       ('realign.mean_image',
                                        'preprocout.@mean'),
                                       ('realign.realignment_parameters',
                                        'preprocout.realign.@parameters'),
                                       ('normalize.normalized_files',
                                        'preprocout.normalized.@normalized_files'),
                                       ('smooth.smoothed_files',
                                        'preprocout.smoothed.@smoothed_files'),
                                       ('skullstrip.out_file',
                                        'preprocout.bet.@out_file'),
                                       ]),
                  ])

"""('binarize.binary_file',
                                        'preprocout.@brainmask'),"""
###
# Run Workflow
print("before graph")
metaflow.write_graph(graph2use='colored')
print("done building")
metaflow.run('MultiProc', plugin_args={'n_procs': 6})


