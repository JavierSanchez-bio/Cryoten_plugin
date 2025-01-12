# -*- coding: utf-8 -*-
# **************************************************************************
# *
# * Authors:     Javier Sanchez (scipion@cnb.csic.es)
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************


import os
import subprocess
from pyworkflow.constants import BETA
import pyworkflow.protocol.params as params
from pyworkflow.utils import Message
from pwem.protocols import EMProtocol
from pwem.objects import Volume  # Import the Volume class to define the output


class CryotenPrefixEnhace(EMProtocol):
    """
    This protocol will enhace the map using Cryoten software.
    IMPORTANT: Classes names should be unique, better prefix them
    """
    _label = 'enhance map'
    _devStatus = BETA

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.outputFilePath = None  # Initialize the outputFilePath attribute

    # -------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        """ Define the input parameters that will be used.
        Params:
            form: this is the form to be populated with sections and params.
        """
        form.addSection(label=Message.LABEL_INPUT)

        form.addParam('inputVolume', params.PointerParam,
                      label='Input Volume',
                      pointerClass='Volume',
                      help='Select the volume to be processed.')

    # --------------------------- STEPS functions ------------------------------
    def _insertAllSteps(self):
        self._insertFunctionStep(self.runShellCommandsStep)
        self._insertFunctionStep(self.createOutputStep)

    def get_conda_path(self):
        """Determine the path to the conda.sh script dynamically."""
        try:
            result = subprocess.run(['conda', 'info', '--base'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            base_path = result.stdout.decode('utf-8').strip()
            if result.returncode == 0 and base_path:
                return os.path.join(base_path, 'etc', 'profile.d', 'conda.sh')
            else:
                raise Exception(f"Failed to determine conda base path: {result.stderr.decode('utf-8')}")
        except Exception as e:
            raise Exception(f"An error occurred while determining conda path: {e}")

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

            print(f"Input file path: {inputFilePath}")

            # Get the base path of the Scipion project
            basePath = self.getProject().getPath()

            # Construct the full path
            fullInputFilePath = os.path.join(basePath, inputFilePath)

            # Print the full input file path for verification
            print(f"Full input file path: {fullInputFilePath}")

            # Determine the conda path dynamically
            condaPath = self.get_conda_path()

            # Get the Scipion base path from an environment variable
            scipion_base_path = os.getenv('SCIPION_BASE_PATH', os.path.expanduser('~/scipion'))

            # Construct the Cryoten path based on the Scipion base path
            cryotenPath = os.path.join(scipion_base_path, 'software/em/cryoten-1.0.0/cryoten')

            # Construct the output file path
            inputFileName = os.path.basename(inputFilePath)
            print(f"Input file name: {inputFileName}")
            outputFileName = os.path.splitext(inputFileName)[0] + '.mrc'
            outputFilePath = os.path.join(cryotenPath, 'output', outputFileName)

            # Construct the command
            command = f"""
                source {condaPath} && \
                conda activate cryoten_env && \
                cd {cryotenPath} && \
                python eval.py {fullInputFilePath} {outputFilePath}
            """
            print(f"Running command: {command}")

            # Execute the command
            stdout, stderr = run_command(command)

            # Log the output and error messages
            print(f"Command output: {stdout}")
            print(f"Command error: {stderr}")

            # Save the output file path for the next step
            self.outputFilePath = outputFilePath
            print(f"Output file path set to: {self.outputFilePath}")

        except Exception as e:
            print(f"An error occurred: {e}")

    def createOutputStep(self):
        """Create output volume and register it in Scipion."""
        if not self.outputFilePath:
            raise RuntimeError("Output file path is not set. Ensure runShellCommandsStep has been executed successfully.")

        outputVolume = Volume()
        outputVolume.setFileName(self.outputFilePath)

        # Copy the voxel size from the input volume to the output volume
        voxelSize = self.inputVolume.get().getSamplingRate()
        outputVolume.setSamplingRate(voxelSize)

        self._defineOutputs(outputVolume=outputVolume)
        self._defineSourceRelation(self.inputVolume, outputVolume)

    # --------------------------- INFO functions -----------------------------------
    def _validate(self):
        errors = []
        return errors

    def _summary(self):
        """ Summarize what the protocol has done"""
        summary = []
        summary.append(f"Output volume: {self.outputFilePath}")
        return summary

    def _methods(self):
        methods = []
        methods.append("This protocol enhances a map using the Cryoten software.")
        return methods
