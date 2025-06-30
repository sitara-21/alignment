#!/bin/bash

step=$1

input_bam=/n/data1/hms/dbmi/gulhan/lab/doga/forAndreas/TP53 	  			 # e.g. /n/data1/hms/dbmi/park/DATA/INFORM_trial/WGS/bam
output_dir=/n/data1/hms/dbmi/gulhan/lab/ankit/TP53/fastq_gz
fastq_pairs_list=/n/data1/hms/dbmi/gulhan/lab/ankit/TP53/fastq_pairs.csv		                						 # csv fle: in the format of read_1.fastq.gz,read_2.fastq.gz (e.g. /n/data1/hms/dbmi/park/SOFTWARE/helper_scripts/preprocessing_scripts/unalign_bams/sample_fix_pairs.csv)
gunzip_list=/n/data1/hms/dbmi/gulhan/lab/ankit/TP53/gunzip_list.csv	               								 # csv file: in the format of read_1.fastq.fix.gz, read_2.fastq.fix.gz (e.g. /n/data1/hms/dbmi/park/SOFTWARE/helper_scripts/preprocessing_scripts/unalign_bams/sample_gunzip_list.csv)

email=


case $step in
0)
    echo "conda activate general3; module load gcc samtools java/jdk-1.8u112"
;;
1)
    # Step 1: BAM --> FASTQ. Unalign the bam files. This may be useful if you want to realign the bam file to a different reference genome.

    module load gcc samtools java

    for file in $input_bam/*bam; do
    # for file in $input_bam/BWES00180.bam $input_bam/TPS869-C.bam $input_bam/T01327-17.bam; do

       name=$(basename $file | cut -d. -f1)

    #    if [ -f "$output_dir/${name}_1.fastq" ] || [ -f "$output_dir/${name}_1.fastq.fix.fastq.gz" ]; then
       if [ -f "$output_dir/${name}_1.fastq.gz" ] || [ -f "$output_dir/${name}_1.fastq.fix.fastq.gz" ]; then
          echo "${name}_1.fastq exists, continue"
          continue
       else
          echo "${name}_1.fastq does not exist. Running..."
       fi

       sbatch -c 1 -p short -t 8:00:00 --mem=2000 --mail-type=FAIL --mail-user=$email --wrap="echo ${name}; samtools fastq -1 $output_dir/${name}_1.fastq.gz -2 $output_dir/${name}_2.fastq.gz $file" -o /n/data1/hms/dbmi/gulhan/lab/ankit/TP53/logs/bam_unalign_step1_%j.out -e /n/data1/hms/dbmi/gulhan/lab/ankit/TP53/logs/bam_unalign_step1_%j.err

    done

;;
2)
    ### WARNING - BEFORE RUNNING THIS STEP, CREATE THE FASTQ_PAIRS_LIST.CSV FILE ###
    ### Step 2: fixed disordered paired reads in fastq files

    module load gcc samtools java/jdk-1.8u112
    echo "modules loaded"

    echo "running run_02.sh..."
    while IFS=, read -r f1 f2; do
       echo "Processing $f1 and $f2"
       sbatch run_02.sh $output_dir/$f1 $output_dir/$f2

    done < $fastq_pairs_list

;;
3)
    ### WARNING - BEFORE RUNNING THIS STEP, CREATE THE GUNZIP_LIST.CSV FILE ###
    ### Step 3: gunzip the fastq file

    while IFS=, read -r f1 f2; do

       echo 'f1'
       echo $f1
       echo 'f2'
       echo $f2
       sbatch run_03.sh $output_dir/$f1 $output_dir/$f2

    done < $gunzip_list

;;
*)

    echo "select a step (first argument for this script)"

;;
esac