#!/usr/bin/env python3
import warnings
warnings.simplefilter(action='ignore', category=DeprecationWarning)
import os
import subprocess
import json
import pandas as pd
import sys


default_input = {
    "node-sweep":{
        "range":[1000]
    },
    "performance-sweep":{
        "range":[1.0]
    },
    "batsched-policy":"easy_bf3",
    "forward-profiles-on-submission":True,
}

failure_workload = {
    "SMTBF-sweep": {
        "compute-SMTBF-from-NMTBF": True,
        "range": [
            32
        ],
        "formula": "1728000000 *(1/i)"
    },
    "MTTR":3600.0,                  # mean time to repair (1hr)
    "seed-repair-times":20,         # repair duration seed
    "seed-failures":20,             # machine id seed
    "seed-failure-machine":20,      # machine id see
    "queue-policy":"ORIGINAL-FCFS", # uses original submit times
    "checkpointing-on":True,
    "synthetic-workload":{
        "type":"parallel_homogeneous",
        "machine-speed":1,
        "force-creation":True,
        "duration-time":"3600:21600:unif",
        "submission-time":"600:exp",
        "number-of-resources":"1:200:unif",
        "wallclock-limit":"101%",
        "number-of-jobs":10000,
        "seed":20,
        "dump-time":"3%",
        "read-time":"2%",
        "checkpoint-interval":"10%:30%"
    }
}

success_workload ={
    "synthetic-workload":{
        "type":"parallel_homogeneous",
        "machine-speed":1,
        "force-creation":True,
        "duration-time":"3600:21600:unif",
        "submission-time":"600:exp",
        "number-of-resources":"1:200:unif",
        "wallclock-limit":"101%",
        "number-of-jobs":20000,
        "seed":20
    }
}

columns = {
    'job': # default columns for out_jobs.csv and post_out_jobs.csv
        [
            'job_id','workload_name','profile','success','workload_num_machines',
            'requested_number_of_resources','requested_time','submission_time','starting_time'
        ],
    'out_job': # additional columns for out_jobs.csv (checked with and without simulated failures)
        [
            'final_state','finish_time','execution_time','waiting_time',
            'turnaround_time','original_start','original_submit'
        ],
    'post_job': # additional columns for post_out_jobs.csv (checked only for simulated failures)
        [
            'real_final_state','real_finish_time','work_progress','SMTBF',
            'checkpointed','checkpoint_interval','read_time','dump_time',
            'total_dumps','total_execution_time','total_waiting_time','total_turnaround_time'
        ],
    'makespan':  # default columns for makespan.csv (checked with and without simulated failures)
        [
            'nodes','number_of_jobs','makespan_sec','makespan_dhms', 'submission_time',
            'avg_tat','avg_tat_dhms','avg_waiting','avg_waiting_dhms','avg_utilization'
        ],
    'makespan_failure': # additional columns for makespan.csv (checked only for simulated failures)
        [
            'SMTBF','NMTBF','MTTR','AAE','repair-time','SMTBF_failures'
        ]
}

file_columns = {
    'out_job_default' : columns['job'] + columns['out_job'],
    'post_job_failure' : columns['job'] + columns['post_job'],
    'makespan_success' : columns['makespan'],
    'makespan_failure' : columns['makespan'] + columns['makespan_failure']
}

result_files = {
    'success': {
        'out_jobs.csv': file_columns['out_job_default'],
        'makespan.csv': file_columns['makespan_success']
    },
    'failure': {
        'out_jobs.csv': file_columns['out_job_default'],
        'post_out_jobs.csv': file_columns['post_job_failure'],
        'makespan.csv': file_columns['makespan_failure']
    }
}


def print_pretty(message, sep='=', indent=4, before=True, after=True):
    size = len(message)+8 if len(message) < 92 else 100
    lspaces = 0 if len(message) > 91 else indent
    divider=sep*size
    if before:
        print(divider, flush=True)
    print(f"{' '*lspaces}{message}")
    if after:
        print(divider, flush=True)


def read_csvfile(csv_file, cols):
    try:
        df = pd.read_csv(csv_file)
        df_filtered = df.filter(cols)
        df_filtered.sort_index(inplace=True)

    except Exception as e:
        print(f"Error: {e}")
        exit(1)
    return df_filtered


