# ElevenLabs MCP setup

Project-scoped config that connects Claude Code to the [ElevenLabs MCP server](https://github.com/elevenlabs/elevenlabs-mcp) (text-to-speech, voice cloning, transcription, and more).

## Requirements

- [`uv`](https://docs.astral.sh/uv/) (provides `uvx`)
- An ElevenLabs API key: https://elevenlabs.io/app/settings/api-keys

## Usage

The server is defined in `.mcp.json`, which reads the key from your environment,
so no secret is committed:

```bash
export ELEVENLABS_API_KEY="sk_..."
claude            # run from this directory; approve the "ElevenLabs" server when asked
```

Check it's connected with `/mcp` inside Claude Code, or `claude mcp list`.

### Alternative: add it just for you (user scope)

```bash
claude mcp add-json ElevenLabs --scope user \
  '{"command":"uvx","args":["elevenlabs-mcp"],"env":{"ELEVENLABS_API_KEY":"sk_..."}}'
```

This stores the key in `~/.claude.json` on your machine instead of this repo.

### Claude Code on the web

Add `ELEVENLABS_API_KEY` as an environment variable in your cloud environment's
settings, and make sure its network access allows PyPI and `api.elevenlabs.io`.
