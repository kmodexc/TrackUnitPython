import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pytrackunit",
    version="0.0.1",
    author="Marius Schlüter",
    author_email="themrslue@googlemail.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/einsteinmaster/TrackUnitPython",
    project_urls={
        "Bug Tracker": "https://github.com/einsteinmaster/TrackUnitPython/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "TrackUnitPython"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)