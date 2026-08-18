# Multi-platform lightweight container for Nextflow Command Builder
FROM python:3.11-slim

LABEL maintainer="Luca Cozzuto"
LABEL description="Interactive HTML Command & Parameter Builder Generator for Nextflow pipelines"
LABEL org.opencontainers.image.source="https://github.com/biocorecrg/nf_command_builder"

WORKDIR /workspace

# Install dependencies
RUN pip install --no-cache-dir pyyaml

# Copy command builder script
COPY nf_command_builder.py /usr/local/bin/nf_command_builder
RUN chmod +x /usr/local/bin/nf_command_builder

ENTRYPOINT ["nf_command_builder"]
CMD ["--help"]
