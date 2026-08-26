import sys
import os
import ee

# Add backend to path so we can import our settings
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.config.settings import settings

def test_gee_auth():
    print("Testing Earth Engine Authentication...")
    try:
        if settings.GEE_SERVICE_ACCOUNT_JSON:
            print(f"Using Service Account JSON: {settings.GEE_SERVICE_ACCOUNT_JSON}")
            credentials = ee.ServiceAccountCredentials(
                "", key_file=settings.GEE_SERVICE_ACCOUNT_JSON
            )
            ee.Initialize(credentials, project=settings.GEE_PROJECT_ID)
        else:
            print("No Service Account JSON found in settings. Make sure your .env is loaded.")
            return

        # Simple test query to Google Servers
        message = ee.String('Hello from the Google Earth Engine servers!').getInfo()
        print(f"\nSUCCESS! Response from Earth Engine: {message}")
        print("Your Service Account is perfectly configured.")
        
    except Exception as e:
        print(f"\nFAILED: {e}")

if __name__ == "__main__":
    test_gee_auth()
