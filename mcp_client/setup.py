from setuptools import setup

setup(
    name="mcp",
    version="0.1.0",
    py_modules=['server', 'agent_tools', 'util'],
    packages=['.'],
    package_dir={'': '.'},
    install_requires=[],
    python_requires=">=3.9",
)