# Evidence Norms Atlas

[Open the interactive Atlas](https://ja-godfrey.github.io/evidence-norms-atlas/) · [Paper](https://openreview.net/forum?id=d3J7bxCLHH) · [Data and reproduction code](https://www.kaggle.com/datasets/jasongodfrey/neurips-evidence-framing-audit/versions/4)

Jason Godfrey, University of Michigan.

This is the public web companion to **Auditing Evidence Framing at NeurIPS: A Decade-Scale Study of Accepted Papers**. It explores the titles and abstracts of 19,361 accepted NeurIPS papers from 2015–2024 through an animated introduction, annual evidence-framing profiles, title/author search, and interactive paper maps. The site distributes bibliographic metadata and derived measurements; it does not redistribute abstracts or excerpts.

## Scope

These are measurements of public evidence framing, not research quality, author intent, reviewer preferences, or acceptance standards. Individual scores are noisy and must not be used to rank papers, authors, labs, tracks, or subfields. The paper documents topic-composition effects, instrument sensitivity, and limits on transfer beyond the studied corpus.

## Source and reproduction

The Atlas assets come from the already published `reproducibility-code/atlas/` snapshot in Kaggle version 4. Embedded scientific data are unchanged. Hosting adds a landing-page title, research links, metadata, and an entry-point alias. `PROVENANCE.json` records the original asset hashes and the unchanged embedded payloads.

Kaggle version 4 remains the paper's fixed data-and-reproduction-code release, including validation outputs and complete reproduction instructions. This repository contains the web presentation. Cite the accompanying paper when using the resource.

## Run locally

Open `index.html` in a current browser, or run `python3 -m http.server 8000` in this directory and visit `http://localhost:8000`. No build step or account is required to explore the site.

GitHub Pages serves the `main` branch root; `.nojekyll` preserves these static files. The desktop animation is 16:9; the mobile animation is 9:16. Annual and paper profiles, search, and maps run in the browser.

## License

Software is MIT-licensed; see [LICENSE](LICENSE). Derived data and documentation are CC BY 4.0 to the extent rights are held by the releaser; see [DATA_LICENSE.md](DATA_LICENSE.md). Paper titles and public author names are bibliographic metadata outside that license grant. Third-party rights remain with their holders.
