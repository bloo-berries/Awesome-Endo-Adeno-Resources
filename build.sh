#!/bin/bash
set -e

echo "===== SIMPLE STATIC HTML BUILD SCRIPT ====="

# Create _site directory
mkdir -p _site

# Create a simple index.html with README.md content
echo "Creating static HTML site from README.md..."
cat > _site/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Awesome Endo and Adeno Resources</title>
  <style>
    body { 
      font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
      line-height: 1.6;
      color: #333;
      max-width: 900px;
      margin: 0 auto;
      padding: 20px;
    }
    a { color: #0366d6; text-decoration: none; }
    a:hover { text-decoration: underline; }
    h1, h2, h3, h4 { margin-top: 24px; margin-bottom: 16px; font-weight: 600; line-height: 1.25; }
    h1 { font-size: 2em; }
    h2 { font-size: 1.5em; padding-bottom: 0.3em; border-bottom: 1px solid #eaecef; }
    h3 { font-size: 1.25em; }
    ul, ol { padding-left: 2em; }
    li { margin-bottom: 0.25em; }
    code { font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace; background-color: rgba(27,31,35,0.05); padding: 0.2em 0.4em; border-radius: 3px; }
    pre { background-color: #f6f8fa; border-radius: 3px; padding: 16px; overflow: auto; }
    pre code { background-color: transparent; padding: 0; }
    blockquote { margin-left: 0; padding-left: 1em; color: #6a737d; border-left: 0.25em solid #dfe2e5; }
    hr { height: 0.25em; padding: 0; margin: 24px 0; background-color: #e1e4e8; border: 0; }
    table { border-collapse: collapse; width: 100%; overflow: auto; }
    table th, table td { padding: 6px 13px; border: 1px solid #dfe2e5; }
    table tr { background-color: #fff; border-top: 1px solid #c6cbd1; }
    table tr:nth-child(2n) { background-color: #f6f8fa; }
  </style>
</head>
<body>
  <h1>Awesome Endo and Adeno Resources</h1>
  <div id="content">
    <pre>
EOF

# Add README content
cat README.md >> _site/index.html

# Close HTML tags
echo '    </pre>
  </div>
</body>
</html>' >> _site/index.html

echo "Static site created successfully"
ls -la _site

# Copy any CSS files
if [ -f "style.css" ]; then
  echo "Copying style.css to _site/"
  cp style.css _site/
fi

# Copy CNAME if it exists
if [ -f "CNAME" ]; then
  echo "Copying CNAME to _site/"
  cp CNAME _site/
fi

echo "===== BUILD COMPLETE =====" 