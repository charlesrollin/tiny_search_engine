# Tiny Search Engine

Information Retrieval project for class IS3013AA

### Table of Contents
+ **[Usage Instructions](#usage-instructions)**  
+ **[Architecture](#architecture)**  
+ **[Performances](#performances)**

## Usage Instructions

```bash
python3 main.py [-h] [-w WEIGHT] [-r] [-e] collection

positional arguments:
  collection            the collection to analyse, 'cs276' or 'cacm'

optional arguments:
  -h, --help            show this help message and exit
  -w WEIGHT, --weight WEIGHT
                        0: TfIdf
                        1: NormalizedTfIdf
                        2: NormalizedFrequency
                        3: PivotedDocumentLengthNormalization
                        4: BM25
                        5: ModifiedBM25
                        6: EvolutionaryLearnedScheme
                        7: DivergenceFromRandomness
                        8: AxiomaticScheme
  -r, --refresh         add this flag to force refresh of index
  -e, --evaluate        add this flag to launch engine evaluation
```

## Architecture

Describe global architecture here & pertinent details.

### Global architecture

#### Index Construction

Constructing the inverted index requires 3 steps:
* Parse: build a simple inverted index for each "block" of the collection
* Merge: merge the block indexes and collect statistics on collection
* Refine: use the statistics to refine the index with weights

Below is the class diagram for the Index Construction Module:

![Results](./img/index_construction.png)

The Parse step is multi-threaded(-ish because of [Python GLI](https://en.wikipedia.org/wiki/Global_interpreter_lock)).
The Merge step outputs various statistics on the collection used (e.g. average length of documents, etc.) to compute advanced weigthing functions.

#### Querying

Two types of queries are supported:

+ Boolean queries of the form: `(foo || bar) && !(foobar)`
+ Vector queries of the form: `foo bar foobar`

![Results](./img/queries.png)

The inverted index file is accessed through the Collection Index Reader. The Reader maintains a map of the position of each term in the index file, which insures a O(1) access to posting lists.

#### Evaluation

The evaluation process runs 64 queries on each of the 9 weight methods selected:

+ the Test Builder manages the whole process by creating an Evaluation Builder for each weight methods.
+ each Evaluation Builder then computes an 11-points interpolated mean curve.
+ eventually, the Test Builder plots the results

Below is the class diagram for the Evaluation Module:

![Results](./img/evaluation.png)

### Zoom In

Detail specific technical choices and their reasons.

### Limitations

Is this engine truly scalable? If not, what could be improved?

## Performances

In this section we will discuss:
* Index construction speed & memory performances
* Index size
* Requests speed & IO performances
* Engine evaluation on test set

### Index Construction

The duration of each step of the index construction is displayed below for both test collections:

| Steps | CACM  | CS276 |
| --- | --- | --- |
| Parse (s)   | 0.6  | 58   |
| Merge (s)   | 0.5  | 70   |
| Refine (s)   | 0.7  | 87   |
| **Total (s)** | 1.8  | 215  |

As we can see, the most expensive step is the refinement of the index: computing weights involves costly mathematical operations whereas parsing and merging involves simple read and copy operations.

### Index size

The index is currently stored as string (hence not the most effective storage method).
```bash
term_id:doc_id, freq, weight|doc_id, freq, weight| ... |doc_id, freq, weight
```
| Items | CACM | CS276 |
| --- | --- | --- |
| Collection size (MB) | 13.1 | 430.7 |
| Index size (MB) | 2.2 | 315.5 |
| ID Mappers (MB) | 0.3 | 13.7 |
| Positions (MB) | 0.2 | 6.5 |
| **Total (MB)** | 2.7 | 335.7 |
| **Ratio (%)** | 20.6 | 77.9 |

From the above table, we can see that this storage method is not viable for real-life search engines.

Indeed, one would implement a compression method to decrease the size of the index.

### Requests performance

To improve the time performance of the requests, this search engine heavily relies on the `position` dictionary.
It maps each term ID to a position in the index and allows a O(1)-ish retrieval of a posting list.

Hence at a new request:
* the position of each unique term is retrieved
* the index file is only opened once

### Engine evaluation on requests set

The test set was composed of:
* 64 raw queries (including non-alphanumerical characters and common words)
* the list of relevant documents for each query

A few tests revealed that some queries explicitly referred to authors of articles. As a consequence, the author tag in the CACM collection was included in the scope of this engine.

#### Measures

To choose the best weighting function, two measures were defined:
* Precision / Recall curves for it is very visual
* Mean Average Precision to easily sort the results

#### Weight functions

Nine weight functions were tested:

1. Basic tf-idf
2. Normalized tf-idf
3. Normalized frequency
4. Pivoted document length normalization
5. BM25 (Okapi)
6. Modified BM25
7. Evolutionary learned scheme
8. Divergence from randomness
9. Axiomatic scheme

Except for the first 3, all these functions were taken from http://ir.dcs.gla.ac.uk/~ronanc/papers/cumminsChapter.pdf

#### Results

This plot sums up the results of the engine evaluation:

![Results](./img/results_riw.png)

One function behaves better than the others: the Evolutionary Learned Scheme.
