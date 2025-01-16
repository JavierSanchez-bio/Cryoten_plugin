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
import pyworkflow.utils as pwutils
import pwem
import subprocess

__version__ = "1.0.0"  # plugin version
_logo = "icon.png"
_references = ['cryoten2025']

# Define V1 before using it
V1 = "1.0.0"

class Plugin(pwem.Plugin):
    _url = "https://github.com/scipion-em/scipion-em-cryoten"
    _supportedVersions = [V1]  # binary version

    @classmethod
    def getEnvActivation(cls):
        return f"conda activate cryoten_env"

    @classmethod
    def getEnviron(cls, gpuID=None):
        """ Setup the environment variables needed to launch the program. """
        environ = pwutils.Environ(os.environ)

        if gpuID is not None:
            environ["CUDA_VISIBLE_DEVICES"] = gpuID

        return environ

    @classmethod
    def getCryotenProgram(cls, program):
        cmd = '%s %s && python %s' % (cls.getCondaActivationCmd(), cls.getEnvActivation(), program)
        return cmd

    @classmethod
    def getCommand(cls, program, args):
        return cls.getCryotenProgram(program) + args

    @classmethod
    def defineBinaries(cls, env):

        def getCryotenInstallationCommands():
            commands = cls.getCondaActivationCmd() + " "
            commands += "if [ ! -d cryoten ]; then git clone https://github.com/jianlin-cheng/cryoten; fi && "
            commands += "cd cryoten && "
            commands += "if [ ! -f cryoten.ckpt ]; then wget https://zenodo.org/records/12693785/files/cryoten.ckpt; fi && "
            commands += "if [ ! -d /home/javier/miniconda/envs/cryoten_env ]; then conda env create -f environment.yaml; fi && "
            commands += f"conda activate cryoten_env && "
            commands += "touch ../cryoten_installed"
            return commands

        installCmds = [(getCryotenInstallationCommands(), "cryoten_installed")]
        env.addPackage('cryoten', version=V1, tar='void.tgz', commands=installCmds, default=True)
