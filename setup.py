import setuptools

from src import __version__


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="update-workspaces-tf-version",
    version=__version__,
    author="Quentin Lemaire",
    author_email="quentin@lemairepro.fr",
    license="MIT",
    keywords="API Terraform TFC",
    description="Bulk update Terraform version of given workspaces",
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/SkYNewZ/bulk-update-terraform-cloud-versions",
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    extras_require={
        "dev": ["black", "twine", "wheel"],
        "test": ["pytest", "coverage", "pytest-cov", "requests-mock"],
    },
    tests_require=["pytest", "pytest-cov"],
    install_requires=["requests", "Click", "colorama"],
    entry_points={
        "console_scripts": [
            "update-workspaces-tf-version=src.__main__:update_workspaces_tf_version",
        ],
    },
)
