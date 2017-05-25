'''
Created on 20 May 2016

@author: Alan Greer
'''
from __future__ import print_function

import argparse
import xlrd

from percival.log import log
from percival.carrier.configuration import find_file
from collections import OrderedDict
from configparser import SafeConfigParser


def options():
    parser = argparse.ArgumentParser()
#    parser.add_argument("-w", "--write", action="store_true",
#                        help="Write the initialisation configuration to the board")
    parser.add_argument("-i", "--input", required=True, action='store', help="Input spreadsheet to parse")
    parser.add_argument("-d", "--directory", action='store', default=".",
                        help="Output directory to write config ini files to")
#    parser.add_argument("-p", "--period", action='store', type=float, default=1.0, help="Control the loop period time")
#    parser.add_argument("channel", action='store', help="Control Channel to scan")
    args = parser.parse_args()
    return args


class WorksheetParser(object):
    def __init__(self, worksheet):
        self._worksheet = worksheet

    def parse(self, field_names):
        empty_count = 0
        column = 0
        fields = {}
        found_channels = {}
        groups = []
        for row in range(0, self._worksheet.nrows):
            value = self._worksheet.cell(row, column).value
            if value == xlrd.empty_cell.value:
                empty_count += 1
            else:
                log.info("Cell: %s", value)
                if '#' in value[0]:
                    log.info("Comment so ignore this cell")
                else:
                    found_field = False
                    for field_name in field_names:
                        if field_name in value:
                            log.info("Found %s tag in row %d", field_name, row)
                            fields[field_name] = row
                            found_field = True
                            break

                    if not found_field:
                        found_channels[value] = row

        # Now loop over all of the columns to capture the group information
        for column in range(1, self._worksheet.ncols):
            group = {}
            # Add the field information to each group dictionary
            for field_name in field_names:
                group[field_name] = self._worksheet.cell(fields[field_name], column).value

            # Now add the channel information
            group["channels"] = {}
            for channel in found_channels:
                value = self._worksheet.cell(found_channels[channel], column).value
                if value == xlrd.empty_cell.value:
                    empty_count += 1
                else:
                    group["channels"][channel] = value
                    log.info("Adding channel [%s] to group", channel)
            groups.append(group)

        return groups


class ControlGroupGenerator(object):
    def __init__(self, workbook):
        self._workbook = workbook

    def generate_ini_file(self, filename):
        if "control_groups" in self._workbook.sheet_names():
            parser = WorksheetParser(self._workbook.sheet_by_name("control_groups"))
            groups = parser.parse(['Group_ID', 'Description'])

            # Now produce an ini file with the group information stored
            group_no = 0
            with open(filename, "w") as file:
                for group in groups:
                    file.write("[Control_Group<{:04d}>]\n".format(group_no))
                    file.write("Group_name = \"{}\"\n".format(group['Group_ID']))
                    file.write("Group_description = \"{}\"\n".format(group['Description']))
                    channel_no = 0
                    for channel in group["channels"]:
                        if group["channels"][channel] == 1:
                            file.write("Channel_name<{:04d}> = \"{}\"\n".format(channel_no, channel))
                            channel_no += 1

                    file.write("\n")
                    group_no += 1


class SetpointGroupGenerator(object):
    def __init__(self, workbook):
        self._workbook = workbook

    def generate_ini_file(self, filename):
        if "setpoint_groups" in self._workbook.sheet_names():
            parser = WorksheetParser(self._workbook.sheet_by_name("setpoint_groups"))
            groups = parser.parse(['Setpoint_ID', 'Description'])

            # Now produce an ini file with the group information stored
            group_no = 0
            with open(filename, "w") as file:
                for group in groups:
                    file.write("[Setpoint_Group<{:04d}>]\n".format(group_no))
                    file.write("Setpoint_name = \"{}\"\n".format(group['Setpoint_ID']))
                    file.write("Setpoint_description = \"{}\"\n".format(group['Description']))
                    for channel in group["channels"]:
                        file.write("{} = {}\n".format(channel, group["channels"][channel]))

                    file.write("\n")
                    group_no += 1


def main():
    args = options()
    log.info(args)

    workbook = xlrd.open_workbook(args.input)
    cgg = ControlGroupGenerator(workbook)
    cgg.generate_ini_file(args.directory+"/ControlGroups.ini")

    sgg = SetpointGroupGenerator(workbook)
    sgg.generate_ini_file(args.directory+"/SetpointGroups.ini")

#    found_ids = None
#    found_comments = None
#    found_channels = {}
#    groups = {}
#    empty_count = 0
#    row = 0
#    column = 0
#    if "control_groups" in workbook.sheet_names():
#        worksheet = workbook.sheet_by_name("control_groups")
#        for row in range(0, worksheet.nrows):
#            value = worksheet.cell(row, column).value
#            if value == xlrd.empty_cell.value:
#                empty_count += 1
#            else:
#                log.info("Cell: %s", value)
#                if '#' in value[0]:
#                    log.info("Comment so ignore this cell")
#                elif 'Group_ID' in value:
#                    log.info("Found Group_ID tag in row %d", row)
#                    found_ids = row
#                elif 'Description' in value:
#                    log.info("Found Description tag in row %d", row)
#                    found_comments = row
#                else:
#                    log.info("This is a channel name %s", value)
#                    found_channels[value] = row
#
#        # Now loop over all of the columns to capture the group information
#        for column in range(1, worksheet.ncols):
#            group_id = worksheet.cell(found_ids, column).value
#            description = worksheet.cell(found_comments, column).value
#            # Create the new group
#            groups[group_id] = {"description": description}
#            groups[group_id]["channels"] = []
#
#            for channel in found_channels:
#                value = worksheet.cell(found_channels[channel], column).value
#                if value == xlrd.empty_cell.value:
#                    empty_count += 1
#                else:
#                    if value == 1:
#                        groups[group_id]["channels"].append(channel)
#                        log.info("Adding channel [%s] to group %s", channel, group_id)
#
#        log.info("Groups dictionary: %s", groups)
#
#    # Now produce an ini file with the group information stored
#    group_no = 0
#    with open("ControlGroups.ini", "w") as file:
#        for group in groups:
#            file.write("[Control_Group<{:04d}>]\n".format(group_no))
#            file.write("Group_name = \"{}\"\n".format(group))
#            file.write("Group_description = \"{}\"\n".format(groups[group]["description"]))
#            channel_no = 0
#            for channel in groups[group]["channels"]:
#                file.write("Channel_name<{:04d}> = \"{}\"\n".format(channel_no, channel))
#                channel_no += 1
#
#            file.write("\n")
#            group_no += 1

    # Create a config object and read in the ini file
    ini_filename = find_file("ControlGroups.ini")
    conf = SafeConfigParser(dict_type=OrderedDict)
    conf.read(ini_filename)
    log.debug("Read Control Groups INI file %s:", ini_filename)
    log.debug("    sections: %s", conf.sections())
    for section in conf.sections():
        log.debug("***** Section: %s", section)
        for item in conf.items(section):
            if "group_name" in item[0]:
                log.debug("    Group Name: %s", item[1].replace('"', ''))
            elif "group_description" in item[0]:
                log.debug("    Description: %s", item[1].replace('"', ''))
            elif "channel_name" in item[0]:
                log.debug("    Item: %s", item[1].replace('"', ''))

if __name__ == '__main__':
    main()
