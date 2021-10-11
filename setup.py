from setuptools import setup

with open("README.md") as f:
    readme = f.read()

setup(
    name="vpype-gcode",
    version="0.10.0",
    description="vpype gcode plugin",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Tatarize",
    author_email="tatarize@gmail.com",
    url="https://github.com/plottertools/vpype-gcode/",
    packages=["vpype_gcode"],
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Environment :: Console",
        "Topic :: Artistic Software",
        "Topic :: Multimedia :: Graphics",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    include_package_data=True,
    install_requires=[
        "click",
        "vpype",
        "numpy",
    ],
    entry_points="""
            [vpype.plugins]
            gwrite=vpype_gcode.gwrite:gwrite
        """,
)
