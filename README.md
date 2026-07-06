# Israeli Artist Co-Performance Network

An interactive map of Hebrew-song performers, built from the
[Hebrew Songs Lyrics](https://www.kaggle.com/datasets/guybarash/hebrew-songs-lyrics)
Kaggle dataset.

**Nodes** are artists; **an edge** connects two artists who perform the same song
(identical title + lyrics), **weighted** by how many songs they share. 

## View it

Open **[`index.html`](index.html)** in any browser — or, once published, the GitHub Pages URL:

> 🔗 Live: _<https://neta-sp.github.io/israeli-singers-network/>_

## Data
- [`artist_network_nodes.csv`](artist_network_nodes.csv) — one row per artist:
  `artist_key`, `partners`, `shared_songs_total`, `community`
- [`artist_network_edges.csv`](artist_network_edges.csv) — one row per pair:
  `artist_key_1`, `artist_key_2`, `shared_songs`

Artists are identified by `artist_key`; Hebrew display names are used only for the on-screen
labels.
