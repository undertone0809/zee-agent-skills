# flomo Export DOM Assumptions

This skill expects the standard flomo export HTML structure.

## Required selectors

- `.user .name`: exported account name (e.g. `@Zeeland`)
- `.memo`: one memo container per note
- `.memo .time`: timestamp text (`YYYY-MM-DD HH:MM:SS`)
- `.memo .content`: memo rich-text HTML

## Attachment selectors

The script scans direct `.files` containers under each `.memo` and extracts attachment paths that start with `file/` from:

- `img[src]`
- `audio[src]`
- `video[src]`
- `source[src]`
- `a[href]`

## Notes

- Some exports include multiple `.files` containers per memo; the script deduplicates attachments by `(kind, path)`.
- Audio transcript blocks (e.g. `.audio-player__content`) are intentionally ignored in this version.
- Folder input mode is strict: the folder must contain exactly one `.html` file at the top level.
