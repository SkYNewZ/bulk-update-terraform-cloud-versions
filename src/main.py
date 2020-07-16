#!/usr/bin/env python3

import os
import requests
import click
import sys
import colorama
from colorama import Fore, Style

if "ATLAS_TOKEN" not in os.environ:
    raise EnvironmentError(f"Failed because 'ATLAS_TOKEN' is not set.")

ATLAS_TOKEN = os.getenv("ATLAS_TOKEN")
# 0.8, 0.9, 0.10, 0.11, 0.12
AVAILABLE_TERRAFORM_VERSIONS = [f"0.{i}" for i in range(8, 13)]


def get_all_workspaces(
    vcs: list,
    searched_terraform_version: str,
    org: str,
    vcs_branch: str,
    target_version: bool,
    page_size=100,
    search_older=True,
) -> list:
    """Return all workspaces by given vcs and terraform version in given Terraform organization"""
    page_number = 1
    w = []
    print(f"{Fore.CYAN}Listing workspaces…")
    while True:
        # Get all workspaces in {page}
        r = requests.get(
            f"https://app.terraform.io/api/v2/organizations/{org}/workspaces?page%5Bnumber%5D={page_number}&page%5Bsize%5D={page_size}",
            headers={"Authorization": f"Bearer {ATLAS_TOKEN}"},
        )

        r = r.json()

        # Get next page number
        page_number = r.get("meta", {}).get("pagination", {}).get("next-page", {})

        # Process all workspaces
        r = r["data"]
        for workspace in r:
            attrs = workspace["attributes"]
            repo = attrs["vcs-repo"]

            workspace_name = attrs["name"]
            # if workspace does not have any vcs
            if not repo:
                print(f"{Fore.YELLOW}[SKIP] '{workspace_name}' does not have any vcs")
                continue

            workspace_vcs_branch = repo["branch"]
            # if workspace vcs does not match a wanted vcs
            if repo["identifier"] not in vcs:
                print(
                    f"{Style.DIM}[SKIP] '{workspace_name}' does not match a wanted vcs ({repo['identifier']})"
                )
                continue

            # check vcs branch
            # If branch not set : "default branch" in TFC
            if workspace_vcs_branch == "":
                print(
                    f"{Fore.YELLOW}[SKIP] '{workspace_name}' does not have any vcs branch specified"
                )
                continue

            # If wanted branch does not match
            if workspace_vcs_branch != vcs_branch:
                print(
                    f"{Style.DIM}[SKIP] '{workspace_name}' does not match a wanted vcs branch ({workspace_vcs_branch})"
                )
                continue

            workspace_terraform_version = attrs["terraform-version"]

            # if already at the wanted version
            if workspace_terraform_version == target_version:
                print(
                    f"{Style.DIM}[SKIP] '{workspace_name}' already at the wanted version."
                )
                continue

            # Search for matching version
            if searched_terraform_version not in workspace_terraform_version:
                # if search_older disable, continue
                if not search_older:
                    print(
                        f"{Style.DIM}[SKIP] '{workspace_name}' do not match wanted version and strict mode is enabled"
                    )
                    continue

                # Get index of workspace version : search with a 'in' comparator. e.g: if 0.8.8 in 0.8 for each version
                # 0.11.14 will be 0.11 and index 3
                for v in AVAILABLE_TERRAFORM_VERSIONS:
                    if v in workspace_terraform_version:
                        current_terraform_version_index = AVAILABLE_TERRAFORM_VERSIONS.index(
                            v
                        )

                    if v in searched_terraform_version:
                        # If we don't find the exact version, try to search a older one
                        # Get index of searched version
                        wanted_terraform_version_index = AVAILABLE_TERRAFORM_VERSIONS.index(
                            v
                        )

                # if current version is older than wanted version, take it
                if current_terraform_version_index > wanted_terraform_version_index:
                    print(
                        f"{Style.DIM}[SKIP] '{workspace_name}' do not match wanted version"
                    )
                    continue

            # We have one, add it to main list
            format_print(workspace, target_version)
            w.append(workspace)

        # Break the loop if we reach the end
        if not page_number or page_number == "null":
            break
    return w


