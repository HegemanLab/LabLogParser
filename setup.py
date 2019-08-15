import setuptools

setuptools.setup(
    name="LabLogParser",
	version='0.1',
    python_requires=">=3.6",
    description="A log processor made in python designed to parse logs and send them to an InfluxDB database.",
    author="Luke Gentle",
    author_email="lentle26@gmail.com",
    url="https://github.com/HegemanLab/LabLogParser",
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": ["LLP = LLP.__main__:main"]},
    package_data={"LLP": ["d3.html", "databases/*"]},
)
