import os
import requests
from PIL import Image
from io import BytesIO

# Create logos directory if it doesn't exist
os.makedirs('static/logos', exist_ok=True)

# NFL team logos with their names
team_logos = {
    'arizona-cardinals': 'https://static.www.nfl.com/image/private/f_auto/league/u9fltoslqdsyao8cpm0k',
    'atlanta-falcons': 'https://static.www.nfl.com/image/private/f_auto/league/d8m7hzpsbrl6pnqht8op',
    'baltimore-ravens': 'https://static.www.nfl.com/image/private/f_auto/league/ucsdijmddsqcj1i9tddd',
    'buffalo-bills': 'https://static.www.nfl.com/image/private/f_auto/league/giphcy6ie9mxbnldntsf',
    'carolina-panthers': 'https://static.www.nfl.com/image/private/f_auto/league/ervfzgrqdpnc7lh5gqwq',
    'chicago-bears': 'https://static.www.nfl.com/image/private/f_auto/league/ra0poq2ivwyahbaq86d2',
    'cincinnati-bengals': 'https://static.www.nfl.com/image/private/f_auto/league/okxpteoliyayufypqalq',
    'cleveland-browns': 'https://static.www.nfl.com/image/private/f_auto/league/fgbn7asx2r4lwkdxmljnvzjdm',
    'dallas-cowboys': 'https://static.www.nfl.com/image/private/f_auto/league/ieid8hoygzdlmzg5pxlw',
    'denver-broncos': 'https://static.www.nfl.com/image/private/f_auto/league/t0p7m5cjdjy18rnzzqbx',
    'detroit-lions': 'https://static.www.nfl.com/image/private/f_auto/league/ocvxwnapdvwevupe4tpr',
    'green-bay-packers': 'https://static.www.nfl.com/image/private/f_auto/league/gppfvr7n8gljgjaqux2x',
    'houston-texans': 'https://static.www.nfl.com/image/private/f_auto/league/bpx88i8nw4nnabuq0oob',
    'indianapolis-colts': 'https://static.www.nfl.com/image/private/f_auto/league/ketwqeuschqzjsllbid5',
    'jacksonville-jaguars': 'https://static.www.nfl.com/image/private/f_auto/league/qycbib6ivrm9dqaexryk',
    'kansas-city-chiefs': 'https://static.www.nfl.com/image/private/f_auto/league/ujshjqvmnxce8m4obmvs',
    'las-vegas-raiders': 'https://static.www.nfl.com/image/private/f_auto/league/gzcojbzcyjgubgyb6xf2',
    'los-angeles-chargers': 'https://static.www.nfl.com/image/private/f_auto/league/ayvwcmluj2ohkdlbiegi',
    'los-angeles-rams': 'https://static.www.nfl.com/image/private/f_auto/league/ayvwcmluj2ohkdlbiegi',
    'miami-dolphins': 'https://static.www.nfl.com/image/private/f_auto/league/lits6p8ycthy9to70bnt',
    'minnesota-vikings': 'https://static.www.nfl.com/image/private/f_auto/league/teguylrnqqmfcwxvcmmz',
    'new-england-patriots': 'https://static.www.nfl.com/image/private/f_auto/league/moyfxx3dq5pio4aiftnc',
    'new-orleans-saints': 'https://static.www.nfl.com/image/private/f_auto/league/grhjkahghjkk17v43hdx',
    'new-york-giants': 'https://static.www.nfl.com/image/private/f_auto/league/t6mhdmgizi6qhndh8b9p',
    'new-york-jets': 'https://static.www.nfl.com/image/private/f_auto/league/ekijosiae96gektbo4iw',
    'philadelphia-eagles': 'https://static.www.nfl.com/image/private/f_auto/league/puhrqgj71gobgdkdo6uq',
    'pittsburgh-steelers': 'https://static.www.nfl.com/image/private/f_auto/league/xujg9t3t4u5nmjgr54wx',
    'san-francisco-49ers': 'https://static.www.nfl.com/image/private/f_auto/league/dxibuyxbk0b9ua5ih9hn',
    'seattle-seahawks': 'https://static.www.nfl.com/image/private/f_auto/league/gcytzwpjdzbpwnwxincg',
    'tampa-bay-buccaneers': 'https://static.www.nfl.com/image/private/f_auto/league/v8uqiualryypwqgvwcih',
    'tennessee-titans': 'https://static.www.nfl.com/image/private/f_auto/league/pln44vuzugjgipyidsre',
    'washington-commanders': 'https://static.www.nfl.com/image/private/f_auto/league/xymxwrxtyj9fhaemhdyd'
}

# Download and save each logo
for team_name, logo_url in team_logos.items():
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

print("Logo download complete!")
