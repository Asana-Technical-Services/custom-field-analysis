import sys
import csv
from .asanaUtils.client import asana_client

"""
input menu + associated functions

used for gathering all user inputs, mapping fields, and verifying that mapping before proceeding.
"""


async def menu(session):
    """
    Collect user inputs of: Personal Access Token, portfolio link, team link, and CSV file.
    provides back the team, mapped project data, necessary project statuses, attribute mapping, portfolio, and the user's Personal Access Token
        project_data,
        project_statuses,
        portfolio,
        session,
        token,
    """

    # get access token
    token = input("paste your personal access account token: ")

    # test the token to ensure it works
    user = await asana_client(
        **{"method": "GET", "url": "/users/me", "session": session, "token": token}
    )
    if not user:
        sys.exit("invalid account token")

    print("\nyou are a member of these workspaces:")
    for space in user["data"]["workspaces"]:
        print(f"{space['name']} - GID: {space['gid']}")

    # get link to portfolio and split it to get the Global ID
    workspace_gid = input("input the workspace GID you want to analyze: ")

    # try getting the workspace from Asana to make sure it exists and we can access it
    workspace = await asana_client(
        **{
            "method": "GET",
            "url": f"/workspaces/{workspace_gid}",
            "session": session,
            "token": token,
        }
    )

    if not workspace:
        sys.exit(
            "could not get workspace or it does not exist. check that you have access to it"
        )

    include_projects = input(
        "Would you also like to count the projects that use the custom field? This can take several minutes longer, depending on your workspace size? (y/N)"
    )

    if include_projects in ["Y", "y", "yes", "Yes"]:
        projects_flag = True
    else:
        projects_flag = False

    print("proceeding...")

    return [
        workspace_gid,
        workspace["data"]["name"],
        projects_flag,
        token,
    ]
