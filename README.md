# Mass Spectrometer Parser
A log processor made in python designed to parse logs and send them to an InfluxDB database.
## Installation
### Requirements
* Python 3.6
### setup.py
Clone the repo and go to the its root directory. Install Mass Spec Log Parser by running the following command.
```
python3 setup.py install
```
## Operation
Run Mass Spec Log Parser by using the MSLP command followed by all the configuration files you want the Lab Log Parser to use.
```
MSLP [repeater] [/path/to/configFile] [/path/to/configFile]
```
### Installing as a windows service
* Install [Anaconda](https://www.anaconda.com/distribution/#download-section)
* [Download NSSM](https://nssm.cc/)
* From the MassSpecLogParser file run `python3 setup.py install`
* Edit Service.bat to include the location of the Anaconda installation and location of the MassSpecLogParser folder
* Place the NSSM folder in a permanent location
* From CMD run `.\nssm.exe install MassSpecLogParser`
* Select Service.bat as the path.
## Roadmap
* Add support for files with Unicode
* Add configuration file instruction page in github
* Format code with python black
* Add Unit Testing
* Perform function time optimization
