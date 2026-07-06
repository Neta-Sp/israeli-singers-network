# Israeli Artist Co-Performance Network

An interactive map of Hebrew-song performers, built from the
[Hebrew Songs Lyrics](https://www.kaggle.com/datasets/guybarash/hebrew-songs-lyrics)
Kaggle dataset.

**Nodes** are artists; **an edge** connects two artists who perform the same song
(identical title + lyrics), **weighted** by how many songs they share. 

## View it

Open **[`index.html`](index.html)** in any browser — or, once published, the GitHub Pages URL:

> 🔗 Live: _<https://neta-sp.github.io/israeli-singers-network/>_

### Interactions
- **scroll** to zoom, **drag the background** to pan
- **drag a node** to pull it around (the layout is physics-based)
- **hover** a node for its name, community, number of partners, and total shared songs

### Legend
- **color** = community (clusters of artists who tend to share repertoire — roughly the
  Mizrahi, classic-rock/singer-songwriter, veteran-vocalist, contemporary-pop, and hip-hop
  scenes)
- **node size** = total shared songs (bigger = more co-performed)
- **edge thickness** = songs the two artists share

## Data
- [`artist_network_nodes.csv`](artist_network_nodes.csv) — one row per artist:
  `artist_key`, `partners`, `shared_songs_total`, `community`
- [`artist_network_edges.csv`](artist_network_edges.csv) — one row per pair:
  `artist_key_1`, `artist_key_2`, `shared_songs`

Artists are identified by `artist_key`; Hebrew display names are used only for the on-screen
labels.
