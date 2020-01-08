import setuptools

setuptools.setup(
    name="MassSpecLogParser",
	version='0.1',
    python_requires=">=3.6",
    description="A log processor made in python designed to parse logs and send them to an InfluxDB database.",
    author="Luke Gentle",
    author_email="lentle26@gmail.com",
    url="https://github.com/HegemanLab/LabLogParser",
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": ["MSLP = MSLP.__main__:main"]},
    package_data={"MSLP": ["d3.html", "databases/*"]},
)
