from setuptools import find_packages, setup
setup(
    name="craamvert",
    packages=find_packages(include=['craamvert']),
    version='0.1.0',
    description='Convert data to fits type according to instruments available at CRAAM',
    author='Bruno Gomes Mortella, Julia V R Paiva',
    license="MIT",
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=["pytest==4.4.1"],
    test_suite="tests",
)