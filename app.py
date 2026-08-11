"""
ShopEasy - Main Application Entry Point
Lab 1: Amazon EBS - Persistent Block Storage
"""

from shopeasy import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=False)
