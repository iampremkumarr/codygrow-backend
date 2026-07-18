import requests
import os

def test_upload():
    url = "http://localhost:8000/api/dataset/upload"
    
    # Create a test CSV file
    test_data = """id,name,age
1,John,25
2,Jane,30
3,Bob,35"""
    
    with open("test_upload.csv", "w") as f:
        f.write(test_data)
    
    # Test the upload
    try:
        with open("test_upload.csv", "rb") as f:
            files = {"file": ("test_upload.csv", f, "text/csv")}
            response = requests.post(url, files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Upload successful!")
            print(f"Response JSON: {response.json()}")
        else:
            print("❌ Upload failed")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Clean up
    if os.path.exists("test_upload.csv"):
        os.remove("test_upload.csv")

if __name__ == "__main__":
    test_upload()