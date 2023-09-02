import requests

# Gets candidates (album, year, track number) for the track
def get_track_info(artist, title):
    # MusicBrainz API request URL
    url = f"https://musicbrainz.org/ws/2/recording/?query=artist:{artist} AND recording:{title}&fmt=json"
    
    # User-Agent header (because they requested nicely)
    headers = {
        "User-Agent": "XPrimental/0.0.1 ( your_mail@gmail.com )"
    }
    
    # API request
    response = requests.get(url, headers=headers)
    data = response.json()

    # Extract candidates for: album, year, track
    albums = []
    if 'recordings' in data:
        recording_info = data['recordings']
        for recording in recording_info:
            received_title = recording.get('title', "Unknown")
            received_artist = recording.get('artist-credit', [{}])[0].get('artist', {}).get('name', "Unknown")
            
            if received_title.lower() != title.lower():
                # print(f"Skipping because of title mismatch ({title} != {received_title})")
                continue
            
            if received_artist.lower() != artist.lower():
                # print(f"Skipping because of artist mismatch ({artist} != {received_artist})")
                continue
            # print(f" !!! Not Skipping. artist: {received_artist}, title: {received_title}")
            release_list = recording.get('releases', [])
            for release in release_list:
                if release.get('title'):
                    album = release.get('title')
                    year  = int(release.get('date', '0').split('-')[0]) if release.get('date', '0').split('-')[0] else 0
                    track = int(release.get('media', [{}])[0].get('track-offset', 0)) + 1
                    albums.append((album, year, track))
    return list(set(albums))

# Auxilary function to get group_id (used for album art)
def get_release_group_id(artist, album):
    try:
        
        # TODO - Add wanted header
        url = f"https://musicbrainz.org/ws/2/release/?query=artist:{artist} AND release:{album}&fmt=json"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if 'releases' in data and data['releases']:
            release = data['releases'][0]
            if 'release-group' in release:
                return release['release-group']['id']
        return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def download_album_artwork(artist, album, filepath):
    release_group_id = get_release_group_id(artist, album)
    url = f"https://coverartarchive.org/release-group/{release_group_id}/front"
    
    try:
        # TODO - Add wanted header
        response = requests.get(url)
        if response.status_code == 200:
            with open(filepath, 'wb') as file:
                file.write(response.content)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")




def main():
    artist = "Skillet"
    track = "Dominion"

    track_info = get_track_info(artist, track)
    print(f"Possible album, year, track for \"{artist} - {track}\":")
    print(track_info)
    index = int(input("Correct choice: "))
    
    # print("\n------------------")

    groupid = get_release_group_id(artist, track_info[index][0])
    download_album_artwork(groupid, "C:\\Temp\\DOMinion.png")
    

if __name__ == "__main__":
    main()
