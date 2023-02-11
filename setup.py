from setuptools import setup


with open("README.md", "r", encoding="utf-8") as fp:
    readme = fp.read()

requires = [
    "scipy",
    "ipython"
    ]


setup(
    name="munotes",
    description="Handle musical notes and their sounds in Python",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=["munotes"],
    package_dir={"munotes": "munotes"},
    python_requires=">=3.7",
    install_requires=requires,
    url="https://github.com/misya11p/munotes",
    project_urls={
        "Source": "https://github.com/misya11p/munotes",
        "API Reference": "https://misya11p.github.io/munotes/",
    },
    author="misya11p",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="music note chord sound waveform",
    license="MIT",
)
