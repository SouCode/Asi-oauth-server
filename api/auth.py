from http.server import BaseHTTPRequestHandler
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse URL and query parameters
        url_parts = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(url_parts.query)
        
        # Get parameters
        code = query_params.get('code', [None])[0]
        state = query_params.get('state', [None])[0]
        error = query_params.get('error', [None])[0]
        
        if error:
            self.send_error_page(f"Authorization error: {error}")
            return
            
        if not code or not state:
            self.send_error_page("Missing authorization code or state")
            return
            
        # Show success for now
        self.send_success_page("Test User", "OAuth flow working!")
    
    def send_success_page(self, user, message):
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Anasi - Connected!</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>✅ {message}</h1>
            <p>OAuth server is working!</p>
            <p>Close this tab and return to Discord</p>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_error_page(self, error_message):
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Anasi - Error</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>❌ Error</h1>
            <p>{error_message}</p>
            <p>Return to Discord and try /connect again</p>
        </body>
        </html>
        """
        
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
