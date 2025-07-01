from time import sleep
import argparse
import os
import re
import ntpath
import glob
import sys
import fileinput
import time
from shutil import copyfile

# aligns bam files to a reference genome. Details specified in input json file. Default reference genome is b37

running=["SRR81691", "SRR81691", "SRR68126", "SRR85997", "SRR61095", "SRR68126", "SRR68126", "SRR81691", "SRR85997", "SRR81691", "SRR81691", "SRR61854", "SRR61095", "SRR85997", "SRR61854", "SRR61095", "SRR81691", "SRR61095"]
to_run=["SRR8599735", "SRR8169141", "SRR6109560", "SRR8169140", "SRR6109563"]
to_run=["5657_OL1"]
running=["SN-48-1."]

def parse_args():
    """Uses argparse to enable user to customize script functionality"""
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-in_dir', '--input_directory', default=None, help='path to directory containing input files')
    parser.add_argument('-in_file', '--input_file_path', help='path to input file')
    parser.add_argument('-out', '--output_directory', default=None, help='directory to which the "/.PreProcessing/" directory containing outputs will be written to')
    parser.add_argument('-n', '--num_cores', default='1', help='slurm job submission option')
    parser.add_argument('-t', '--runtime', default='1-00:00:00', help='slurm job submission option')
    parser.add_argument('-p', '--queue', default='short', help='slurm job submission option')
    parser.add_argument('--account', default='gulhan_dcg18', help='slurm job submission option')
    parser.add_argument('-psuper', '--queue_super', default='park', help='slurm job submission option')
    parser.add_argument('--mem_per_cpu', default='8G', help='slurm job submission option')
    parser.add_argument('--mail_type', default='FAIL', help='slurm job submission option')
    parser.add_argument('--mail_user', default='asingh46@mgh.harvard.edu', help='slurm job submission option')
    #parser.add_argument('-o', '--output', default='/n/data1/hms/dbmi/gulhan/lab/ankit/slurm_output/bam_align_%j.out', help='slurm job submission option')
    #parser.add_argument('-e', '--error', default='/n/data1/hms/dbmi/gulhan/lab/ankit/slurm_output/bam_align_%j.err', help='slurm job submission option')
    parser.add_argument('-overrides', '--overrides_path', default='/n/data1/hms/dbmi/gulhan/lab/software/victor/scripts/GATK_Somatic_SNPs_Indels/overrides.conf', help='path to overrides.conf file')
    parser.add_argument('-cromwell', '--cromwell_path', default='/n/data1/hms/dbmi/gulhan/lab/software/alon/software/cromwell-36.jar', help='path to cromwell.jar file')
    parser.add_argument('-gatk_wdl', '--gatk4_data_processing_path', default='/n/data1/hms/dbmi/gulhan/lab/software/victor/scripts/GATK_Somatic_SNPs_Indels/processing-for-variant-discovery-gatk4.wdl', help='path to gatk4-data-processing file')
    parser.add_argument('-input_json', '--input_json_path', default='/n/data1/hms/dbmi/gulhan/lab/software/victor/scripts/GATK_Somatic_SNPs_Indels/processing-for-variant-discovery-gatk4.b37.wgs.inputs.json', help='path to gatk4-data-processing file')
    parser.add_argument('-r1', type=int, default=0)
    parser.add_argument('-r2', type=int, default=1000000000)
    parser.add_argument('-csv', default=None)
    parser.add_argument('-stall', type=int, default=1)
    return parser.parse_args()

def clean_arg_paths(args):
    """Modifies all user-inputted directory paths such that they end with a '/'"""
    d = vars(args)
    for arg in d.keys():
        if 'input_directory' in arg and d[arg]=='./': d[arg] = os.getcwd()
        if 'output_directory' in arg and d[arg]=='./': d[arg] = os.getcwd()    
        if 'directory' in arg and d[arg] is not None and d[arg][-1] != '/': d[arg] += '/'
    if d['queue'] != 'park' and d['queue'] != 'priopark':
        d['overrides_path'] = '/n/data1/hms/dbmi/gulhan/lab/ankit/scripts/alignment_scripts/overrides.non_park.conf'

def return_input_files(args, ext):
    input_bams = [os.path.realpath(file) for file in glob.glob(args.input_directory + '*.' + ext)]
    return input_bams

def sort_by_size(input_files):
    for i in range(len(input_files)):
        input_files[i] = (input_files[i], os.path.getsize(input_files[i]))
    input_files.sort(key=lambda filename: filename[1])
    for i in range(len(input_files)):
        input_files[i] = input_files[i][0]
    return input_files

