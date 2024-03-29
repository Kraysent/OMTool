from distutils.core import setup

setup(
    name="omtool",
    version="0.4.0",
    author="Artyom Zaporozhets",
    url="https://github.com/Kraysent/OMTool",
    description="Package and program that models N-Body problem in galactic evolution application.",
    long_description=open("README.md").read(),
    long_description_content_type="text/x-markdown",
    license="Apache-2.0",
    packages=[
        "omtool",
        "omtool.core",
        "omtool.core.datamodel",
        "omtool.core.configs",
        "omtool.core.utils",
        "omtool.core.integrators",
        "omtool.core.models",
        "omtool.core.tasks",
        "omtool.actions_before",
        "omtool.actions_after",
        "omtool.visualizer",
    ],
    test_suite="tests",
)
