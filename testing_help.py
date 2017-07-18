###
# Import modules
from os.path import join as opj
import nipype.interfaces.fsl
from nipype.interfaces.afni import Despike
from nipype.interfaces.freesurfer import (BBRegister, ApplyVolTransform,
                                          Binarize, MRIConvert, FSCommand, Tkregister2)
import nipype.interfaces.spm as spm
from nipype.interfaces.utility import Function, IdentityInterface
from nipype.interfaces.io import FreeSurferSource, SelectFiles, DataSink
from nipype.algorithms.rapidart import ArtifactDetect
from nipype.algorithms.misc import TSNR, Gunzip
from nipype.algorithms.modelgen import SpecifySPMModel
from nipype.pipeline.engine import Workflow, Node, MapNode
# MATLAB - Specify path to current SPM and the MATLAB's default∫\ mode
from nipype.interfaces.matlab import MatlabCommand

spm.Normalize.help()
#>>> from nipype.interfaces.freesurfer import BBRegister
