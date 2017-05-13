import scrape
import pandas as pd
import allmusic

genre_df = allmusic.get_genre()

#df = allmusic.scrape_albums(genre_df.iloc[1:3])

df = genre_df.iloc[2:3]

for idx, row in df.iterrows():
    genre_name = row['genre']
    genre_id = row['subgenre_id']

    allmusic.scrape_albums(genre_name, genre_id)