def update_workspace_terraform_version(update_to: str, workspace: dict, org: str):
    """Switch given workspace Terraform version to given version"""
    workspace_name = workspace["attributes"]["name"]
    payload = {
        "data": {
            "attributes": {"name": workspace_name, "terraform_version": update_to},
            "type": "workspaces",
        }
    }
    r = requests.patch(
        f"https://app.terraform.io/api/v2/organizations/{org}/workspaces/{workspace_name}",
        json=payload,
        headers={
            "Content-Type": "application/vnd.api+json",
            "Authorization": f"Bearer {ATLAS_TOKEN}",
        },
    )

    if r.status_code >= 400:
        err = r.json()["errors"][0]["title"]
        print(f"{Fore.RED}Workspace '{workspace_name}' error: {err}")
        return

    print(f"{Fore.GREEN}Workspace: '{workspace_name}' done.")


def format_print(w: dict, terraform_version: str):
    """Format workspace name and version into console"""
    n = w["attributes"]["name"]
    v = w["attributes"]["terraform-version"]
    print(f"{Fore.CYAN}Workspace: '{n}' ({v}) will be updated to {terraform_version}.")


def validate_terraform_version(check: str) -> bool:
    """Check if given Terraform version is available"""
    return any(version in check for version in AVAILABLE_TERRAFORM_VERSIONS)


@click.command()
@click.option(
    "--vcs",
    multiple=True,
    help="VCS to search workspaces with. Multiple options are authorized",
    required=True,
)
@click.option(
    "--terraform-version",
    help="Terraform version to search for to search workspaces with. E.g: 0.11",
    required=True,
)
@click.option("--org", help="Terraform Cloud organization", required=True)
@click.option(
    "--branch",
    help="VCS branch to search workspaces with",
    default="master",
    show_default=True,
)
@click.option(
    "--target-version",
    help="Terraform version to update to. E.g: 0.12.18",
    show_default=True,
    default="0.12.18",
)
@click.option(
    "--strict",
    help="Only search workspaces which exactly match given version",
    show_default=True,
    default=False,
    type=bool,
    is_flag=True,
)
def main(
    vcs: tuple,
    terraform_version: str,
    org: str,
    branch: str,
    target_version: str,
    strict: bool,
):
    colorama.init(autoreset=True)

    # Ensure given Terraform version exist
    v = ", ".join(AVAILABLE_TERRAFORM_VERSIONS)
    if not validate_terraform_version(terraform_version):
        print(
            f"{Fore.RED}Invalid Terraform version to search with. Given: {terraform_version}. Want: {v}{Fore.RED}"
        )
        sys.exit(1)

    if not validate_terraform_version(target_version):
        print(
            f"{Fore.RED}Invalid Terraform version to set to workspaces. Given: {target_version}. Want: {v}{Fore.RED}"
        )
        sys.exit(1)

    # Get all workspaces
    workspaces = get_all_workspaces(
        vcs=list(vcs),
        searched_terraform_version=terraform_version,
        org=org,
        vcs_branch=branch,
        search_older=not strict,
        target_version=target_version,
    )

    l = len(workspaces)
    vcs = "|".join(vcs)
    print(
        f"\n{Fore.GREEN}Found {l} workspace(s) matching '{vcs}' vcs, {branch} branch and Terraform version {terraform_version}."
    )
    if not l:
        print(f"{Fore.GREEN}Nothing to do.")
        sys.exit(0)

    while True:
        i = input(
            f"\n{Fore.YELLOW}Proceed ? Operation cannot be revert… (y/N) "
        ).upper()
        if i != "Y" and i != "N":
            continue

        if i == "N":
            print("Exiting…")
            sys.exit(0)

        else:
            break

    # Lauch main process : update all given workspaces with given Terraform version in given org
    for w in workspaces:
        update_workspace_terraform_version(
            update_to=target_version, workspace=w, org=org
        )

    print(f"\n{Fore.GREEN}Done.")


if __name__ == "__main__":
    main()
