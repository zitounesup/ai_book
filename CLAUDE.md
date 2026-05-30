# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Supporting code for [The Welch Labs Illustrated Guide to AI](https://www.welchlabs.com/ai-book).
It is **not a software package** — it is a collection of standalone Jupyter
notebooks that generate the figures, animations, and worked examples used in
the book, plus the data assets and rendering tooling behind them. There is no
application to build, no installable module, and no test suite. The "product"
is the notebooks and the visual artifacts they produce.

## Repository organization

Notebooks live at the repo root and are grouped by **book chapter via a numeric
filename prefix**. A chapter can have several notebooks (a main one plus
focused side examples); they are independent and meant to be run top-to-bottom.

| Prefix | Chapter topic |
|--------|---------------|
| `1_`   | Perceptron (incl. cats-vs-dogs classifier) |
| `2_`   | Gradient descent (and the `wormhole` loss-landscape example) |
| `3_`   | Backpropagation |
| `4_`   | Deep learning |
| `5_`   | AlexNet |
| `6_`   | Neural scaling laws (GPT-3/GPT-4 curves, MNIST scaling example) |
| `7_`   | Mechanistic interpretability |
| `8_`   | Attention (incl. DeepSeek example) |
| `9_`   | Diffusion / Stable Diffusion (DDPM, DDIM, CLIP, guidance, conditioning) |

Supporting directories:
- `exercises/` — reader exercise notebooks, named to mirror the chapter prefixes (`1_`, `2_`, `3_`, `8_`, `9_`).
- `data/` — image/asset inputs and saved artifacts consumed by notebooks: `.jpg/.png` images, `.pth` PyTorch weights (e.g. `2_1.pth`), and `.npy` arrays (e.g. `loss_landscape.npy`). Notebooks reference these by relative path, so run notebooks from the repo root.
- `tools/notebook_converter_1.ipynb` — renders notebooks into the book's styled SVG/PNG code listings and extracts output images. See below.
- `build_your_own_perceptron/` — hardware companion for chapter 1: a parts list (`perceptron_parts_list.csv`) and design files (`.ai`, `.png`) for a physical perceptron, not code.

## Environment & dependencies

- Python **3.11** (notebook kernels saved with 3.11.7).
- **There is no `requirements.txt` / `pyproject.toml`.** Dependencies are
  whatever each notebook imports; install per-notebook on demand. The
  recurring stack across notebooks is: `numpy`, `matplotlib`, `torch` /
  `torchvision`, `transformers`, `diffusers`, `huggingface_hub`, `tqdm`,
  `opencv-python` (`cv2`), `Pillow`, `pandas`, `plotly`, `einops`,
  `jaxtyping`. Specialized notebooks also use `transformer_lens` (ch. 7
  mech interp), `umap-learn` (embeddings viz), and `smalldiffusion` (ch. 9).
- Several notebooks load Hugging Face models/weights and are GPU-oriented
  (diffusion, attention, mech-interp); expect large downloads and CUDA use.

## Working with the notebooks

- Run notebooks from the repository root so relative `data/...` paths resolve.
- Execute a single notebook headless / regenerate its outputs:
  ```
  jupyter nbconvert --to notebook --execute --inplace <notebook>.ipynb
  ```
- These notebooks contain heavy embedded outputs (rendered images, base64
  plots) — that is why individual files reach multiple MB and why git diffs
  are large. Committed output is intentional (it feeds the book), so do **not**
  strip outputs unless explicitly asked.

## The notebook converter (book rendering)

`tools/notebook_converter_1.ipynb` is the pipeline that turns these notebooks
into the typeset code listings in the book. It defines the Welch Labs visual
style (e.g. `CHILL_BROWN='#948979'`, `SOLARIZED_BACKGROUND_COLOR='#fdf4e0'`,
fixed cell/canvas widths) and exposes:
- `process_jupyter_notebook(...)` — render a notebook to SVG (optionally split into sections).
- a PNG-extraction variant and `extract_and_save_output_images(...)` — pull output images out of a notebook into an asset directory.

Driver calls are kept commented out with author-specific absolute paths (the
book's design/asset folders). When using these helpers, supply your own
input/output paths rather than relying on those commented examples.

## Conventions

- Match the existing chapter-prefix naming when adding a notebook for a
  chapter (`<chapter#>_<short_name>.ipynb`), and put exercise variants under
  `exercises/` with the same prefix.
- Keep new input assets in `data/` and reference them by relative path.
- Code style is pedagogical/illustrative: prioritize clarity and matching the
  book's explanation over abstraction. There are no shared library modules —
  each notebook is self-contained.

## License

MIT (see `LICENSE`).
