#!/usr/bin/env python3
"""
Nextflow Command Builder Generator
==================================
Generates an interactive, standalone HTML command and parameter builder
from Nextflow pipeline configuration files (`nextflow.config`) and parameters YAML (`params.yaml`).

Author: Luca Cozzuto & DeepMind AI
"""

import argparse
import json
import os
import re
import sys
import yaml


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} Command Builder</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #f8fafc;
            --bg-secondary: #ffffff;
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --accent-primary: #0ea5e9;
            --accent-hover: #0284c7;
            --border-color: #e2e8f0;
            --code-bg: #1e293b;
            --code-text: #f8fafc;
            --section-bg: #f1f5f9;
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.5;
            padding: 2rem 1rem;
        }}
        .container {{
            max-width: 1040px;
            margin: 0 auto;
        }}
        header {{
            margin-bottom: 2rem;
            text-align: center;
        }}
        h1 {{
            font-size: 2.25rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            color: var(--text-primary);
            letter-spacing: -0.025em;
        }}
        .subtitle {{
            color: var(--text-secondary);
            font-size: 1.05rem;
            max-width: 650px;
            margin: 0 auto;
        }}
        .card {{
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 2rem;
            box-shadow: var(--shadow-md);
            margin-bottom: 2rem;
        }}
        .section-header {{
            grid-column: 1 / -1;
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--text-primary);
            padding: 0.5rem 0.75rem;
            background-color: var(--section-bg);
            border-left: 4px solid var(--accent-primary);
            border-radius: 4px;
            margin-top: 0.75rem;
            margin-bottom: 0.25rem;
        }}
        .section-header:first-of-type {{
            margin-top: 0;
        }}
        .grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }}
        @media (min-width: 768px) {{
            .grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        .form-group {{
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}
        .form-group.full-width {{
            grid-column: 1 / -1;
        }}
        label {{
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--text-primary);
        }}
        .help-text {{
            font-size: 0.75rem;
            color: var(--text-secondary);
            margin-top: -0.25rem;
            line-height: 1.35;
        }}
        select, input[type="text"], input[type="number"] {{
            width: 100%;
            padding: 0.625rem 0.875rem;
            font-size: 0.875rem;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            background-color: var(--bg-secondary);
            color: var(--text-primary);
            transition: border-color 0.15s ease, box-shadow 0.15s ease;
        }}
        select:focus, input[type="text"]:focus, input[type="number"]:focus {{
            border-color: var(--accent-primary);
            box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.15);
            outline: none;
        }}
        .checkbox-group {{
            flex-direction: row;
            align-items: center;
            gap: 0.75rem;
        }}
        .checkbox-group input[type="checkbox"] {{
            width: 1.2rem;
            height: 1.2rem;
            accent-color: var(--accent-primary);
            cursor: pointer;
        }}
        .checkbox-group label {{
            cursor: pointer;
            margin-bottom: 0;
        }}
        .output-card {{
            background-color: var(--code-bg);
            color: var(--code-text);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: var(--shadow-md);
            margin-bottom: 1.5rem;
        }}
        .output-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding-bottom: 0.75rem;
        }}
        .output-title {{
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #94a3b8;
            font-weight: 600;
        }}
        .copy-btn {{
            background-color: rgba(255, 255, 255, 0.1);
            border: none;
            color: var(--code-text);
            padding: 0.375rem 0.75rem;
            font-size: 0.75rem;
            font-weight: 500;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.15s ease;
        }}
        .copy-btn:hover {{
            background-color: rgba(255, 255, 255, 0.2);
        }}
        pre {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.875rem;
            white-space: pre-wrap;
            word-wrap: break-word;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{title} Command Builder</h1>
            <p class="subtitle">{description}</p>
        </header>

        <div class="card">
            <div class="grid" id="formInputs"></div>
        </div>

        <div class="output-card">
            <div class="output-header">
                <span class="output-title">Nextflow Command</span>
                <button class="copy-btn" id="copyCmdBtn">Copy</button>
            </div>
            <pre><code id="commandOutput"></code></pre>
        </div>
        
        <div class="output-card">
            <div class="output-header">
                <span class="output-title">params.yaml Content</span>
                <button class="copy-btn" id="copyYamlBtn">Copy YAML</button>
            </div>
            <pre><code id="yamlOutput"></code></pre>
        </div>
    </div>

    <script>
        const inputsData = {fields_json};
        const pipelinePath = "{pipeline_path}";

        function renderInputs() {{
            const container = document.getElementById('formInputs');
            let currentSection = null;

            inputsData.forEach(field => {{
                if (field.section && field.section !== currentSection) {{
                    currentSection = field.section;
                    const secHeader = document.createElement('div');
                    secHeader.className = 'section-header';
                    secHeader.textContent = currentSection;
                    container.appendChild(secHeader);
                }}

                const formGroup = document.createElement('div');
                formGroup.className = 'form-group' + (field.type === 'checkbox' ? ' checkbox-group' : '');
                if (field.fullWidth) formGroup.classList.add('full-width');

                if (field.type === 'checkbox') {{
                    formGroup.innerHTML = `<input type="checkbox" id="${{field.id}}" ${{field.default ? 'checked' : ''}}>
                                           <label for="${{field.id}}">${{field.label}}</label>`;
                }} else {{
                    formGroup.innerHTML = `<label for="${{field.id}}">${{field.label}}</label>`;
                    if (field.type === 'select') {{
                        const select = document.createElement('select');
                        select.id = field.id;
                        field.options.forEach(opt => {{
                            const option = document.createElement('option');
                            option.value = opt;
                            option.textContent = opt;
                            if (opt === field.default) option.selected = true;
                            select.appendChild(option);
                        }});
                        formGroup.appendChild(select);
                    }} else {{
                        const input = document.createElement('input');
                        input.type = field.type;
                        input.id = field.id;
                        input.value = field.default !== undefined && field.default !== null ? field.default : '';
                        if (field.placeholder) input.placeholder = field.placeholder;
                        formGroup.appendChild(input);
                    }}
                }}
                if (field.help) {{
                    const help = document.createElement('span');
                    help.className = 'help-text';
                    help.textContent = field.help;
                    formGroup.appendChild(help);
                }}
                container.appendChild(formGroup);
            }});

            container.querySelectorAll('input, select').forEach(el => {{
                el.addEventListener('input', generateCommand);
                el.addEventListener('change', generateCommand);
            }});

            generateCommand();
        }}

        function generateCommand() {{
            let cmd = `nextflow run ${{pipelinePath}}`;
            let yaml = '';
            
            const profileEl = document.getElementById('profile');
            if (profileEl && profileEl.value) {{
                cmd += ` -profile ${{profileEl.value}}`;
            }}
            
            const workDirEl = document.getElementById('work_dir');
            if (workDirEl && workDirEl.value.trim() !== '') {{
                cmd += ` -w ${{workDirEl.value.trim()}}`;
            }}
            
            const resumeEl = document.getElementById('resume');
            if (resumeEl && resumeEl.checked) {{
                cmd += ' -resume';
            }}

            const bgEl = document.getElementById('bg');
            if (bgEl && bgEl.checked) {{
                cmd += ' -bg';
            }}

            const paramsFileEl = document.getElementById('paramsFile');
            const paramsFile = (paramsFileEl && paramsFileEl.value.trim()) ? paramsFileEl.value.trim() : 'params.yaml';
            cmd += ` -params-file ${{paramsFile}}`;

            inputsData.forEach(field => {{
                if (['profile', 'work_dir', 'paramsFile', 'resume', 'bg'].includes(field.id)) return;
                
                const el = document.getElementById(field.id);
                if (!el) return;

                if (field.type === 'checkbox') {{
                    const isChecked = el.checked;
                    if (isChecked || field.default !== false) {{
                        yaml += `${{field.id}}: ${{isChecked}}\\n`;
                    }}
                }} else {{
                    const val = el.value;
                    if (val !== '') {{
                        if (field.type === 'number') {{
                            yaml += `${{field.id}}: ${{val}}\\n`;
                        }} else {{
                            yaml += `${{field.id}}: "${{val}}"\\n`;
                        }}
                    }} else if (field.preserveEmpty) {{
                        yaml += `${{field.id}}: ""\\n`;
                    }}
                }}
            }});
            
            document.getElementById('commandOutput').textContent = cmd;
            document.getElementById('yamlOutput').textContent = yaml;
        }}

        document.getElementById('copyCmdBtn').addEventListener('click', () => {{
            navigator.clipboard.writeText(document.getElementById('commandOutput').textContent).then(() => {{
                const btn = document.getElementById('copyCmdBtn');
                btn.textContent = 'Copied!';
                setTimeout(() => btn.textContent = 'Copy', 2000);
            }});
        }});
        
        document.getElementById('copyYamlBtn').addEventListener('click', () => {{
            navigator.clipboard.writeText(document.getElementById('yamlOutput').textContent).then(() => {{
                const btn = document.getElementById('copyYamlBtn');
                btn.textContent = 'Copied!';
                setTimeout(() => btn.textContent = 'Copy YAML', 2000);
            }});
        }});

        renderInputs();
    </script>
</body>
</html>"""


def parse_nextflow_config(config_path):
    """
    Parses nextflow.config to extract profiles and manifest metadata.
    """
    profiles = []
    manifest = {
        'name': '',
        'description': 'Quickly configure and construct your Nextflow pipeline execution.',
        'version': '',
        'author': ''
    }

    if not os.path.exists(config_path):
        return ['standard', 'local'], manifest

    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove single-line and multi-line comments
    content_no_comments = re.sub(r'/\*[\s\S]*?\*/', '', content)
    
    # Extract manifest details
    m_match = re.search(r'manifest\s*\{([^}]+)\}', content_no_comments, re.DOTALL)
    if m_match:
        m_block = m_match.group(1)
        for line in m_block.splitlines():
            line = line.strip()
            name_m = re.search(r'name\s*=\s*[\'"]([^\'"]+)[\'"]', line)
            if name_m:
                manifest['name'] = name_m.group(1)
            desc_m = re.search(r'description\s*=\s*[\'"]([^\'"]+)[\'"]', line)
            if desc_m:
                manifest['description'] = desc_m.group(1)
            ver_m = re.search(r'version\s*=\s*[\'"]([^\'"]+)[\'"]', line)
            if ver_m:
                manifest['version'] = ver_m.group(1)
            auth_m = re.search(r'author\s*=\s*[\'"]([^\'"]+)[\'"]', line)
            if auth_m:
                manifest['author'] = auth_m.group(1)

    # Extract profiles block
    p_match = re.search(r'profiles\s*\{(.*)', content_no_comments, re.DOTALL)
    if p_match:
        block = p_match.group(1)
        depth = 1
        lines = block.splitlines()
        for line in lines:
            line_str = line.strip()
            # Ignore lines starting with //
            if line_str.startswith('//'):
                continue
            
            # Find profile entry when depth is 1
            if depth == 1:
                prof_m = re.match(r'([a-zA-Z0-9_-]+)\s*\{', line_str)
                if prof_m:
                    prof_name = prof_m.group(1)
                    if prof_name not in profiles:
                        profiles.append(prof_name)

            # Update brace depth
            open_count = line_str.count('{')
            close_count = line_str.count('}')
            depth += open_count - close_count
            if depth <= 0:
                break

    if not profiles:
        profiles = ['standard', 'local']

    return profiles, manifest


def clean_token(token):
    t = token.strip(' "\'():;.,')
    t = re.sub(r'^(?:(?:it\s+)?can\s+be\s+(?:either\s+)?|(?:it\s+)?must\s+be\s+(?:either\s+)?|either\s+|or\s+)', '', t, flags=re.IGNORECASE).strip(' "\'()')
    if ' for ' in t.lower():
        t = re.split(r'\s+for\s+', t, flags=re.IGNORECASE)[0].strip()
    return t


def parse_comment_options(help_text):
    """
    Intelligently extracts allowed choices/options from parameter comments.
    """
    if not help_text:
        return []
    
    # Check parenthetical forms: (can be YES or skip), (YES / NO), (YES, NO)
    pm = re.search(r'\(\s*(?:(?:(?:it\s+)?(?:can|must)\s+be\s+)?|(?:YES|NO|skip|true|false)\s*(?:\/|,|\bor\b))([^\)]+)\)', help_text, re.IGNORECASE)
    if pm:
        raw = pm.group(0).strip('()')
        tokens = re.split(r'\s*/\s*|\s*,\s*|\s+or\s+', raw)
        opts = [clean_token(t) for t in tokens if clean_token(t)]
        opts = [o for o in opts if len(o) < 30 and not any(w in o.lower() for w in ['empty', 'must', 'apply', 'implied', 'implies', 'case', 'value', 'path'])]
        if len(opts) >= 2:
            return list(dict.fromkeys(opts))

    # Strip annotations in parentheses: (for DNA), (for mRNA, etc.)
    clean_help = re.sub(r'\([^)]*\)', '', help_text)
    
    # Check explicit 'can be', 'either', 'options:', 'choices:'
    m = re.search(r'(?:(?:it\s+)?can\s+be\s+(?:either\s+)?|(?:options|choices)\s*:\s*|\beither\s+)([^.]+)', clean_help, re.IGNORECASE)
    if m:
        phrase = m.group(1)
        tokens = re.split(r'\s*/\s*|\s*,\s*|\s+or\s+', phrase)
        opts = []
        for t in tokens:
            ct = clean_token(t)
            if ct and len(ct.split()) <= 2 and not any(w in ct.lower() for w in ['empty', 'must', 'apply', 'implied', 'implies', 'case', 'value', 'path', 'if']):
                ct = ct.split()[0].strip(' "\'()')
                if ct:
                    opts.append(ct)
        if len(opts) >= 2:
            return list(dict.fromkeys(opts))
            
    return []


def format_label(key):
    """
    Converts snake_case or camelCase key into a human-friendly label.
    """
    words = key.replace('_', ' ').replace('-', ' ').split()
    return ' '.join(w.capitalize() for w in words)


def parse_params_yaml(yaml_path):
    """
    Parses a params.yaml file to extract fields, comments, defaults, types, and sections.
    """
    if not os.path.exists(yaml_path):
        return []

    with open(yaml_path, 'r', encoding='utf-8') as f:
        raw_lines = f.readlines()

    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            parsed_data = yaml.safe_load(f) or {}
    except Exception:
        parsed_data = {}

    fields = []
    pending_comments = []
    current_section = None

    for line in raw_lines:
        # Check indentation: only process top-level keys
        if line.startswith(' ') or line.startswith('\t'):
            continue

        stripped = line.strip()
        if not stripped:
            continue

        # Check comment lines
        if stripped.startswith('#'):
            # Detect section header, e.g., "# Input files #" or "# --- Input files ---"
            sec_m = re.match(r'^#+[\s\-=*]*([A-Za-z0-9][A-Za-z0-9\s&/_()-]+?)[\s\-=*]*#*$', stripped)
            if sec_m and not stripped.startswith('##'):
                candidate = sec_m.group(1).strip()
                if candidate and not all(c in '=-*#' for c in candidate) and len(candidate) > 2:
                    current_section = candidate
            else:
                comment_clean = stripped.lstrip('#').strip()
                if comment_clean and not all(c in '=-*#' for c in comment_clean):
                    pending_comments.append(comment_clean)
            continue

        # Match key-value line
        kv_m = re.match(r'^([a-zA-Z0-9_.-]+)\s*:\s*(.*)$', stripped)
        if kv_m:
            key = kv_m.group(1)
            raw_val = kv_m.group(2).strip()

            help_text = ' '.join(pending_comments).strip()
            pending_comments = []

            # Get parsed value if available
            parsed_val = parsed_data.get(key, None)
            if parsed_val is None and raw_val:
                try:
                    parsed_val = yaml.safe_load(raw_val)
                except Exception:
                    parsed_val = raw_val.strip(' "\'')

            # Avoid rendering full nested dictionaries as simple inputs
            if isinstance(parsed_val, dict):
                continue

            # Determine field type and options
            options = parse_comment_options(help_text)
            field_type = "text"
            default_val = parsed_val

            if isinstance(parsed_val, bool):
                field_type = "checkbox"
                default_val = parsed_val
            elif isinstance(parsed_val, (int, float)) and not isinstance(parsed_val, bool):
                field_type = "number"
                default_val = parsed_val
            elif options:
                field_type = "select"
                if default_val not in options and default_val is not None and str(default_val) != "":
                    options.insert(0, str(default_val))
                default_val = str(default_val) if default_val is not None else options[0]
            elif str(parsed_val).upper() in ['YES', 'NO']:
                field_type = "select"
                options = ['YES', 'NO']
                default_val = str(parsed_val).upper()
            else:
                field_type = "text"
                default_val = "" if parsed_val is None else str(parsed_val)

            placeholder = f"Path to {key}" if any(w in key.lower() for w in ['input', 'file', 'ref', 'anno', 'path', 'dir']) else ""

            field_dict = {
                "id": key,
                "label": format_label(key),
                "type": field_type,
                "default": default_val
            }
            if current_section:
                field_dict["section"] = current_section
            if placeholder:
                field_dict["placeholder"] = placeholder
            if options:
                field_dict["options"] = options
            if help_text:
                field_dict["help"] = help_text

            fields.append(field_dict)

    return fields


def generate_builder_html(pipeline_dir=".", config_file=None, params_file=None, output_file=None, title=None, main_script="main.nf"):
    """
    Main function to generate the HTML command builder file.
    """
    pipeline_dir = os.path.abspath(pipeline_dir)

    # Locate config and params
    if not config_file:
        candidate_config = os.path.join(pipeline_dir, "nextflow.config")
        config_file = candidate_config if os.path.exists(candidate_config) else None

    if not params_file:
        for candidate in ["params.yaml", "params.yml", "params.test.yaml", "parameters.yaml"]:
            p = os.path.join(pipeline_dir, candidate)
            if os.path.exists(p):
                params_file = p
                break

    # Parse config
    profiles, manifest = parse_nextflow_config(config_file) if config_file else (['standard', 'local'], {})
    
    # Parse params
    pipeline_fields = parse_params_yaml(params_file) if params_file else []

    # Title and description
    pipe_name = os.path.basename(pipeline_dir.rstrip("/"))
    final_title = title or manifest.get('name') or format_label(pipe_name)
    description = manifest.get('description') or "Quickly configure and construct your Nextflow pipeline execution."

    # Build common execution fields
    default_profile = "local" if "local" in profiles else (profiles[0] if profiles else "standard")
    common_fields = [
        {
            "id": "profile",
            "label": "Nextflow Profile",
            "type": "select",
            "options": profiles,
            "default": default_profile,
            "section": "Execution Settings"
        },
        {
            "id": "work_dir",
            "label": "Work Directory",
            "type": "text",
            "default": "",
            "placeholder": "work (Optional)",
            "fullWidth": True,
            "section": "Execution Settings"
        },
        {
            "id": "paramsFile",
            "label": "Params File Name",
            "type": "text",
            "default": "params.yaml",
            "placeholder": "params.yaml",
            "fullWidth": True,
            "help": "The filename to save the generated YAML under (default: params.yaml).",
            "section": "Execution Settings"
        },
        {
            "id": "resume",
            "label": "Resume Execution (-resume)",
            "type": "checkbox",
            "default": False,
            "section": "Execution Settings"
        },
        {
            "id": "bg",
            "label": "Run in Background (-bg)",
            "type": "checkbox",
            "default": False,
            "section": "Execution Settings"
        }
    ]

    all_fields = common_fields + pipeline_fields

    html_content = HTML_TEMPLATE.format(
        title=final_title,
        description=description,
        pipeline_path=main_script,
        fields_json=json.dumps(all_fields)
    )

    # Determine output file path
    if not output_file:
        docs_dir = os.path.join(pipeline_dir, "docs")
        os.makedirs(docs_dir, exist_ok=True)
        output_file = os.path.join(docs_dir, f"command_builder_{pipe_name}.html")
    else:
        out_dir = os.path.dirname(os.path.abspath(output_file))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    return output_file


def main():
    parser = argparse.ArgumentParser(
        description="Generate interactive HTML Command Builder for Nextflow pipelines from nextflow.config and params.yaml."
    )
    parser.add_argument(
        "pipeline_dir",
        nargs="?",
        default=".",
        help="Path to Nextflow pipeline directory (default: current directory)"
    )
    parser.add_argument(
        "-c", "--config",
        dest="config_file",
        default=None,
        help="Path to nextflow.config file (default: <pipeline_dir>/nextflow.config)"
    )
    parser.add_argument(
        "-p", "--params",
        dest="params_file",
        default=None,
        help="Path to params.yaml file (default: <pipeline_dir>/params.yaml)"
    )
    parser.add_argument(
        "-o", "--output",
        dest="output_file",
        default=None,
        help="Path to output HTML file (default: <pipeline_dir>/docs/command_builder_<name>.html)"
    )
    parser.add_argument(
        "-t", "--title",
        dest="title",
        default=None,
        help="Custom title for the command builder"
    )
    parser.add_argument(
        "-m", "--main",
        dest="main_script",
        default="main.nf",
        help="Main Nextflow script path/name in the generated command (default: main.nf)"
    )

    args = parser.parse_args()

    try:
        out_path = generate_builder_html(
            pipeline_dir=args.pipeline_dir,
            config_file=args.config_file,
            params_file=args.params_file,
            output_file=args.output_file,
            title=args.title,
            main_script=args.main_script
        )
        print(f"Successfully generated HTML Command Builder: {out_path}")
    except Exception as e:
        print(f"Error generating command builder: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
