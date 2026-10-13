16 queries (holdout_queries.json) over 92 schools; candidate limits [10, 25, 50]; RANKING_VERSION v1.4, document v3.0
queries per category: {'exact_vocabulary': 4, 'filtered': 2, 'state_name': 4, 'structured_only': 2, 'synonym': 3, 'world_knowledge': 1}
production equivalence: 96 query runs match the real SemanticSearchService exactly

## Overall

| configuration | limit | pool recall | retriever RP@10 | end-to-end RP@10 | 95% CI | filtered queries empty | mean fit (page) | p50 / p95 ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| before v1.2: hash | 10 | 0.27 | 0.46 | 0.46 | 0.28-0.65 | 1/2 | 79.7 | 1.61 / 1.68 |
| before v1.2: hash | 25 | 0.50 | 0.51 | 0.49 | 0.33-0.67 | 0/2 | 83.2 | 3.18 / 5.02 |
| before v1.2: hash | 50 | 0.76 | 0.55 | 0.46 | 0.31-0.61 | 0/2 | 84.8 | 12.22 / 16.12 |
| before v1.2: lexical fallback | 10 | 0.34 | 0.55 | 0.55 | 0.37-0.73 | 1/2 | 79.9 | 1.86 / 3.13 |
| before v1.2: lexical fallback | 25 | 0.59 | 0.57 | 0.58 | 0.39-0.75 | 1/2 | 83.6 | 5.45 / 7.39 |
| before v1.2: lexical fallback | 50 | 0.83 | 0.65 | 0.46 | 0.31-0.60 | 0/2 | 85.1 | 10.46 / 12.92 |
| v1.2: hash | 10 | 0.50 | 0.69 | 0.69 | 0.52-0.87 | 0/2 | 79.8 | 3.51 / 4.22 |
| v1.2: hash | 25 | 0.70 | 0.69 | 0.71 | 0.54-0.88 | 0/2 | 80.9 | 6.76 / 8.86 |
| v1.2: hash | 50 | 0.84 | 0.69 | 0.70 | 0.53-0.87 | 0/2 | 81.2 | 9.36 / 11.20 |
| v1.3 production: full-text | 10 | 0.56 | 0.76 | 0.76 | 0.57-0.93 | 0/2 | 80.3 | 8.54 / 11.69 |
| v1.3 production: full-text | 25 | 0.72 | 0.76 | 0.79 | 0.63-0.94 | 0/2 | 83.1 | 15.49 / 19.46 |
| v1.3 production: full-text | 50 | 0.86 | 0.76 | 0.79 | 0.64-0.93 | 0/2 | 83.6 | 18.72 / 22.96 |
| v1.3 production: lexical fallback | 10 | 0.55 | 0.75 | 0.75 | 0.56-0.91 | 0/2 | 79.9 | 2.12 / 2.67 |
| v1.3 production: lexical fallback | 25 | 0.72 | 0.75 | 0.80 | 0.65-0.93 | 0/2 | 83.1 | 4.16 / 4.92 |
| v1.3 production: lexical fallback | 50 | 0.85 | 0.75 | 0.79 | 0.65-0.93 | 0/2 | 83.7 | 4.92 / 8.52 |
| model2vec potion-base-8M | 10 | 0.54 | 0.74 | 0.74 | 0.59-0.88 | 0/2 | 80.5 | 1.13 / 2.60 |
| model2vec potion-base-8M | 25 | 0.70 | 0.74 | 0.74 | 0.59-0.88 | 0/2 | 80.5 | 2.15 / 3.66 |
| model2vec potion-base-8M | 50 | 0.84 | 0.74 | 0.74 | 0.59-0.88 | 0/2 | 80.5 | 6.06 / 9.39 |
| hybrid: lexical + model2vec (RRF) | 10 | 0.56 | 0.78 | 0.78 | 0.59-0.94 | 0/2 | 80.2 | 2.11 / 3.10 |
| hybrid: lexical + model2vec (RRF) | 25 | 0.72 | 0.78 | 0.78 | 0.59-0.94 | 0/2 | 80.2 | 4.22 / 6.01 |
| hybrid: lexical + model2vec (RRF) | 50 | 0.85 | 0.78 | 0.78 | 0.59-0.94 | 0/2 | 80.2 | 5.53 / 9.72 |
| hybrid: full-text + model2vec (RRF) | 10 | 0.56 | 0.76 | 0.76 | 0.57-0.93 | 0/2 | 80.3 | 12.18 / 17.73 |
| hybrid: full-text + model2vec (RRF) | 25 | 0.71 | 0.76 | 0.76 | 0.57-0.93 | 0/2 | 80.3 | 16.54 / 21.47 |
| hybrid: full-text + model2vec (RRF) | 50 | 0.86 | 0.76 | 0.76 | 0.57-0.93 | 0/2 | 80.3 | 18.96 / 22.92 |

## End-to-end RP@10 by query category, candidate limit 50

| configuration | exact_vocabulary | filtered | state_name | structured_only | synonym | world_knowledge |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| before v1.2: hash | 0.33 | 0.94 | 0.31 | 0.45 | 0.63 | 0.10 |
| before v1.2: lexical fallback | 0.49 | 0.81 | 0.19 | 0.50 | 0.60 | 0.20 |
| v1.2: hash | 0.66 | 1.00 | 1.00 | 0.30 | 0.67 | 0.00 |
| v1.3 production: full-text | 0.97 | 1.00 | 1.00 | 0.35 | 0.63 | 0.20 |
| v1.3 production: lexical fallback | 0.95 | 1.00 | 1.00 | 0.40 | 0.63 | 0.20 |
| model2vec potion-base-8M | 0.72 | 1.00 | 1.00 | 0.25 | 0.73 | 0.20 |
| hybrid: lexical + model2vec (RRF) | 0.97 | 1.00 | 1.00 | 0.20 | 0.67 | 0.10 |
| hybrid: full-text + model2vec (RRF) | 0.93 | 1.00 | 1.00 | 0.20 | 0.67 | 0.10 |

