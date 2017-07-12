###
# Import modules
from os.path import join as opj
from nipype.interfaces.fsl import BET
from nipype.interfaces.afni import Despike
from nipype.interfaces.freesurfer import (BBRegister, ApplyVolTransform,
                                          Binarize, MRIConvert, FSCommand)
from nipype.interfaces.spm import (SliceTiming, Realign, Smooth, Level1Design,
                                   EstimateModel, EstimateContrast, Coregister, Normalize)
from nipype.interfaces.utility import Function, IdentityInterface
from nipype.interfaces.io import FreeSurferSource, SelectFiles, DataSink
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

# FreeSurfer - Specify the location of the freesurfer folder
fs_dir = '/Volumes/Research2/Lighthall_Lab/experiments/cjfmri-1/data/fmri/Lucy_testing/Copy/Func/freesurfer'
#'/Volumes/Research2/Lighthall_Lab/experiments/cjfmri-1/data/fmri/Lucy_testing/Copy/Func/freesurfer'
FSCommand.set_default_subjects_dir(fs_dir)



###
# Specify variables
experiment_dir = '/Volumes/Research2/Lighthall_Lab/experiments/cjfmri-1/data/fmri/Lucy_testing/Copy/Func'          # location of experiment folder
subject_list = ["1002", "1003", "1004"]                   # list of subject identifiers
output_dir = 'output_fMRI_example_1st'        # name of 1st-level output folder
working_dir = 'workingdir_fMRI_example_1st'   # name of 1st-level working directory

number_of_slices = 38                         # number of slices in volume
TR = 2.0                                      # time repetition of volume
fwhm_size = 6                                 # size of FWHM in mm

TPMLocation = "/Applications/MATLAB_R2015a.app/toolbox/spm12/tpm/TPM.nii"

print("finish set up")
###
# Specify Preprocessing Nodes

infosource = Node(IdentityInterface(fields=['subject_id']),
                  name="infosource")
infosource.iterables = [('subject_id', subject_list)]



#specifically for the bbregister to get the anatomical scans
templates2 = {'func': 'freesurfer/{subject_id}/mri/brainmask.nii.gz'}
selectfiles2 = Node(SelectFiles(templates2,
                               base_directory=experiment_dir),
                   name="selectfiles")




# Despike - Removes 'spikes' from the 3D+time input dataset
bet = MapNode(BET(output_type='NIFTI'), name='bet', iterfield = ['in_file'])

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
                               ref_slice=2),
                   name="sliceTiming")

#note added

# Realign - correct for motion
realign = Node(Realign(register_to_mean=True),
               name="realign")

# TSNR - remove polynomials 2nd order
tsnr = MapNode(TSNR(regress_poly=2),
               name='tsnr', iterfield=['in_file'])

# Artifact Detection - determine which of the images in the functional series
#   are outliers. This is based on deviation in intensity or movement.
art = Node(ArtifactDetect(norm_threshold=1,
                          zintensity_threshold=3,
                          mask_type='file',
                          parameter_source='SPM',
                          use_differences=[True, False]
                         ),
           name="art")

# Gunzip - unzip functional
gunzip = MapNode(Gunzip(), name="gunzip", iterfield=['in_file'])

#Gunzip - unzip anatomical
gunzip2 = Node(Gunzip(), name="gunzip2")


# Smooth - to smooth the images with a given kernel
smooth = Node(Smooth(fwhm=fwhm_size),
              name="smooth")

# FreeSurferSource - Data grabber specific for FreeSurfer data



# BBRegister - coregister a volume to the Freesurfer anatomical
"""bbregister = Node(BBRegister(init='fsl',
                             contrast_type='t1',
                             out_fsl_file=True),
                  name='bbregister')"""

coregister = Node(Coregister(), name='coregister')

# Volume Transformation - transform the brainmask into functional space
"""applyVolTrans = Node(ApplyVolTransform(inverse=True),
                     name='applyVolTrans')"""


#replaces volume transformation
normalize = Node(interface=Normalize(), name="normalize")
normalize.inputs.template = TPMLocation

