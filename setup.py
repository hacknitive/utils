from setuptools import setup, find_packages

# =========================================================== 
# LONG DESCRIPTION
# ===========================================================
with open("README.md", "r", encoding="utf-8") as handler:
    LONG_DESCRIPTION = handler.read()


# ===========================================================
#  REQUIREMENTS
# ===========================================================
def parse_requirements(filename):
    with open(filename) as f:
        return f.read().splitlines()

INSTALL_REQUIRES = parse_requirements('requirements.txt')

# ===========================================================
# SETUP
# ===========================================================
setup(
    name="utils",
    version="v0.0.2",
    packages=find_packages(include=['utils', 'utils.*']),
    install_requires=INSTALL_REQUIRES,
    author="Reza 'Sam' Aghamohammadi (Hacknitive)",
    author_email="hacknitive@gmail.com",
    description="Utility for ...",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/hacknitive/utils",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
