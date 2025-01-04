# -*- coding: utf-8 -*-
# **************************************************************************
# *
# * Authors:     JAVIER SANCHEZ (scipion@cnb.csic.es)
# *
# * CNB - CSIC
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


"""
Describe your python module here:
This module will integrate CryoTen functionality into Scipion.
"""
from enum import Enum

from pyworkflow.constants import BETA
import pyworkflow.protocol.params as params
from pyworkflow.utils import Message
from pyworkflow.object import String
from pwem.protocols import EMProtocol

class outputs(Enum):
    resultPath = String

class CryotenPrefixRunCryoTen(EMProtocol):
    """
    This protocol will run CryoTen software with specified parameters.
    IMPORTANT: Classes names should be unique, better prefix them
    """
    _label = 'Run CryoTen'
    _devStatus = BETA
    _possibleOutputs = outputs

    # -------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        """ Define the input parameters that will be used.
        Params:
            form: this is the form to be populated with sections and params.
        """
        form.addSection(label=Message.LABEL_INPUT)

        form.addParam('inputFile', params.StringParam,
                      label='Input file',
                      help='Path to the input file for CryoTen.',
                      important=True)

        form.addParam('outputDir', params.StringParam,
                      label='Output directory',
                      help='Directory where CryoTen results will be saved.',
                      important=True)

        form.addParam('additionalParams', params.StringParam,
                      label='Additional parameters',
                      help='Optional additional parameters to pass to CryoTen.',
                      default='')

    # --------------------------- STEPS functions ------------------------------
    def _insertAllSteps(self):
        # Insert processing steps
        self._insertFunctionStep(self.runCryoTenStep)
        self._insertFunctionStep(self.createOutputStep)

    def runCryoTenStep(self):
        """ Run the CryoTen software with the provided parameters. """
        import os

        inputFile = self.inputFile.get()
        outputDir = self.outputDir.get()
        additionalParams = self.additionalParams.get()

        # Ensure the output directory exists
        if not os.path.exists(outputDir):
            os.makedirs(outputDir)

        # Construct the CryoTen command
        cryotenCommand = f"cryoten --input {inputFile} --output {outputDir} {additionalParams}"

        # Execute the command
        print(f"Running CryoTen command: {cryotenCommand}")
        os.system(cryotenCommand)

    def createOutputStep(self):
        """ Define outputs for the protocol. """
        resultPath = f"{self.outputDir.get()}/results"

        self._defineOutputs(**{outputs.resultPath.name: resultPath})
        self._defineSourceRelation(self.inputFile, resultPath)

    # --------------------------- INFO functions -----------------------------------
    def _validate(self):
        errors = []

        if not self.inputFile.get():
            errors.append("Input file is required.")
        if not self.outputDir.get():
            errors.append("Output directory is required.")

        return errors

    def _summary(self):
        """ Summarize what the protocol has done."""
        summary = []

        if self.isFinished():
            summary.append(f"CryoTen has been executed. Results are stored in {self.outputDir.get()}.")
        return summary

    def _methods(self):
        methods = []

        if self.isFinished():
            methods.append(f"CryoTen was executed with input file: {self.inputFile.get()} and results saved to: {self.outputDir.get()}.")
        return methods
