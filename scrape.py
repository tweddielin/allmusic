import pandas as pd
import allmusic
import os

if os.path.isfile('data/genres.csv'):
    print('genre dic exists')
    genre_df = pd.read_csv('data/genres.csv')
else:
    genre_df = allmusic.get_allgenre()

target_genre = 'jazz'
criterion = genre_df['genre'].map(lambda x: target_genre.lower() in x.lower())
genre_df = genre_df[criterion]

#df = allmusic.scrape_albums(genre_df.iloc[1:3])

df = genre_df.iloc[7:9]

for idx, row in df.iterrows():
    genre_name = row['genre']
    genre_id = row['subgenre_id']

    allmusic.scrape_albums(genre_name, genre_id)


