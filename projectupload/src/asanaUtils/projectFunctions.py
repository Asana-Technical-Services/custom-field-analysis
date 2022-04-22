from operator import contains
from client import asana_client
import sys
import os
import random
import asyncio
import re


async def create_projects(projects, team, token):

    # rate limits impose a limit of 15 writes per user
    # so, every 14 calls we wait for the previous calls to finish
    # requests array
    requests = []
    project_results = []
    project_counter = 0
    for project in projects:
        print(project)
        # increment project counter
        project_counter += 1

        data = {"data": {"name": project["name"], "team": team["gid"]}}

        requests.append(
            asana_client(
                **{
                    "method": "POST",
                    "url": "/projects",
                    "data": data,
                    "token": token,
                }
            )
        )

        if project_counter % 14 == 0 or project_counter == len(projects):
            project_results += await asyncio.gather(*requests)
            requests = []

    for i in range(0, len(projects)):
        projects[i]["gid"] = project_results[i]["gid"]

    return projects


async def add_projects_to_portfolio(projects, portfolio, token):
    # rate limits impose a limit of 15 writes per user
    # so, every 14 calls we wait to gather
    requests = []
    results = []
    project_counter = 0
    print(projects)
    for project in projects:
        # increment project counter
        project_counter += 1
        print(project)

        data = {"data": {"item": project["gid"]}}

        requests.append(
            asana_client(
                **{
                    "method": "POST",
                    "url": f"/portfolios/{portfolio['gid']}/addItem",
                    "data": data,
                    "token": token,
                }
            )
        )

        if project_counter % 14 == 0 or project_counter == len(projects):
            results += await asyncio.gather(*requests)
            requests = []

    return


async def set_project_custom_fields(projects, attribute_mapping, token):

    requests = []
    results = []
    project_counter = 0
    for project in projects:
        # increment project counter
        project_counter += 1

        data = {"data": project}

        requests.append(
            asana_client(
                **{
                    "method": "PUT",
                    "url": f"/projects/{project['gid']}",
                    "data": data,
                    "token": token,
                }
            )
        )

        if project_counter % 14 == 0 or project_counter == len(projects):
            results += await asyncio.gather(*requests)
            requests = []

    return results


def map_project_fields(project, attribute_mapping):
    project_data = {"custom_fields": {}, "owner": None}

    for field in project:

        if project[field] != "" and field in attribute_mapping:
            attribute = attribute_mapping[field]

            ## check for standard field use cases
            if attribute == "name":
                project_data[attribute] = project[field]

            elif attribute == "owner":
                if re.search(
                    "[a-zA-Z0-9._%+-]*?@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}", project[field]
                ):
                    project_data[attribute] = project[field]
                else:
                    print(
                        f'WARN: could not map Owner on a project as the input "{project[field]}" isn\'t a valid email'
                    )

            elif attribute == "start_on":
                if re.search("\d{4}-\d{2}\-\d{2}", project[field]):
                    if (
                        "due_date" in project_data
                        and project_data["due_date"] <= project[field]
                    ):
                        print(
                            f"WARN: start date on project is before its due date - will not map start date"
                        )
                    else:
                        project_data[attribute] = project[field]
                else:
                    print(
                        f'WARN: could not map start date on project as the input "{project[field]}" must be in "yyyy-mm-dd" format'
                    )

            elif attribute == "due_date":
                if re.search("\d{4}-\d{2}\-\d{2}", project[field]):
                    if (
                        "start_date" in project_data
                        and project_data["start_date"] >= project[field]
                    ):
                        print(
                            f"WARN: start date on project is before its due date - will not map start date"
                        )
                        del project_data["start_date"]

                    project_data[attribute] = project[field]
                else:
                    print(
                        f'WARN: could not map end date on project as the input "{project[field]}" must be in "yyyy-mm-dd" format'
                    )

            # if the field isn't the GID and isn't a standard field, it's a custom field
            else:
                if attribute["type"] == "text":
                    project_data["custom_fields"][attribute["gid"]] = project[field]

                elif attribute["type"] == "number":
                    try:
                        number_value = float(project[field])
                    except:
                        print(
                            f'WARN: could not map number field "{field}"on project as the input "{project[field]}" isn\'t a numeric value'
                        )
                    else:
                        project_data["custom_fields"][attribute["gid"]] = number_value

                elif attribute["type"] == "enum":
                    try:
                        enum_option_gid = attribute["enum_dict"][
                            project[field].lower()
                        ]["gid"]
                    except:
                        print(
                            f'WARN: could not map enum field "{field}" on project as the input "{project[field]}" isn\'t an option'
                        )
                    else:
                        project_data["custom_fields"][
                            attribute["gid"]
                        ] = enum_option_gid

                elif attribute["type"] == "multi_enum":
                    multi_values = []
                    desired_values = project[field]
                    if desired_values:
                        desired_values = desired_values.replace('"', "").split(",")
                        for value in desired_values:
                            stripped_value = value.strip().lower()
                            try:
                                enum_option_gid = attribute["enum_dict"][
                                    stripped_value
                                ]["gid"]
                            except:
                                print(
                                    f'WARN: could not map a value on the multi-enum field "{field}" on project as the input "{project[field]}" isn\'t an option'
                                )
                            else:
                                project_data["custom_fields"][
                                    attribute["gid"]
                                ] = enum_option_gid
                            multi_values.append(
                                attribute["enum_dict"][stripped_value]["gid"]
                            )

                        project_data["custom_fields"][attribute["gid"]] = multi_values

    if "start_on" in project_data and "due_date" not in project_data:
        project_data["due_date"] = project_data["start_on"]
        del project_data["start_on"]

        print(
            f"WARN: there is only a start date on project. Using the start date as its due date"
        )

    elif "start_on" in project_data and "due_date" in project_data:
        if project_data["due_date"] <= project_data["start_on"]:
            print(
                f"WARN: start date on project is before its due date - will not map start date"
            )
            del project_data["start_on"]

    return project_data