# print result file differences
def print_differences(result_diffs, runs, test_type="success"):
    valid = True
    for i in range(1, runs+1):
        print(f"\n[Simulation Run #{i}]:")
        for fname, diff_data in result_diffs[f'Run_{i}'].items():
            print(f"File '{fname}' contains errors for {diff_data['count']} job(s)")
            if diff_data['count'] != 0:
                print(f"> Saved error report to : {diff_data['diff_file']}")
                valid = False
    if valid:
        print_pretty(f"Successfully verified results for experiment: 'test_simulator_{test_type}'", after=False)
    else:
        print_pretty(f"Failed to verify results for experiment: 'test_simulator_{test_type}'", after=False)




def compare_results(correct_result_path, test_result_path, diff_result_path, runs, test_type='success'):
    print_pretty(f"Checking 'test_simulator_{test_type}' simulation results for correctness ")
    diff_result={}
    for i in range(1, runs+1):
        diff_run=diff_result[f'Run_{i}']={}
        for fname, cols in result_files[test_type].items():
            test_file=f"{test_result_path}/Run_{i}/output/expe-out/{fname}"
            correct_file=f"{correct_result_path}/{test_type}/{fname}"

            correct_df = read_csvfile(correct_file, cols)
            test_df = read_csvfile(test_file, cols)
            try:
                diff_df = correct_df.compare(test_df)
                diff_df = diff_df.rename(columns={"self":"correct","other":"result"})
            except Exception as e:
                print(f"Error: Cannot compare test results for {fname}, {e}")
                continue

            diff_run[fname]={}
            diff_run[fname]['count'] = diff_df.shape[0]
            if diff_df.shape[0] != 0:
                diff_dir=f"{diff_result_path}/test_simulator_{test_type}/Run_{i}"
                diff_run[fname]['diff_file'] = f"{diff_dir}/errors-{fname}"
                os.makedirs(diff_dir, exist_ok=True)
                diff_df.to_csv(diff_run[fname]['diff_file'])

    return diff_result


# adds json onjects to simulator config
def add_object(config, expe_name, param_name, **kwargs):
    if expe_name not in config:
        config[expe_name] = {}
    if param_name not in config[expe_name]:
        config[expe_name][param_name] = kwargs
    else:
        config[expe_name][param_name].update(kwargs)


# creates a config file with specified settings
def create_simulator_config(filepath, failures, runs=1):
    config = {}
    expe_name = "test-expe"
    add_object(config, expe_name, "input", **default_input)
    if failures:
        add_object(config, expe_name, "input", **failure_workload)
    else:
        add_object(config, expe_name, "input", **success_workload)
    add_object(config, expe_name, "output", **{"avg-makespan": runs})
    fpath=filepath
    with open(fpath, "w") as json_file:
        json.dump(config, json_file, indent=4)
    print_pretty(f"[Generated Config]: {fpath}")


# generates simulator cmd with appropriate options
def generate_cmd_string(cmdargs,prefix):
    options = []
    cmd_parts = [f"{prefix}/basefiles/myBatchTasks.sh"]
    for arg, value in cmdargs.items():
        if isinstance(value, dict):
            cmd_arg =  " ".join([f"{arg} {sub_arg} {sub_value}" for sub_arg, sub_value in value.items()])
        else:
            cmd_arg = f"{arg} {value}"
        options.append(cmd_arg)

    cmd_parts += options
    cmd_string = ' '.join(cmd_parts)
    return cmd_parts, cmd_string

# creates config file, cmd to run, and runs simulator
def run_simulator(test_config, test_args,prefix):
    create_simulator_config(**test_config)
    cmd_parts, cmd_string = generate_cmd_string(test_args,prefix)
    print_pretty(f"[Running command]: {cmd_string}", before=False)
    process = subprocess.run(cmd_string, shell=True, stdout=True, stderr=True)
    print(process.returncode, flush=True)


# decides cmd options based on environment and run mode
def get_cmd_args(mode, environment, runs, tasksAtOnce):
    run_options = {
        'serial': {
            'local': {'-p': 'none'},
            'slurm': {'-p': 'tasks', '-t': 1},
            'runs': 1
        },
        'parallel':{
            'local': {'-p': 'background', '-t': tasksAtOnce},
            'slurm': {'-p': 'tasks', '-t': tasksAtOnce},
            'runs': runs
        }
    }
    cmd_options = run_options[mode][environment]
    runs = run_options[mode]['runs']
    return cmd_options, runs


