import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="takedown",
    version="0.1.1",
    author="Zesheng Xing",
    author_email="zsxing@ucdavis.edu",
    description="A simple python script/package that allows users to search potential copyright violated information "
                "on GitHub",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zsxing99/Takedown-script",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    install_requires=[
        "requests~=2.23.0",
        "PyYAML~=5.3.1"
    ],
    project_urls={
        "GitHub": "https://github.com/zsxing99/Takedown-script",
        "GitLab": "https://gitlab.com/luplab/luptakedown"
    },
    entry_points={
        'console_scripts': [
            'takedown = takedown.takedown:main'
        ]
    },
)
