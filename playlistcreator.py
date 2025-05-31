from flask import Flask, request, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

CLIENT_ID = '14ffb593a0634a4cbaa3e6acb5e302cd'
CLIENT_SECRET = '9bf9d56d9d22472d9d20bfd77f6b9f19'
REDIRECT_URI = 'https://localhost:8888/callback'
SCOPE = 'playlist-modify-public'

sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        redirect_uri=REDIRECT_URI,
                        scope=SCOPE)

@app.route('/')
def login():
    return redirect(sp_oauth.get_authorize_url())

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    sp = spotipy.Spotify(auth=token_info['access_token'])

    # Puedes cambiar aquí el nombre del artista
    artist_name = request.args.get('artist', default='Bad Bunny')  
    user_id = sp.me()['id']

    # Buscar artista
    results = sp.search(q=f'artist:{artist_name}', type='artist')
    items = results['artists']['items']
    if not items:
        return 'Artista no encontrado.'
    artist_id = items[0]['id']

    # Obtener canciones
    track_ids = []
    albums = sp.artist_albums(artist_id, album_type='album,single', limit=50)
    seen = set()

    for album in albums['items']:
        if album['id'] in seen:
            continue
        seen.add(album['id'])
        tracks = sp.album_tracks(album['id'])
        for track in tracks['items']:
            track_ids.append(track['id'])

    # Crear playlist
    playlist = sp.user_playlist_create(user_id, f"Todas las de {artist_name}", public=True)

    for i in range(0, len(track_ids), 100):
        sp.playlist_add_items(playlist['id'], track_ids[i:i+100])

    return f"""
        ✅ Playlist creada:<br>
        <a href="{playlist['external_urls']['spotify']}" target="_blank">{playlist['name']}</a><br><br>
        👉 Puedes probar con otro artista: <code>?artist=Drake</code>
    """

if __name__ == '__main__':
    app.run(port=8888)
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Render usa PORT dinámico
    app.run(host='0.0.0.0', port=port)
