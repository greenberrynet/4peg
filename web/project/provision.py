#!/usr/local/bin/python3
#
# Author: Josh Horton
# Email: josh.horton@aos5.com

import csv
import sys
import jinja2
import os
import argparse


def print_instructions():
    print ("\n\n-----------------------------------------------------------")
    print ("Please enter arguments for provisioning.")
    print ("-----------------------------------------------------------\n")
    print ("Usage: ./provision.py devices.csv template.j2")
    print ("\n")
    print ("devices.csv")
    print ("The csv file used in provisioning must have variables used")
    print ("in the template file defined in the first line of the csv file.")
    print ("\n")
    print ("template.j2")
    print ("The template file is a jinja2 formatted file with variables ")
    print ("matching the column headers of the csv file.")
    print ("\n")


#arg_output_dir = './'
#arg_csv_file = ''
#arg_template_file = ''

argparser = argparse.ArgumentParser()
argparser.add_argument("-c", "--csv", help="CSV File", required=True)
argparser.add_argument("-t", "--template", help="Jinja2 Template File", required=True)
argparser.add_argument("-d", "--dir", help="Output Directory")

args = argparser.parse_args()

if args.csv:
    arg_csv_file = args.csv
if args.template:
    arg_template_file = args.template
if args.dir:
    arg_output_dir = args.dir


loader = jinja2.FileSystemLoader(os.getcwd())

jenv = jinja2.Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)

template = jenv.get_template(arg_template_file)

csv_file = open(arg_csv_file,"r")
reader = csv.DictReader(csv_file)

for line in reader:
    try: 
        config_file_name = line['filename']
    except:
        print ("\nError: At least one column header in your CSV file must be 'filename'\n")
        exit()
    if arg_output_dir:
        config_file = open ("%s/%s" % (arg_output_dir,config_file_name),"w")
        config_file.write(template.render(line))
        config_file.close()
    else:
        print(template.render(line))

csv_file.close()
