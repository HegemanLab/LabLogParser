# Lab Log Parser
A log processor made in python designed to parse logs and send them to an InfluxDB database.
## Installation
### Requirements
* Python3
### setup.py
Clone the repo and go to the its root directory. Install Lab Log Parser by running the following command.
```
python3 setup.py install
```
## Operation
Run LabLogParser by using the LLP command followed by all the configuration files you want the Lab Log Parser to use.
```
LLP [/path/to/configFile] [/path/to/configFile]
```
## Roadmap
* Add option to specify timezone in config file and convert timestamp to UTC.  (How should daylight savings be handled?)
* Add support for files with Unicode
* Add configuration file instruction page in github
* Format code with python black
* Add Unit Testing
* Perform function time optimization
