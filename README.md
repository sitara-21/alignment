# Alignment/Unalignment Pipeline
Align or Unalign files to a reference genome using GATK best practices.

## Overview
This pipeline is used for unaligning/aligning sequencing data. For eg. to convert hg19 aligned BAM files to hg38 (bam_hg19->FASTQ->bam_hg39). It consists of two main scripts:

* Unalignment: 00_unalign_bams_new.sh step_number
* Alignment: 00_run_align_call_filter_hg38.sh step_number
  
Both follow a stepwise approach, allowing users to run specific steps as needed. Please, setup the environment before execution.

## Unalignment
The pipeline consists of multiple steps that can be executed by specifying the number in the same script as follows:

```./00_unalign_bams_new.sh step_number stall r1 r2```

The parameters are:
- stall: seconds to wait between job submissions.

- r1: index of the first job to be submitted

- r2: index of the last job to be submitted

This allows the user to submit in batches and not all the files at the same time. For eg. first run 0-25 (r1:0, r2:25 -> processes first 25 files with 25th file not being processed in this run), second 25-50 (r1:25, r2:50 -> processes next 25 files with 50th file not being processed in this run), etc.

### Steps Description
#### Step1
Aligned BAM --> FASTQ: Unalign the bam files and create fastq files from them.

#### Step2
Fixes disordered paired reads in fastq files generated in previous step. Create a CSV file specifying the fastq files to be fixed. Sample CSV file (fastq_pairs.csv) attached for reference. ```run_02.sh``` runs ```repair.sh``` that does the disordered read fixing.

#### Step3
This step gunzips the fixed fastq file from previous step for downstream operations. ```run_03.sh``` performs this operation. CSV file can be used to specify a subset of files from a folder to perform this step. Sample CSV (gunzip_list.csv) file attached for reference.
