import re
from setuptools import setup, find_packages

with open("README.md", mode="r", encoding="utf-8") as f:
    readme = f.read()

# parse the version instead of importing it to avoid dependency-related crashes
with open("repobee_sanitizer/__version.py", mode="r", encoding="utf-8",) as f:
    line = f.readline()
    __version__ = line.split("=")[1].strip(" '\"\n")
    assert re.match(r"^\d+(\.\d+){2}(-(alpha|beta|rc)(\.\d+)?)?$", __version__)

test_requirements = ["pytest", "repobee", "pytest-cov"]
required = ["repobee-plug"]

setup(
    name="repobee-sanitizer",
    version=__version__,
    description="A plugin for RepoBee to sanitize master repositories before "
    "being pushed to students",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Simon Larsén",
    author_email="slarse@slar.se",
    url="https://github.com/repobee/repobee-sanitizer",
    download_url="https://github.com/"
    "repobee"
    "/repobee-sanitizer"
    "/archive/v{}.tar.gz".format(__version__),
    license="MIT",
    packages=find_packages(exclude=("tests", "docs")),
    tests_require=test_requirements,
    install_requires=required,
    extras_require=dict(TEST=test_requirements),
    include_package_data=True,
    zip_safe=False,
)
