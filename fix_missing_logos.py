import os
import requests
from PIL import Image
from io import BytesIO

# Missing team logos
missing_logos = {
    'cleveland-browns': 'https://static.www.nfl.com/image/private/f_auto/league/vwbgsmkpbgdvpkj4mfgn',
    'dallas-cowboys': 'https://static.www.nfl.com/image/private/f_auto/league/havlcpqxcm7vxwqrq63m'
}

# Download and save each logo
for team_name, logo_url in missing_logos.items():
    try:
        response = requests.get(logo_url)
        if response.status_code == 200:
            # Open the image and convert to PNG
            img = Image.open(BytesIO(response.content))
            
            # Save as PNG
            output_path = f'static/logos/{team_name}.png'
            img.save(output_path, 'PNG')
            print(f"Downloaded {team_name} logo to {output_path}")
        else:
            print(f"Failed to download {team_name} logo: HTTP {response.status_code}")
    except Exception as e:
        print(f"Error downloading {team_name} logo: {e}")

print("Logo fix complete!")
