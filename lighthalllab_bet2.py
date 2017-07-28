from nipype.interfaces.fsl import BET
from os.path import join as opj
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.io import SelectFiles, DataSink
from nipype.pipeline.engine import Workflow, Node


#replace
experiment_dir = ""        # location of experiment folder
data_dir = opj(experiment_dir, 'data')  # location of data folder


subject_list = ["1002", "1003", "1004"]   # list of subject identifiers
session_list = ['anat']              # list of session identifiers

output_dir = 'output_anatbet_3'          # name of output folder
working_dir = 'workingdir_firstSteps'     # name of working directory

print("bruh")

# Create Node
bet = Node(BET(), name='bet_node')


# Create a preprocessing workflow
preproc = Workflow(name='preproc')
preproc.base_dir = opj(experiment_dir, working_dir)



infosource = Node(IdentityInterface(fields=['subject_id',
                                            'session_id']),
                  name="infosource")

infosource.iterables = [('subject_id', subject_list),
                        ('session_id', session_list)]

# SelectFiles
templates = {'func': '{subject_id}/Struct.nii.gz'}
selectfiles = Node(SelectFiles(templates,
                               base_directory=experiment_dir),
                   name="selectfiles")


print("checking")
# Datasink
datasink = Node(DataSink(base_directory=experiment_dir,
                         container=output_dir),
                name="datasink")

# Use the following DataSink output substitutions
substitutions = [('_subject_id', ''),
                 ('_session_id_', '')]
datasink.inputs.substitutions = substitutions

# Connect SelectFiles and DataSink to the workflow
preproc.connect([(infosource, selectfiles, [('subject_id', 'subject_id'),
                                            ('session_id', 'session_id')]),
                 (selectfiles, bet, [('func', 'in_file')]),
                 (bet, datasink, [('out_file', 'bet.@out_file')])

                 ])


print("done")

res = preproc.run()



print("done")# Import BET from the FSL interface