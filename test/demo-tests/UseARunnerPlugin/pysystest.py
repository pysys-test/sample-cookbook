__pysys_title__   = r""" Demo of using a runner plugin called MyRunnerPlugin to access state shared across tests """
#                        ===============================================================================

__pysys_purpose__ = r""" 
	"""

__pysys_authors__ = "pysysuser"
__pysys_created__ = "1999-12-31"

import pysys
from pysys.constants import *
from pysys.basetest import BaseTest

class PySysTest(BaseTest):
	def execute(self):
		pass

	def validate(self):
		self.log.info('Used myrunnerplugin to get Python version: %s', self.runner.myrunnerplugin.pythonVersion)
		self.assertThat('len(pythonVersionString) > 0', pythonVersionString=self.runner.myrunnerplugin.pythonVersion)

	