from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as fp:
    readme = fp.read()

setup(
    name="munotes",
    description="Handle musical note and chord in Python",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=["munotes"],
    package_dir={"munotes": "munotes"},
    url="https://github.com/misya11p/munotes",
    author="misya11p",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="music note chord",
    license="MIT",
)