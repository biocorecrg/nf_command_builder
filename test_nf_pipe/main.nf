#!/usr/bin/env nextflow

nextflow.enable.dsl = 2

/*
 * ==============================================================================
 * Test Nextflow Pipeline
 * ==============================================================================
 * Demonstrates parameter handling and profile switching (local vs hpc)
 */

// Pipeline parameter defaults
params.input             = "${projectDir}/data/sample.fastq"
params.reference         = "${projectDir}/data/reference.fasta"
params.annotation        = ""
params.aligner           = "minimap2"
params.qc_mode           = "standard"
params.variant_caller    = "freebayes"
params.filter_quality    = "YES"
params.threads           = 2
params.min_read_length   = 50
params.subsample_pct     = 100
params.output_dir        = "results"
params.save_intermediate = false
params.verbose           = true
params.slackhook         = "skip"

process QC_CHECK {
    tag "QC on ${reads.name}"
    label 'process_low'
    publishDir "${params.output_dir}/qc", mode: 'copy'

    input:
    path reads

    output:
    path "qc_summary.txt", emit: report

    script:
    """
    echo "Running QC check on ${reads}" > qc_summary.txt
    echo "QC mode: ${params.qc_mode}" >> qc_summary.txt
    echo "Min read length: ${params.min_read_length}" >> qc_summary.txt
    echo "Filter quality: ${params.filter_quality}" >> qc_summary.txt
    echo "Total lines in input: \$(wc -l < ${reads})" >> qc_summary.txt
    """
}

process ALIGN_READS {
    tag "Align with ${params.aligner}"
    label 'process_medium'
    publishDir "${params.output_dir}/alignment", mode: 'copy'

    input:
    path reads
    path ref

    output:
    path "aligned_reads.txt", emit: aln

    script:
    if (params.aligner != 'skip')
        """
        echo "Aligning ${reads} to ${ref} using ${params.aligner}..." > aligned_reads.txt
        echo "Threads allocated: ${task.cpus}" >> aligned_reads.txt
        echo "Subsample percentage: ${params.subsample_pct}%" >> aligned_reads.txt
        """
    else
        """
        echo "Skipping alignment as requested" > aligned_reads.txt
        """
}

process GENERATE_REPORT {
    tag "Summary Report"
    label 'process_low'
    publishDir "${params.output_dir}/report", mode: 'copy'

    input:
    path qc_report
    path aln_report

    output:
    path "pipeline_summary.md", emit: summary

    script:
    """
    cat <<EOF > pipeline_summary.md
    # Pipeline Execution Summary
    - **Workflow Profile**: ${workflow.profile}
    - **Aligner Used**: ${params.aligner}
    - **QC Mode**: ${params.qc_mode}
    - **Variant Caller**: ${params.variant_caller}
    - **Status**: SUCCESS

    ## QC Details
    \$(cat ${qc_report})

    ## Alignment Details
    \$(cat ${aln_report})
    EOF
    """
}

workflow {
    log.info """
    ==================================================
     Test Nextflow Pipeline v1.0.0
    ==================================================
     Profile         : ${workflow.profile}
     Input File      : ${params.input}
     Reference       : ${params.reference}
     Aligner         : ${params.aligner}
     QC Mode         : ${params.qc_mode}
     Variant Caller  : ${params.variant_caller}
     Output Dir      : ${params.output_dir}
     Threads         : ${params.threads}
    ==================================================
    """

    input_ch = Channel.fromPath(params.input, checkIfExists: true)
    ref_ch   = Channel.fromPath(params.reference, checkIfExists: true)

    qc_out  = QC_CHECK(input_ch)
    aln_out = ALIGN_READS(input_ch, ref_ch)
    GENERATE_REPORT(qc_out.report, aln_out.aln)
}
