# metafunctor-data

Public data substrate for participation features on metafunctor.com.

Apps live as path-namespaced subdirectories. Currently:

- `jigsaw/`: weekly AI-generated jigsaw puzzles. New `YYYY-Www/` directory each Monday via the GitHub Actions cron in `.github/workflows/jigsaw-weekly.yml`. Browser at https://metafunctor.com/arcade/jigsaw places pieces by committing here via the [git-native](https://github.com/queelius/git-native) library.

The commit log is the record. Anyone can clone this repo at any time.
