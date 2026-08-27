#!/usr/bin/env python3
"""
Nextflow Command Builder Generator
==================================
Generates an interactive, standalone HTML command and parameter builder
from Nextflow pipeline configuration files (`nextflow.config`) and parameters YAML (`params.yaml`).

Preserves 100% of original YAML comments, nested blocks (e.g. progPars),
indentation, and formatting in the final output.

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
        const yamlLinesData = {yaml_lines_json};
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
            
            const profileEl = document.getElementById('profile');
            if (profileEl && profileEl.value) {{
                cmd += ` -profile ${{profileEl.value}}`;
            }}

            const outputDirEl = document.getElementById('output_dir');
            if (outputDirEl && outputDirEl.value.trim() !== '') {{
                cmd += ` -o ${{outputDirEl.value.trim()}}`;
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

            const towerEl = document.getElementById('with_tower');
            if (towerEl && towerEl.checked) {{
                cmd += ' -with-tower';
            }}

            const reportEl = document.getElementById('with_report');
            if (reportEl && reportEl.checked) {{
                cmd += ' -with-report';
            }}

            const paramsFileEl = document.getElementById('paramsFile');
            const paramsFile = (paramsFileEl && paramsFileEl.value.trim()) ? paramsFileEl.value.trim() : 'params.yaml';
            cmd += ` -params-file ${{paramsFile}}`;

            let yaml = '';
            if (yamlLinesData && yamlLinesData.length > 0) {{
                yamlLinesData.forEach(line => {{
                    if (line.type === 'comment') {{
                        yaml += line.text + '\\n';
                    }} else if (line.type === 'empty') {{
                        yaml += '\\n';
                    }} else if (line.type === 'parent') {{
                        yaml += line.text + '\\n';
                    }} else if (line.type === 'field') {{
                        const el = document.getElementById(line.id);
                        let val = line.val;
                        if (el) {{
                            val = (el.type === 'checkbox') ? el.checked : el.value;
                        }}
                        
                        let valStr = '';
                        if (typeof val === 'boolean' || line.isBool) {{
                            valStr = val ? 'true' : 'false';
                        }} else if (line.isNumber) {{
                            valStr = (val !== '' && val !== null && val !== undefined) ? String(val) : '0';
                        }} else if (line.quote === '"') {{
                            valStr = `"${{val}}"`;
                        }} else if (line.quote === "'") {{
                            valStr = `'${{val}}'`;
                        }} else {{
                            valStr = String(val);
                        }}
                        
                        const colonSep = line.colonSep || ': ';
                        yaml += `${{line.indent}}${{line.key}}${{colonSep}}${{valStr}}${{line.inlineComment || ''}}\\n`;
                    }}
                }});
            }} else {{
                // Fallback if no yamlLinesData
                inputsData.forEach(field => {{
                    if (['profile', 'output_dir', 'work_dir', 'paramsFile', 'resume', 'bg', 'with_tower', 'with_report'].includes(field.id)) return;
                    const el = document.getElementById(field.id);
                    if (!el) return;
                    if (field.type === 'checkbox') {{
                        yaml += `${{field.id}}: ${{el.checked}}\\n`;
                    }} else {{
                        const v = el.value;
                        if (field.type === 'number') {{
                            yaml += `${{field.id}}: ${{v}}\\n`;
                        }} else {{
                            yaml += `${{field.id}}: "${{v}}"\\n`;
                        }}
                    }}
                }});
            }}
            
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

    config_dir = os.path.dirname(os.path.abspath(config_path))
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove multi-line comments
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
    skip_regex = r'(?://|#)\s*skip\s+in\s+(?:the\s+)?(?:command\s+)?builder'
    p_match = re.search(r'profiles\s*\{(.*)', content_no_comments, re.DOTALL)
    if p_match:
        block = p_match.group(1)
        depth = 1
        current_profile = None
        profile_lines = []
        pending_comments = []

        for line in block.splitlines():
            line_str = line.strip()

            if line_str.startswith('//'):
                if depth == 1:
                    pending_comments.append(line_str)
                elif current_profile is not None:
                    profile_lines.append(line_str)
                continue

            if depth == 1:
                prof_m = re.match(r'([a-zA-Z0-9_-]+)\s*\{', line_str)
                if prof_m:
                    current_profile = prof_m.group(1)
                    profile_lines = [line_str] + pending_comments
                    pending_comments = []

            elif depth > 1 and current_profile is not None:
                profile_lines.append(line_str)

            open_count = line_str.count('{')
            close_count = line_str.count('}')
            depth += open_count - close_count

            if depth == 1 and current_profile is not None:
                # Finished analyzing this profile block
                profile_text = '\n'.join(profile_lines)
                should_skip = False

                if re.search(skip_regex, profile_text, re.IGNORECASE):
                    should_skip = True

                # Check any included config files
                inc_matches = re.findall(r'includeConfig\s+[\'"]([^\'"]+)[\'"]', profile_text)
                for inc_file in inc_matches:
                    clean_inc = inc_file.replace('$projectDir/', '').replace('${projectDir}/', '').replace('$baseDir/', '').replace('${baseDir}/', '')
                    inc_path = os.path.normpath(os.path.join(config_dir, clean_inc))
                    if os.path.exists(inc_path):
                        with open(inc_path, 'r', encoding='utf-8') as inc_f:
                            if re.search(skip_regex, inc_f.read(), re.IGNORECASE):
                                should_skip = True
                                break

                if not should_skip and current_profile not in profiles:
                    profiles.append(current_profile)

                current_profile = None
                profile_lines = []

            if depth <= 0:
                break

    if not profiles:
        profiles = ['standard', 'local']

    return profiles, manifest


NON_OPTION_WORDS = [
    'empty', 'must', 'apply', 'implied', 'implies', 'case', 'value', 'path',
    'url', 'uri', 'file', 'string', 'number', 'regex', 'int', 'float',
    'directory', 'dir', 'pattern', 'text', 'format', 'threshold', 'parameter'
]


def clean_token(token):
    t = token.strip(' "\'():;.,')
    t = re.sub(r'^(?:(?:it\s+)?can\s+be\s+(?:either\s+)?|(?:it\s+)?must\s+be\s+(?:either\s+)?|either\s+|or\s+|a\s+|an\s+)', '', t, flags=re.IGNORECASE).strip(' "\'()')
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
        opts = [o for o in opts if len(o) < 30 and not any(w in o.lower() for w in NON_OPTION_WORDS)]
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
            if ct and len(ct.split()) <= 2 and not any(w in ct.lower() for w in NON_OPTION_WORDS + ['if']):
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


def parse_params_yaml_full(yaml_path):
    """
    Parses a params.yaml file:
    1. Extracts all lines (comments, sections, nested blocks, empty lines) to ensure 100% exact YAML preservation.
    2. Builds form input descriptors for all scalar keys.
    """
    if not os.path.exists(yaml_path):
        return [], []

    with open(yaml_path, 'r', encoding='utf-8') as f:
        raw_lines = f.readlines()

    yaml_lines = []
    form_fields = []
    
    pending_comments = []
    current_section = None
    parent_stack = []  # List of (indent_level, key_name)

    for line in raw_lines:
        raw_line = line.rstrip('\r\n')
        stripped = raw_line.strip()

        # Empty line
        if not stripped:
            yaml_lines.append({'type': 'empty'})
            continue

        # Comment line
        if stripped.startswith('#'):
            sec_m = re.match(r'^#+[\s\-=*]*([A-Za-z0-9][A-Za-z0-9\s&/_()-]+?)[\s\-=*]*#*$', stripped)
            if sec_m and not stripped.startswith('##'):
                candidate = sec_m.group(1).strip()
                if candidate and not all(c in '=-*#' for c in candidate) and len(candidate) > 2:
                    current_section = candidate
            else:
                c_clean = stripped.lstrip('#').strip()
                if c_clean and not all(c in '=-*#' for c in c_clean):
                    pending_comments.append(c_clean)

            yaml_lines.append({'type': 'comment', 'text': raw_line})
            continue

        # Measure indentation
        indent_len = len(raw_line) - len(raw_line.lstrip())

        # Update parent stack
        while parent_stack and parent_stack[-1][0] >= indent_len:
            parent_stack.pop()

        # Check if parent block (key without value, e.g. 'header:' or 'progPars:')
        parent_m = re.match(r'^(\s*)([a-zA-Z0-9_.-]+)\s*:\s*(?:#.*)?$', raw_line)
        if parent_m:
            p_indent = parent_m.group(1)
            p_key = parent_m.group(2)
            parent_stack.append((indent_len, p_key))
            yaml_lines.append({'type': 'parent', 'text': raw_line})
            continue

        # Key-value line
        kv_m = re.match(r'^(\s*)([a-zA-Z0-9_.-]+)(\s*:\s*)(.*?)(?:\s+(#.*))?$', raw_line)
        if kv_m:
            k_indent = kv_m.group(1)
            k_key = kv_m.group(2)
            k_colon_sep = kv_m.group(3)
            k_val = kv_m.group(4).strip()
            k_inline_comment = kv_m.group(5) or ''

            path_parts = [p[1] for p in parent_stack] + [k_key]
            field_id = '__'.join(path_parts)

            # If top-level key is output_dir, ignore it from params.yaml as it is handled by the -o Nextflow CLI flag
            if len(path_parts) == 1 and k_key in ['output_dir']:
                pending_comments = []
                continue

            quote = ''
            parsed_val = k_val
            is_bool = False
            is_number = False

            if (k_val.startswith('\"') and k_val.endswith('\"')) or (k_val.startswith('\'') and k_val.endswith('\'')):
                quote = k_val[0]
                parsed_val = k_val[1:-1]
            elif k_val.lower() in ['true', 'false']:
                is_bool = True
                parsed_val = (k_val.lower() == 'true')
            else:
                try:
                    num = float(k_val)
                    is_number = True
                    parsed_val = int(k_val) if k_val.isdigit() else num
                except ValueError:
                    parsed_val = k_val

            help_text = ' '.join(pending_comments).strip()
            pending_comments = []

            yaml_lines.append({
                'type': 'field',
                'id': field_id,
                'key': k_key,
                'indent': k_indent,
                'colonSep': k_colon_sep,
                'quote': quote,
                'val': parsed_val,
                'isBool': is_bool,
                'isNumber': is_number,
                'inlineComment': f' {k_inline_comment}' if k_inline_comment else ''
            })

            # Create form field entry
            options = parse_comment_options(help_text)
            field_type = "text"

            if is_bool:
                field_type = "checkbox"
            elif is_number:
                field_type = "number"
            elif options:
                field_type = "select"
                if parsed_val not in options and parsed_val is not None and str(parsed_val) != "":
                    options.insert(0, str(parsed_val))
                parsed_val = str(parsed_val) if parsed_val is not None else options[0]
            elif str(parsed_val).upper() in ['YES', 'NO']:
                field_type = "select"
                options = ['YES', 'NO']
                parsed_val = str(parsed_val).upper()

            # Format human label
            label = format_label(k_key)
            if len(path_parts) > 1:
                prefix = ' > '.join(format_label(p) for p in path_parts[:-1])
                label = f"{label} ({prefix})"

            placeholder = ""
            if any(w in k_key.lower() for w in ['slack', 'webhook']):
                placeholder = "Webhook URL or skip"
            elif any(w in k_key.lower() for w in ['input', 'file', 'ref', 'anno', 'path', 'dir']):
                placeholder = f"Path to {k_key}"

            # Determine section
            field_section = current_section
            if not field_section:
                field_section = format_label(path_parts[0]) if len(path_parts) > 1 else "Parameters"

            field_dict = {
                "id": field_id,
                "label": label,
                "type": field_type,
                "default": parsed_val,
                "section": field_section
            }
            if placeholder:
                field_dict["placeholder"] = placeholder
            if options:
                field_dict["options"] = options
            if help_text:
                field_dict["help"] = help_text

            form_fields.append(field_dict)

    return yaml_lines, form_fields


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
        for candidate in ["params.yaml", "params.yml", "params.test.yaml", "params.pod.yaml", "parameters.yaml"]:
            p = os.path.join(pipeline_dir, candidate)
            if os.path.exists(p):
                params_file = p
                break

    # Parse config
    profiles, manifest = parse_nextflow_config(config_file) if config_file else (['standard', 'local'], {})
    
    # Parse params preserving exact lines & comments
    yaml_lines, pipeline_fields = parse_params_yaml_full(params_file) if params_file else ([], [])

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
            "id": "output_dir",
            "label": "Output Directory (-o)",
            "type": "text",
            "default": "results",
            "placeholder": "results",
            "fullWidth": True,
            "help": "Directory where final output files and reports will be saved (-o).",
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
        },
        {
            "id": "with_tower",
            "label": "Nextflow Tower / Seqera (-with-tower)",
            "type": "checkbox",
            "default": False,
            "section": "Execution Settings"
        },
        {
            "id": "with_report",
            "label": "Execution Report (-with-report)",
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
        fields_json=json.dumps(all_fields),
        yaml_lines_json=json.dumps(yaml_lines)
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
        description="Generate interactive HTML Command Builder for Nextflow pipelines preserving exact YAML comments and structure."
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
