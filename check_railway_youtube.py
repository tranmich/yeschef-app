"""
Check if Railway has YouTube integration deployed
"""
import requests
import time

RAILWAY_URL = "https://yeschefapp-production.up.railway.app"

def check_railway_deployment():
    print("="*80)
    print("🚂 CHECKING RAILWAY DEPLOYMENT STATUS")
    print("="*80)
    
    # Check health endpoint
    print(f"\n📡 Checking {RAILWAY_URL}/api/health...")
    try:
        response = requests.get(f"{RAILWAY_URL}/api/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            print("✅ Railway server is responding")
            print(f"\n📊 Capabilities:")
            for key, value in health.get('capabilities', {}).items():
                status = "✅" if value else "❌"
                print(f"   {status} {key}: {value}")
            
            if health.get('capabilities', {}).get('recipe_import'):
                print("\n✅ Recipe import is enabled!")
            else:
                print("\n⚠️  Recipe import is disabled")
                
        else:
            print(f"⚠️  Server responded with status {response.status_code}")
    except requests.exceptions.Timeout:
        print("❌ Server timeout - may still be deploying")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*80)
    print("📱 TESTING YOUTUBE URL IMPORT")
    print("="*80)
    print("\n⚠️  Note: This requires authentication token")
    print("   The mobile app will handle authentication automatically")
    print(f"\n📍 When the mobile app sends a YouTube URL to:")
    print(f"   POST {RAILWAY_URL}/api/recipes/import/url")
    print(f"   {{\"url\": \"https://youtube.com/watch?v=VIDEO_ID\"}}")
    print(f"\n   The server should:")
    print("   1. Detect it's a YouTube URL")
    print("   2. Extract video metadata + transcript")
    print("   3. Parse with GPT-4")
    print("   4. Return structured recipe")
    
    print("\n" + "="*80)
    print("⏱️  DEPLOYMENT TIMING")
    print("="*80)
    print("\nRailway typically takes 2-3 minutes to deploy")
    print("Check the Railway dashboard for deployment status:")
    print("https://railway.app/project/YOUR_PROJECT_ID")
    
    print("\n✅ Once deployment completes:")
    print("   1. Try importing a YouTube video in the mobile app")
    print("   2. You should see:")
    print("      - Recipe title ✅")
    print("      - Full ingredients list ✅")
    print("      - Step-by-step instructions ✅")
    print("      - Source attribution ✅")

if __name__ == "__main__":
    check_railway_deployment()
    
    print("\n" + "="*80)
    print("🔄 Want to monitor deployment?")
    print("="*80)
    print("\nOption 1: Watch Railway dashboard")
    print("Option 2: Keep checking health endpoint:")
    print(f"   curl {RAILWAY_URL}/api/health")
    print("\nOption 3: Check deployment logs in Railway dashboard")
