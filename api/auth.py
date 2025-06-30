from http.server import BaseHTTPRequestHandler
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle OAuth callbacks from Discord and Twitch"""
        
        # Parse the URL and query parameters
        url_parts = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(url_parts.query)
        
        # Get parameters
        code = query_params.get('code', [None])[0]
        state = query_params.get('state', [None])[0]
        error = query_params.get('error', [None])[0]
        
        if error:
            self.send_error_page(f"Authorization error: {error}")
            return
        
        if not code:
            self.send_error_page("Missing authorization code")
            return
        
        # Determine if this is Discord or Twitch callback based on path
        if url_parts.path == '/api/auth/discord':
            self.handle_discord_callback(code, state)
        elif url_parts.path == '/api/auth/twitch':
            self.handle_twitch_callback(code, state)
        else:
            self.send_error_page("Invalid callback endpoint")
    
    def handle_discord_callback(self, code, state):
        """Handle Discord OAuth callback - redirect to Twitch"""
        try:
            # Extract Discord user info from state (discord_id_username format)
            discord_info = state if state else "unknown_user"
            
            # Generate Twitch OAuth URL
            twitch_oauth_url = self.generate_twitch_oauth_url(discord_info)
            
            # Redirect to Twitch OAuth
            self.send_response(302)
            self.send_header('Location', twitch_oauth_url)
            self.end_headers()
            
        except Exception as e:
            self.send_error_page(f"Discord callback error: {str(e)}")
    
    def handle_twitch_callback(self, code, state):
        """Handle Twitch OAuth callback - show success"""
        try:
            # Show success page
            self.send_success_page(state, code)
            
        except Exception as e:
            self.send_error_page(f"Twitch callback error: {str(e)}")
    
    def generate_twitch_oauth_url(self, discord_info):
        """Generate Twitch OAuth URL"""
        state = f"twitch_{discord_info}"
        
        params = {
            'response_type': 'code',
            'client_id': 'ccaxnoh0txxw0iulm4fxvq81km1dnd',  # Your Twitch Client ID
            'redirect_uri': 'https://asi-oauth-server.vercel.app/api/auth/twitch',
            'scope': 'clips:edit chat:read bits:read channel:read:redemptions',
            'state': state,
            'force_verify': 'true'
        }
        
        query_string = urllib.parse.urlencode(params)
        return f"https://id.twitch.tv/oauth2/authorize?{query_string}"
    
    def send_success_page(self, state, code):
        """Send success page with connection details"""
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
                    background: #f8f9fa; border: 2px solid #28a745; border-radius: 8px;
                    padding: 15px; margin: 20px 0; font-family: monospace;
                    word-break: break-all; font-size: 14px;
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
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-icon">✅</div>
                <h1>Successfully Connected!</h1>
                <p>Your Twitch account has been linked to Anasi</p>
                
                <div class="code-box">
                    <strong>Authorization Code:</strong><br>
                    {code}
                </div>
                
                <div class="instructions">
                    <strong>🎯 Next Steps:</strong><br>
                    1. Copy the authorization code above<br>
                    2. Go back to Discord<br>
                    3. Use <code>/complete &lt;code&gt;</code> with that code<br>
                    4. Start monitoring with <code>/monitor &lt;streamer&gt;</code>
                </div>
                
                <button class="close-btn" onclick="window.close()">Close Tab</button>
            </div>
            
            <script>
                // Auto-select code for easy copying
                document.querySelector('.code-box').addEventListener('click', function() {{
                    var range = document.createRange();
                    range.selectNode(this);
                    window.getSelection().removeAllRanges();
                    window.getSelection().addRange(range);
                }});
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
