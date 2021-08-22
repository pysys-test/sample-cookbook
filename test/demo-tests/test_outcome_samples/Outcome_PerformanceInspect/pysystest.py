__pysys_title__   = r""" Demo of outcomes - INSPECT .svg charts from performance testing """
#                        ===============================================================================

__pysys_purpose__ = r""" Demonstrates how the INSPECT outcome prevents output files being purged (even with the --purge flag), 
	and how extra test artifacts can be collected based on filename using a writer (nb: this doesn't require 
	an INSPECT outcome, and in fact is often used instead of INSPECT), and how performance results can be logged.
	"""

__pysys_authors__ = "pysysuser"
__pysys_created__ = "1999-12-31"

__pysys_groups__           = "performance, disableCoverage; inherit=true"
__pysys_modes__            = r""" lambda helper: helper.inheritedModes+[
	# For now we run this test in just one mode, but could add additional modes if desired.
	{'mode':'CompressionGZip'}
	] """

import pysys
from pysys.constants import *

class PySysTest(pysys.basetest.BaseTest):
	def execute(self):
		server = self.startPython([self.input+'/my_server.py'], stdouterr='my_server', background=True)
		self.startPython([self.input+'/http_perf_client.py', 'measuring_the_thing'], stdouterr='http_perf_client')
	
	def validate(self):	
		# Before reporting performance results always assert that there were no errors - it would be very misleading to 
		# record any performance numbers if the test didn't actually do what it was meant to. 
		self.assertGrep('my_server.out', r' (ERROR|FATAL|WARN) .*', contains=False)
		self.assertGrep('http_perf_client.out', r'.*(ERROR|Error|Exception).*', contains=False)
		
		self.logFileContents('http_perf_client.out', includes=['Completed .+response iterations.+'])
		
		# Use grep to extract the data we need to calculate the throughput rate, with a regular expression.
		actualIterations = self.grep('http_perf_client.out', 'Completed (.*) response iterations')
		timeSecs = float(self.grep('http_perf_client.out', 'Completed .* response iterations in (.*) seconds'))
		
		# Now we call reportPerformanceResult to report the main performance numbers in a CSV file, for later analysis 
		# and comparison between versions. 
		# It's best to report "rates" rather than the total time taken, so that we can tweak the iteration count later 
		# if needed to get more stable numbers. 
		self.reportPerformanceResult(int(actualIterations.replace(',',''))/timeSecs, 
			# Each performance result is identified by a short string that uniquely identifies it. Make sure this 
			#   includes information about what mode it's running in and what this test does so that there's no need to 
			#   cross-reference the pysystest.* files to understand what it's doing. 
			# The unit is usually one of the predefined strings - "/s" (=per second; biggerIsBetter=True) for rates, 
			# or "ns" (=nanoseconds; biggerIsBetter=False) for small time values such as latencies; 
			# alternatively pass an instance of PerformanceUnit instance if you want custom units.  
			'MyServer /sensorValues response throughput rate with %s' % self.mode, '/s')
		
		# Extract all the latency values, convert to nanoseconds (which is the recommended units for sub-second 
		# values), and sort them so we can calculate the median.
		nsLatencies = sorted([float(latency)*(1000*1000*1000) for latency in 
			self.grepAll('http_perf_client.out', 'Response latency sample: (.*) seconds')])

		self.reportPerformanceResult(nsLatencies[len(nsLatencies)//2], 
			# Put the key information at the start of the string so it's easy to read when this string is sorted 
			# together with performance results from other tests. For example, here we put "latency" before 
			# saying whether this is a max or median, etc so that all the latency values are together. 
			'MyServer /sensorValues response latency median with %s' % self.mode, 'ns', 
			
			resultDetails=[('latencySamples',len(nsLatencies))])

		self.reportPerformanceResult(max(nsLatencies), 
			'MyServer /sensorValues response latency max with %s' % self.mode, 'ns', 
			resultDetails=[('latencySamples',len(nsLatencies))])
		
		# Optionally, you could also produce some detailed files (e.g. graphical plots of the performance 
		# characteristics for which many Python plugins are available) and then collect together the file types of 
		# interest, e.g. 
		self.addOutcome(INSPECT, 'Review the charts for desired performance characteristics: %s'%
			', '.join(sorted(f for f in os.listdir(self.output) if f.endswith('.svg'))))