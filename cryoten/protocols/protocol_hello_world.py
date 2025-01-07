# -*- coding: utf-8 -*-
# **************************************************************************

"""
Describe your python module here:
This module will run the provided shell commands.
"""
import os
import subprocess
from pyworkflow.constants import BETA
import pyworkflow.protocol.params as params
from pyworkflow.utils import Message
from pwem.protocols import EMProtocol
from pwem.objects import Volume  # Import the Volume class to define the output


class CryotenPrefixHelloWorld(EMProtocol):
    """
    This protocol will run the provided shell commands.
    IMPORTANT: Classes names should be unique, better prefix them
    """
    _label = 'enhance map'
    _devStatus = BETA

    # -------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        """ Define the input parameters that will be used.
        Params:
            form: this is the form to be populated with sections and params.
        """
        form.addSection(label=Message.LABEL_INPUT)

        form.addParam('condaPath', params.StringParam,
                      default='/home/javier/miniconda/etc/profile.d/conda.sh',
                      label='Conda Path',
                      help='Path to the conda.sh script.')

        form.addParam('projectPath', params.StringParam,
                      default='/home/javier/cryoten',
                      label='Path to cryoten',
                      help='Path to the Cryoten software folder.')

        form.addParam('outputFile', params.StringParam,
                      default='/home/javier/cryoten/output/emd_1111_cryoten.mrc',
                      label='Output File',
                      help='Path to the output file (.mrc).')

        form.addParam('inputVolume', params.PointerParam,
                      label='Input Volume',
                      pointerClass='Volume',
                      help='Select the volume to be processed.')

    # --------------------------- STEPS functions ------------------------------
    def _insertAllSteps(self):
        self._insertFunctionStep(self.runShellCommandsStep)
        self._insertFunctionStep(self.createOutputStep)

    def runShellCommandsStep(self):
        def run_command(command):
            """Run a shell command and handle any errors."""
            process = subprocess.run(command, shell=True, executable='/bin/bash', stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
            stdout = process.stdout.decode('utf-8')
            stderr = process.stderr.decode('utf-8')
            if process.returncode != 0:
                raise Exception(f"Command '{command}' failed with error: {stderr}")
            return stdout, stderr

        try:
            # Get the file path of the input volume
            inputFilePath = self.inputVolume.get().getFileName()

            # Get the base path of the Scipion project
            basePath = self.getProject().getPath()

            # Construct the full path
            fullInputFilePath = os.path.join(basePath, inputFilePath)

            # Print the full input file path for verification
            print(f"Full input file path: {fullInputFilePath}")

            # Construct the command
            command = f"""
                source {self.condaPath.get()} && \
                conda activate cryoten_env && \
                cd {self.projectPath.get()} && \
                python eval.py {fullInputFilePath} {self.outputFile.get()}
            """
            print(f"Running command: {command}")

            # Execute the command
            stdout, stderr = run_command(command)

            # Log the output and error messages
            print(f"Command output: {stdout}")
            print(f"Command error: {stderr}")

        except Exception as e:
            print(f"An error occurred: {e}")

    def createOutputStep(self):
        """Create output volume and register it in Scipion."""
        outputVolume = Volume()
        outputVolume.setFileName(self.outputFile.get())
        self._defineOutputs(outputVolume=outputVolume)
        self._defineSourceRelation(self.inputVolume, outputVolume)

    # --------------------------- INFO functions -----------------------------------
    def _validate(self):
        errors = []
        return errors

    def _summary(self):
        """ Summarize what the protocol has done"""
        summary = []
        summary.append(f"Output volume: {self.outputFile.get()}")
        return summary

    def _methods(self):
        methods = []
        methods.append("This protocol enhances a map using the Cryoten software.")
        return methods