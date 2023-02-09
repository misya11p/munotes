from setuptools import setup


with open('README.md', 'r', encoding='utf-8') as fp:
    readme = fp.read()

requires = ["scipy", "IPython"]


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
    author="misya11p",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="music note chord sound",
    license="MIT",
)