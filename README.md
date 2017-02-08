# Tiny Search Engine

Information Retrieval project for class IS3013AA

### Table of Contents
+ **[Usage Instructions](#usage-instructions)**  
+ **[Architecture](#architecture)**  
    + **[Global Architecture](#global-architecture)**
    + **[Zoom in](#zoom-in)**
    + **[Limitations](#limitations)**
+ **[Performances](#performances)**
    + **[Index Construction](#index-construction)**
    + **[Index Size](#index-size)**
    + **[Requests Performance](#requests-performance)**
    + **[Engine Evaluation](#engine-evaluation)**

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
  -m MEMORY, --memory MEMORY
                        set memory limitations
```

<dl>
    <dt>Build index and start engine</dt>
    <dd><code>python3 main.py {cacm or cs276} -w {0 .. 8} -r</code></dd>
    <dt>Start engine with last index</dt>
    <dd><code>python3 main.py {cacm or cs276}</code> (raises an error if there is no last index)</dd>
    <dt>Start engine evaluation</dt>
    <dd><code>python3 main.py cacm -e</code> (evaluation only supported for cacm)</dd>
</dl>

***

## Architecture

### Global architecture

#### Index Construction

The construction of the inverted index follows 2 steps:
* Parse: build a simple inverted index for each "block" of the collection and collect statistics. Additionally the data is cleaned:
    * Porter2 stemming (using the `PorterStemmer` package)
    * Removal of common words
* Merge: merge the block indexes and use the statistics to refine the posting lists with weights

Below is the class diagram for the Index Construction Module:

![Results](./img/index_construction.png)

The Parse step is multi-threaded(-ish because of [Python GLI](https://en.wikipedia.org/wiki/Global_interpreter_lock)). It outputs various statistics on the collection (e.g. average length of documents) used to compute advanced weighting functions.

The Merge step is a many-producers one-consumer process that was implemented with no concurrent programming. Because it writes the index sequentially, the Merger can store the position of each term of the collection within the file. The map produced will be used when querying the engine.

#### Querying

Two types of queries are supported:

+ Boolean queries of the form: `(foo || bar) && !(foobar)`
+ Vector queries of the form: `foo bar foobar`

![Results](./img/queries.png)

The inverted index file is accessed through the Collection Index Reader. The Reader uses the map that was produced during the construction of the index to retrieve posting lists. Hence getting the list of potentially relevant documents on a query is a O(1)(-ish) operation.

For this reason, no K-Top algorithm was implemented in this exercise.

#### Evaluation

The evaluation process runs 64 queries on each of the 9 weight methods selected:

+ the Test Builder manages the whole process by creating an Evaluation Builder for each weight methods.
+ each Evaluation Builder then computes an 11-points interpolated mean curve.
+ eventually, the Test Builder plots the results

Below is the class diagram for the Evaluation Module:

![Results](./img/evaluation.png)

### Zoom In

Detail specific technical choices and their reasons. Potential subjects:

* The use of read / write queues (part of it is already detailled in the Limitations section)
* The WeightFactory

Maybe this should be moved as an Appendix?

### Limitations

While this engine works fine with the CACM and CS276 collections, it is not truly scalable for two major reasons:

#### In-memory maps

In order to handle a request, this engine needs two maps:

* `terms = {term: term_id}` maps a term with its id
* `docs = {doc_id: doc_path}` maps a doc id with the document it represents

In addition, a third map improves performances when searching for a posting list in the index file.

These maps are a dense index on a set of IDs. If we were to reach the billion terms in a collection, such maps would not fit in memory anymore. One would instead turn them into non-dense indexes pointing at a range of IDs (either stored  in a local file or on another machine).

Such a solution  makes the whole system scalable but has an impact on performances. Hence the use of dense indexes in this engine.

#### IO Buffers

During the construction of the index, this engine uses simple (i.e. homemade) read/write queues. To represent the memory limitations of the system, these queues have a limited capacty, expressed as an amount of lines.
The default limitation is set to 2200 lines (empirically chosen), which means we assume no more than 2200 posting lists can fit in-memory.

However, posting lists do not have an homogeneous size (long-tail phenomenon) and their size directly depends on the size of the collection! Hence the simplicity of the current queues does not allow a "true" scalability.

To fix this, one would check the size of each posting list before loading it in memory and would express the capacity of the queues as an amount of bytes. This approach will work until posting lists are too big to fit in memory individually.

***

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
| Parse (s)   | 0.9  | 74   |
| Merge (s)   | 0.8  | 105   |
| **Total (s)** | 1.7  | 179  |

The steps are quite equivalent in complexity for both use expensive operations: 

* the stemming in the Parse step
* the weights computations in the Merge step (costly mathematical operations)

### Index size

The index is currently stored as a string (hence not the most effective storage method).
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

From the `Ratio` line of the above table, we can see that this storage method is not viable for real-life search engines.

As a solution, one would implement a compression method to decrease the size of the index.

### Requests performance

To improve the time performance of the requests, this search engine heavily relies on a `position` dictionary.
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

One function behaves better than the others with a MAP of 0.533: the Evolutionary Learned Scheme (#7). However this weight needs an extra statistic to be computed, hence building the index lasts ~ 12% longer when using it.