# prompts user for option from list and returns input
def prompt_selection(prompt, options, default='1'):
    print_pretty(prompt)
    for key, value in options.items():
        option = f"[{key}]:\t{value}"
        if key == default:
            option += " (default)"
        print(option)
    if len(options.items()) == 1:
        print(f"Auto selected option: {default}")
        return options[default]
    selection = input(f"\nEnter option number: ").strip() or default
    if selection not in options:
        print(f"\tError: Selection '{selection}' is invalid")
        return prompt_selection(prompt, options, default)
    return options[selection]


# prompts user for option from list and returns input
def prompt_integer(prompt, minmax=(1,1E6), default=1):
    num_str = input(prompt).strip() or f"{default}"
    try:
        num = int(num_str)
        if num < minmax[0] or num > minmax[1]:
            print(f"\tError: Please enter an integer between {minmax[0]}-{minmax[1]}")
            return prompt_integer(prompt, minmax, default)
        else:
            return num
    except ValueError:
        print("\tError: Please enter a valid integer")
        return prompt_integer(prompt, minmax, default)


# gets user information to generate config and run cmd
def menu_option():
    compatible_modes = {
        'bare-metal': {'1': 'serial', '2': 'parallel'},
        'charliecloud': {'1': 'serial', '2': 'parallel'},
        'docker': {'1': 'serial'}
    }
    environment = prompt_selection("Environment Types", {'1': 'local', '2': 'slurm'}, default='1')
    method = prompt_selection("Installation Methods", {'1': 'bare-metal', '2': 'charliecloud', '3': 'docker'}, default='1')
    mode = prompt_selection("Simulation Modes", compatible_modes[method], default='1')
    runs = 1
    tasksAtOnce = 1
    if mode == 'parallel':
        print_pretty("Parallel")
        print("Next you will be prompted for 'total simulations' and then 'tasks at once'.\n")
        print("'total simulations - Number of total simulations to run.")
        print("'tasks at once' - Number of simulations to run in parallel on each node.")
        print("\n")
        prompt_integer("Press Enter to continue...")
        print("")
        runs = prompt_integer(f"Number of 'total simulations': ")
        tasksAtOnce = prompt_integer(f"Number of 'tasks at once': ")
    return environment, method, mode, runs, tasksAtOnce


def main():
    prefix = os.environ.get('prefix')
    if not prefix:
        scriptPath=os.path.expanduser(str(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))).rstrip("/")
        print(f"Error: Please set prefix=? in: '{scriptPath}/batsim_environment.sh'")
        print(f"Then source it to enter your batsim environment: source .../simulator/basefiles/batsim_environment.sh")
        sys.exit(1)
    test_path=f"{prefix}/basefiles/tests"
    expected_path =f"{test_path}/expected_results"
    diffs_path = f"{test_path}/test_reports"
    conf_path=f"{prefix}/configs"
    os.makedirs(conf_path, exist_ok=True)
    conf_name='test_simulator'

    environment, method, mode, runs, tasksAtOnce = menu_option()
    args, runs = get_cmd_args(mode, environment, runs, tasksAtOnce)

    # delete past tests
    os.system(f"rm -rf {prefix}/experiments/{conf_name}_success")
    os.system(f"rm -rf {prefix}/experiments/{conf_name}_failure")

    # run tests for simulation with failures off
    success_config = {'filepath': f'{conf_path}/{conf_name}_success.config', 'failures': False, 'runs': runs}
    success_args = {'-f': f'{conf_path}/{conf_name}_success.config' , '-o': f'{conf_name}_success', '-m': method, **args}
    run_simulator(success_config, success_args,prefix)

    #check for differences in results
    success_path =f"{prefix}/experiments/{conf_name}_success/test-expe/experiment_1/id_1"
    success_diffs = compare_results(expected_path, success_path, diffs_path, runs, 'success')
    print_differences(success_diffs, runs, 'success')

    # run tests for simulation with failures on
    failure_config = {'filepath': f'{conf_path}/{conf_name}_failure.config', 'failures': True, 'runs': runs}
    failure_args = {'-f': f'{conf_path}/{conf_name}_failure.config', '-o': f'{conf_name}_failure', '-m': method, **args}
    run_simulator(failure_config, failure_args,prefix)

    # check for differences in results
    failure_path =f"{prefix}/experiments/{conf_name}_failure/test-expe/experiment_1/id_1"
    failure_diffs = compare_results(expected_path, failure_path, diffs_path, runs, 'failure')
    print_differences(failure_diffs, runs, 'failure')

main()
