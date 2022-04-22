"""uploads projects to Asana"""

__version__ = "0.1"

import os
import asyncio
import sys
from asanaUtils.client import asana_client
from menu import menu
from asanaUtils.projectFunctions import (
    create_projects,
    add_projects_to_portfolio,
    set_project_custom_fields,
)

##############################################
##              Main Function               ##
##  orchestrates all other functionality    ##
##############################################


async def main():
    [team, project_inputs, attribute_mapping, portfolio, token] = await menu()

    print("Creating projects...")
    projects = await create_projects(project_inputs, team, token)

    # add projects to portfolio
    print("Adding projects to the portfolio...")
    await add_projects_to_portfolio(projects, portfolio, token)
    print("Setting custom field values...")
    await set_project_custom_fields(projects, attribute_mapping, token)

    print(
        f"Complete! check out the results at https://app.asana.com/0/{portfolio['gid']}/overview"
    )

    return


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted - goodbye")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
