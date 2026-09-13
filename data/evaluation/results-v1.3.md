35 queries over 92 schools; candidate limits [10, 25, 50]; RANKING_VERSION v1.3, document v3.0
queries per category: {'exact_vocabulary': 10, 'filtered': 6, 'state_name': 6, 'structured_only': 3, 'synonym': 7, 'world_knowledge': 3}
production equivalence: 210 query runs match the real SemanticSearchService exactly

## Overall

| configuration | limit | pool recall | retriever P@10 | end-to-end P@10 | filtered queries empty | mean fit (page) | p50 / p95 ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| before v1.2: hash | 10 | 0.45 | 0.46 | 0.46 | 5/6 | 77.6 | 1.51 / 1.89 |
| before v1.2: hash | 25 | 0.64 | 0.51 | 0.34 | 3/6 | 80.3 | 2.61 / 3.70 |
| before v1.2: hash | 50 | 0.85 | 0.60 | 0.35 | 0/6 | 81.5 | 3.84 / 4.14 |
| before v1.2: lexical fallback | 10 | 0.54 | 0.54 | 0.54 | 6/6 | 76.4 | 0.91 / 1.23 |
| before v1.2: lexical fallback | 25 | 0.72 | 0.60 | 0.36 | 4/6 | 80.1 | 1.70 / 1.93 |
| before v1.2: lexical fallback | 50 | 0.85 | 0.66 | 0.30 | 2/6 | 81.3 | 3.11 / 3.37 |
| v1.2: hash | 10 | 0.75 | 0.75 | 0.75 | 0/6 | 77.6 | 1.56 / 2.15 |
| v1.2: hash | 25 | 0.88 | 0.75 | 0.77 | 0/6 | 78.0 | 2.23 / 2.47 |
| v1.2: hash | 50 | 0.93 | 0.75 | 0.77 | 0/6 | 78.1 | 3.53 / 3.77 |
| v1.3 production: full-text | 10 | 0.86 | 0.87 | 0.87 | 0/6 | 77.5 | 5.52 / 6.45 |
| v1.3 production: full-text | 25 | 0.92 | 0.87 | 0.87 | 0/6 | 79.6 | 6.56 / 7.48 |
| v1.3 production: full-text | 50 | 0.95 | 0.87 | 0.86 | 0/6 | 80.0 | 7.54 / 8.96 |
| v1.3 production: lexical fallback | 10 | 0.84 | 0.84 | 0.84 | 0/6 | 77.6 | 0.87 / 0.94 |
| v1.3 production: lexical fallback | 25 | 0.93 | 0.84 | 0.86 | 0/6 | 79.5 | 1.67 / 1.78 |
| v1.3 production: lexical fallback | 50 | 0.95 | 0.84 | 0.86 | 0/6 | 79.8 | 2.98 / 4.28 |
| model2vec potion-base-8M | 10 | 0.86 | 0.86 | 0.86 | 0/6 | 77.8 | 0.93 / 1.11 |
| model2vec potion-base-8M | 25 | 0.96 | 0.86 | 0.86 | 0/6 | 77.8 | 1.74 / 1.87 |
| model2vec potion-base-8M | 50 | 0.99 | 0.86 | 0.86 | 0/6 | 77.8 | 3.04 / 3.45 |
| hybrid: lexical + model2vec (RRF) | 10 | 0.91 | 0.91 | 0.91 | 0/6 | 77.9 | 0.93 / 1.16 |
| hybrid: lexical + model2vec (RRF) | 25 | 0.94 | 0.91 | 0.91 | 0/6 | 77.9 | 1.66 / 1.73 |
| hybrid: lexical + model2vec (RRF) | 50 | 0.98 | 0.91 | 0.91 | 0/6 | 77.9 | 2.96 / 3.14 |
| hybrid: full-text + model2vec (RRF) | 10 | 0.88 | 0.89 | 0.89 | 0/6 | 77.8 | 5.74 / 6.34 |
| hybrid: full-text + model2vec (RRF) | 25 | 0.95 | 0.89 | 0.89 | 0/6 | 77.8 | 6.94 / 8.23 |
| hybrid: full-text + model2vec (RRF) | 50 | 0.99 | 0.89 | 0.89 | 0/6 | 77.8 | 7.79 / 9.81 |

## End-to-end P@10 by query category, candidate limit 50

| configuration | exact_vocabulary | filtered | state_name | structured_only | synonym | world_knowledge |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| before v1.2: hash | 0.20 | 1.00 | 0.32 | 0.21 | 0.16 | 0.21 |
| before v1.2: lexical fallback | 0.23 | 0.67 | 0.28 | 0.18 | 0.26 | 0.00 |
| v1.2: hash | 0.88 | 1.00 | 0.98 | 0.60 | 0.62 | 0.00 |
| v1.3 production: full-text | 1.00 | 1.00 | 0.97 | 0.93 | 0.78 | 0.00 |
| v1.3 production: lexical fallback | 0.94 | 1.00 | 1.00 | 0.74 | 0.93 | 0.00 |
| model2vec potion-base-8M | 0.96 | 1.00 | 1.00 | 0.61 | 0.85 | 0.29 |
| hybrid: lexical + model2vec (RRF) | 0.98 | 1.00 | 1.00 | 0.87 | 0.98 | 0.25 |
| hybrid: full-text + model2vec (RRF) | 0.98 | 1.00 | 1.00 | 0.80 | 0.87 | 0.25 |

## Per query

