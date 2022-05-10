from distutils.core import setup

setup(
    name="omtool",
    version="0.1.0",
    author="Kraysent",
    url="https://github.com/Kraysent/OMTool",
    description="Package and program that models N-Body problem in galactic evolution application.",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    license="Apache 2.0",
    packages=[
        "omtool",
        "omtool.core",
        "omtool.core.datamodel",
        "omtool.core.utils",
        "omtool.core.creation",
        "omtool.core.integration",
        "omtool.core.analysis",
        "omtool.handlers",
        "omtool.tasks",
        "omtool.io_service",
        "omtool.json_logger",
        "omtool.visualizer",
    ],
)
