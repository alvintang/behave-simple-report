#!/usr/bin/python

import sys, getopt, os, json
import datetime, time

def print_help_and_exit(exit_code,exit_msg=''):
    if exit_msg == '':
        print('test.py -i <inputfile> -o <outputfile>')
    else:
        print(exit_msg)
    sys.exit(exit_code)

def process_results(directory, failed_list, broken_list, skipped_list):
    processed_list = []
    passed = 0
    directory_files = os.listdir(directory)
    directory_files.sort(key=lambda x: os.stat(os.path.join(directory, x)).st_mtime, reverse=True)

    for filename in directory_files:
        with open(directory+filename, "r") as read_file:
            json_file = json.load(read_file)

            if json_file["status"] == "passed":
                if json_file["name"] not in processed_list:
                    processed_list.append(json_file["name"])
                    passed = passed + 1
            elif json_file["status"] == "failed":
                if json_file["name"] not in processed_list:
                    processed_list.append(json_file["name"])
                    failed_list[json_file["name"]] = json_file["statusDetails"]["message"]
            elif json_file["status"] == "broken":
                if json_file["name"] not in processed_list:
                    processed_list.append(json_file["name"])
                    broken_list[json_file["name"]] = json_file["statusDetails"]["message"]
            elif json_file["status"] == "skipped":
                if json_file["name"] not in processed_list:
                    processed_list.append(json_file["name"])
                    skipped_list[json_file["name"]] = ''

    return passed

# def check_args(argv):
#     opt_args_map = {}
#     required_opts = ["-i", "-r"]
#     required_args = ["-i", "-r"]
#
#     skip_index = []
#     for idx, arg in enumerate(argv):
#         if idx in skip_index:
#             continue
#
#         if arg in required_opts:
#             required_opts.remove(arg)
#
#         if arg in required_args:
#             if idx+1 > len(argv):
#                 print_help_and_exit(2)
#             opt_args_map[arg] = argv[idx+1]
#         else:
#             opt_args_map[arg] = True
#
#     return opt_args_map


def main(argv):
    results_dir = ''
    inputfile = ''
    outputfile = 'output.html'
    replace_strings = ''
    replace_values = ''
    replace_map = {}
    pass_message = "Tests Passed"
    fail_message = "Tests Failed"

    test_success = True
    result_color = "green"
    test_total = 0
    success_rate = 0
    required = ["-i","--ifile","-r","--rdir"]

    # options = check_args(argv)
    # print(options)

    # python2 parse-results.py -i index.html -r ../../behave-api-service/features/allure-results/ \
    # --replace-strings=project-name,build-datetime \
    # --replace-values=CoreEng/Olniku/kls/kalupi-regression-test,1563341384185

    try:
        opts, args = getopt.getopt(argv,"hi:o:r:",["ifile=","ofile=","rdir=","pass-message=","fail-message=","replace-strings=","replace-values="])
    except getopt.GetoptError:
        print_help_and_exit(2)

    if len(opts) == 0:
        print_help_and_exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print_help_and_exit(0)
        elif opt in ("-i", "--ifile"):
            inputfile = arg
            required.remove("-i")
            required.remove("--ifile")
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-r", "--rdir"):
            results_dir = arg
            required.remove("-r")
            required.remove("--rdir")
        elif opt in ("--pass-message"):
            pass_message = arg
        elif opt in ("--fail-message"):
            fail_message = arg
        elif opt in ("--replace-strings"):
            replace_strings = arg
        elif opt in ("--replace-values"):
            replace_values = arg

    if len(required) > 0:
        print("missing required parameters: ", required)
        sys.exit(2)

    replace_strings = replace_strings.split(',')
    replace_values = replace_values.split(',')

    if len(replace_strings) != len(replace_values):
        print_help_and_exit(2,"Error: replace-strings length does not match replace-values")

    for idx, str in enumerate(replace_strings):
        replace_map[str] = replace_values[idx]

    print(replace_map)
    # print('Input directory is ', results_dir)
    # print('Input template is ', inputfile)
    # print('Output file is ', outputfile)
    #
    # build_duration = float(build_duration) / 1000;
    broken_list = {}
    failed_list = {}
    skipped_list = {}
    passed = process_results(results_dir, failed_list, broken_list, skipped_list)
    test_total = passed + len(broken_list) + len(failed_list) + len(skipped_list)
    success_rate = (float(passed) / float(test_total)) * 100

    print("passed:", passed)
    print("failed:", len(failed_list))
    # print("failed_list", failed_list)
    print("broken:", len(broken_list))
    # print("broken_list", broken_list)
    print("skipped:", len(skipped_list))
    # print("skipped_list", skipped_list)
    print("test_total", test_total)
    print("success_rate", success_rate)

    if len(failed_list) > 0 or len(broken_list) > 0:
        test_success = True
        result_color = "red"

    with open(inputfile, 'r') as f_in:
        with open(outputfile, 'w') as f_out:
            for line in f_in:
                if "${test_success}" in line:
                    replaced_line = line.replace("${test_success}", pass_message if test_success else fail_message)
                elif "${total_count}" in line:
                    replaced_line = line.replace("${total_count}", test_total.__str__())
                elif "${passed_count}" in line:
                    replaced_line = line.replace("${passed_count}", passed.__str__())
                elif "${failed_count}" in line:
                    replaced_line = line.replace("${failed_count}", len(failed_list).__str__())
                elif "${skipped_count}" in line:
                    replaced_line = line.replace("${skipped_count}", len(skipped_list).__str__())
                elif "${broken_count}" in line:
                    replaced_line = line.replace("${broken_count}", len(broken_list).__str__())
                elif "${success_rate}" in line:
                    replaced_line = line.replace("${success_rate}", "%.2f" % (success_rate))
                else:
                    for key,val in replace_map.items():
                        key = "${"+key+"}"
                        if key in line:
                            replaced_line = line.replace(key, val)
                            break
                        else:
                            replaced_line = line

                f_out.write(line.replace(line, replaced_line))

if __name__ == "__main__":
   main(sys.argv[1:])