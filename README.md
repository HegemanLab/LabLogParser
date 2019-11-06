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
MSLP [/path/to/configFile] [/path/to/configFile]
```
## Roadmap
* Add support for files with Unicode
* Add configuration file instruction page in github
* Format code with python black
* Add Unit Testing
* Perform function time optimization
