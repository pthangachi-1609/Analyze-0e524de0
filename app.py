#!/usr/bin/env python3
import os
import sys
import json
from flask import Flask, render_template_string

app = Flask(__name__)

# Inline CSS for consistency across runtime and export
CSS = """
body { font-family: Arial, sans-serif; padding: 20px; background: #f6f6f6; color: #333; }
h1 { color: #2c3e50; }
a { color: #1a73e8; text-decoration: none; }
a:hover { text-decoration: underline; }
table { border-collapse: collapse; width: 100%; background: #fff; }
th, td { border: 1px solid #ddd; padding: 8px; }
th { background: #f2f2f2; }
"""

# Simple HTML templates (rendered via Flask's template engine)
TEMPLATES = {
    'index': """
<!doctype html>
<html>
<head>
  <title>App Index</title>
  <style>{{ css }}</style>
</head>
<body>
  <h1>Application Overview</h1>
  <ul>
    <li><a href="/data">Data Preview</a></li>
    <li><a href="/attachments">Attachments</a></li>
    <li><a href="/execute">Execute Script</a></li>
    <li><a href="/export">Export Static Site</a></li>
  </ul>
  <p>{{ message }}</p>
</body>
</html>
""",
    'data': """
<!doctype html>
<html>
<head><title>Data</title><style>{{ css }}</style></head>
<body>
  <h1>Data Preview</h1>
  <div>{{ data_table|safe }}</div>
  <a href="/">Back</a>
</body>
</html>
""",
    'attachments': """
<!doctype html>
<html>
<head><title>Attachments</title><style>{{ css }}</style></head>
<body>
  <h1>Attachments</h1>
  <ul>
  {% for a in attachments %}
    <li>
      <strong>{{ a.name }}</strong><br/>
      {% if a.data_uri %}
        {% if a.data_uri.startswith('data:image') %}
          <img src="{{ a.data_uri }}" alt="{{ a.name }}" style="max-width:400px;"/>
        {% else %}
          <a href="{{ a.data_uri }}" download="{{ a.name }}">Download</a>
        {% endif %}
      {% else %}
        <em>No data URI available</em>
      {% endif %}
    </li>
  {% endfor %}
  </ul>
  <a href="/">Back</a>
</body>
</html>
""",
    'execute': """
<!doctype html>
<html>
<head><title>Execute</title><style>{{ css }}</style></head>
<body>
  <h1>Execute Script Result</h1>
  <pre>{{ result }}</pre>
  <a href="/">Back</a>
</body>
</html>
""",
    'export_notice': """
<!doctype html>
<html><head><title>Export</title><style>{{ css }}</style></head><body>
  <h1>Static Site Export Created</h1>
  <p>Exported to: {{ output_dir }}</p>
  <a href="/">Back</a>
</body></html>
"""
}

def load_attachments():
    attachments = []
    data_json_path = 'data.json'
    if os.path.exists(data_json_path):
        try:
            with open(data_json_path, 'r', encoding='utf-8') as f:
                payload = json.load(f)
            for item in payload.get('attachments', []):
                name = item.get('name', '')
                url = item.get('url', '')
                data_uri = None
                if isinstance(url, str) and url.startswith('data:'):
                    data_uri = url
                attachments.append({'name': name, 'data_uri': data_uri})
        except Exception:
            # If parsing fails, provide a silent placeholder
            attachments.append({'name': 'data.json parse error', 'data_uri': None})
    return attachments

def load_data_html():
    # Try to load data.csv; if absent, try to convert data.xlsx -> data.csv
    try:
        import pandas as pd
    except Exception:
        return "<p>Pandas is required to render data. Install Pandas 2.3+ to view data.</p>"

    data_effective = None
    if os.path.exists('data.csv'):
        try:
            df = pd.read_csv('data.csv')
            data_effective = df
        except Exception as e:
            return "<p>Error reading data.csv: {}</p>".format(e)
    else:
        if os.path.exists('data.xlsx'):
            try:
                df = pd.read_excel('data.xlsx')
                data_effective = df
                # Persist a CSV for consistency if possible
                try:
                    df.to_csv('data.csv', index=False)
                except Exception:
                    pass
            except Exception as e:
                return "<p>Error converting data.xlsx: {}</p>".format(e)

    if isinstance(data_effective, pd.DataFrame):
        try:
            # Render as HTML table
            return data_effective.to_html(index=False)
        except Exception as e:
            return "<p>Error rendering data to HTML: {}</p>".format(e)
    return "<p>No data available.</p>"

def ensure_csv_from_excel():
    # Convert data.xlsx to data.csv if needed
    if not os.path.exists('data.csv') and os.path.exists('data.xlsx'):
        try:
            import pandas as pd
            df = pd.read_excel('data.xlsx')
            df.to_csv('data.csv', index=False)
        except Exception:
            pass

# Routes
@app.route('/')
def index():
    return render_template_string(TEMPLATES['index'], css=CSS, message="")

@app.route('/data')
def data_view():
    html_table = load_data_html()
    return render_template_string(TEMPLATES['data'], css=CSS, data_table=html_table)

@app.route('/attachments')
def attachments_view():
    attachments = load_attachments()
    return render_template_string(TEMPLATES['attachments'], css=CSS, attachments=attachments)

@app.route('/execute')
def execute_view():
    result = ""
    try:
        import importlib.util
        import pathlib
        path = pathlib.Path('execute.py')
        if path.exists():
            spec = importlib.util.spec_from_file_location("execute_module", str(path))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, 'run') and callable(module.run):
                resp = module.run()
                result = repr(resp)
            else:
                result = "execute.py loaded but no run() function found."
        else:
            result = "execute.py not found."
    except Exception as e:
        result = "Error running execute.py: {}".format(e)
    return render_template_string(TEMPLATES['execute'], css=CSS, result=result)

@app.route('/export')
def export():
    output_dir = os.path.join(os.getcwd(), 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    attachments = load_attachments()
    data_html = load_data_html()

    with app.app_context():
        index_html = render_template_string(TEMPLATES['index'], css=CSS, message="Static site ready for offline viewing.")
        data_html_page = render_template_string(TEMPLATES['data'], css=CSS, data_table=data_html)
        attachments_html = render_template_string(TEMPLATES['attachments'], css=CSS, attachments=attachments)
        # CSS file for export
        try:
            with open(os.path.join(output_dir, 'styles.css'), 'w', encoding='utf-8') as f:
                f.write(CSS)
        except Exception:
            pass
        with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(index_html)
        with open(os.path.join(output_dir, 'data.html'), 'w', encoding='utf-8') as f:
            f.write(data_html_page)
        with open(os.path.join(output_dir, 'attachments.html'), 'w', encoding='utf-8') as f:
            f.write(attachments_html)
        execute_html = render_template_string(TEMPLATES['execute'], css=CSS, result="Exported static pages.")
        with open(os.path.join(output_dir, 'execute.html'), 'w', encoding='utf-8') as f:
            f.write(execute_html)
        notice = render_template_string(TEMPLATES['export_notice'], css=CSS, output_dir=output_dir)
        return notice

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--export', action='store_true', help='Export static site to output/')
    args = parser.parse_args()

    # Ensure data.csv is present if possible
    ensure_csv_from_excel()

    if args.export:
        # Perform export to output/
        export()
    else:
        # Development server
        app.run(host='0.0.0.0', port=5000, debug=True)