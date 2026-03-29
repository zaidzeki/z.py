# DESIGN

## Bundle mode format

Each file entry is written sequentially as:

1. `path_len`: 16-bit unsigned integer (big-endian)
2. `path`: UTF-8 bytes
3. `data_len`: 32-bit unsigned integer (big-endian)
4. `data`: raw file bytes

Directory inputs are supported only with `recursively=True`; extracted files are restored relative to the output directory.