| configuration | limit | query | category | relevant | pool | pool recall | retriever P@10 | end-to-end P@10 | empty |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| before v1.2: hash | 10 | tx-engineering | state_name | 5 | 10 | 0.80 | 0.80 | 0.80 |  |
| before v1.2: hash | 10 | ca-computer-science | state_name | 3 | 10 | 0.67 | 0.67 | 0.67 |  |
| before v1.2: hash | 10 | fl-business | state_name | 7 | 10 | 0.14 | 0.14 | 0.14 |  |
| before v1.2: hash | 10 | ma-private | state_name | 6 | 10 | 0.17 | 0.17 | 0.17 |  |
| before v1.2: hash | 10 | tx-health | state_name | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| before v1.2: hash | 10 | ga-psychology | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: hash | 10 | midwest-public | exact_vocabulary | 9 | 10 | 0.89 | 0.89 | 0.89 |  |
| before v1.2: hash | 10 | south-suburban | exact_vocabulary | 8 | 10 | 0.75 | 0.75 | 0.75 |  |
| before v1.2: hash | 10 | small-private | exact_vocabulary | 6 | 10 | 0.67 | 0.67 | 0.67 |  |
| before v1.2: hash | 10 | town-setting | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: hash | 10 | northeast-mathematics | exact_vocabulary | 5 | 10 | 0.80 | 0.80 | 0.80 |  |
| before v1.2: hash | 10 | agriculture | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: hash | 10 | legal-studies | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: hash | 10 | education | exact_vocabulary | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| before v1.2: hash | 10 | criminal-justice | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: hash | 10 | performing-arts | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: hash | 10 | division-three | synonym | 9 | 10 | 0.22 | 0.22 | 0.22 |  |
| before v1.2: hash | 10 | division-two | synonym | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| before v1.2: hash | 10 | fl-nursing | synonym | 5 | 10 | 0.40 | 0.40 | 0.40 |  |
| before v1.2: hash | 10 | oh-big-state | synonym | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| before v1.2: hash | 10 | ga-tech-focused | synonym | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| before v1.2: hash | 10 | midwest-coding | synonym | 6 | 10 | 0.33 | 0.33 | 0.33 |  |
| before v1.2: hash | 10 | film-theater | synonym | 5 | 10 | 0.20 | 0.20 | 0.20 |  |
| before v1.2: hash | 10 | bay-area-cs | world_knowledge | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| before v1.2: hash | 10 | hbcu | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| before v1.2: hash | 10 | ivy-league | world_knowledge | 8 | 10 | 0.12 | 0.12 | 0.12 |  |
| before v1.2: hash | 10 | tx-cheap-public | structured_only | 4 | 10 | 0.25 | 0.25 | 0.25 |  |
| before v1.2: hash | 10 | small-classes | structured_only | 17 | 10 | 0.12 | 0.20 | 0.20 |  |
| before v1.2: hash | 10 | south-selective-private | structured_only | 6 | 10 | 0.33 | 0.33 | 0.33 |  |
| before v1.2: hash | 10 | filter-or-engineering | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| before v1.2: hash | 10 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: hash | 10 | filter-ut-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| before v1.2: hash | 10 | filter-dc-social-sciences | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| before v1.2: hash | 10 | filter-ms-health | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| before v1.2: hash | 10 | filter-private-affordable-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| before v1.2: hash | 25 | tx-engineering | state_name | 5 | 25 | 1.00 | 0.80 | 0.40 |  |
| before v1.2: hash | 25 | ca-computer-science | state_name | 3 | 25 | 1.00 | 0.67 | 1.00 |  |
| before v1.2: hash | 25 | fl-business | state_name | 7 | 25 | 0.29 | 0.14 | 0.14 |  |
| before v1.2: hash | 25 | ma-private | state_name | 6 | 25 | 0.67 | 0.17 | 0.17 |  |
| before v1.2: hash | 25 | tx-health | state_name | 2 | 25 | 1.00 | 0.50 | 0.00 |  |
| before v1.2: hash | 25 | ga-psychology | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: hash | 25 | midwest-public | exact_vocabulary | 9 | 25 | 1.00 | 0.89 | 0.56 |  |
| before v1.2: hash | 25 | south-suburban | exact_vocabulary | 8 | 25 | 1.00 | 0.75 | 0.50 |  |
| before v1.2: hash | 25 | small-private | exact_vocabulary | 6 | 25 | 0.83 | 0.67 | 0.50 |  |
| before v1.2: hash | 25 | town-setting | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| before v1.2: hash | 25 | northeast-mathematics | exact_vocabulary | 5 | 25 | 1.00 | 0.80 | 0.80 |  |
| before v1.2: hash | 25 | agriculture | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: hash | 25 | legal-studies | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| before v1.2: hash | 25 | education | exact_vocabulary | 2 | 25 | 1.00 | 0.50 | 0.00 |  |
| before v1.2: hash | 25 | criminal-justice | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| before v1.2: hash | 25 | performing-arts | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 0.20 |  |
| before v1.2: hash | 25 | division-three | synonym | 9 | 25 | 0.33 | 0.22 | 0.22 |  |
| before v1.2: hash | 25 | division-two | synonym | 2 | 25 | 0.00 | 0.00 | 0.00 |  |
| before v1.2: hash | 25 | fl-nursing | synonym | 5 | 25 | 0.60 | 0.40 | 0.00 |  |
| before v1.2: hash | 25 | oh-big-state | synonym | 2 | 25 | 0.00 | 0.00 | 0.00 |  |
| before v1.2: hash | 25 | ga-tech-focused | synonym | 2 | 25 | 0.50 | 0.50 | 0.50 |  |
| before v1.2: hash | 25 | midwest-coding | synonym | 6 | 25 | 0.50 | 0.33 | 0.50 |  |
| before v1.2: hash | 25 | film-theater | synonym | 5 | 25 | 0.20 | 0.20 | 0.00 |  |
| before v1.2: hash | 25 | bay-area-cs | world_knowledge | 2 | 25 | 0.50 | 0.50 | 0.50 |  |
| before v1.2: hash | 25 | hbcu | world_knowledge | 2 | 25 | 0.00 | 0.00 | 0.00 |  |
| before v1.2: hash | 25 | ivy-league | world_knowledge | 8 | 25 | 0.50 | 0.12 | 0.25 |  |
| before v1.2: hash | 25 | tx-cheap-public | structured_only | 4 | 25 | 0.75 | 0.25 | 0.00 |  |
| before v1.2: hash | 25 | small-classes | structured_only | 17 | 25 | 0.24 | 0.20 | 0.20 |  |
| before v1.2: hash | 25 | south-selective-private | structured_only | 6 | 25 | 0.67 | 0.33 | 0.50 |  |
| before v1.2: hash | 25 | filter-or-engineering | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| before v1.2: hash | 25 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: hash | 25 | filter-ut-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| before v1.2: hash | 25 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: hash | 25 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: hash | 25 | filter-private-affordable-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| before v1.2: hash | 50 | tx-engineering | state_name | 5 | 50 | 1.00 | 0.80 | 0.40 |  |
| before v1.2: hash | 50 | ca-computer-science | state_name | 3 | 50 | 1.00 | 0.67 | 0.33 |  |
| before v1.2: hash | 50 | fl-business | state_name | 7 | 50 | 0.86 | 0.14 | 0.00 |  |
| before v1.2: hash | 50 | ma-private | state_name | 6 | 50 | 1.00 | 0.17 | 0.17 |  |
| before v1.2: hash | 50 | tx-health | state_name | 2 | 50 | 1.00 | 0.50 | 0.00 |  |
| before v1.2: hash | 50 | ga-psychology | state_name | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: hash | 50 | midwest-public | exact_vocabulary | 9 | 50 | 1.00 | 0.89 | 0.33 |  |
| before v1.2: hash | 50 | south-suburban | exact_vocabulary | 8 | 50 | 1.00 | 0.75 | 0.12 |  |
| before v1.2: hash | 50 | small-private | exact_vocabulary | 6 | 50 | 0.83 | 0.67 | 0.17 |  |
| before v1.2: hash | 50 | town-setting | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| before v1.2: hash | 50 | northeast-mathematics | exact_vocabulary | 5 | 50 | 1.00 | 0.80 | 0.20 |  |
| before v1.2: hash | 50 | agriculture | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: hash | 50 | legal-studies | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| before v1.2: hash | 50 | education | exact_vocabulary | 2 | 50 | 1.00 | 0.50 | 0.00 |  |
| before v1.2: hash | 50 | criminal-justice | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| before v1.2: hash | 50 | performing-arts | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 0.20 |  |
| before v1.2: hash | 50 | division-three | synonym | 9 | 50 | 0.67 | 0.22 | 0.11 |  |
| before v1.2: hash | 50 | division-two | synonym | 2 | 50 | 0.00 | 0.00 | 0.00 |  |
| before v1.2: hash | 50 | fl-nursing | synonym | 5 | 50 | 0.80 | 0.40 | 0.00 |  |
| before v1.2: hash | 50 | oh-big-state | synonym | 2 | 50 | 0.00 | 0.00 | 0.00 |  |
| before v1.2: hash | 50 | ga-tech-focused | synonym | 2 | 50 | 1.00 | 0.50 | 0.50 |  |
| before v1.2: hash | 50 | midwest-coding | synonym | 6 | 50 | 1.00 | 0.33 | 0.50 |  |
| before v1.2: hash | 50 | film-theater | synonym | 5 | 50 | 0.60 | 0.20 | 0.00 |  |
| before v1.2: hash | 50 | bay-area-cs | world_knowledge | 2 | 50 | 1.00 | 0.50 | 0.50 |  |
| before v1.2: hash | 50 | hbcu | world_knowledge | 2 | 50 | 0.00 | 0.00 | 0.00 |  |
| before v1.2: hash | 50 | ivy-league | world_knowledge | 8 | 50 | 0.88 | 0.12 | 0.12 |  |
| before v1.2: hash | 50 | tx-cheap-public | structured_only | 4 | 50 | 0.75 | 0.25 | 0.00 |  |
| before v1.2: hash | 50 | small-classes | structured_only | 17 | 50 | 0.59 | 0.20 | 0.30 |  |
| before v1.2: hash | 50 | south-selective-private | structured_only | 6 | 50 | 0.83 | 0.33 | 0.33 |  |
| before v1.2: hash | 50 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: hash | 50 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: hash | 50 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: hash | 50 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: hash | 50 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: hash | 50 | filter-private-affordable-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 10 | tx-engineering | state_name | 5 | 10 | 0.80 | 0.80 | 0.80 |  |
| before v1.2: lexical fallback | 10 | ca-computer-science | state_name | 3 | 10 | 0.67 | 0.67 | 0.67 |  |
| before v1.2: lexical fallback | 10 | fl-business | state_name | 7 | 10 | 0.86 | 0.86 | 0.86 |  |
| before v1.2: lexical fallback | 10 | ma-private | state_name | 6 | 10 | 0.17 | 0.17 | 0.17 |  |
| before v1.2: lexical fallback | 10 | tx-health | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 10 | ga-psychology | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 10 | midwest-public | exact_vocabulary | 9 | 10 | 0.56 | 0.56 | 0.56 |  |
| before v1.2: lexical fallback | 10 | south-suburban | exact_vocabulary | 8 | 10 | 0.62 | 0.62 | 0.62 |  |
| before v1.2: lexical fallback | 10 | small-private | exact_vocabulary | 6 | 10 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 10 | town-setting | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 10 | northeast-mathematics | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 10 | agriculture | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 10 | legal-studies | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 10 | education | exact_vocabulary | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 10 | criminal-justice | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 10 | performing-arts | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 10 | division-three | synonym | 9 | 10 | 0.11 | 0.11 | 0.11 |  |
| before v1.2: lexical fallback | 10 | division-two | synonym | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| before v1.2: lexical fallback | 10 | fl-nursing | synonym | 5 | 10 | 0.80 | 0.80 | 0.80 |  |
| before v1.2: lexical fallback | 10 | oh-big-state | synonym | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| before v1.2: lexical fallback | 10 | ga-tech-focused | synonym | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| before v1.2: lexical fallback | 10 | midwest-coding | synonym | 6 | 10 | 0.67 | 0.67 | 0.67 |  |
| before v1.2: lexical fallback | 10 | film-theater | synonym | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 10 | bay-area-cs | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| before v1.2: lexical fallback | 10 | hbcu | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| before v1.2: lexical fallback | 10 | ivy-league | world_knowledge | 8 | 10 | 0.00 | 0.00 | 0.00 |  |
| before v1.2: lexical fallback | 10 | tx-cheap-public | structured_only | 4 | 10 | 0.75 | 0.75 | 0.75 |  |
| before v1.2: lexical fallback | 10 | small-classes | structured_only | 17 | 10 | 0.24 | 0.40 | 0.40 |  |
| before v1.2: lexical fallback | 10 | south-selective-private | structured_only | 6 | 10 | 0.67 | 0.67 | 0.67 |  |
| before v1.2: lexical fallback | 10 | filter-or-engineering | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| before v1.2: lexical fallback | 10 | filter-wa-computer-science | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| before v1.2: lexical fallback | 10 | filter-ut-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| before v1.2: lexical fallback | 10 | filter-dc-social-sciences | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| before v1.2: lexical fallback | 10 | filter-ms-health | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| before v1.2: lexical fallback | 10 | filter-private-affordable-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| before v1.2: lexical fallback | 25 | tx-engineering | state_name | 5 | 25 | 0.80 | 0.80 | 0.20 |  |
| before v1.2: lexical fallback | 25 | ca-computer-science | state_name | 3 | 25 | 0.67 | 0.67 | 0.67 |  |
| before v1.2: lexical fallback | 25 | fl-business | state_name | 7 | 25 | 1.00 | 0.86 | 0.43 |  |
| before v1.2: lexical fallback | 25 | ma-private | state_name | 6 | 25 | 1.00 | 0.17 | 0.33 |  |
| before v1.2: lexical fallback | 25 | tx-health | state_name | 2 | 25 | 1.00 | 1.00 | 0.00 |  |
| before v1.2: lexical fallback | 25 | ga-psychology | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 25 | midwest-public | exact_vocabulary | 9 | 25 | 1.00 | 0.56 | 0.67 |  |
| before v1.2: lexical fallback | 25 | south-suburban | exact_vocabulary | 8 | 25 | 1.00 | 0.62 | 0.50 |  |
| before v1.2: lexical fallback | 25 | small-private | exact_vocabulary | 6 | 25 | 1.00 | 1.00 | 0.50 |  |
| before v1.2: lexical fallback | 25 | town-setting | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| before v1.2: lexical fallback | 25 | northeast-mathematics | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 0.80 |  |
| before v1.2: lexical fallback | 25 | agriculture | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 25 | legal-studies | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| before v1.2: lexical fallback | 25 | education | exact_vocabulary | 2 | 25 | 1.00 | 1.00 | 0.00 |  |
| before v1.2: lexical fallback | 25 | criminal-justice | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| before v1.2: lexical fallback | 25 | performing-arts | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 0.20 |  |
| before v1.2: lexical fallback | 25 | division-three | synonym | 9 | 25 | 0.11 | 0.11 | 0.11 |  |
| before v1.2: lexical fallback | 25 | division-two | synonym | 2 | 25 | 0.50 | 0.00 | 0.50 |  |
| before v1.2: lexical fallback | 25 | fl-nursing | synonym | 5 | 25 | 0.80 | 0.80 | 0.00 |  |
| before v1.2: lexical fallback | 25 | oh-big-state | synonym | 2 | 25 | 0.50 | 0.50 | 0.50 |  |
| before v1.2: lexical fallback | 25 | ga-tech-focused | synonym | 2 | 25 | 0.50 | 0.50 | 0.50 |  |
| before v1.2: lexical fallback | 25 | midwest-coding | synonym | 6 | 25 | 1.00 | 0.67 | 1.00 |  |
| before v1.2: lexical fallback | 25 | film-theater | synonym | 5 | 25 | 1.00 | 1.00 | 0.20 |  |
| before v1.2: lexical fallback | 25 | bay-area-cs | world_knowledge | 2 | 25 | 0.50 | 0.00 | 0.50 |  |
| before v1.2: lexical fallback | 25 | hbcu | world_knowledge | 2 | 25 | 0.50 | 0.00 | 0.00 |  |
| before v1.2: lexical fallback | 25 | ivy-league | world_knowledge | 8 | 25 | 0.12 | 0.00 | 0.00 |  |
| before v1.2: lexical fallback | 25 | tx-cheap-public | structured_only | 4 | 25 | 0.75 | 0.75 | 0.00 |  |
| before v1.2: lexical fallback | 25 | small-classes | structured_only | 17 | 25 | 0.29 | 0.40 | 0.30 |  |
| before v1.2: lexical fallback | 25 | south-selective-private | structured_only | 6 | 25 | 1.00 | 0.67 | 0.67 |  |
| before v1.2: lexical fallback | 25 | filter-or-engineering | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| before v1.2: lexical fallback | 25 | filter-wa-computer-science | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| before v1.2: lexical fallback | 25 | filter-ut-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| before v1.2: lexical fallback | 25 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 25 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 25 | filter-private-affordable-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| before v1.2: lexical fallback | 50 | tx-engineering | state_name | 5 | 50 | 1.00 | 0.80 | 0.40 |  |
| before v1.2: lexical fallback | 50 | ca-computer-science | state_name | 3 | 50 | 1.00 | 0.67 | 0.00 |  |
| before v1.2: lexical fallback | 50 | fl-business | state_name | 7 | 50 | 1.00 | 0.86 | 0.14 |  |
| before v1.2: lexical fallback | 50 | ma-private | state_name | 6 | 50 | 1.00 | 0.17 | 0.17 |  |
| before v1.2: lexical fallback | 50 | tx-health | state_name | 2 | 50 | 1.00 | 1.00 | 0.00 |  |
| before v1.2: lexical fallback | 50 | ga-psychology | state_name | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 50 | midwest-public | exact_vocabulary | 9 | 50 | 1.00 | 0.56 | 0.33 |  |
| before v1.2: lexical fallback | 50 | south-suburban | exact_vocabulary | 8 | 50 | 1.00 | 0.62 | 0.25 |  |
| before v1.2: lexical fallback | 50 | small-private | exact_vocabulary | 6 | 50 | 1.00 | 1.00 | 0.33 |  |
| before v1.2: lexical fallback | 50 | town-setting | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| before v1.2: lexical fallback | 50 | northeast-mathematics | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 0.20 |  |
| before v1.2: lexical fallback | 50 | agriculture | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 50 | legal-studies | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| before v1.2: lexical fallback | 50 | education | exact_vocabulary | 2 | 50 | 1.00 | 1.00 | 0.00 |  |
| before v1.2: lexical fallback | 50 | criminal-justice | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| before v1.2: lexical fallback | 50 | performing-arts | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 0.20 |  |
| before v1.2: lexical fallback | 50 | division-three | synonym | 9 | 50 | 0.67 | 0.11 | 0.11 |  |
| before v1.2: lexical fallback | 50 | division-two | synonym | 2 | 50 | 1.00 | 0.00 | 0.50 |  |
| before v1.2: lexical fallback | 50 | fl-nursing | synonym | 5 | 50 | 1.00 | 0.80 | 0.00 |  |
| before v1.2: lexical fallback | 50 | oh-big-state | synonym | 2 | 50 | 0.50 | 0.50 | 0.00 |  |
| before v1.2: lexical fallback | 50 | ga-tech-focused | synonym | 2 | 50 | 0.50 | 0.50 | 0.50 |  |
| before v1.2: lexical fallback | 50 | midwest-coding | synonym | 6 | 50 | 1.00 | 0.67 | 0.50 |  |
| before v1.2: lexical fallback | 50 | film-theater | synonym | 5 | 50 | 1.00 | 1.00 | 0.20 |  |
| before v1.2: lexical fallback | 50 | bay-area-cs | world_knowledge | 2 | 50 | 0.50 | 0.00 | 0.00 |  |
| before v1.2: lexical fallback | 50 | hbcu | world_knowledge | 2 | 50 | 1.00 | 0.00 | 0.00 |  |
| before v1.2: lexical fallback | 50 | ivy-league | world_knowledge | 8 | 50 | 0.25 | 0.00 | 0.00 |  |
| before v1.2: lexical fallback | 50 | tx-cheap-public | structured_only | 4 | 50 | 0.75 | 0.75 | 0.00 |  |
| before v1.2: lexical fallback | 50 | small-classes | structured_only | 17 | 50 | 0.59 | 0.40 | 0.20 |  |
| before v1.2: lexical fallback | 50 | south-selective-private | structured_only | 6 | 50 | 1.00 | 0.67 | 0.33 |  |
| before v1.2: lexical fallback | 50 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 50 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 50 | filter-ut-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| before v1.2: lexical fallback | 50 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 50 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| before v1.2: lexical fallback | 50 | filter-private-affordable-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| v1.2: hash | 10 | tx-engineering | state_name | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | ca-computer-science | state_name | 3 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | fl-business | state_name | 7 | 10 | 0.86 | 0.86 | 0.86 |  |
| v1.2: hash | 10 | ma-private | state_name | 6 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | tx-health | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | ga-psychology | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | midwest-public | exact_vocabulary | 9 | 10 | 0.67 | 0.67 | 0.67 |  |
| v1.2: hash | 10 | south-suburban | exact_vocabulary | 8 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | small-private | exact_vocabulary | 6 | 10 | 0.67 | 0.67 | 0.67 |  |
| v1.2: hash | 10 | town-setting | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | northeast-mathematics | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | agriculture | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | legal-studies | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | education | exact_vocabulary | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| v1.2: hash | 10 | criminal-justice | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | performing-arts | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | division-three | synonym | 9 | 10 | 0.67 | 0.67 | 0.67 |  |
| v1.2: hash | 10 | division-two | synonym | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| v1.2: hash | 10 | fl-nursing | synonym | 5 | 10 | 0.80 | 0.80 | 0.80 |  |
| v1.2: hash | 10 | oh-big-state | synonym | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| v1.2: hash | 10 | ga-tech-focused | synonym | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | midwest-coding | synonym | 6 | 10 | 0.17 | 0.17 | 0.17 |  |
| v1.2: hash | 10 | film-theater | synonym | 5 | 10 | 0.20 | 0.20 | 0.20 |  |
| v1.2: hash | 10 | bay-area-cs | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| v1.2: hash | 10 | hbcu | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| v1.2: hash | 10 | ivy-league | world_knowledge | 8 | 10 | 0.00 | 0.00 | 0.00 |  |
| v1.2: hash | 10 | tx-cheap-public | structured_only | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | small-classes | structured_only | 17 | 10 | 0.18 | 0.30 | 0.30 |  |
| v1.2: hash | 10 | south-selective-private | structured_only | 6 | 10 | 0.50 | 0.50 | 0.50 |  |
| v1.2: hash | 10 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 10 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | tx-engineering | state_name | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | ca-computer-science | state_name | 3 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | fl-business | state_name | 7 | 25 | 1.00 | 0.86 | 0.86 |  |
| v1.2: hash | 25 | ma-private | state_name | 6 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | tx-health | state_name | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | ga-psychology | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | midwest-public | exact_vocabulary | 9 | 25 | 0.89 | 0.67 | 0.67 |  |
| v1.2: hash | 25 | south-suburban | exact_vocabulary | 8 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | small-private | exact_vocabulary | 6 | 25 | 1.00 | 0.67 | 0.67 |  |
| v1.2: hash | 25 | town-setting | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | northeast-mathematics | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | agriculture | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | legal-studies | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | education | exact_vocabulary | 2 | 25 | 1.00 | 0.50 | 0.50 |  |
| v1.2: hash | 25 | criminal-justice | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | performing-arts | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | division-three | synonym | 9 | 25 | 0.89 | 0.67 | 0.67 |  |
| v1.2: hash | 25 | division-two | synonym | 2 | 25 | 1.00 | 0.50 | 1.00 |  |
| v1.2: hash | 25 | fl-nursing | synonym | 5 | 25 | 1.00 | 0.80 | 0.80 |  |
| v1.2: hash | 25 | oh-big-state | synonym | 2 | 25 | 0.50 | 0.50 | 0.50 |  |
| v1.2: hash | 25 | ga-tech-focused | synonym | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | midwest-coding | synonym | 6 | 25 | 0.83 | 0.17 | 0.17 |  |
| v1.2: hash | 25 | film-theater | synonym | 5 | 25 | 0.60 | 0.20 | 0.20 |  |
| v1.2: hash | 25 | bay-area-cs | world_knowledge | 2 | 25 | 0.50 | 0.00 | 0.00 |  |
| v1.2: hash | 25 | hbcu | world_knowledge | 2 | 25 | 0.00 | 0.00 | 0.00 |  |
| v1.2: hash | 25 | ivy-league | world_knowledge | 8 | 25 | 0.25 | 0.00 | 0.00 |  |
| v1.2: hash | 25 | tx-cheap-public | structured_only | 4 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | small-classes | structured_only | 17 | 25 | 0.47 | 0.30 | 0.30 |  |
| v1.2: hash | 25 | south-selective-private | structured_only | 6 | 25 | 1.00 | 0.50 | 0.50 |  |
| v1.2: hash | 25 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 25 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | tx-engineering | state_name | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | ca-computer-science | state_name | 3 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | fl-business | state_name | 7 | 50 | 1.00 | 0.86 | 0.86 |  |
| v1.2: hash | 50 | ma-private | state_name | 6 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | tx-health | state_name | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | ga-psychology | state_name | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | midwest-public | exact_vocabulary | 9 | 50 | 1.00 | 0.67 | 0.67 |  |
| v1.2: hash | 50 | south-suburban | exact_vocabulary | 8 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | small-private | exact_vocabulary | 6 | 50 | 1.00 | 0.67 | 0.67 |  |
| v1.2: hash | 50 | town-setting | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | northeast-mathematics | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | agriculture | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | legal-studies | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | education | exact_vocabulary | 2 | 50 | 1.00 | 0.50 | 0.50 |  |
| v1.2: hash | 50 | criminal-justice | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | performing-arts | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | division-three | synonym | 9 | 50 | 1.00 | 0.67 | 0.67 |  |
| v1.2: hash | 50 | division-two | synonym | 2 | 50 | 1.00 | 0.50 | 1.00 |  |
| v1.2: hash | 50 | fl-nursing | synonym | 5 | 50 | 1.00 | 0.80 | 0.80 |  |
| v1.2: hash | 50 | oh-big-state | synonym | 2 | 50 | 1.00 | 0.50 | 0.50 |  |
| v1.2: hash | 50 | ga-tech-focused | synonym | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | midwest-coding | synonym | 6 | 50 | 0.83 | 0.17 | 0.17 |  |
| v1.2: hash | 50 | film-theater | synonym | 5 | 50 | 0.60 | 0.20 | 0.20 |  |
| v1.2: hash | 50 | bay-area-cs | world_knowledge | 2 | 50 | 0.50 | 0.00 | 0.00 |  |
| v1.2: hash | 50 | hbcu | world_knowledge | 2 | 50 | 0.00 | 0.00 | 0.00 |  |
| v1.2: hash | 50 | ivy-league | world_knowledge | 8 | 50 | 1.00 | 0.00 | 0.00 |  |
| v1.2: hash | 50 | tx-cheap-public | structured_only | 4 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | small-classes | structured_only | 17 | 50 | 0.65 | 0.30 | 0.30 |  |
| v1.2: hash | 50 | south-selective-private | structured_only | 6 | 50 | 1.00 | 0.50 | 0.50 |  |
| v1.2: hash | 50 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.2: hash | 50 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | tx-engineering | state_name | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | ca-computer-science | state_name | 3 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | fl-business | state_name | 7 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | ma-private | state_name | 6 | 10 | 0.83 | 0.83 | 0.83 |  |
| v1.3 production: full-text | 10 | tx-health | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | ga-psychology | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | midwest-public | exact_vocabulary | 9 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | south-suburban | exact_vocabulary | 8 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | small-private | exact_vocabulary | 6 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | town-setting | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | northeast-mathematics | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | agriculture | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | legal-studies | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | education | exact_vocabulary | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | criminal-justice | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | performing-arts | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | division-three | synonym | 9 | 10 | 0.78 | 0.78 | 0.78 |  |
| v1.3 production: full-text | 10 | division-two | synonym | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | fl-nursing | synonym | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | oh-big-state | synonym | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | ga-tech-focused | synonym | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | midwest-coding | synonym | 6 | 10 | 0.67 | 0.67 | 0.67 |  |
| v1.3 production: full-text | 10 | film-theater | synonym | 5 | 10 | 0.20 | 0.20 | 0.20 |  |
| v1.3 production: full-text | 10 | bay-area-cs | world_knowledge | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| v1.3 production: full-text | 10 | hbcu | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| v1.3 production: full-text | 10 | ivy-league | world_knowledge | 8 | 10 | 0.00 | 0.00 | 0.00 |  |
| v1.3 production: full-text | 10 | tx-cheap-public | structured_only | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | small-classes | structured_only | 17 | 10 | 0.24 | 0.40 | 0.40 |  |
| v1.3 production: full-text | 10 | south-selective-private | structured_only | 6 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 10 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | tx-engineering | state_name | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | ca-computer-science | state_name | 3 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | fl-business | state_name | 7 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | ma-private | state_name | 6 | 25 | 1.00 | 0.83 | 0.83 |  |
| v1.3 production: full-text | 25 | tx-health | state_name | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | ga-psychology | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | midwest-public | exact_vocabulary | 9 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | south-suburban | exact_vocabulary | 8 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | small-private | exact_vocabulary | 6 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | town-setting | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | northeast-mathematics | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | agriculture | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | legal-studies | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | education | exact_vocabulary | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | criminal-justice | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | performing-arts | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | division-three | synonym | 9 | 25 | 0.89 | 0.78 | 0.78 |  |
| v1.3 production: full-text | 25 | division-two | synonym | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | fl-nursing | synonym | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | oh-big-state | synonym | 2 | 25 | 1.00 | 1.00 | 0.50 |  |
| v1.3 production: full-text | 25 | ga-tech-focused | synonym | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | midwest-coding | synonym | 6 | 25 | 1.00 | 0.67 | 1.00 |  |
| v1.3 production: full-text | 25 | film-theater | synonym | 5 | 25 | 0.40 | 0.20 | 0.20 |  |
| v1.3 production: full-text | 25 | bay-area-cs | world_knowledge | 2 | 25 | 0.50 | 0.50 | 0.50 |  |
| v1.3 production: full-text | 25 | hbcu | world_knowledge | 2 | 25 | 0.50 | 0.00 | 0.00 |  |
| v1.3 production: full-text | 25 | ivy-league | world_knowledge | 8 | 25 | 0.12 | 0.00 | 0.00 |  |
| v1.3 production: full-text | 25 | tx-cheap-public | structured_only | 4 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | small-classes | structured_only | 17 | 25 | 0.71 | 0.40 | 0.70 |  |
| v1.3 production: full-text | 25 | south-selective-private | structured_only | 6 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 25 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | tx-engineering | state_name | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | ca-computer-science | state_name | 3 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | fl-business | state_name | 7 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | ma-private | state_name | 6 | 50 | 1.00 | 0.83 | 0.83 |  |
| v1.3 production: full-text | 50 | tx-health | state_name | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | ga-psychology | state_name | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | midwest-public | exact_vocabulary | 9 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | south-suburban | exact_vocabulary | 8 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | small-private | exact_vocabulary | 6 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | town-setting | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | northeast-mathematics | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | agriculture | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | legal-studies | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | education | exact_vocabulary | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | criminal-justice | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | performing-arts | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | division-three | synonym | 9 | 50 | 1.00 | 0.78 | 0.78 |  |
| v1.3 production: full-text | 50 | division-two | synonym | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | fl-nursing | synonym | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | oh-big-state | synonym | 2 | 50 | 1.00 | 1.00 | 0.50 |  |
| v1.3 production: full-text | 50 | ga-tech-focused | synonym | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | midwest-coding | synonym | 6 | 50 | 1.00 | 0.67 | 1.00 |  |
| v1.3 production: full-text | 50 | film-theater | synonym | 5 | 50 | 0.40 | 0.20 | 0.20 |  |
| v1.3 production: full-text | 50 | bay-area-cs | world_knowledge | 2 | 50 | 0.50 | 0.50 | 0.00 |  |
| v1.3 production: full-text | 50 | hbcu | world_knowledge | 2 | 50 | 1.00 | 0.00 | 0.00 |  |
| v1.3 production: full-text | 50 | ivy-league | world_knowledge | 8 | 50 | 0.25 | 0.00 | 0.00 |  |
| v1.3 production: full-text | 50 | tx-cheap-public | structured_only | 4 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | small-classes | structured_only | 17 | 50 | 1.00 | 0.40 | 0.80 |  |
| v1.3 production: full-text | 50 | south-selective-private | structured_only | 6 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: full-text | 50 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | tx-engineering | state_name | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | ca-computer-science | state_name | 3 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | fl-business | state_name | 7 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | ma-private | state_name | 6 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | tx-health | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | ga-psychology | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | midwest-public | exact_vocabulary | 9 | 10 | 0.78 | 0.78 | 0.78 |  |
| v1.3 production: lexical fallback | 10 | south-suburban | exact_vocabulary | 8 | 10 | 0.62 | 0.62 | 0.62 |  |
| v1.3 production: lexical fallback | 10 | small-private | exact_vocabulary | 6 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | town-setting | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | northeast-mathematics | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | agriculture | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | legal-studies | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | education | exact_vocabulary | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | criminal-justice | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | performing-arts | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | division-three | synonym | 9 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | division-two | synonym | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | fl-nursing | synonym | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | oh-big-state | synonym | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| v1.3 production: lexical fallback | 10 | ga-tech-focused | synonym | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | midwest-coding | synonym | 6 | 10 | 0.50 | 0.50 | 0.50 |  |
| v1.3 production: lexical fallback | 10 | film-theater | synonym | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | bay-area-cs | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| v1.3 production: lexical fallback | 10 | hbcu | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| v1.3 production: lexical fallback | 10 | ivy-league | world_knowledge | 8 | 10 | 0.00 | 0.00 | 0.00 |  |
| v1.3 production: lexical fallback | 10 | tx-cheap-public | structured_only | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | small-classes | structured_only | 17 | 10 | 0.24 | 0.40 | 0.40 |  |
| v1.3 production: lexical fallback | 10 | south-selective-private | structured_only | 6 | 10 | 0.67 | 0.67 | 0.67 |  |
| v1.3 production: lexical fallback | 10 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 10 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | tx-engineering | state_name | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | ca-computer-science | state_name | 3 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | fl-business | state_name | 7 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | ma-private | state_name | 6 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | tx-health | state_name | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | ga-psychology | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | midwest-public | exact_vocabulary | 9 | 25 | 1.00 | 0.78 | 0.67 |  |
| v1.3 production: lexical fallback | 25 | south-suburban | exact_vocabulary | 8 | 25 | 1.00 | 0.62 | 0.75 |  |
| v1.3 production: lexical fallback | 25 | small-private | exact_vocabulary | 6 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | town-setting | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | northeast-mathematics | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | agriculture | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | legal-studies | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | education | exact_vocabulary | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | criminal-justice | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | performing-arts | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | division-three | synonym | 9 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | division-two | synonym | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | fl-nursing | synonym | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | oh-big-state | synonym | 2 | 25 | 1.00 | 0.50 | 0.50 |  |
| v1.3 production: lexical fallback | 25 | ga-tech-focused | synonym | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | midwest-coding | synonym | 6 | 25 | 1.00 | 0.50 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | film-theater | synonym | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | bay-area-cs | world_knowledge | 2 | 25 | 0.50 | 0.00 | 0.00 |  |
| v1.3 production: lexical fallback | 25 | hbcu | world_knowledge | 2 | 25 | 0.50 | 0.00 | 0.00 |  |
| v1.3 production: lexical fallback | 25 | ivy-league | world_knowledge | 8 | 25 | 0.12 | 0.00 | 0.00 |  |
| v1.3 production: lexical fallback | 25 | tx-cheap-public | structured_only | 4 | 25 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | small-classes | structured_only | 17 | 25 | 0.29 | 0.40 | 0.40 |  |
| v1.3 production: lexical fallback | 25 | south-selective-private | structured_only | 6 | 25 | 1.00 | 0.67 | 0.83 |  |
| v1.3 production: lexical fallback | 25 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 25 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | tx-engineering | state_name | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | ca-computer-science | state_name | 3 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | fl-business | state_name | 7 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | ma-private | state_name | 6 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | tx-health | state_name | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | ga-psychology | state_name | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | midwest-public | exact_vocabulary | 9 | 50 | 1.00 | 0.78 | 0.67 |  |
| v1.3 production: lexical fallback | 50 | south-suburban | exact_vocabulary | 8 | 50 | 1.00 | 0.62 | 0.75 |  |
| v1.3 production: lexical fallback | 50 | small-private | exact_vocabulary | 6 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | town-setting | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | northeast-mathematics | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | agriculture | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | legal-studies | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | education | exact_vocabulary | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | criminal-justice | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | performing-arts | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | division-three | synonym | 9 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | division-two | synonym | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | fl-nursing | synonym | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | oh-big-state | synonym | 2 | 50 | 1.00 | 0.50 | 0.50 |  |
| v1.3 production: lexical fallback | 50 | ga-tech-focused | synonym | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | midwest-coding | synonym | 6 | 50 | 1.00 | 0.50 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | film-theater | synonym | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | bay-area-cs | world_knowledge | 2 | 50 | 0.50 | 0.00 | 0.00 |  |
| v1.3 production: lexical fallback | 50 | hbcu | world_knowledge | 2 | 50 | 1.00 | 0.00 | 0.00 |  |
| v1.3 production: lexical fallback | 50 | ivy-league | world_knowledge | 8 | 50 | 0.25 | 0.00 | 0.00 |  |
| v1.3 production: lexical fallback | 50 | tx-cheap-public | structured_only | 4 | 50 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | small-classes | structured_only | 17 | 50 | 0.59 | 0.40 | 0.40 |  |
| v1.3 production: lexical fallback | 50 | south-selective-private | structured_only | 6 | 50 | 1.00 | 0.67 | 0.83 |  |
| v1.3 production: lexical fallback | 50 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| v1.3 production: lexical fallback | 50 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | tx-engineering | state_name | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | ca-computer-science | state_name | 3 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | fl-business | state_name | 7 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | ma-private | state_name | 6 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | tx-health | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | ga-psychology | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | midwest-public | exact_vocabulary | 9 | 10 | 0.89 | 0.89 | 0.89 |  |
| model2vec potion-base-8M | 10 | south-suburban | exact_vocabulary | 8 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | small-private | exact_vocabulary | 6 | 10 | 0.67 | 0.67 | 0.67 |  |
| model2vec potion-base-8M | 10 | town-setting | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | northeast-mathematics | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | agriculture | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | legal-studies | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | education | exact_vocabulary | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | criminal-justice | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | performing-arts | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | division-three | synonym | 9 | 10 | 0.44 | 0.44 | 0.44 |  |
| model2vec potion-base-8M | 10 | division-two | synonym | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| model2vec potion-base-8M | 10 | fl-nursing | synonym | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | oh-big-state | synonym | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | ga-tech-focused | synonym | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | midwest-coding | synonym | 6 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | film-theater | synonym | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | bay-area-cs | world_knowledge | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| model2vec potion-base-8M | 10 | hbcu | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| model2vec potion-base-8M | 10 | ivy-league | world_knowledge | 8 | 10 | 0.38 | 0.38 | 0.38 |  |
| model2vec potion-base-8M | 10 | tx-cheap-public | structured_only | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | small-classes | structured_only | 17 | 10 | 0.29 | 0.50 | 0.50 |  |
| model2vec potion-base-8M | 10 | south-selective-private | structured_only | 6 | 10 | 0.33 | 0.33 | 0.33 |  |
| model2vec potion-base-8M | 10 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 10 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | tx-engineering | state_name | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | ca-computer-science | state_name | 3 | 25 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | fl-business | state_name | 7 | 25 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | ma-private | state_name | 6 | 25 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | tx-health | state_name | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | ga-psychology | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | midwest-public | exact_vocabulary | 9 | 25 | 1.00 | 0.89 | 0.89 |  |
| model2vec potion-base-8M | 25 | south-suburban | exact_vocabulary | 8 | 25 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | small-private | exact_vocabulary | 6 | 25 | 1.00 | 0.67 | 0.67 |  |
| model2vec potion-base-8M | 25 | town-setting | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | northeast-mathematics | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | agriculture | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | legal-studies | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | education | exact_vocabulary | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | criminal-justice | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | performing-arts | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | division-three | synonym | 9 | 25 | 0.89 | 0.44 | 0.44 |  |
| model2vec potion-base-8M | 25 | division-two | synonym | 2 | 25 | 1.00 | 0.50 | 0.50 |  |
| model2vec potion-base-8M | 25 | fl-nursing | synonym | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | oh-big-state | synonym | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | ga-tech-focused | synonym | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | midwest-coding | synonym | 6 | 25 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | film-theater | synonym | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | bay-area-cs | world_knowledge | 2 | 25 | 1.00 | 0.50 | 0.50 |  |
| model2vec potion-base-8M | 25 | hbcu | world_knowledge | 2 | 25 | 0.50 | 0.00 | 0.00 |  |
| model2vec potion-base-8M | 25 | ivy-league | world_knowledge | 8 | 25 | 0.75 | 0.38 | 0.38 |  |
| model2vec potion-base-8M | 25 | tx-cheap-public | structured_only | 4 | 25 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | small-classes | structured_only | 17 | 25 | 0.59 | 0.50 | 0.50 |  |
| model2vec potion-base-8M | 25 | south-selective-private | structured_only | 6 | 25 | 1.00 | 0.33 | 0.33 |  |
| model2vec potion-base-8M | 25 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 25 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | tx-engineering | state_name | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | ca-computer-science | state_name | 3 | 50 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | fl-business | state_name | 7 | 50 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | ma-private | state_name | 6 | 50 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | tx-health | state_name | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | ga-psychology | state_name | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | midwest-public | exact_vocabulary | 9 | 50 | 1.00 | 0.89 | 0.89 |  |
| model2vec potion-base-8M | 50 | south-suburban | exact_vocabulary | 8 | 50 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | small-private | exact_vocabulary | 6 | 50 | 1.00 | 0.67 | 0.67 |  |
| model2vec potion-base-8M | 50 | town-setting | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | northeast-mathematics | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | agriculture | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | legal-studies | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | education | exact_vocabulary | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | criminal-justice | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | performing-arts | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | division-three | synonym | 9 | 50 | 1.00 | 0.44 | 0.44 |  |
| model2vec potion-base-8M | 50 | division-two | synonym | 2 | 50 | 1.00 | 0.50 | 0.50 |  |
| model2vec potion-base-8M | 50 | fl-nursing | synonym | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | oh-big-state | synonym | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | ga-tech-focused | synonym | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | midwest-coding | synonym | 6 | 50 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | film-theater | synonym | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | bay-area-cs | world_knowledge | 2 | 50 | 1.00 | 0.50 | 0.50 |  |
| model2vec potion-base-8M | 50 | hbcu | world_knowledge | 2 | 50 | 0.50 | 0.00 | 0.00 |  |
| model2vec potion-base-8M | 50 | ivy-league | world_knowledge | 8 | 50 | 1.00 | 0.38 | 0.38 |  |
| model2vec potion-base-8M | 50 | tx-cheap-public | structured_only | 4 | 50 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | small-classes | structured_only | 17 | 50 | 1.00 | 0.50 | 0.50 |  |
| model2vec potion-base-8M | 50 | south-selective-private | structured_only | 6 | 50 | 1.00 | 0.33 | 0.33 |  |
| model2vec potion-base-8M | 50 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| model2vec potion-base-8M | 50 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | tx-engineering | state_name | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | ca-computer-science | state_name | 3 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | fl-business | state_name | 7 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | ma-private | state_name | 6 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | tx-health | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | ga-psychology | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | midwest-public | exact_vocabulary | 9 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | south-suburban | exact_vocabulary | 8 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | small-private | exact_vocabulary | 6 | 10 | 0.83 | 0.83 | 0.83 |  |
| hybrid: lexical + model2vec (RRF) | 10 | town-setting | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | northeast-mathematics | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | agriculture | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | legal-studies | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | education | exact_vocabulary | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | criminal-justice | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | performing-arts | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | division-three | synonym | 9 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | division-two | synonym | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | fl-nursing | synonym | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | oh-big-state | synonym | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | ga-tech-focused | synonym | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | midwest-coding | synonym | 6 | 10 | 0.83 | 0.83 | 0.83 |  |
| hybrid: lexical + model2vec (RRF) | 10 | film-theater | synonym | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | bay-area-cs | world_knowledge | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| hybrid: lexical + model2vec (RRF) | 10 | hbcu | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | ivy-league | world_knowledge | 8 | 10 | 0.25 | 0.25 | 0.25 |  |
| hybrid: lexical + model2vec (RRF) | 10 | tx-cheap-public | structured_only | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | small-classes | structured_only | 17 | 10 | 0.35 | 0.60 | 0.60 |  |
| hybrid: lexical + model2vec (RRF) | 10 | south-selective-private | structured_only | 6 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 10 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | tx-engineering | state_name | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | ca-computer-science | state_name | 3 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | fl-business | state_name | 7 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | ma-private | state_name | 6 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | tx-health | state_name | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | ga-psychology | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | midwest-public | exact_vocabulary | 9 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | south-suburban | exact_vocabulary | 8 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | small-private | exact_vocabulary | 6 | 25 | 1.00 | 0.83 | 0.83 |  |
| hybrid: lexical + model2vec (RRF) | 25 | town-setting | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | northeast-mathematics | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | agriculture | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | legal-studies | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | education | exact_vocabulary | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | criminal-justice | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | performing-arts | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | division-three | synonym | 9 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | division-two | synonym | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | fl-nursing | synonym | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | oh-big-state | synonym | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | ga-tech-focused | synonym | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | midwest-coding | synonym | 6 | 25 | 1.00 | 0.83 | 0.83 |  |
| hybrid: lexical + model2vec (RRF) | 25 | film-theater | synonym | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | bay-area-cs | world_knowledge | 2 | 25 | 0.50 | 0.50 | 0.50 |  |
| hybrid: lexical + model2vec (RRF) | 25 | hbcu | world_knowledge | 2 | 25 | 0.50 | 0.00 | 0.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | ivy-league | world_knowledge | 8 | 25 | 0.38 | 0.25 | 0.25 |  |
| hybrid: lexical + model2vec (RRF) | 25 | tx-cheap-public | structured_only | 4 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | small-classes | structured_only | 17 | 25 | 0.53 | 0.60 | 0.60 |  |
| hybrid: lexical + model2vec (RRF) | 25 | south-selective-private | structured_only | 6 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 25 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | tx-engineering | state_name | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | ca-computer-science | state_name | 3 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | fl-business | state_name | 7 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | ma-private | state_name | 6 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | tx-health | state_name | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | ga-psychology | state_name | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | midwest-public | exact_vocabulary | 9 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | south-suburban | exact_vocabulary | 8 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | small-private | exact_vocabulary | 6 | 50 | 1.00 | 0.83 | 0.83 |  |
| hybrid: lexical + model2vec (RRF) | 50 | town-setting | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | northeast-mathematics | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | agriculture | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | legal-studies | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | education | exact_vocabulary | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | criminal-justice | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | performing-arts | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | division-three | synonym | 9 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | division-two | synonym | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | fl-nursing | synonym | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | oh-big-state | synonym | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | ga-tech-focused | synonym | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | midwest-coding | synonym | 6 | 50 | 1.00 | 0.83 | 0.83 |  |
| hybrid: lexical + model2vec (RRF) | 50 | film-theater | synonym | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | bay-area-cs | world_knowledge | 2 | 50 | 0.50 | 0.50 | 0.50 |  |
| hybrid: lexical + model2vec (RRF) | 50 | hbcu | world_knowledge | 2 | 50 | 1.00 | 0.00 | 0.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | ivy-league | world_knowledge | 8 | 50 | 0.75 | 0.25 | 0.25 |  |
| hybrid: lexical + model2vec (RRF) | 50 | tx-cheap-public | structured_only | 4 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | small-classes | structured_only | 17 | 50 | 0.94 | 0.60 | 0.60 |  |
| hybrid: lexical + model2vec (RRF) | 50 | south-selective-private | structured_only | 6 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: lexical + model2vec (RRF) | 50 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | tx-engineering | state_name | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | ca-computer-science | state_name | 3 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | fl-business | state_name | 7 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | ma-private | state_name | 6 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | tx-health | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | ga-psychology | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | midwest-public | exact_vocabulary | 9 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | south-suburban | exact_vocabulary | 8 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | small-private | exact_vocabulary | 6 | 10 | 0.83 | 0.83 | 0.83 |  |
| hybrid: full-text + model2vec (RRF) | 10 | town-setting | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | northeast-mathematics | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | agriculture | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | legal-studies | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | education | exact_vocabulary | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | criminal-justice | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | performing-arts | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | division-three | synonym | 9 | 10 | 0.89 | 0.89 | 0.89 |  |
| hybrid: full-text + model2vec (RRF) | 10 | division-two | synonym | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | fl-nursing | synonym | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | oh-big-state | synonym | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | ga-tech-focused | synonym | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | midwest-coding | synonym | 6 | 10 | 0.83 | 0.83 | 0.83 |  |
| hybrid: full-text + model2vec (RRF) | 10 | film-theater | synonym | 5 | 10 | 0.40 | 0.40 | 0.40 |  |
| hybrid: full-text + model2vec (RRF) | 10 | bay-area-cs | world_knowledge | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| hybrid: full-text + model2vec (RRF) | 10 | hbcu | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | ivy-league | world_knowledge | 8 | 10 | 0.25 | 0.25 | 0.25 |  |
| hybrid: full-text + model2vec (RRF) | 10 | tx-cheap-public | structured_only | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | small-classes | structured_only | 17 | 10 | 0.24 | 0.40 | 0.40 |  |
| hybrid: full-text + model2vec (RRF) | 10 | south-selective-private | structured_only | 6 | 10 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 10 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | tx-engineering | state_name | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | ca-computer-science | state_name | 3 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | fl-business | state_name | 7 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | ma-private | state_name | 6 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | tx-health | state_name | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | ga-psychology | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | midwest-public | exact_vocabulary | 9 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | south-suburban | exact_vocabulary | 8 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | small-private | exact_vocabulary | 6 | 25 | 1.00 | 0.83 | 0.83 |  |
| hybrid: full-text + model2vec (RRF) | 25 | town-setting | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | northeast-mathematics | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | agriculture | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | legal-studies | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | education | exact_vocabulary | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | criminal-justice | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | performing-arts | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | division-three | synonym | 9 | 25 | 0.89 | 0.89 | 0.89 |  |
| hybrid: full-text + model2vec (RRF) | 25 | division-two | synonym | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | fl-nursing | synonym | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | oh-big-state | synonym | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | ga-tech-focused | synonym | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | midwest-coding | synonym | 6 | 25 | 1.00 | 0.83 | 0.83 |  |
| hybrid: full-text + model2vec (RRF) | 25 | film-theater | synonym | 5 | 25 | 1.00 | 0.40 | 0.40 |  |
| hybrid: full-text + model2vec (RRF) | 25 | bay-area-cs | world_knowledge | 2 | 25 | 0.50 | 0.50 | 0.50 |  |
| hybrid: full-text + model2vec (RRF) | 25 | hbcu | world_knowledge | 2 | 25 | 0.50 | 0.00 | 0.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | ivy-league | world_knowledge | 8 | 25 | 0.38 | 0.25 | 0.25 |  |
| hybrid: full-text + model2vec (RRF) | 25 | tx-cheap-public | structured_only | 4 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | small-classes | structured_only | 17 | 25 | 0.82 | 0.40 | 0.40 |  |
| hybrid: full-text + model2vec (RRF) | 25 | south-selective-private | structured_only | 6 | 25 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 25 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | tx-engineering | state_name | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | ca-computer-science | state_name | 3 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | fl-business | state_name | 7 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | ma-private | state_name | 6 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | tx-health | state_name | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | ga-psychology | state_name | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | midwest-public | exact_vocabulary | 9 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | south-suburban | exact_vocabulary | 8 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | small-private | exact_vocabulary | 6 | 50 | 1.00 | 0.83 | 0.83 |  |
| hybrid: full-text + model2vec (RRF) | 50 | town-setting | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | northeast-mathematics | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | agriculture | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | legal-studies | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | education | exact_vocabulary | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | criminal-justice | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | performing-arts | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | division-three | synonym | 9 | 50 | 1.00 | 0.89 | 0.89 |  |
| hybrid: full-text + model2vec (RRF) | 50 | division-two | synonym | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | fl-nursing | synonym | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | oh-big-state | synonym | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | ga-tech-focused | synonym | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | midwest-coding | synonym | 6 | 50 | 1.00 | 0.83 | 0.83 |  |
| hybrid: full-text + model2vec (RRF) | 50 | film-theater | synonym | 5 | 50 | 1.00 | 0.40 | 0.40 |  |
| hybrid: full-text + model2vec (RRF) | 50 | bay-area-cs | world_knowledge | 2 | 50 | 1.00 | 0.50 | 0.50 |  |
| hybrid: full-text + model2vec (RRF) | 50 | hbcu | world_knowledge | 2 | 50 | 1.00 | 0.00 | 0.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | ivy-league | world_knowledge | 8 | 50 | 0.75 | 0.25 | 0.25 |  |
| hybrid: full-text + model2vec (RRF) | 50 | tx-cheap-public | structured_only | 4 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | small-classes | structured_only | 17 | 50 | 1.00 | 0.40 | 0.40 |  |
| hybrid: full-text + model2vec (RRF) | 50 | south-selective-private | structured_only | 6 | 50 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hybrid: full-text + model2vec (RRF) | 50 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
