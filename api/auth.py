from http.server import BaseHTTPRequestHandler
import urllib.parse
import urllib.request
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle OAuth callbacks from Twitch - AUTOMATIC VERSION"""
        
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
            # Try automatic sending, fallback to manual if fails
            success = self.send_to_discord_bot(code, state)
            if success:
                self.send_automatic_success_page(code, state)
            else:
                self.send_manual_fallback_page(code, state)
        else:
            self.send_error_page(f"Invalid callback endpoint: {url_parts.path}")
    
    def send_to_discord_bot(self, code, state):
        """Send authorization code to Discord bot using urllib (no external dependencies)"""
        try:
            # Get Discord bot webhook URL from environment
            discord_bot_url = os.getenv('DISCORD_BOT_WEBHOOK_URL')
            
            if not discord_bot_url:
                print("⚠️ DISCORD_BOT_WEBHOOK_URL not set, falling back to manual")
                return False
            
            # Extract Discord ID from state
            discord_id = state.split('_')[0] if state and '_' in state else 'unknown'
            
            # Prepare webhook data
            webhook_data = {
                'discord_user_id': discord_id,
                'auth_code': code,
                'state': state,
                'source': 'vercel_oauth_server',
                'timestamp': 'auto_processed'
            }
            
            # Send using urllib (no external dependencies)
            data = json.dumps(webhook_data).encode('utf-8')
            req = urllib.request.Request(
                discord_bot_url,
                data=data,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Anasi-OAuth-Server/1.0'
                },
                method='POST'
            )
            
            # Make request with timeout
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    print(f"✅ Successfully sent OAuth code to Discord bot for user {discord_id}")
                    return True
                else:
                    print(f"⚠️ Discord bot responded with status {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error sending to Discord bot: {e}")
            return False
    
    def send_automatic_success_page(self, code, state):
        """Success page for automatic processing"""
        discord_id = state.split('_')[0] if state and '_' in state else 'unknown'
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>✅ Anasi - Automatically Connected!</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #00ff87 0%, #60efff 100%);
                    margin: 0; padding: 0; display: flex; justify-content: center;
                    align-items: center; min-height: 100vh;
                }}
                .container {{
                    background: white; padding: 3rem; border-radius: 20px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1); text-align: center;
                    max-width: 500px; margin: 20px; animation: slideIn 0.5s ease-out;
                }}
                @keyframes slideIn {{
                    from {{ opacity: 0; transform: translateY(-30px); }}
                    to {{ opacity: 1; transform: translateY(0); }}
                }}
                .success-icon {{ font-size: 5rem; color: #00ff87; margin-bottom: 1rem; }}
                h1 {{ color: #333; margin-bottom: 1rem; font-size: 2.2rem; }}
                .auto-message {{
                    background: #e8f5e8; border: 2px solid #00ff87; border-radius: 12px;
                    padding: 25px; margin: 25px 0; font-size: 18px;
                }}
                .status-check {{
                    background: #f0f9ff; border-left: 4px solid #0ea5e9;
                    padding: 20px; margin-top: 1.5rem; border-radius: 8px;
                    text-align: left;
                }}
                .close-btn {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; border: none; padding: 15px 30px; border-radius: 12px;
                    cursor: pointer; font-size: 1.1rem; margin-top: 1.5rem;
                    transition: transform 0.2s ease;
                }}
                .close-btn:hover {{ transform: translateY(-2px); }}
                .spinner {{
                    border: 3px solid #f3f3f3; border-top: 3px solid #00ff87;
                    border-radius: 50%; width: 30px; height: 30px;
                    animation: spin 1s linear infinite; margin: 0 auto 15px;
                }}
                @keyframes spin {{
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}
                .checkmark {{
                    color: #00ff87; font-size: 1.2em; margin-right: 8px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-icon">🎉</div>
                <h1>🤖 Automatically Connected!</h1>
                <p style="font-size: 1.3rem; color: #666; margin-bottom: 2rem;">
                    Your Twitch account is being linked automatically
                </p>
                
                <div class="auto-message">
                    <div class="spinner"></div>
                    <strong>✨ Magic in Progress!</strong><br>
                    Your authorization was sent directly to your Discord bot.<br>
                    <strong>No manual steps required!</strong>
                </div>
                
                <div class="status-check">
                    <strong>🎯 What's Happening Right Now:</strong><br><br>
                    <span class="checkmark">✅</span><strong>Twitch authorized</strong> your account<br>
                    <span class="checkmark">🔄</span><strong>Anasi is processing</strong> your connection<br>
                    <span class="checkmark">💬</span><strong>Discord notification</strong> incoming...<br>
                    <span class="checkmark">🚀</span><strong>Ready to monitor</strong> streamers in ~5 seconds!
                </div>
                
                <div style="margin-top: 2rem; padding: 20px; background: #fff3cd; border-radius: 12px; border: 1px solid #ffeaa7;">
                    <strong>🎮 What's Next:</strong><br>
                    Return to Discord and use <code>/monitor &lt;streamer&gt;</code> to start monitoring viral moments!
                </div>
                
                <button class="close-btn" onclick="window.close()">🔙 Return to Discord</button>
                
                <p style="margin-top: 1.5rem; font-size: 0.9rem; color: #888;">
                    Professional OAuth • Powered by Vercel + Railway
                </p>
            </div>
            
            <script>
                // Auto-close after 10 seconds
                setTimeout(function() {{
                    window.close();
                }}, 10000);
                
                // Update status after 3 seconds
                setTimeout(function() {{
                    var statusDiv = document.querySelector('.status-check');
                    statusDiv.innerHTML = `
                        <strong>🎯 Processing Complete:</strong><br><br>
                        <span class="checkmark">✅</span><strong>Twitch authorized</strong> your account<br>
                        <span class="checkmark">✅</span><strong>Anasi processed</strong> your connection<br>
                        <span class="checkmark">✅</span><strong>Discord notification</strong> sent<br>
                        <span class="checkmark">✅</span><strong>Ready to monitor</strong> streamers!
                    `;
                }}, 3000);
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_manual_fallback_page(self, code, state):
        """Fallback manual page if automatic fails"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>⚠️ Anasi - Manual Connection Required</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #ffa726 0%, #fb8c00 100%);
                    margin: 0; padding: 0; display: flex; justify-content: center;
                    align-items: center; min-height: 100vh;
                }}
                .container {{
                    background: white; padding: 2.5rem; border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3); text-align: center;
                    max-width: 550px; margin: 20px;
                }}
                .warning-icon {{ font-size: 4rem; color: #ff9800; margin-bottom: 1rem; }}
                h1 {{ color: #333; margin-bottom: 1rem; }}
                .code-box {{
                    background: #f8f9fa; border: 3px solid #ff9800; border-radius: 12px;
                    padding: 20px; margin: 20px 0; font-family: 'Courier New', monospace;
                    word-break: break-all; font-size: 14px; cursor: pointer;
                    font-weight: bold; max-height: 120px; overflow-y: auto;
                    line-height: 1.4;
                }}
                .code-box:hover {{
                    background: #e9ecef; border-color: #e65100;
                }}
                .instructions {{
                    background: #fff3e0; padding: 20px; border-radius: 12px;
                    margin-top: 1.5rem; border-left: 4px solid #ff9800;
                    text-align: left;
                }}
                .copy-btn {{
                    background: #ff9800; color: white; border: none;
                    padding: 15px 30px; border-radius: 10px; cursor: pointer;
                    margin: 15px 5px; font-size: 16px; transition: all 0.2s;
                    font-weight: bold;
                }}
                .copy-btn:hover {{ background: #e65100; transform: translateY(-2px); }}
                .close-btn {{
                    background: #6c757d; color: white; border: none;
                    padding: 12px 24px; border-radius: 8px; cursor: pointer;
                    margin-top: 20px; font-size: 14px;
                }}
                .step {{ margin: 8px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="warning-icon">⚠️</div>
                <h1>Manual Connection Required</h1>
                <p style="font-size: 1.1rem; color: #666;">
                    Automatic processing is temporarily unavailable.<br>
                    Please complete the connection manually:
                </p>
                
                <div class="code-box" onclick="selectCode()" title="Click to select authorization code">
                    {code}
                </div>
                
                <button class="copy-btn" onclick="copyCode()">📋 Copy Authorization Code</button>
                
                <div class="instructions">
                    <strong>📋 Manual Connection Steps:</strong><br><br>
                    <div class="step"><strong>1.</strong> Copy the authorization code above ⬆️</div>
                    <div class="step"><strong>2.</strong> Return to Discord</div>
                    <div class="step"><strong>3.</strong> Use this command: <code>/complete &lt;paste-code-here&gt;</code></div>
                    <div class="step"><strong>4.</strong> Your account will be linked instantly!</div>
                </div>
                
                <button class="close-btn" onclick="window.close()">🔙 Close This Tab</button>
                
                <p style="margin-top: 1.5rem; font-size: 0.9rem; color: #888;">
                    Don't worry - manual connection works just as well! 👍
                </p>
            </div>
            
            <script>
                function selectCode() {{
                    var codeBox = document.querySelector('.code-box');
                    if (window.getSelection && document.createRange) {{
                        var range = document.createRange();
                        range.selectNodeContents(codeBox);
                        var selection = window.getSelection();
                        selection.removeAllRanges();
                        selection.addRange(range);
                    }}
                }}
                
                function copyCode() {{
                    var code = "{code}";
                    if (navigator.clipboard && navigator.clipboard.writeText) {{
                        navigator.clipboard.writeText(code).then(function() {{
                            var btn = document.querySelector('.copy-btn');
                            var originalText = btn.textContent;
                            btn.textContent = '✅ Copied to Clipboard!';
                            btn.style.background = '#4caf50';
                            setTimeout(function() {{
                                btn.textContent = originalText;
                                btn.style.background = '#ff9800';
                            }}, 2500);
                        }}).catch(function() {{
                            selectCode();
                            alert('Code selected! Press Ctrl+C (or Cmd+C on Mac) to copy.');
                        }});
                    }} else {{
                        selectCode();
                        alert('Code selected! Press Ctrl+C (or Cmd+C on Mac) to copy.');
                    }}
                }}
                
                // Auto-select code on page load for easier copying
                window.onload = function() {{
                    selectCode();
                }};
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
            <title>❌ Anasi - Connection Error</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
                    margin: 0; padding: 20px; display: flex; justify-content: center;
                    align-items: center; min-height: 100vh;
                }}
                .container {{ 
                    background: white; padding: 2.5rem; border-radius: 15px; 
                    max-width: 450px; margin: 0 auto; text-align: center;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                }}
                .error-icon {{ font-size: 4rem; color: #dc3545; margin-bottom: 1rem; }}
                h1 {{ color: #333; margin-bottom: 1rem; }}
                .error-message {{ 
                    background: #f8d7da; padding: 20px; border-radius: 12px; 
                    color: #721c24; margin: 20px 0; border: 1px solid #f5c6cb;
                    font-weight: bold;
                }}
                .retry-info {{
                    background: #e3f2fd; padding: 15px; border-radius: 8px;
                    margin-top: 1rem; color: #0d47a1;
                }}
                .retry-btn {{
                    background: #007bff; color: white; border: none;
                    padding: 15px 30px; border-radius: 10px; cursor: pointer;
                    margin-top: 20px; font-size: 16px; text-decoration: none;
                    display: inline-block; font-weight: bold;
                }}
                .retry-btn:hover {{ background: #0056b3; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error-icon">❌</div>
                <h1>Connection Failed</h1>
                <div class="error-message">{error_message}</div>
                
                <div class="retry-info">
                    <strong>🔄 What to do next:</strong><br><br>
                    1. Go back to Discord<br>
                    2. Use <code>/connect</code> to try again<br>
                    3. If the problem persists, the manual method always works!
                </div>
                
                <p style="margin-top: 1.5rem; font-size: 0.9rem; color: #666;">
                    This is usually a temporary issue and resolves quickly.
                </p>
            </div>
        </body>
        </html>
        """
        
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())