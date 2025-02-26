from flask import Flask, request, Response
import re
import argparse
import os

# Parse command line arguments
parser = argparse.ArgumentParser(description='XFO Nesting Test Server')
parser.add_argument('--max-depth', type=int, default=200, help='Maximum nesting depth (default: 200)')
args = parser.parse_args()

# Get max depth from command line or environment variable
MAX_DEPTH = int(os.environ.get('XFO_MAX_DEPTH', args.max_depth))

app = Flask(__name__)

@app.route('/<path:path>')
def serve_path(path):
    # Handle numeric paths (1 through MAX_DEPTH)
    if path.isdigit():
        level = int(path)
        
        if level < MAX_DEPTH:
            # Calculate progress percentage
            progress_percent = (level / MAX_DEPTH) * 100
            
            # Return page that iframes the next level
            html = f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Victim Level {level}</title>
                    <style>
                        body, html {{
                            margin: 0;
                            padding: 0;
                            height: 100%;
                            width: 100%;
                            overflow: hidden;
                        }}
                        iframe {{
                            width: 100%;
                            height: calc(100% - 5px);
                            border: none;
                            margin-top: 5px;
                        }}
                        .progress-bar {{
                            position: fixed;
                            top: 0;
                            left: 0;
                            height: 5px;
                            background: #4CAF50;
                            width: {progress_percent}%;
                            z-index: 1000;
                        }}
                    </style>
                </head>
                <body>
                    <div class="progress-bar"></div>
                    <iframe src="/{level + 1}"></iframe>
                </body>
            </html>
            """
            return Response(html)
        else:
            # The last level iframes gg.html
            html = f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Victim Level {level}</title>
                    <style>
                        body, html {{
                            margin: 0;
                            padding: 0;
                            height: 100%;
                            width: 100%;
                            overflow: hidden;
                        }}
                        iframe {{
                            width: 100%;
                            height: calc(100% - 5px);
                            border: none;
                            margin-top: 5px;
                        }}
                        .progress-bar {{
                            position: fixed;
                            top: 0;
                            left: 0;
                            height: 5px;
                            background: #ff5555;
                            width: 100%;
                            z-index: 1000;
                        }}
                    </style>
                </head>
                <body>
                    <div class="progress-bar"></div>
                    <iframe src="/gg.html"></iframe>
                </body>
            </html>
            """
            return Response(html)
    
    # Handle the gg.html path
    elif path == "gg.html":
        html = """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Target Page (gg.html)</title>
                <style>
                    body {
                        background-color: #ffcccc;
                        font-family: Arial, sans-serif;
                        text-align: center;
                        padding: 50px;
                        margin: 0;
                    }
                    .success-message {
                        background-color: #ff5555;
                        color: white;
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                        margin: 20px auto;
                        max-width: 600px;
                        animation: pulse 2s infinite;
                    }
                    @keyframes pulse {
                        0% { transform: scale(1); }
                        50% { transform: scale(1.05); }
                        100% { transform: scale(1); }
                    }
                    h1 {
                        color: red;
                    }
                </style>
            </head>
            <body>
                <h1>Target Content (gg.html)</h1>
                <div class="success-message">
                    <h2>XFO BYPASS SUCCESSFUL!</h2>
                    <p>This page has XFO: SAMEORIGIN header</p>
                    <p>If you can see this content in the iframe chain, then XFO has been bypassed!</p>
                </div>
            </body>
        </html>
        """
        # Return with the XFO: SAMEORIGIN header
        response = Response(html)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        return response
        
# Return 404 for other paths
@app.route('/<path:invalid_path>')
def not_found(invalid_path):
    if not invalid_path.isdigit() and invalid_path != "gg.html":
        return "Not Found", 404

@app.route('/')
def index():
    return f"""
    <html>
        <head>
            <title>XFO Test Server</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    line-height: 1.6;
                }}
                h1 {{
                    color: #333;
                    border-bottom: 1px solid #ccc;
                    padding-bottom: 10px;
                }}
                .info-box {{
                    background: #f5f5f5;
                    border-left: 4px solid #0066cc;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .config {{
                    background: #e6f7ff;
                    border: 1px solid #91d5ff;
                    padding: 10px 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .button {{
                    display: inline-block;
                    padding: 10px 15px;
                    background: #4CAF50;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    margin-right: 10px;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <h1>XFO Nesting Test Server</h1>
            
            <div class="config">
                <h3>Current Configuration</h3>
                <p>Maximum nesting depth: <strong>{MAX_DEPTH}</strong></p>
            </div>
            
            <div class="info-box">
                <p>This server simulates victim.com for testing X-Frame-Options with deeply nested iframes.</p>
                <p>Visit paths /1 through /{MAX_DEPTH} to test the nesting behavior.</p>
                <p>/gg.html has the X-Frame-Options: SAMEORIGIN header.</p>
            </div>
            
            <p>
                <a href="/1" class="button">Start the Test</a>
            </p>
        </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') 