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

*Insert nice class diagrams*

### Zoom In

Detail specific technical choices and their reasons.

### Limitations

Is this engine truly scalable? If not, what could be improved?

## Performances

Describe here:
* Index construction speed & memory performances
* Index size
* Requests speed & IO performances
* Engine performance on test set