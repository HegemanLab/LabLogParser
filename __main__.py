#*** main *********************************************************************************
# The function calls functions to parse files
# 
# The function calls the function to parse the configuration file for each config file passed
# as an argument.  It then calls fileSelector.
#
# Uses the os.path and sys libraries
#
#******************************************************************************************
def main():
	import LLP.read

	#The library used for determining if a file exists
	import os.path
	#Library for passing arguments with python script
	import sys
	if(len(sys.argv) == 1):												#If the doesn't provide an argument use a configFile in the same directory
		configs = LLP.read.parseConfigFile(os.path.join(os.path.dirname(__file__), "configFile"))
		LLP.read.fileSelector(configs)
	else:																#Parse the file provided.
		n = 1
		while(n < len(sys.argv)):										#For each config file passed
			configs = LLP.read.parseConfigFile(sys.argv[n])				#Parse the config file
			LLP.read.fileSelector(configs)								#Run the parser based on the config file's settings
			n += 1


if __name__ == "__main__":
	main()
