from http.server import BaseHTTPRequestHandler
import urllib.parse
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle OAuth callbacks from Discord and Twitch"""
        
        # Parse the URL and query parameters
        url_parts = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(url_parts.query)
        
        # Get parameters
        code = query_params.get('code', [None])[0] if 'code' in query_params else None
        state = query_params.get('state', [None])[0] if 'state' in query_params else None
        error = query_params.get('error', [None])[0] if 'error' in query_params else None
        
        if error:
            self.send_error_page(f"Authorization error: {error}")
            return
        
        if not code:
            self.send_error_page("Missing authorization code")
            return
        
        # Determine callback type by path
        if url_parts.path == '/api/auth/twitch':
            self.send_success_page_with_code(code, state)
        else:
            self.send_error_page(f"Invalid callback endpoint: {url_parts.path}")
    
    def send_success_page_with_code(self, code, state):
        """Send success page WITH authorization code"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Anasi - Successfully Connected!</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0; padding: 0; display: flex; justify-content: center;
                    align-items: center; min-height: 100vh;
                }}
                .container {{
                    background: white; padding: 2rem; border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3); text-align: center;
                    max-width: 500px; margin: 20px;
                }}
                .success-icon {{ font-size: 4rem; color: #28a745; margin-bottom: 1rem; }}
                h1 {{ color: #333; margin-bottom: 1rem; }}
                .code-box {{
                    background: #f8f9fa; border: 3px solid #28a745; border-radius: 8px;
                    padding: 20px; margin: 20px 0; font-family: monospace;
                    word-break: break-all; font-size: 16px; cursor: pointer;
                    font-weight: bold;
                }}
                .code-box:hover {{
                    background: #e9ecef; border-color: #20c997;
                }}
                .instructions {{
                    background: #e3f2fd; padding: 15px; border-radius: 8px;
                    margin-top: 1rem; border-left: 4px solid #2196f3;
                }}
                .close-btn {{
                    background: #6f42c1; color: white; border: none;
                    padding: 12px 24px; border-radius: 8px; cursor: pointer;
                    font-size: 1rem; margin-top: 1rem;
                }}
                .copy-btn {{
                    background: #28a745; color: white; border: none;
                    padding: 8px 16px; border-radius: 5px; cursor: pointer;
                    margin-top: 10px; font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-icon">✅</div>
                <h1>Successfully Connected!</h1>
                <p>Your Twitch account has been linked to Anasi</p>
                
                <div class="code-box" onclick="selectCode()" title="Click to select authorization code">
                    {code}
                </div>
                
                <button class="copy-btn" onclick="copyCode()">📋 Copy Code</button>
                
                <div class="instructions">
                    <strong>🎯 Next Steps:</strong><br>
                    1. <strong>Copy the code above</strong> (click it or use copy button)<br>
                    2. <strong>Go back to Discord</strong><br>
                    3. <strong>Use command:</strong> <code>/complete {code[:20]}...</code><br>
                    4. <strong>Start monitoring:</strong> <code>/monitor &lt;streamer&gt;</code>
                </div>
                
                <button class="close-btn" onclick="window.close()">Close Tab</button>
            </div>
            
            <script>
                function selectCode() {{
                    var codeBox = document.querySelector('.code-box');
                    var range = document.createRange();
                    range.selectNode(codeBox);
                    window.getSelection().removeAllRanges();
                    window.getSelection().addRange(range);
                }}
                
                function copyCode() {{
                    var code = "{code}";
                    navigator.clipboard.writeText(code).then(function() {{
                        var btn = document.querySelector('.copy-btn');
                        btn.textContent = '✅ Copied!';
                        btn.style.background = '#20c997';
                        setTimeout(function() {{
                            btn.textContent = '📋 Copy Code';
                            btn.style.background = '#28a745';
                        }}, 2000);
                    }});
                }}
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_error_page(self, error_message):
        """Send error page"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Anasi - Connection Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #ff6b6b; 
                       margin: 0; padding: 20px; text-align: center; }}
                .container {{ background: white; padding: 2rem; border-radius: 15px; 
                             max-width: 400px; margin: 0 auto; }}
                .error-icon {{ font-size: 3rem; color: #dc3545; }}
                h1 {{ color: #333; }}
                .error-message {{ background: #f8d7da; padding: 15px; 
                                 border-radius: 8px; color: #721c24; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error-icon">❌</div>
                <h1>Connection Failed</h1>
                <div class="error-message">{error_message}</div>
                <p>Go back to Discord and try <code>/connect</code> again</p>
            </div>
        </body>
        </html>
        """
        
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
