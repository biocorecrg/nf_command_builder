# Nextflow Command Builder (`nf_command_builder`)

An automated generator that produces modern, interactive HTML command and parameter builders for Nextflow pipelines by parsing `nextflow.config` and `params.yaml`.

The generated standalone HTML file allows users to dynamically configure pipeline options, choose execution profiles, preview the generated `nextflow run` command in real-time, and copy the customized `params.yaml` with one click.

---

## Features

- **Automatic Profile Discovery**: Reads `nextflow.config` to dynamically extract all available profiles (e.g. `local`, `hpc`, `standard`, `test`, `newcrg`, `novoa`, etc.).
- **Smart Parameter Inference**: Analyzes `params.yaml` values, types, section headers, and inline comments to generate:
  - **Dropdown selects** when choices or options are annotated in comments (`## Can be minimap2 / bwa / skip`, `(can be YES or skip)`).
  - **Number inputs** for integer and float thresholds.
  - **Checkboxes** for booleans (`true`/`false`).
  - **Text fields** with auto-generated placeholder paths.
  - **Tooltips / Help text** extracted directly from doc comments.
  - **Grouped section headers** for visual clarity.
- **Real-Time Interactive UI**:
  - Live Nextflow command preview (`-profile`, `-w`, `-params-file`, `-resume`, `-bg`).
  - Live formatted `params.yaml` content generator.
  - One-click copy buttons with visual feedback.
  - Responsive, modern design with zero external JavaScript dependencies.

---

## Quick Start

### 1. Run with Python (Local)

**Prerequisites:** Python 3.8+ and PyYAML.

```bash
pip install pyyaml
```

**Generate Command Builder for a pipeline:**

```bash
# Basic usage (scans test_nf_pipe/nextflow.config and test_nf_pipe/params.yaml)
python3 nf_command_builder.py test_nf_pipe

# Specify custom config, params, or output paths:
python3 nf_command_builder.py test_nf_pipe \
  --config test_nf_pipe/nextflow.config \
  --params test_nf_pipe/params.yaml \
  --output test_nf_pipe/docs/command_builder.html \
  --title "My Custom Pipeline"
```

Open the generated HTML file in any browser:
```bash
open test_nf_pipe/docs/command_builder_test_nf_pipe.html
```

---

### 2. Run with Docker

Pre-built multi-platform container images are automatically published to GitHub Container Registry (GHCR):

```bash
# View help
docker run --rm ghcr.io/biocorecrg/nf_command_builder:latest --help

# Generate builder for a pipeline in the current directory
docker run --rm -v "$(pwd):/workspace" \
  ghcr.io/biocorecrg/nf_command_builder:latest \
  /workspace/test_nf_pipe -o /workspace/test_nf_pipe/docs/command_builder_test_nf_pipe.html
```

---

### 3. Run with Singularity / Apptainer

On HPC clusters where Singularity or Apptainer is available:

```bash
# Using Apptainer / Singularity with the docker image directly
singularity run docker://ghcr.io/biocorecrg/nf_command_builder:latest test_nf_pipe -o test_nf_pipe/docs/command_builder_test_nf_pipe.html

# Or pull the SIF image locally
singularity pull nf_command_builder.sif docker://ghcr.io/biocorecrg/nf_command_builder:latest
./nf_command_builder.sif test_nf_pipe -o test_nf_pipe/docs/command_builder_test_nf_pipe.html
```

---

## CLI Options

```text
usage: nf_command_builder.py [-h] [-c CONFIG_FILE] [-p PARAMS_FILE] [-o OUTPUT_FILE]
                             [-t TITLE] [-m MAIN_SCRIPT]
                             [pipeline_dir]

positional arguments:
  pipeline_dir          Path to Nextflow pipeline directory (default: current directory)

options:
  -h, --help            show this help message and exit
  -c, --config CONFIG_FILE
                        Path to nextflow.config file (default: <pipeline_dir>/nextflow.config)
  -p, --params PARAMS_FILE
                        Path to params.yaml file (default: <pipeline_dir>/params.yaml)
  -o, --output OUTPUT_FILE
                        Path to output HTML file (default: <pipeline_dir>/docs/command_builder_<name>.html)
  -t, --title TITLE     Custom title for the command builder
  -m, --main MAIN_SCRIPT
                        Main Nextflow script path/name in the generated command (default: main.nf)
```

---

## How to Annotate `params.yaml`

The generator recognizes structured comments above parameters to automatically configure form controls and tooltips:

```yaml
# Section Name
# ------------

## Path to input FASTQ or BAM file
input: "data/sample.fastq"

## Read alignment tool. Can be minimap2 / bwa / bowtie2 / skip
aligner: "minimap2"

## Filter low quality reads. Can be YES or skip
filter_quality: "YES"

## Number of CPU threads to allocate per task
threads: 4

## Save intermediate alignment BAM files (true/false)
save_intermediate: false
```

- **Section Headers**: Lines like `# Input Files #` or `# ---- Section ----` create visual grouping dividers in the form.
- **Select Dropdowns**: Phrases like `Can be opt1 / opt2 / skip`, `either X or Y`, or `(can be YES or skip)` automatically convert text inputs into dropdown menus.
- **Help Text**: Any comment preceding the parameter key is converted into description text underneath the input.

---

## Example Pipeline: `test_nf_pipe`

This repository includes a sample Nextflow pipeline in [`test_nf_pipe/`](test_nf_pipe/) demonstrating profile switching between **`local`** and **`hpc`** (Slurm) execution:

```
test_nf_pipe/
├── main.nf                 # Nextflow workflow implementation
├── nextflow.config         # Config with local and hpc profile switch
├── params.yaml             # Documented pipeline parameters
├── conf/
│   ├── local.config        # Local execution limits and resources
│   └── hpc.config          # Slurm cluster partition, queues, and resources
├── data/
│   ├── sample.fastq        # Mock input data
│   └── reference.fasta     # Mock reference FASTA
└── docs/
    └── command_builder_test_nf_pipe.html # Generated interactive builder
```

### Running the Example Pipeline

```bash
# Run locally
nextflow run test_nf_pipe/main.nf -profile local -params-file test_nf_pipe/params.yaml

# Run on HPC with Slurm
nextflow run test_nf_pipe/main.nf -profile hpc -params-file test_nf_pipe/params.yaml
```

---

## GitHub CI, Pages & Container Registry

This repository includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that:
1. **Automated Tests**: Validates the command builder generator and runs `test_nf_pipe` with Nextflow.
2. **GitHub Pages**: Automatically compiles the HTML command builder into `docs/index.html` and `docs/command_builder_test_nf_pipe.html` and deploys it live to GitHub Pages.
3. **Container Registry**: Builds and publishes multi-platform Docker container images to GitHub Packages / Container Registry (`ghcr.io/biocorecrg/nf_command_builder`).