# Binarize -  binarize and dilate an image to create a brainmask
binarize = Node(Binarize(min=0.5,
                         dilate=1,
                         out_type='nii'),
                name='binarize')


print("finished nodes")
###
# Specify Preprocessing Workflow & Connect Nodes

# Create a preprocessing workflow
preproc = Workflow(name='preproc')

# Connect all components of the preprocessing workflow
# Coregister: source image is the anatomical image, mean_image is the functional image
preproc.connect([(bet, sliceTiming, [('out_file', 'in_files')]),
                 (infosource, selectfiles2, [('subject_id', 'subject_id')]),
                 (selectfiles2, gunzip2, [('func', 'in_file')]),
                 (gunzip2, coregister, [('out_file', 'source')]),
                 #(sliceTiming, bet, [('timecorrected_files', 'in_file')]),
                 (sliceTiming, realign, [('timecorrected_files', 'in_files')]),
                 (realign, tsnr, [('realigned_files', 'in_file')]),
                 (tsnr, art, [('detrended_file', 'realigned_files')]),
                 (realign, art, [('mean_image', 'mask_file'),
                                 ('realignment_parameters',
                                  'realignment_parameters')]),
                 (tsnr, gunzip, [('detrended_file', 'in_file')]),
                 (gunzip, smooth, [('out_file', 'in_files')]),
                 (realign, coregister, [('mean_image', 'target')]),
                 (gunzip2, normalize, [('out_file', 'source')]),
                 (coregister, normalize, [('coregistered_files', 'apply_to_files')]),
                 #(coregister, normalize, [('coregistered_source', 'source')]),
                 #(realign, applyVolTrans, [('mean_image', 'source_file')]),
                 #(applyVolTrans, binarize, [('transformed_file', 'in_file')]),
                 ])





print("finish preprocess workflow")
###
# Specify 1st-Level Analysis Nodes



"""
# SpecifyModel - Generates SPM-specific Model
modelspec = Node(SpecifySPMModel(concatenate_runs=False,
                                 input_units='secs',
                                 output_units='secs',
                                 time_repetition=TR,
                                 high_pass_filter_cutoff=128),
                 name="modelspec")

# Level1Design - Generates an SPM design matrix
level1design = Node(Level1Design(bases={'hrf': {'derivs': [0, 0]}},
                                 timing_units='secs',
                                 interscan_interval=TR,
                                 model_serial_correlations='AR(1)'),
                    name="level1design")

# EstimateModel - estimate the parameters of the model
level1estimate = Node(EstimateModel(estimation_method={'Classical': 1}),
                      name="level1estimate")

# EstimateContrast - estimates contrasts
conestimate = Node(EstimateContrast(), name="conestimate")

# Volume Transformation - transform contrasts into anatomical space
applyVolReg = MapNode(ApplyVolTransform(fs_target=True),
                      name='applyVolReg',
                      iterfield=['source_file'])

# MRIConvert - to gzip output files
mriconvert = MapNode(MRIConvert(out_type='niigz'),
                     name='mriconvert',
                     iterfield=['in_file'])


###
# Specify 1st-Level Analysis Workflow & Connect Nodes

# Initiation of the 1st-level analysis workflow
l1analysis = Workflow(name='l1analysis')

# Connect up the 1st-level analysis components
l1analysis.connect([(modelspec, level1design, [('session_info',
                                                'session_info')]),
                    (level1design, level1estimate, [('spm_mat_file',
                                                     'spm_mat_file')]),
                    (level1estimate, conestimate, [('spm_mat_file',
                                                    'spm_mat_file'),
                                                   ('beta_images',
                                                    'beta_images'),
                                                   ('residual_image',
                                                    'residual_image')]),
                    (conestimate, applyVolReg, [('con_images',
                                                 'source_file')]),
                    (applyVolReg, mriconvert, [('transformed_file',
                                                'in_file')]),
                    ])
"""


# Specify Meta-Workflow & Connect Sub-Workflows
metaflow = Workflow(name='metaflow')
metaflow.base_dir = opj(experiment_dir, working_dir)

