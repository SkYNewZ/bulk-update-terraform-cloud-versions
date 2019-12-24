# bulk-update-terraform-cloud-versions

[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Python script to masssively update Terraform version in given Terraform Cloud workspaces

## Getting started

You need a valid Python3.7 environment with pip installed

```bash
$ git clone https://github.com/SkYNewZ/bulk-update-terraform-cloud-versions.git bulk-update-terraform-cloud-versions
$ cd bulk-update-terraform-cloud-versions
$ pip install -e .
```

## Usage

```
➜ update-workspaces-tf-version --help
Usage: update-workspaces-tf-version [OPTIONS]

Options:
  --vcs TEXT                VCS to search workspaces with. Multiple options
                            are authorized  [required]
  --terraform-version TEXT  Terraform version to search for to search
                            workspaces with. E.g: 0.11  [required]
  --org TEXT                Terraform Cloud organization  [required]
  --branch TEXT             VCS branch to search workspaces with  [default:
                            master]
  --target-version TEXT     Terraform version to update to. E.g: 0.12.18
                            [default: 0.12.18]
  --strict                  Only search workspaces which exactly match given
                            version  [default: False]
  --help                    Show this message and exit.
```
