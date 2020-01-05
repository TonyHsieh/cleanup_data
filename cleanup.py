from sys import argv
import csv
import pprint as pp
import argparse
import pathlib

# CleanFile function
def cleanFile(targetFilename):
    print("CLEANING FILE: " + targetFilename)
    data_list = []
    # set up data dictionary
    with open(targetFilename) as datafile:
        data_reader = csv.DictReader(datafile, delimiter='\t')
        for line in data_reader:
            data_list.append(dict(line))

    # filter out crap into a dictionary
    tumor_dict = {line['Phenotype']: (line['Sample Name'], line['Phenotype'], line['Total Cells']) for line in data_list if (
        line['Tissue Category'] == "tumor") and ((line['Phenotype'] != "All") and (line['Phenotype'] != "others"))}

    # sum up total Cells
    overall_total_cells = 0
    for k in tumor_dict:
        overall_total_cells += int(tumor_dict[k][2])
    #print ("Total Cells = " + str(overall_total_cells))

    # do the stupid combination of WT/d16 + WT/d16/p95M
    phenotype_list = ["p95M", "p95MC", "WT/d16 + WT/d16/p95M", "WT/d16/p95MC"]
    #print (tumor_dict.get('WT/d16'))

    if tumor_dict.get('WT/d16') is None:
        total_cells_WTd16 = 0
    else:
        total_cells_WTd16 = int(tumor_dict['WT/d16'][2])
        tumor_dict.pop('WT/d16', None)

    if tumor_dict.get('WT/d16/p95M') is None:
        total_cells_WTd16p95M = 0
    else:
        total_cells_WTd16p95M = int(tumor_dict['WT/d16/p95M'][2])
        tumor_dict.pop('WT/d16/p95M', None)

    tumor_dict[phenotype_list[2]] = (tumor_dict[phenotype_list[0]][0], tumor_dict[phenotype_list[0]][2], str(
        total_cells_WTd16+total_cells_WTd16p95M))

    # output - if no file create new otherwise append
    outfile = open("clean_data.txt", "a+")

    for p in phenotype_list:
        tmp = tumor_dict.get(p)
        if tmp is None:
            tempstr = tumor_dict[phenotype_list[0]][0] + \
                "\t" + p + "\t0\t0.0\n"
        else:
            percentage = float(tmp[2]) / overall_total_cells
            tempstr = tmp[0] + "\t" + p + "\t" + \
                tmp[2] + "\t" + str(percentage) + "\n"
        # print(tempstr)
        outfile.write(tempstr)

    # close file
    outfile.close()

    # test output
    # pp.pprint(tumor_dict)


# Main Function
# use argparse to get the args properly. - from https://docs.python.org/3/library/argparse.html#module-argparse
parser = argparse.ArgumentParser(
    description='Clean up Data files in current directory.')
parser.add_argument('--file', dest='file', action='store',
                    help='Clean up a specified file (default: all files in current directory)')
parser.add_argument('--path', dest='path', action='store',
                    help='Target specified directory (default: current directory)', default='.')
args = parser.parse_args()
# print(args.file)

if (args.file is not None):
    cleanFile(args.file)
else:
        # define the path with pathlib - from https://stackabuse.com/python-list-files-in-a-directory/
    targetDirectory = pathlib.Path(args.path)
    # define the pattern
    targetPattern = "*summary.txt"

    for targetFile in targetDirectory.glob(targetPattern):
        cleanFile(args.path + "/" + targetFile.name)
    # --------