"""
metaflow.connect([(preproc, l1analysis, [('realign.realignment_parameters',
                                          'modelspec.realignment_parameters'),
                                         ('smooth.smoothed_files',
                                          'modelspec.functional_runs'),
                                         ('art.outlier_files',
                                          'modelspec.outlier_files'),
                                         ('binarize.binary_file',
                                          'level1design.mask_image'),
                                         ('bbregister.out_reg_file',
                                          'applyVolReg.reg_file'),
                                         ]),
                  ])


###
# Specify Model - Condition, Onset, Duration, Contrast

# Condition names
condition_names = ['congruent', 'incongruent']



# Contrasts
cont01 = ['congruent',   'T', condition_names, [1, 0]]
cont02 = ['incongruent', 'T', condition_names, [0, 1]]
cont03 = ['congruent vs incongruent', 'T', condition_names, [1, -1]]
cont04 = ['incongruent vs congruent', 'T', condition_names, [-1, 1]]
cont05 = ['Cond vs zero', 'F', [cont01, cont02]]
cont06 = ['Diff vs zero', 'F', [cont03, cont04]]

contrast_list = [cont01, cont02, cont03, cont04, cont05, cont06]

# Function to get Subject specific condition information
def get_subject_info(subject_id):
    from os.path import join as opj
    path = '/Volumes/Research2/Lighthall_Lab/experiments/cjfmri-1/data/fmri/Lucy_testing/Nipype/nipype_tutorial/data/%s' % subject_id
    onset_info = []
    for run in ['01', '02']:
        for cond in ['01', '02', '03', '04']:
            onset_file = opj(path, 'onset_run0%s_cond0%s.txt'%(run, cond))
            with open(onset_file, 'rt') as f:
                for line in f:
                    info = line.strip().split()
                    if info[1] != '0.00':
                        onset_info.append(['cond0%s'%cond,
                                           'run0%s'%run,
                                           float(info[0])])
    onset_run1_congruent = []
    onset_run1_incongruent = []
    onset_run2_congruent = []
    onset_run2_incongruent = []

    for info in onset_info:
        if info[1] == 'run001':
            if info[0] == 'cond001' or info[0] == 'cond002':
                onset_run1_congruent.append(info[2])
            elif info[0] == 'cond003' or info[0] == 'cond004':
                onset_run1_incongruent.append(info[2])
        if info[1] == 'run002':
            if info[0] == 'cond001' or info[0] == 'cond002':
                onset_run2_congruent.append(info[2])
            elif info[0] == 'cond003' or info[0] == 'cond004':
                onset_run2_incongruent.append(info[2])

    onset_list = [sorted(onset_run1_congruent), sorted(onset_run1_incongruent),
                  sorted(onset_run2_congruent), sorted(onset_run2_incongruent)]

    from nipype.interfaces.base import Bunch
    condition_names = ['congruent', 'incongruent']

    subjectinfo = []
    for r in range(2):
        onsets = [onset_list[r*2], onset_list[r*2+1]]
        subjectinfo.insert(r,
                           Bunch(conditions=condition_names,
                                 onsets=onsets,
                                 durations=[[0], [0]],
                                 amplitudes=None,
                                 tmod=None,
                                 pmod=None,
                                 regressor_names=None,
                                 regressors=None))
    return subjectinfo

# Get Subject Info - get subject specific condition information
getsubjectinfo = Node(Function(input_names=['subject_id'],
                               output_names=['subject_info'],
                               function=get_subject_info),
                      name='getsubjectinfo')

"""
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
metaflow.connect([(infosource, selectfiles, [('subject_id', 'subject_id')]),
                  #(infosource, selectfiles2, [('subject_id', 'subject_anat')]),
                  #(selectfiles2, preproc, [('func', 'bbregister.source_file')]),
                  (selectfiles, preproc, [('func', 'bet.in_file')]),
                  (preproc, datasink, [('realign.mean_image',
                                        'preprocout.@mean'),
                                       ('realign.realignment_parameters',
                                        'preprocout.@parameters'),
                                       ('art.outlier_files',
                                        'preprocout.@outliers'),
                                       ('art.plot_files',
                                        'preprocout.@plot'),
                                       ('coregister.coregistered_files',
                                        'preprocout.@coregistered_files'),
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
print(bet.out_file)

