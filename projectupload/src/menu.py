import sys
import csv
from asanaUtils.client import asana_client
from asanaUtils.projectFunctions import map_project_fields

##################################
##      Input Menu Function     ##
##  for collecting user inputs  ##
##################################


async def menu():
    # get access token
    token = input("paste your personal access account token: ")

    # test the token to ensure it works

    user = await asana_client(**{"method": "GET", "url": "/users/me", "token": token})
    if not user:
        sys.exit("invalid account token")

    # get link to portfolio, split to get the ID
    portfolio_link = input(
        "paste a link to the portfolio (https://app.asana.com/0/portfolio/12345/list): "
    )

    portfolio_id = portfolio_link.split("/")[-2]

    portfolio = await asana_client(
        **{"method": "GET", "url": f"/portfolios/{portfolio_id}", "token": token}
    )

    if not portfolio:
        sys.exit(
            "could not get portfolio or it does not exist. check that you have access to it"
        )

    portfolio_items = await asana_client(
        **{"method": "GET", "url": f"/portfolios/{portfolio_id}/items", "token": token}
    )

    portfolio_length = len(portfolio_items)
    print(portfolio_items)

    custom_fields = {}
    # create dictionary which maps the name of the custom field from the portfolio to the field metadata
    for field_setting in portfolio["custom_field_settings"]:
        field_name = field_setting["custom_field"]["name"].lower()
        custom_fields[field_name] = field_setting["custom_field"]

        # if the custom field is an enum or a multi-enum,
        # take the array of enum options and turn it into a dict for easier use later
        if "enum" in field_setting["custom_field"]["type"]:
            enum_dict = {}
            # for every enum option in the array
            for i in range(0, len(field_setting["custom_field"]["enum_options"])):

                # get the enum option
                enum_option = field_setting["custom_field"]["enum_options"][i]

                # use its name as the key, and set the value
                enum_dict[enum_option["name"].lower()] = enum_option

            custom_fields[field_name]["enum_dict"] = enum_dict

    custom_field_string = ""

    for key in custom_fields.keys():
        custom_field_string += key + ", "

    custom_field_string = custom_field_string[0:-2]
    print(f"Using portfolio {portfolio['name']} with custom fields:")
    print(custom_field_string)

    team_link = input(
        "\n \n paste a link to the team you'd like the new projects to be created in: (https://app.asana.com/0/12345/overview): "
    )

    team_id = team_link.split("/")[-2]

    team = await asana_client(
        **{"method": "GET", "url": f"/teams/{team_id}", "token": token}
    )

    if not team:
        sys.exit(
            "\n could not get team or it does not exist. check that you have access to it"
        )
    print(f"\n ok, we'll use the team: {team['name']}")

    file_path = input(
        "\n drag and drop your file to this terminal or enter the file path to the CSV file of projects:"
    ).strip()

    dialect = csv.excel
    dialect.delimiter = ","
    project_inputs = []
    with open(file_path, mode="r", encoding="utf-8-sig") as f:
        project_file = csv.DictReader(f, dialect="excel")
        for item in project_file:
            project_inputs.append(item)

    if len(project_inputs) < 1:
        sys.exit("no projects found in file")

    input_custom_fields = project_inputs[0].keys()

    attribute_mapping = {}

    has_name = False

    print("attribute mapping: \n csv header \t => \t portfolio custom field ")
    for input_field in input_custom_fields:
        # account for standard fields:
        if input_field.lower() == "name" or input_field.lower() == "project name":
            attribute_mapping[input_field] = "name"
            has_name = True
            print(f"{input_field}\t => \t name")

        elif input_field.lower() == "owner":
            attribute_mapping[input_field] = "owner"
            print(f"{input_field}\t => \t owner")

        elif input_field.lower() in ["date", "due date", "end date", "end on", "end"]:
            attribute_mapping[input_field] = "due_date"
            print(f"{input_field}\t => \t due date")

        elif input_field.lower() in [
            "start on",
            "start date",
            "start",
            "begin",
            "begin on",
        ]:
            attribute_mapping[input_field] = "start_on"
            print(f"{input_field}\t => \t start on")

        else:
            for key in custom_fields.keys():
                if key.lower() == input_field.lower():
                    attribute_mapping[input_field] = custom_fields.pop(key)
                    print(
                        f"{input_field}\t => \t {attribute_mapping[input_field]['name']}"
                    )
                    break

            if input_field not in attribute_mapping.keys():
                print(f"{input_field}\t => \t NO MAPPING FOUND IN PORTFOLIO")

    for key in custom_fields:
        print(f"NOT FOUND IN CSV: {key}")

    if not has_name:
        sys.exit(
            "ERR: name was not found in the CSV, cannot create projects without a name! \n exiting."
        )

    print("\n")
    project_data = []
    for project in project_inputs:
        new_project = map_project_fields(project, attribute_mapping)
        if "name" in new_project and new_project["name"] != "":
            project_data.append(new_project)

    if (portfolio_length + len(project_data)) >= 250:
        sys.exit(
            "Portfolios can only contain 250 projects, and uploading this CSV will hit that limit. - please reduce the size or use a different portfolio"
        )

    confirmation = input("proceed? (Y/n)")

    if confirmation.lower() == "n":
        sys.exit("goodbye!")

    return [team, project_data, attribute_mapping, portfolio, token]