def generate_input_json(args, input_file):
    dir = args.output_directory + '.PreProcessing/' + '.' + os.path.basename(input_file) + '/'
    os.makedirs(dir, exist_ok=True)
    
    copyfile(args.input_json_path, dir + 'input.json')
    with fileinput.FileInput(dir + 'input.json', inplace=True) as file:
        for line in file:
            print(line.replace(
            "SRR475190", re.sub('.bam', '', os.path.basename(input_file))).replace(
            "output_dir/.PreProcessing/.sample_name/list.txt", dir + 'list.txt').replace(
            "output_dir/", args.output_directory + '.PreProcessing/'), end='')

    copyfile(args.overrides_path, dir + 'overrides.conf')
    with fileinput.FileInput(dir + 'overrides.conf', inplace=True) as file:
        for line in file:
            print(line.replace(
            "priopark", args.queue), end='')

    copyfile(args.gatk4_data_processing_path, dir + 'processing-for-variant-discovery-gatk4.wdl')
    with fileinput.FileInput(dir + 'processing-for-variant-discovery-gatk4.wdl', inplace=True) as file:
        for line in file:
            print(line.replace(
            "priopark", args.queue), end='')

    return dir + 'input.json'

def generate_txt(args, input_file, input_json):
    with open(re.sub('input.json', 'list.txt', input_json), 'w') as file:
        file.write(input_file)

def return_slurm_command(args):
    """Returns slurm command given args provided"""
    slurm_command = '#!/bin/bash\n' + \
                '#SBATCH -n ' + args.num_cores + '\n' + \
                '#SBATCH -t ' + args.runtime + '\n' + \
                '#SBATCH -p ' + args.queue + '\n' + \
                '#SBATCH --mem-per-cpu=' + args.mem_per_cpu + '\n' + \
                '#SBATCH --account=' + args.account + '\n' + \
                '#SBATCH --mail-type=' + args.mail_type + '\n' + \
                '#SBATCH --mail-user=' + args.mail_user + '\n'
# 		'#SBATCH --exclude=compute-p-17-[34-46]' + '\n'
    # if args.queue in ['park', 'priopark']:
    #     slurm_command += '#SBATCH --account=park_contrib' + '\n'
    return slurm_command

def gen_output_file_name(args, input_file):
    output_file_name = args.output_directory + '.PreProcessing/' + '.' + os.path.basename(input_file) + '/' + os.path.basename(input_file)
    return output_file_name

def return_primary_command(args, output_file_name, input_file, input_json):
    primary_command = 'java -Dconfig.file=' + re.sub('input.json', 'overrides.conf', input_json) + ' -jar ' + args.cromwell_path + ' run ' + re.sub('input.json', 'processing-for-variant-discovery-gatk4.wdl', input_json) + ' -i ' + input_json
    return primary_command

def gen_sh_file_name(args, output_file_name):
    """Generates sh file name"""
    sh_file_name = os.path.dirname(output_file_name) + '/.sh/' + os.path.basename(output_file_name) + '.sh'
    return sh_file_name

def write_out(args, slurm_command, primary_command, sh_file_name):
    """"""
    os.makedirs(os.path.dirname(sh_file_name), exist_ok=True)
    with open(sh_file_name, 'w') as file:
        file.write(slurm_command + primary_command)

def submit_job(sh_file_name):
    os.chdir(os.path.dirname(sh_file_name))
    os.system('chmod +x ' + os.path.basename(sh_file_name))
    os.system('sbatch ./' + os.path.basename(sh_file_name))

def main():
    args = parse_args()
    clean_arg_paths(args)
     
    #os.system('module load gcc/6.2.0 python/2.7.12 samtools/1.3.1 bwa/0.7.15')      

    if args.csv is None:
        input_files = return_input_files(args, 'bam') if args.input_directory is not None else [args.input_file_path]
    else:
        input_files = []
        with open(args.csv, 'r') as file:
            for line in file:
                input_files.append(line.rstrip())
    print(input_files)
    print(args.input_directory)
    print(args.output_directory) 
    #print(input_files)
    #samples = return_samples(args)
    #print(samples)
        
    start = args.r1
    end = min(args.r2, len(input_files))
    #print(start, end) 
    for input_file in input_files[start:end]:
        sample_name = input_file.split('/')[-1].split('.')[0]
        if sample_name[0:8] in running:
            continue
#        if sample_name not in to_run:
#            continue
        input_json = generate_input_json(args, input_file)
        generate_txt(args, input_file, input_json)
        slurm_command = return_slurm_command(args)
        output_file_name = gen_output_file_name(args, input_file)
        primary_command = return_primary_command(args, output_file_name, input_file, input_json)

        sh_file_name = gen_sh_file_name(args, output_file_name)
        write_out(args, slurm_command, primary_command, sh_file_name)
        output_dir = os.path.join(args.output_directory, ".PreProcessing")
        sample = os.path.basename(input_file).split('.bam')[0]
        bam_sample = os.path.join(output_dir, sample + ".bam")
        print("try " + bam_sample)
        if not os.path.isfile(bam_sample):
            print("run " + bam_sample)
            time.sleep(args.stall)
            submit_job(sh_file_name)
        
if __name__ == "__main__":
    main()
