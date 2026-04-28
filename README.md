# metafunctor-data

Public data substrate for participation features on metafunctor.com.

Apps live as path-namespaced subdirectories. Currently:

- `jigsaw/`: weekly AI-generated jigsaw puzzles. New `YYYY-Www/` directory each Monday via the GitHub Actions cron in `.github/workflows/jigsaw-weekly.yml`. Browser at https://metafunctor.com/arcade/jigsaw places pieces by committing here via the [git-native](https://github.com/queelius/git-native) library.

The commit log is the record. Anyone can clone this repo at any time.

## Configuration

Required for the weekly cron in `.github/workflows/jigsaw-weekly.yml`:

| Setting | Type   | Default          | Notes |
|---------|--------|------------------|-------|
| `OPENAI_API_KEY`    | secret | (none, required)  | API key for OpenAI or any OpenAI-compatible endpoint |
| `OPENAI_BASE_URL`   | var    | (unset = api.openai.com) | Override to point at a self-hosted endpoint |
| `OPENAI_IMAGE_MODEL`| var    | `gpt-image-1`     | Model name; must be supported by the endpoint |

Set in repo: Settings, then Secrets and variables, then Actions.
