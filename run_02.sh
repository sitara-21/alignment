#!/bin/bash

#SBATCH -c 1                              # Request core count
#SBATCH -N 1                               # Request one node (if you request more than one core with -c, also using
                                           # -N 1 means all cores will be on the same node)
#SBATCH -t 8:00:00                        # Runtime in D-HH:MM format
#SBATCH -p short                 # Partition to run in
#SBATCH --account=gulhan_dcg18
#SBATCH --mem=20G  
#SBATCH -o /n/data1/hms/dbmi/gulhan/lab/ankit/TP53/logs/bam_unalign_step2_%j.out    
#SBATCH -e /n/data1/hms/dbmi/gulhan/lab/ankit/TP53/logs/bam_unalign_step2_%j.err                    
#SBATCH --mail-type=FAIL                    # Type of email notification- BEGIN,END,FAIL,ALL

output_dir=/n/data1/hms/dbmi/gulhan/lab/ankit/TP53/fastq_gz
f1=$1
f2=$2

n1=$(basename $f1 .gz)
n2=$(basename $f2 .gz)

gunzip $f1
gunzip $f2

echo "running repair.sh"
bash repair.sh in1=$output_dir/$n1 in2=$output_dir/$n2 out1=$output_dir/$n1.fix.fastq out2=$output_dir/$n2.fix.fastq outs=$output_dir/$n1.single.fastq repair -Xmx40g

#mv $n1.fix $n1
#mv $n2.fix $n2

#gzip $n1
#gzip $n2
