# Dream-loop meta (this product only)

Copy into **this product’s** `.dream-loop/meta.md`. Gitignore `.dream-loop/`. Never commit sqlite or round DBs.

Update every 5 rounds. One row per round. Do not mix another product’s scores.
For a failed crop gate, record score /10 as N/A and the composition failure; do not invent a full score.

| round | score /10 | kept? | change class | failure mode |
|------:|----------:|:-----:|:-------------|:-------------|
| 1 | | | camera \| massing \| material \| mesh | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

## Stall

If best score did not rise by a full point in 2 rounds: stop nibble, ask the user. Do not euler-hunt.

## Camera keep

Camera that last raised composition: (path or blend camera name)

If next round drops composition: revert that camera. Do not “fix” with euler.
