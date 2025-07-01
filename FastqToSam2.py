import gzip
import argparse
import os
import re
import ntpath
import glob
import sys
import time

def parse_args():
    """Uses argparse to enable user to customize script functionality"""
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-in_dir', '--input_directory', default='./', help='path to directory containing input files')
    parser.add_argument('-out', '--output_directory', default='./', help='directory to which the "/.FastqToSam/" directory containing outputs will be written to')
    parser.add_argument('-n', '--num_cores', default='1', help='slurm job submission option')
    parser.add_argument('-t', '--runtime', default='1-0:00:00', help='slurm job submission option')
    parser.add_argument('-p', '--queue', default='short', help='slurm job submission option')
    parser.add_argument('--account', default='gulhan_dcg18', help='slurm job submission option')
    parser.add_argument('--mem_per_cpu', default='4G', help='slurm job submission option')
    parser.add_argument('--mail_type', default='FAIL', help='slurm job submission option')
    parser.add_argument('--mail_user', default='asingh46@mgh.harvard.edu', help='slurm job submission option')
    parser.add_argument('-o', '--output', default='/n/data1/hms/dbmi/gulhan/lab/ankit/slurm_output/bam_align_step2_%j.out', help='slurm job submission option')
    parser.add_argument('-e', '--error', default='/n/data1/hms/dbmi/gulhan/lab/ankit/slurm_output/bam_align_step2_%j.err', help='slurm job submission option')
    parser.add_argument('-picard', '--picard_path', default='/n/data1/hms/dbmi/gulhan/lab/software/alon/software/picard.jar', help='path to software')
    parser.add_argument('-library', '--library_name', default='lib_name', help='name of the library the sample was prepared with')
    parser.add_argument('-csv', default=None)
    parser.add_argument('-r1', type=int, default=0)
    parser.add_argument('-r2', type=int, default=100000000000)
    parser.add_argument('-stall', type=int, default=1)
    return parser.parse_args()

def clean_arg_paths(args):
    """Modifies all user-inputted directory paths such that they end with a '/'"""
    d = vars(args)
    for arg in d.keys():
        if 'input_directory' in arg and d[arg]=='./': d[arg] = os.getcwd() 
        if 'output_directory' in arg and d[arg]=='./': d[arg] = os.getcwd()    
        if 'directory' in arg and d[arg] is not None and d[arg][-1] != '/': d[arg] += '/'

def return_input_files(args, ext):
    #input_fastqs = [os.path.realpath(file) for file in glob.glob(args.input_directory + '*' + ext)]
    input_fastqs = [os.path.abspath(file) for file in glob.glob(args.input_directory + '*' + ext)]
    return input_fastqs

def return_samples(input_fastqs):
    #input_fastqs = return_input_files(args, 'fastq.gz')
    samples = []
    for input_fastq in input_fastqs:
        samples.append(
            re.sub('.*\.', '', 
            re.sub('_1.fastq', '',
            re.sub('_2.fastq', '',
            re.sub('_R1_001.*fastq.gz', '',
            re.sub('_R2_001.*fastq.gz', '',
            re.sub('.R1.fastq.gz', '',
            re.sub('.R2.fastq.gz', '',
            re.sub('_1.fastq.gz', '',
            re.sub('_2.fastq.gz', '', 
            re.sub('.1.fq.gz', '',
            re.sub('.2.fq.gz', '',
            re.sub('_1.fastq.fix.fastq.gz', '',
            re.sub('_2.fastq.fix.fastq.gz', '',
                ntpath.basename(input_fastq)))))))))))))))
    #return samples
    samples = list(set(samples))
    samples.sort()
    return samples

def return_sample_input_files(sample, input_files):
    sample_input_files = []
    for input_file in input_files:
        if sample in ntpath.basename(input_file):
            sample_input_files.append(input_file)
    sample_input_files.sort()
    return sample_input_files

def return_slurm_command(args):
    """Returns slurm command given args provided"""
    slurm_command = '#!/bin/bash\n' + \
                '#SBATCH -n ' + args.num_cores + '\n' + \
                '#SBATCH -t ' + args.runtime + '\n' + \
                '#SBATCH -p ' + args.queue + '\n' + \
                '#SBATCH --mem-per-cpu=' + args.mem_per_cpu + '\n' + \
                '#SBATCH --account=' + args.account + '\n' + \
                '#SBATCH -o ' + args.output + '\n' + \
                '#SBATCH -e ' + args.error + '\n' + \
                '#SBATCH --mail-type=' + args.mail_type + '\n' + \
                '#SBATCH --mail-user=' + args.mail_user + '\n'
    # if args.queue in ['park', 'priopark']:
    #     slurm_command += '#SBATCH --account=park_contrib' + '\n'
    return slurm_command

def gen_output_file_name(args, sample):
    output_file_name = args.output_directory + '.FastqToSam/' + sample + '.bam'
    return output_file_name

def return_primary_command(args, output_file_name, sample, sample_input_files):
    tmp_dir = args.output_directory + '.FastqToSam/.sh/tmp'
    os.makedirs(tmp_dir, exist_ok=True)
    primary_command = 'java -Xmx8G -Djava.io.tmpdir=' + tmp_dir + ' -jar ' + args.picard_path + ' FastqToSam' ' \\' + '\n' + \
    '\t' + 'FASTQ=' + sample_input_files[0] + ' \\' + '\n' + \
    '\t' + 'FASTQ2=' + sample_input_files[1] + ' \\' + '\n' + \
    '\t' + 'OUTPUT=' + args.output_directory + '.FastqToSam/' + sample + '.bam' ' \\' + '\n' + \
    '\t' + 'READ_GROUP_NAME=' + sample + '_RG' ' \\' + '\n' + \
    '\t' + 'SAMPLE_NAME=' + sample + ' \\' + '\n' + \
    '\t' + 'LIBRARY_NAME=' + args.library_name + ' \\' + '\n' + \
    '\t' + 'PLATFORM=illumina' + ' \\' + '\n' + \
    '\t' + 'TMP_DIR=' + tmp_dir
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
    #input_files = return_input_files(args, 'fastq.gz')
    #print(input_files)

    if args.csv is  None:  
        #input_files = return_input_files(args, 'fastq.gz')
        input_files = return_input_files(args, 'fastq.gz')
    else:
        input_files = [] 
        with open(args.csv, 'r') as file: 
            for line in file: 
                input_files.append(line.rstrip())

    print(input_files)
    samples = return_samples(input_files)
    #samples = return_samples(args)

    start = args.r1
    end = min(args.r2, len(samples))
    #print(start, end)
    for sample in samples[start:end]:
        sample_input_files = return_sample_input_files(sample, input_files)
        print(sample_input_files)
        slurm_command = return_slurm_command(args)
        output_file_name = gen_output_file_name(args, sample)
        primary_command = return_primary_command(args, output_file_name, sample, sample_input_files)

        sh_file_name = gen_sh_file_name(args, output_file_name)
        write_out(args, slurm_command, primary_command, sh_file_name)
        
        sample_name = ntpath.basename(sample).split('.')[0]
        path_to_bam = os.path.join(os.path.join(args.output_directory, ".FastqToSam"), sample_name + '.bam')
        print(sample_name) 
        print(path_to_bam) 
        if not os.path.isfile(path_to_bam):
            print(path_to_bam) 
            time.sleep(args.stall)
            submit_job(sh_file_name)

if __name__ == "__main__":
    main()
