#!/bin/bash

step=$1

# fastq.gz files -> FastqToSam2.py -> unaligned bam files -> PreProcessing.py -> aligned bam files

# email for slurm job notifications
email=

# Can put all normal and fastq files into the same directory. Will later need to organize into a csv to match tumors to normals.
fastq_path=/n/data1/hms/dbmi/gulhan/lab/ankit/TP53/fastq_gz
output_path=/n/data1/hms/dbmi/gulhan/lab/ankit/TP53/fastq_gz
# output_path_new=/n/data1/hms/dbmi/gulhan/lab/DATA/Termeer/WES_plasma/sandra_files
csv=/n/data1/hms/dbmi/gulhan/lab/ankit/TP53/preprocessing.csv

# look at the readme for alternative references if needed
alignment_json=/n/data1/hms/dbmi/gulhan/lab/ankit/scripts/alignment_scripts/processing-for-variant-discovery-gatk4.hg38.tp53.inputs.json

# should match the fasta in the above file:
fasta=/n/data1/hms/dbmi/park/antuan/references/Homo_sapiens_assembly38.fasta

# look at the readme for alternative time if needed
alignment_wdl=/n/data1/hms/dbmi/gulhan/lab/ankit/scripts/alignment_scripts/processing-for-variant-discovery-gatk4.short.wdl

case $step in
0)
    echo "Set up conda env (only need to do it once)"
    echo "conda env create -f /n/data1/hms/dbmi/park/SOFTWARE/helper_scripts/SNVCurate_pipeline_scripts/SNVCurate.yml"
    echo "To activate your environment, run this line (assuming you kept the name of the conda env as SNVCurate:"
    echo "module load gcc java/jdk-1.8u112 python/3.6.0 samtools htslib bcftools bwa; conda activate SNVCurate"
    
;;
1)
    echo "compressing fastq files"
    for fastq in ${fastq_path}/*.fastq; do
        sbatch -c 1 -p short -t 12:00:00 --mem=1000 --wrap="gzip $fastq"
    done

;;
2)
    echo "converting fastq.gz files -> unaligned bam files. Creates .FastqToSam folder in the output"
    echo "change the -stall param as needed and the -r1 and -r2 as needed"
    module load gcc java/jdk-1.8u112 python/3.6.0 samtools htslib bcftools bwa 
    source /n/app/miniconda3/23.1.0/etc/profile.d/conda.sh 
    conda activate /n/data1/hms/dbmi/gulhan/lab/ankit/conda_envs/SNVCurate
    python3 /n/data1/hms/dbmi/gulhan/lab/ankit/scripts/alignment_scripts/FastqToSam2.py \
        -in_dir ${fastq_path} \
        -out ${output_path} \
        -csv ${csv} \
        --mem_per_cpu 10G -t 12:00:00 -stall 1 -r1 0 -r2 220 -o /n/data1/hms/dbmi/gulhan/lab/ankit/TP53/logs/bam_align_step2_%j.out -e /n/data1/hms/dbmi/gulhan/lab/ankit/TP53/logs/bam_align_step2_%j.err
;;
2b)
    echo "converting fastq.gz files -> unaligned bam files -- SINGLE END VERSION -- Creates .FastqToSam folder in the output"
    echo "change the -stall param as needed and the -r1 and -r2 as needed"
    python3 /n/data1/hms/dbmi/park/victor/scripts/GATK_Somatic_SNPs_Indels/FastqToSam2_single_end.py  \
        -in_dir ${fastq_path} \
        -out ${output_path} \
        -p park -stall 1 -r1 0 -r2 10000
;;
3)
    echo "unaligned bam files -> aligned bam files. Creates a .PreProcessing folder"
    echo "change the -t param if running smaller files, and can change the processing "
    echo "change the -stall param as needed and the -r1 and -r2 as needed"
    module load gcc java/jdk-1.8u112 python/3.6.0 samtools htslib bcftools bwa
    source /n/app/miniconda3/23.1.0/etc/profile.d/conda.sh
    conda activate /n/data1/hms/dbmi/gulhan/lab/ankit/conda_envs/SNVCurate
    python3 /n/data1/hms/dbmi/gulhan/lab/ankit/scripts/alignment_scripts/PreProcessing.py \
        -in_dir ${output_path}/.FastqToSam \
        -out ${output_path} \
        -input_json ${alignment_json} \
        -gatk_wdl ${alignment_wdl} \
        -n 1 -t 48:00:00 \
        -p medium \
        --mem_per_cpu 15G \
        -csv ${csv} -stall 100 -r1 0 -r2 15

;;

*)
    echo "select a step (first argument for this script)" 
;;
esac

