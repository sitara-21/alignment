#!/bin/bash

#SBATCH -c 1                              # Request core count
#SBATCH -N 1                               # Request one node (if you request more than one core with -c, also using
                                           # -N 1 means all cores will be on the same node)
#SBATCH -t 8:00:00                        # Runtime in D-HH:MM format
#SBATCH -p short                 # Partition to run in
#BATCH --account=gulhan_dcg18
#SBATCH --mem=10G                          # Memory total in MB (for all cores)
#SBATCH --mail-type=FAIL                    # Type of email notification- BEGIN,END,FAIL,ALL
#SBATCH -o /n/data1/hms/dbmi/gulhan/lab/ankit/TP53/logs/bam_unalign_step3_%j.out    
#SBATCH -e /n/data1/hms/dbmi/gulhan/lab/ankit/TP53/logs/bam_unalign_step3_%j.err

f1=$1
f2=$2

gzip $f1
gzip $f2