## Per query

| configuration | limit | query | category | relevant | pool | pool recall | retriever RP@10 | end-to-end RP@10 | empty |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| before v1.2: hash | 10 | ho-ca-biology | state_name | 4 | 10 | 0.25 | 0.25 | 0.25 |  |
| before v1.2: hash | 10 | ho-ny-computer-science | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: hash | 10 | ho-mi-engineering | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: hash | 10 | ho-il-private | state_name | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| before v1.2: hash | 10 | ho-west-public | exact_vocabulary | 13 | 10 | 0.31 | 0.40 | 0.40 |  |
| before v1.2: hash | 10 | ho-urban-private | exact_vocabulary | 29 | 10 | 0.34 | 1.00 | 1.00 |  |
| before v1.2: hash | 10 | ho-large-south-public | exact_vocabulary | 24 | 10 | 0.33 | 0.80 | 0.80 |  |
| before v1.2: hash | 10 | ho-division-iii | exact_vocabulary | 9 | 10 | 0.11 | 0.11 | 0.11 |  |
| before v1.2: hash | 10 | ho-pre-med | synonym | 45 | 10 | 0.16 | 0.70 | 0.70 |  |
| before v1.2: hash | 10 | ho-economics | synonym | 39 | 10 | 0.08 | 0.30 | 0.30 |  |
| before v1.2: hash | 10 | ho-software | synonym | 53 | 10 | 0.15 | 0.80 | 0.80 |  |
| before v1.2: hash | 10 | ho-affordable | structured_only | 41 | 10 | 0.10 | 0.40 | 0.40 |  |
| before v1.2: hash | 10 | ho-highly-selective | structured_only | 20 | 10 | 0.05 | 0.10 | 0.10 |  |
| before v1.2: hash | 10 | ho-big-ten | world_knowledge | 15 | 10 | 0.00 | 0.00 | 0.00 |  |
| before v1.2: hash | 10 | ho-filter-tx-biology | filtered | 4 | 0 | 0.00 | 0.00 | 0.00 | yes |
| before v1.2: hash | 10 | ho-filter-cheap-public-cs | filtered | 8 | 4 | 0.50 | 0.50 | 0.50 |  |
| before v1.2: hash | 25 | ho-ca-biology | state_name | 4 | 25 | 0.75 | 0.25 | 0.75 |  |
| before v1.2: hash | 25 | ho-ny-computer-science | state_name | 2 | 25 | 1.00 | 1.00 | 0.00 |  |
| before v1.2: hash | 25 | ho-mi-engineering | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: hash | 25 | ho-il-private | state_name | 2 | 25 | 0.00 | 0.00 | 0.00 |  |
| before v1.2: hash | 25 | ho-west-public | exact_vocabulary | 13 | 25 | 0.69 | 0.40 | 0.50 |  |
| before v1.2: hash | 25 | ho-urban-private | exact_vocabulary | 29 | 25 | 0.79 | 1.00 | 0.80 |  |
| before v1.2: hash | 25 | ho-large-south-public | exact_vocabulary | 24 | 25 | 0.83 | 0.80 | 0.70 |  |
| before v1.2: hash | 25 | ho-division-iii | exact_vocabulary | 9 | 25 | 0.22 | 0.11 | 0.00 |  |
| before v1.2: hash | 25 | ho-pre-med | synonym | 45 | 25 | 0.29 | 0.70 | 0.60 |  |
| before v1.2: hash | 25 | ho-economics | synonym | 39 | 25 | 0.31 | 0.30 | 0.60 |  |
| before v1.2: hash | 25 | ho-software | synonym | 53 | 25 | 0.36 | 0.80 | 0.80 |  |
| before v1.2: hash | 25 | ho-affordable | structured_only | 41 | 25 | 0.34 | 0.40 | 0.60 |  |
| before v1.2: hash | 25 | ho-highly-selective | structured_only | 20 | 25 | 0.10 | 0.10 | 0.20 |  |
| before v1.2: hash | 25 | ho-big-ten | world_knowledge | 15 | 25 | 0.07 | 0.00 | 0.10 |  |
| before v1.2: hash | 25 | ho-filter-tx-biology | filtered | 4 | 1 | 0.25 | 0.25 | 0.25 |  |
| before v1.2: hash | 25 | ho-filter-cheap-public-cs | filtered | 8 | 8 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: hash | 50 | ho-ca-biology | state_name | 4 | 50 | 1.00 | 0.25 | 0.75 |  |
| before v1.2: hash | 50 | ho-ny-computer-science | state_name | 2 | 50 | 1.00 | 1.00 | 0.00 |  |
| before v1.2: hash | 50 | ho-mi-engineering | state_name | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| before v1.2: hash | 50 | ho-il-private | state_name | 2 | 50 | 1.00 | 0.00 | 0.50 |  |
| before v1.2: hash | 50 | ho-west-public | exact_vocabulary | 13 | 50 | 1.00 | 0.40 | 0.40 |  |
| before v1.2: hash | 50 | ho-urban-private | exact_vocabulary | 29 | 50 | 1.00 | 1.00 | 0.60 |  |
| before v1.2: hash | 50 | ho-large-south-public | exact_vocabulary | 24 | 50 | 1.00 | 0.80 | 0.30 |  |
| before v1.2: hash | 50 | ho-division-iii | exact_vocabulary | 9 | 50 | 0.22 | 0.11 | 0.00 |  |
| before v1.2: hash | 50 | ho-pre-med | synonym | 45 | 50 | 0.60 | 0.70 | 0.60 |  |
| before v1.2: hash | 50 | ho-economics | synonym | 39 | 50 | 0.54 | 0.30 | 0.50 |  |
| before v1.2: hash | 50 | ho-software | synonym | 53 | 50 | 0.70 | 0.80 | 0.80 |  |
| before v1.2: hash | 50 | ho-affordable | structured_only | 41 | 50 | 0.56 | 0.40 | 0.60 |  |
| before v1.2: hash | 50 | ho-highly-selective | structured_only | 20 | 50 | 0.25 | 0.10 | 0.30 |  |
| before v1.2: hash | 50 | ho-big-ten | world_knowledge | 15 | 50 | 0.27 | 0.00 | 0.10 |  |
| before v1.2: hash | 50 | ho-filter-tx-biology | filtered | 4 | 5 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: hash | 50 | ho-filter-cheap-public-cs | filtered | 8 | 13 | 1.00 | 1.00 | 0.88 |  |
| before v1.2: lexical fallback | 10 | ho-ca-biology | state_name | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 10 | ho-ny-computer-science | state_name | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| before v1.2: lexical fallback | 10 | ho-mi-engineering | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 10 | ho-il-private | state_name | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| before v1.2: lexical fallback | 10 | ho-west-public | exact_vocabulary | 13 | 10 | 0.54 | 0.70 | 0.70 |  |
| before v1.2: lexical fallback | 10 | ho-urban-private | exact_vocabulary | 29 | 10 | 0.34 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 10 | ho-large-south-public | exact_vocabulary | 24 | 10 | 0.42 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 10 | ho-division-iii | exact_vocabulary | 9 | 10 | 0.11 | 0.11 | 0.11 |  |
| before v1.2: lexical fallback | 10 | ho-pre-med | synonym | 45 | 10 | 0.11 | 0.50 | 0.50 |  |
| before v1.2: lexical fallback | 10 | ho-economics | synonym | 39 | 10 | 0.08 | 0.30 | 0.30 |  |
| before v1.2: lexical fallback | 10 | ho-software | synonym | 53 | 10 | 0.19 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 10 | ho-affordable | structured_only | 41 | 10 | 0.17 | 0.70 | 0.70 |  |
| before v1.2: lexical fallback | 10 | ho-highly-selective | structured_only | 20 | 10 | 0.05 | 0.10 | 0.10 |  |
| before v1.2: lexical fallback | 10 | ho-big-ten | world_knowledge | 15 | 10 | 0.00 | 0.00 | 0.00 |  |
| before v1.2: lexical fallback | 10 | ho-filter-tx-biology | filtered | 4 | 0 | 0.00 | 0.00 | 0.00 | yes |
| before v1.2: lexical fallback | 10 | ho-filter-cheap-public-cs | filtered | 8 | 3 | 0.38 | 0.38 | 0.38 |  |
| before v1.2: lexical fallback | 25 | ho-ca-biology | state_name | 4 | 25 | 1.00 | 1.00 | 0.75 |  |
| before v1.2: lexical fallback | 25 | ho-ny-computer-science | state_name | 2 | 25 | 1.00 | 0.50 | 0.00 |  |
| before v1.2: lexical fallback | 25 | ho-mi-engineering | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 25 | ho-il-private | state_name | 2 | 25 | 1.00 | 0.50 | 0.50 |  |
| before v1.2: lexical fallback | 25 | ho-west-public | exact_vocabulary | 13 | 25 | 1.00 | 0.70 | 0.70 |  |
| before v1.2: lexical fallback | 25 | ho-urban-private | exact_vocabulary | 29 | 25 | 0.86 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 25 | ho-large-south-public | exact_vocabulary | 24 | 25 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 25 | ho-division-iii | exact_vocabulary | 9 | 25 | 0.11 | 0.11 | 0.11 |  |
| before v1.2: lexical fallback | 25 | ho-pre-med | synonym | 45 | 25 | 0.33 | 0.50 | 0.60 |  |
| before v1.2: lexical fallback | 25 | ho-economics | synonym | 39 | 25 | 0.28 | 0.30 | 0.60 |  |
| before v1.2: lexical fallback | 25 | ho-software | synonym | 53 | 25 | 0.47 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 25 | ho-affordable | structured_only | 41 | 25 | 0.41 | 0.70 | 0.80 |  |
| before v1.2: lexical fallback | 25 | ho-highly-selective | structured_only | 20 | 25 | 0.15 | 0.10 | 0.30 |  |
| before v1.2: lexical fallback | 25 | ho-big-ten | world_knowledge | 15 | 25 | 0.13 | 0.00 | 0.10 |  |
| before v1.2: lexical fallback | 25 | ho-filter-tx-biology | filtered | 4 | 0 | 0.00 | 0.00 | 0.00 | yes |
| before v1.2: lexical fallback | 25 | ho-filter-cheap-public-cs | filtered | 8 | 6 | 0.75 | 0.75 | 0.75 |  |
| before v1.2: lexical fallback | 50 | ho-ca-biology | state_name | 4 | 50 | 1.00 | 1.00 | 0.75 |  |
| before v1.2: lexical fallback | 50 | ho-ny-computer-science | state_name | 2 | 50 | 1.00 | 0.50 | 0.00 |  |
| before v1.2: lexical fallback | 50 | ho-mi-engineering | state_name | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| before v1.2: lexical fallback | 50 | ho-il-private | state_name | 2 | 50 | 1.00 | 0.50 | 0.00 |  |
| before v1.2: lexical fallback | 50 | ho-west-public | exact_vocabulary | 13 | 50 | 1.00 | 0.70 | 0.40 |  |
| before v1.2: lexical fallback | 50 | ho-urban-private | exact_vocabulary | 29 | 50 | 1.00 | 1.00 | 0.70 |  |
| before v1.2: lexical fallback | 50 | ho-large-south-public | exact_vocabulary | 24 | 50 | 1.00 | 1.00 | 0.40 |  |
| before v1.2: lexical fallback | 50 | ho-division-iii | exact_vocabulary | 9 | 50 | 0.67 | 0.11 | 0.44 |  |
| before v1.2: lexical fallback | 50 | ho-pre-med | synonym | 45 | 50 | 0.62 | 0.50 | 0.40 |  |
| before v1.2: lexical fallback | 50 | ho-economics | synonym | 39 | 50 | 0.56 | 0.30 | 0.50 |  |
| before v1.2: lexical fallback | 50 | ho-software | synonym | 53 | 50 | 0.81 | 1.00 | 0.90 |  |
| before v1.2: lexical fallback | 50 | ho-affordable | structured_only | 41 | 50 | 0.63 | 0.70 | 0.60 |  |
| before v1.2: lexical fallback | 50 | ho-highly-selective | structured_only | 20 | 50 | 0.45 | 0.10 | 0.40 |  |
| before v1.2: lexical fallback | 50 | ho-big-ten | world_knowledge | 15 | 50 | 0.60 | 0.00 | 0.20 |  |
| before v1.2: lexical fallback | 50 | ho-filter-tx-biology | filtered | 4 | 4 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 50 | ho-filter-cheap-public-cs | filtered | 8 | 16 | 1.00 | 1.00 | 0.62 |  |
| v1.2: hash | 10 | ho-ca-biology | state_name | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | ho-ny-computer-science | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | ho-mi-engineering | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | ho-il-private | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | ho-west-public | exact_vocabulary | 13 | 10 | 0.15 | 0.20 | 0.20 |  |
| v1.2: hash | 10 | ho-urban-private | exact_vocabulary | 29 | 10 | 0.34 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | ho-large-south-public | exact_vocabulary | 24 | 10 | 0.38 | 0.90 | 0.90 |  |
| v1.2: hash | 10 | ho-division-iii | exact_vocabulary | 9 | 10 | 0.56 | 0.56 | 0.56 |  |
| v1.2: hash | 10 | ho-pre-med | synonym | 45 | 10 | 0.11 | 0.50 | 0.50 |  |
| v1.2: hash | 10 | ho-economics | synonym | 39 | 10 | 0.08 | 0.30 | 0.30 |  |
| v1.2: hash | 10 | ho-software | synonym | 53 | 10 | 0.19 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | ho-affordable | structured_only | 41 | 10 | 0.10 | 0.40 | 0.40 |  |
| v1.2: hash | 10 | ho-highly-selective | structured_only | 20 | 10 | 0.05 | 0.10 | 0.10 |  |
| v1.2: hash | 10 | ho-big-ten | world_knowledge | 15 | 10 | 0.07 | 0.10 | 0.10 |  |
| v1.2: hash | 10 | ho-filter-tx-biology | filtered | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | ho-filter-cheap-public-cs | filtered | 8 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | ho-ca-biology | state_name | 4 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | ho-ny-computer-science | state_name | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | ho-mi-engineering | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | ho-il-private | state_name | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | ho-west-public | exact_vocabulary | 13 | 25 | 0.69 | 0.20 | 0.20 |  |
| v1.2: hash | 25 | ho-urban-private | exact_vocabulary | 29 | 25 | 0.79 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | ho-large-south-public | exact_vocabulary | 24 | 25 | 0.92 | 0.90 | 0.90 |  |
| v1.2: hash | 25 | ho-division-iii | exact_vocabulary | 9 | 25 | 1.00 | 0.56 | 0.56 |  |
| v1.2: hash | 25 | ho-pre-med | synonym | 45 | 25 | 0.33 | 0.50 | 0.50 |  |
| v1.2: hash | 25 | ho-economics | synonym | 39 | 25 | 0.28 | 0.30 | 0.60 |  |
| v1.2: hash | 25 | ho-software | synonym | 53 | 25 | 0.47 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | ho-affordable | structured_only | 41 | 25 | 0.32 | 0.40 | 0.40 |  |
| v1.2: hash | 25 | ho-highly-selective | structured_only | 20 | 25 | 0.20 | 0.10 | 0.20 |  |
| v1.2: hash | 25 | ho-big-ten | world_knowledge | 15 | 25 | 0.13 | 0.10 | 0.00 |  |
| v1.2: hash | 25 | ho-filter-tx-biology | filtered | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | ho-filter-cheap-public-cs | filtered | 8 | 23 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | ho-ca-biology | state_name | 4 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | ho-ny-computer-science | state_name | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | ho-mi-engineering | state_name | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | ho-il-private | state_name | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | ho-west-public | exact_vocabulary | 13 | 50 | 1.00 | 0.20 | 0.20 |  |
| v1.2: hash | 50 | ho-urban-private | exact_vocabulary | 29 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | ho-large-south-public | exact_vocabulary | 24 | 50 | 1.00 | 0.90 | 0.90 |  |
| v1.2: hash | 50 | ho-division-iii | exact_vocabulary | 9 | 50 | 1.00 | 0.56 | 0.56 |  |
| v1.2: hash | 50 | ho-pre-med | synonym | 45 | 50 | 0.62 | 0.50 | 0.50 |  |
| v1.2: hash | 50 | ho-economics | synonym | 39 | 50 | 0.56 | 0.30 | 0.50 |  |
| v1.2: hash | 50 | ho-software | synonym | 53 | 50 | 0.74 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | ho-affordable | structured_only | 41 | 50 | 0.59 | 0.40 | 0.40 |  |
| v1.2: hash | 50 | ho-highly-selective | structured_only | 20 | 50 | 0.55 | 0.10 | 0.20 |  |
| v1.2: hash | 50 | ho-big-ten | world_knowledge | 15 | 50 | 0.40 | 0.10 | 0.00 |  |
| v1.2: hash | 50 | ho-filter-tx-biology | filtered | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | ho-filter-cheap-public-cs | filtered | 8 | 23 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | ho-ca-biology | state_name | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | ho-ny-computer-science | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | ho-mi-engineering | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | ho-il-private | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | ho-west-public | exact_vocabulary | 13 | 10 | 0.77 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | ho-urban-private | exact_vocabulary | 29 | 10 | 0.34 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | ho-large-south-public | exact_vocabulary | 24 | 10 | 0.42 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | ho-division-iii | exact_vocabulary | 9 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | ho-pre-med | synonym | 45 | 10 | 0.11 | 0.50 | 0.50 |  |
| v1.3 production: full-text | 10 | ho-economics | synonym | 39 | 10 | 0.08 | 0.30 | 0.30 |  |
| v1.3 production: full-text | 10 | ho-software | synonym | 53 | 10 | 0.19 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | ho-affordable | structured_only | 41 | 10 | 0.07 | 0.30 | 0.30 |  |
| v1.3 production: full-text | 10 | ho-highly-selective | structured_only | 20 | 10 | 0.05 | 0.10 | 0.10 |  |
| v1.3 production: full-text | 10 | ho-big-ten | world_knowledge | 15 | 10 | 0.00 | 0.00 | 0.00 |  |
| v1.3 production: full-text | 10 | ho-filter-tx-biology | filtered | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | ho-filter-cheap-public-cs | filtered | 8 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | ho-ca-biology | state_name | 4 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | ho-ny-computer-science | state_name | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | ho-mi-engineering | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | ho-il-private | state_name | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | ho-west-public | exact_vocabulary | 13 | 25 | 1.00 | 1.00 | 0.90 |  |
| v1.3 production: full-text | 25 | ho-urban-private | exact_vocabulary | 29 | 25 | 0.86 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | ho-large-south-public | exact_vocabulary | 24 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | ho-division-iii | exact_vocabulary | 9 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | ho-pre-med | synonym | 45 | 25 | 0.33 | 0.50 | 0.60 |  |
| v1.3 production: full-text | 25 | ho-economics | synonym | 39 | 25 | 0.28 | 0.30 | 0.60 |  |
| v1.3 production: full-text | 25 | ho-software | synonym | 53 | 25 | 0.47 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | ho-affordable | structured_only | 41 | 25 | 0.32 | 0.30 | 0.40 |  |
| v1.3 production: full-text | 25 | ho-highly-selective | structured_only | 20 | 25 | 0.15 | 0.10 | 0.10 |  |
| v1.3 production: full-text | 25 | ho-big-ten | world_knowledge | 15 | 25 | 0.13 | 0.00 | 0.10 |  |
| v1.3 production: full-text | 25 | ho-filter-tx-biology | filtered | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | ho-filter-cheap-public-cs | filtered | 8 | 23 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | ho-ca-biology | state_name | 4 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | ho-ny-computer-science | state_name | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | ho-mi-engineering | state_name | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | ho-il-private | state_name | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | ho-west-public | exact_vocabulary | 13 | 50 | 1.00 | 1.00 | 0.90 |  |
| v1.3 production: full-text | 50 | ho-urban-private | exact_vocabulary | 29 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | ho-large-south-public | exact_vocabulary | 24 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | ho-division-iii | exact_vocabulary | 9 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | ho-pre-med | synonym | 45 | 50 | 0.62 | 0.50 | 0.40 |  |
| v1.3 production: full-text | 50 | ho-economics | synonym | 39 | 50 | 0.56 | 0.30 | 0.50 |  |
| v1.3 production: full-text | 50 | ho-software | synonym | 53 | 50 | 0.81 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | ho-affordable | structured_only | 41 | 50 | 0.61 | 0.30 | 0.40 |  |
| v1.3 production: full-text | 50 | ho-highly-selective | structured_only | 20 | 50 | 0.60 | 0.10 | 0.30 |  |
| v1.3 production: full-text | 50 | ho-big-ten | world_knowledge | 15 | 50 | 0.60 | 0.00 | 0.20 |  |
| v1.3 production: full-text | 50 | ho-filter-tx-biology | filtered | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | ho-filter-cheap-public-cs | filtered | 8 | 23 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | ho-ca-biology | state_name | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | ho-ny-computer-science | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | ho-mi-engineering | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | ho-il-private | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | ho-west-public | exact_vocabulary | 13 | 10 | 0.62 | 0.80 | 0.80 |  |
| v1.3 production: lexical fallback | 10 | ho-urban-private | exact_vocabulary | 29 | 10 | 0.34 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | ho-large-south-public | exact_vocabulary | 24 | 10 | 0.42 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | ho-division-iii | exact_vocabulary | 9 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | ho-pre-med | synonym | 45 | 10 | 0.11 | 0.50 | 0.50 |  |
| v1.3 production: lexical fallback | 10 | ho-economics | synonym | 39 | 10 | 0.08 | 0.30 | 0.30 |  |
| v1.3 production: lexical fallback | 10 | ho-software | synonym | 53 | 10 | 0.19 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | ho-affordable | structured_only | 41 | 10 | 0.07 | 0.30 | 0.30 |  |
| v1.3 production: lexical fallback | 10 | ho-highly-selective | structured_only | 20 | 10 | 0.05 | 0.10 | 0.10 |  |
| v1.3 production: lexical fallback | 10 | ho-big-ten | world_knowledge | 15 | 10 | 0.00 | 0.00 | 0.00 |  |
| v1.3 production: lexical fallback | 10 | ho-filter-tx-biology | filtered | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | ho-filter-cheap-public-cs | filtered | 8 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | ho-ca-biology | state_name | 4 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | ho-ny-computer-science | state_name | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | ho-mi-engineering | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | ho-il-private | state_name | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | ho-west-public | exact_vocabulary | 13 | 25 | 1.00 | 0.80 | 0.80 |  |
| v1.3 production: lexical fallback | 25 | ho-urban-private | exact_vocabulary | 29 | 25 | 0.86 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | ho-large-south-public | exact_vocabulary | 24 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | ho-division-iii | exact_vocabulary | 9 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | ho-pre-med | synonym | 45 | 25 | 0.33 | 0.50 | 0.60 |  |
| v1.3 production: lexical fallback | 25 | ho-economics | synonym | 39 | 25 | 0.28 | 0.30 | 0.60 |  |
| v1.3 production: lexical fallback | 25 | ho-software | synonym | 53 | 25 | 0.47 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | ho-affordable | structured_only | 41 | 25 | 0.32 | 0.30 | 0.40 |  |
| v1.3 production: lexical fallback | 25 | ho-highly-selective | structured_only | 20 | 25 | 0.15 | 0.10 | 0.30 |  |
| v1.3 production: lexical fallback | 25 | ho-big-ten | world_knowledge | 15 | 25 | 0.13 | 0.00 | 0.10 |  |
| v1.3 production: lexical fallback | 25 | ho-filter-tx-biology | filtered | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | ho-filter-cheap-public-cs | filtered | 8 | 23 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | ho-ca-biology | state_name | 4 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | ho-ny-computer-science | state_name | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | ho-mi-engineering | state_name | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | ho-il-private | state_name | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | ho-west-public | exact_vocabulary | 13 | 50 | 1.00 | 0.80 | 0.80 |  |
| v1.3 production: lexical fallback | 50 | ho-urban-private | exact_vocabulary | 29 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | ho-large-south-public | exact_vocabulary | 24 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | ho-division-iii | exact_vocabulary | 9 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | ho-pre-med | synonym | 45 | 50 | 0.62 | 0.50 | 0.40 |  |
| v1.3 production: lexical fallback | 50 | ho-economics | synonym | 39 | 50 | 0.56 | 0.30 | 0.50 |  |
| v1.3 production: lexical fallback | 50 | ho-software | synonym | 53 | 50 | 0.81 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | ho-affordable | structured_only | 41 | 50 | 0.61 | 0.30 | 0.40 |  |
| v1.3 production: lexical fallback | 50 | ho-highly-selective | structured_only | 20 | 50 | 0.45 | 0.10 | 0.40 |  |
| v1.3 production: lexical fallback | 50 | ho-big-ten | world_knowledge | 15 | 50 | 0.60 | 0.00 | 0.20 |  |
| v1.3 production: lexical fallback | 50 | ho-filter-tx-biology | filtered | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | ho-filter-cheap-public-cs | filtered | 8 | 23 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | ho-ca-biology | state_name | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | ho-ny-computer-science | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | ho-mi-engineering | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | ho-il-private | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | ho-west-public | exact_vocabulary | 13 | 10 | 0.38 | 0.50 | 0.50 |  |
| model2vec potion-base-8M | 10 | ho-urban-private | exact_vocabulary | 29 | 10 | 0.24 | 0.70 | 0.70 |  |
| model2vec potion-base-8M | 10 | ho-large-south-public | exact_vocabulary | 24 | 10 | 0.38 | 0.90 | 0.90 |  |
| model2vec potion-base-8M | 10 | ho-division-iii | exact_vocabulary | 9 | 10 | 0.78 | 0.78 | 0.78 |  |
| model2vec potion-base-8M | 10 | ho-pre-med | synonym | 45 | 10 | 0.18 | 0.80 | 0.80 |  |
| model2vec potion-base-8M | 10 | ho-economics | synonym | 39 | 10 | 0.10 | 0.40 | 0.40 |  |
| model2vec potion-base-8M | 10 | ho-software | synonym | 53 | 10 | 0.19 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | ho-affordable | structured_only | 41 | 10 | 0.05 | 0.20 | 0.20 |  |
| model2vec potion-base-8M | 10 | ho-highly-selective | structured_only | 20 | 10 | 0.15 | 0.30 | 0.30 |  |
| model2vec potion-base-8M | 10 | ho-big-ten | world_knowledge | 15 | 10 | 0.13 | 0.20 | 0.20 |  |
| model2vec potion-base-8M | 10 | ho-filter-tx-biology | filtered | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | ho-filter-cheap-public-cs | filtered | 8 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | ho-ca-biology | state_name | 4 | 25 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | ho-ny-computer-science | state_name | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | ho-mi-engineering | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | ho-il-private | state_name | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | ho-west-public | exact_vocabulary | 13 | 25 | 0.69 | 0.50 | 0.50 |  |
| model2vec potion-base-8M | 25 | ho-urban-private | exact_vocabulary | 29 | 25 | 0.69 | 0.70 | 0.70 |  |
| model2vec potion-base-8M | 25 | ho-large-south-public | exact_vocabulary | 24 | 25 | 0.88 | 0.90 | 0.90 |  |
| model2vec potion-base-8M | 25 | ho-division-iii | exact_vocabulary | 9 | 25 | 1.00 | 0.78 | 0.78 |  |
| model2vec potion-base-8M | 25 | ho-pre-med | synonym | 45 | 25 | 0.47 | 0.80 | 0.80 |  |
| model2vec potion-base-8M | 25 | ho-economics | synonym | 39 | 25 | 0.26 | 0.40 | 0.40 |  |
| model2vec potion-base-8M | 25 | ho-software | synonym | 53 | 25 | 0.47 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | ho-affordable | structured_only | 41 | 25 | 0.15 | 0.20 | 0.20 |  |
| model2vec potion-base-8M | 25 | ho-highly-selective | structured_only | 20 | 25 | 0.30 | 0.30 | 0.30 |  |
| model2vec potion-base-8M | 25 | ho-big-ten | world_knowledge | 15 | 25 | 0.27 | 0.20 | 0.20 |  |
| model2vec potion-base-8M | 25 | ho-filter-tx-biology | filtered | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | ho-filter-cheap-public-cs | filtered | 8 | 23 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | ho-ca-biology | state_name | 4 | 50 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | ho-ny-computer-science | state_name | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | ho-mi-engineering | state_name | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | ho-il-private | state_name | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | ho-west-public | exact_vocabulary | 13 | 50 | 0.92 | 0.50 | 0.50 |  |
| model2vec potion-base-8M | 50 | ho-urban-private | exact_vocabulary | 29 | 50 | 1.00 | 0.70 | 0.70 |  |
| model2vec potion-base-8M | 50 | ho-large-south-public | exact_vocabulary | 24 | 50 | 0.96 | 0.90 | 0.90 |  |
| model2vec potion-base-8M | 50 | ho-division-iii | exact_vocabulary | 9 | 50 | 1.00 | 0.78 | 0.78 |  |
| model2vec potion-base-8M | 50 | ho-pre-med | synonym | 45 | 50 | 0.67 | 0.80 | 0.80 |  |
| model2vec potion-base-8M | 50 | ho-economics | synonym | 39 | 50 | 0.54 | 0.40 | 0.40 |  |
| model2vec potion-base-8M | 50 | ho-software | synonym | 53 | 50 | 0.92 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | ho-affordable | structured_only | 41 | 50 | 0.34 | 0.20 | 0.20 |  |
| model2vec potion-base-8M | 50 | ho-highly-selective | structured_only | 20 | 50 | 0.60 | 0.30 | 0.30 |  |
| model2vec potion-base-8M | 50 | ho-big-ten | world_knowledge | 15 | 50 | 0.53 | 0.20 | 0.20 |  |
| model2vec potion-base-8M | 50 | ho-filter-tx-biology | filtered | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | ho-filter-cheap-public-cs | filtered | 8 | 23 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | ho-ca-biology | state_name | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | ho-ny-computer-science | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | ho-mi-engineering | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | ho-il-private | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | ho-west-public | exact_vocabulary | 13 | 10 | 0.69 | 0.90 | 0.90 |  |
| hybrid: lexical + model2vec (RRF) | 10 | ho-urban-private | exact_vocabulary | 29 | 10 | 0.34 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | ho-large-south-public | exact_vocabulary | 24 | 10 | 0.42 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | ho-division-iii | exact_vocabulary | 9 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | ho-pre-med | synonym | 45 | 10 | 0.20 | 0.90 | 0.90 |  |
| hybrid: lexical + model2vec (RRF) | 10 | ho-economics | synonym | 39 | 10 | 0.03 | 0.10 | 0.10 |  |
| hybrid: lexical + model2vec (RRF) | 10 | ho-software | synonym | 53 | 10 | 0.19 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | ho-affordable | structured_only | 41 | 10 | 0.10 | 0.40 | 0.40 |  |
| hybrid: lexical + model2vec (RRF) | 10 | ho-highly-selective | structured_only | 20 | 10 | 0.00 | 0.00 | 0.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | ho-big-ten | world_knowledge | 15 | 10 | 0.07 | 0.10 | 0.10 |  |
| hybrid: lexical + model2vec (RRF) | 10 | ho-filter-tx-biology | filtered | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | ho-filter-cheap-public-cs | filtered | 8 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | ho-ca-biology | state_name | 4 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | ho-ny-computer-science | state_name | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | ho-mi-engineering | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | ho-il-private | state_name | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | ho-west-public | exact_vocabulary | 13 | 25 | 1.00 | 0.90 | 0.90 |  |
| hybrid: lexical + model2vec (RRF) | 25 | ho-urban-private | exact_vocabulary | 29 | 25 | 0.83 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | ho-large-south-public | exact_vocabulary | 24 | 25 | 0.96 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | ho-division-iii | exact_vocabulary | 9 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | ho-pre-med | synonym | 45 | 25 | 0.38 | 0.90 | 0.90 |  |
| hybrid: lexical + model2vec (RRF) | 25 | ho-economics | synonym | 39 | 25 | 0.21 | 0.10 | 0.10 |  |
| hybrid: lexical + model2vec (RRF) | 25 | ho-software | synonym | 53 | 25 | 0.47 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | ho-affordable | structured_only | 41 | 25 | 0.20 | 0.40 | 0.40 |  |
| hybrid: lexical + model2vec (RRF) | 25 | ho-highly-selective | structured_only | 20 | 25 | 0.25 | 0.00 | 0.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | ho-big-ten | world_knowledge | 15 | 25 | 0.20 | 0.10 | 0.10 |  |
| hybrid: lexical + model2vec (RRF) | 25 | ho-filter-tx-biology | filtered | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | ho-filter-cheap-public-cs | filtered | 8 | 23 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | ho-ca-biology | state_name | 4 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | ho-ny-computer-science | state_name | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | ho-mi-engineering | state_name | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | ho-il-private | state_name | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | ho-west-public | exact_vocabulary | 13 | 50 | 1.00 | 0.90 | 0.90 |  |
| hybrid: lexical + model2vec (RRF) | 50 | ho-urban-private | exact_vocabulary | 29 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | ho-large-south-public | exact_vocabulary | 24 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | ho-division-iii | exact_vocabulary | 9 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | ho-pre-med | synonym | 45 | 50 | 0.69 | 0.90 | 0.90 |  |
| hybrid: lexical + model2vec (RRF) | 50 | ho-economics | synonym | 39 | 50 | 0.62 | 0.10 | 0.10 |  |
| hybrid: lexical + model2vec (RRF) | 50 | ho-software | synonym | 53 | 50 | 0.85 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | ho-affordable | structured_only | 41 | 50 | 0.44 | 0.40 | 0.40 |  |
| hybrid: lexical + model2vec (RRF) | 50 | ho-highly-selective | structured_only | 20 | 50 | 0.60 | 0.00 | 0.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | ho-big-ten | world_knowledge | 15 | 50 | 0.47 | 0.10 | 0.10 |  |
| hybrid: lexical + model2vec (RRF) | 50 | ho-filter-tx-biology | filtered | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | ho-filter-cheap-public-cs | filtered | 8 | 23 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | ho-ca-biology | state_name | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | ho-ny-computer-science | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | ho-mi-engineering | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | ho-il-private | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | ho-west-public | exact_vocabulary | 13 | 10 | 0.62 | 0.80 | 0.80 |  |
| hybrid: full-text + model2vec (RRF) | 10 | ho-urban-private | exact_vocabulary | 29 | 10 | 0.34 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | ho-large-south-public | exact_vocabulary | 24 | 10 | 0.38 | 0.90 | 0.90 |  |
| hybrid: full-text + model2vec (RRF) | 10 | ho-division-iii | exact_vocabulary | 9 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | ho-pre-med | synonym | 45 | 10 | 0.20 | 0.90 | 0.90 |  |
| hybrid: full-text + model2vec (RRF) | 10 | ho-economics | synonym | 39 | 10 | 0.03 | 0.10 | 0.10 |  |
| hybrid: full-text + model2vec (RRF) | 10 | ho-software | synonym | 53 | 10 | 0.19 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | ho-affordable | structured_only | 41 | 10 | 0.10 | 0.40 | 0.40 |  |
| hybrid: full-text + model2vec (RRF) | 10 | ho-highly-selective | structured_only | 20 | 10 | 0.00 | 0.00 | 0.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | ho-big-ten | world_knowledge | 15 | 10 | 0.07 | 0.10 | 0.10 |  |
| hybrid: full-text + model2vec (RRF) | 10 | ho-filter-tx-biology | filtered | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | ho-filter-cheap-public-cs | filtered | 8 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | ho-ca-biology | state_name | 4 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | ho-ny-computer-science | state_name | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | ho-mi-engineering | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | ho-il-private | state_name | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | ho-west-public | exact_vocabulary | 13 | 25 | 1.00 | 0.80 | 0.80 |  |
| hybrid: full-text + model2vec (RRF) | 25 | ho-urban-private | exact_vocabulary | 29 | 25 | 0.79 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | ho-large-south-public | exact_vocabulary | 24 | 25 | 0.96 | 0.90 | 0.90 |  |
| hybrid: full-text + model2vec (RRF) | 25 | ho-division-iii | exact_vocabulary | 9 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | ho-pre-med | synonym | 45 | 25 | 0.38 | 0.90 | 0.90 |  |
| hybrid: full-text + model2vec (RRF) | 25 | ho-economics | synonym | 39 | 25 | 0.21 | 0.10 | 0.10 |  |
| hybrid: full-text + model2vec (RRF) | 25 | ho-software | synonym | 53 | 25 | 0.47 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | ho-affordable | structured_only | 41 | 25 | 0.20 | 0.40 | 0.40 |  |
| hybrid: full-text + model2vec (RRF) | 25 | ho-highly-selective | structured_only | 20 | 25 | 0.20 | 0.00 | 0.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | ho-big-ten | world_knowledge | 15 | 25 | 0.20 | 0.10 | 0.10 |  |
| hybrid: full-text + model2vec (RRF) | 25 | ho-filter-tx-biology | filtered | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | ho-filter-cheap-public-cs | filtered | 8 | 23 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | ho-ca-biology | state_name | 4 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | ho-ny-computer-science | state_name | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | ho-mi-engineering | state_name | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | ho-il-private | state_name | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | ho-west-public | exact_vocabulary | 13 | 50 | 1.00 | 0.80 | 0.80 |  |
| hybrid: full-text + model2vec (RRF) | 50 | ho-urban-private | exact_vocabulary | 29 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | ho-large-south-public | exact_vocabulary | 24 | 50 | 1.00 | 0.90 | 0.90 |  |
| hybrid: full-text + model2vec (RRF) | 50 | ho-division-iii | exact_vocabulary | 9 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | ho-pre-med | synonym | 45 | 50 | 0.69 | 0.90 | 0.90 |  |
| hybrid: full-text + model2vec (RRF) | 50 | ho-economics | synonym | 39 | 50 | 0.62 | 0.10 | 0.10 |  |
| hybrid: full-text + model2vec (RRF) | 50 | ho-software | synonym | 53 | 50 | 0.85 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | ho-affordable | structured_only | 41 | 50 | 0.44 | 0.40 | 0.40 |  |
| hybrid: full-text + model2vec (RRF) | 50 | ho-highly-selective | structured_only | 20 | 50 | 0.65 | 0.00 | 0.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | ho-big-ten | world_knowledge | 15 | 50 | 0.47 | 0.10 | 0.10 |  |
| hybrid: full-text + model2vec (RRF) | 50 | ho-filter-tx-biology | filtered | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | ho-filter-cheap-public-cs | filtered | 8 | 23 | 1.00 | 1.00 | 1.00 |  |
