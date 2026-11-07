# Data and documentation license

Jason Godfrey, University of Michigan, jgod@umich.edu.

The derived numerical features, scores, embeddings, axis definitions and anchors, validation packets and ratings, analysis outputs, and release documentation are offered under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/), to the extent rights exist and are held by the releaser. Attribute Jason Godfrey and cite the accompanying paper. Software is separately licensed under the MIT license in LICENSE within the code snapshot.

The anchor descriptions were constructed by synthesizing features across several examples; see the release's ANCHORS and PROVENANCE documentation. Any third-party expression remains outside this license grant.

Paper titles and the public author names in the searchable explorer are included as bibliographic metadata and are **not covered by our CC BY 4.0 grant**. The release does not grant rights in third-party materials. Abstracts, abstract sentences, excerpts, cached HTML, PDFs and BibTeX are not redistributed. In the dataset, paper-author names appear only in the searchable explorer's embedded JSON; CSVs and processed corpus metadata omit them. Official proceedings links and the reviewed title/abstract SHA-256 hashes are retained. The included MIT-licensed code snapshot also contains searchable previews and a documented four-record author backfill sidecar used to build the explorer. Numerical embeddings do not license the underlying text. The [NeurIPS copyright policy](https://neurips.cc/FAQ/Copyright) describes the source papers' rights; authors retain their copyright. See also [US Copyright Office Circular 33](https://www.copyright.gov/circs/circ33.pdf) concerning titles.

Encoder weights are not bundled. Models used: `sentence-transformers/all-MiniLM-L6-v2` (Apache-2.0), `sentence-transformers/allenai-specter` (Apache-2.0), and `BAAI/bge-small-en-v1.5` (MIT).

LLM-agent ratings were generated using the author's personal Claude and OpenAI accounts for construct-validity research, as confirmed by the author during release preparation. Their applicable service terms govern those services. Purely machine-generated outputs may not be copyrightable; this grant applies only to rights the releaser holds. This notice does not assert a particular historical subscription plan or contract. Rater identities and missing model provenance are documented in RATERS.md.

## Intended use and limitations

The audit supports aggregate year, track and topic-neighborhood analysis of public evidence framing in accepted NeurIPS papers and reproduction of the accompanying study. Per-paper scores are noisy measurements of how a title and abstract frame evidence, not judgments of paper quality. They should not be used to judge or rank individual papers, authors, labs, tracks or subfields; infer author intent; or approximate private reviewer judgments. These scientific use recommendations do not impose additional restrictions on the CC BY 4.0 license.
