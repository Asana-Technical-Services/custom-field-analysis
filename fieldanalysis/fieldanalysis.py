"""uploads projects to Asana"""

__version__ = "0.1"

from operator import truediv
import os
import asyncio
import aiohttp
import sys
from .menu import menu

from .asanaUtils.client import asana_client
import csv

##############################################
##              Main Function               ##
##  orchestrates all other functionality    ##
##############################################


async def projectupload():
    """an async function to upload projects from a CSV to a portfolio in Asana"""

    ## create the client session with aiohttp - this library allows us to send multiple API requests at once in conjunction with asyncio
    async with aiohttp.ClientSession() as session:

        [
            workspace,
            token,
        ] = await menu(session)

        customFieldCounter = {}

        # get all projects in a workspace
        hasMore = True
        requests = []
        results = []
        limit = 100
        offset = ""
        url = f"/workspaces/{workspace}/projects?limit={limit}&opt_fields=custom_field_settings.custom_field"

        totalcount = 0

        while hasMore == True:

            if offset != "":
                url = f"/workspaces/{workspace}/projects?limit={limit}&opt_fields=custom_field_settings.custom_field&offset={offset}"

            result = await asana_client(
                **{
                    "method": "GET",
                    "url": url,
                    "session": session,
                    "token": token,
                }
            )

            projects = result["data"]

            if "next_page" in result:
                if result["next_page"] != None:
                    offset = result["next_page"]["offset"]
                else:
                    hasMore = False
            else:
                hasMore = False

            for project in projects:
                totalcount += 1
                for customFieldSetting in project["custom_field_settings"]:
                    if customFieldSetting["custom_field"]["gid"] in customFieldCounter:
                        customFieldCounter[customFieldSetting["custom_field"]["gid"]][
                            "count"
                        ] += 1
                    else:
                        customFieldCounter[
                            customFieldSetting["custom_field"]["gid"]
                        ] = customFieldSetting["custom_field"]
                        customFieldCounter[customFieldSetting["custom_field"]["gid"]][
                            "count"
                        ] = 1
            print(f"analyzed {totalcount} projects")

        print("done!")

        fileName = "Asana_Custom_Field_Audit_Sheet.csv"

        headers = ["gid", "count", "name", "type"]

        with open(fileName, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(list(customFieldCounter.values()))

    return


## main function which is targeted by the CLI command
def main():
    """runs the project upload function asynchronously"""

    try:
        asyncio.run(projectupload())
    except KeyboardInterrupt:
        print("\nInterrupted - goodbye")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


## if this file is run directly via Python:
if __name__ == "__main__":
    try:
        asyncio.run(projectupload())
    except KeyboardInterrupt:
        print("\nInterrupted - goodbye")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
