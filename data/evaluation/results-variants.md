35 queries over 92 schools; candidate limits [10, 25, 50]
queries per category: {'exact_vocabulary': 10, 'filtered': 6, 'state_name': 6, 'structured_only': 3, 'synonym': 7, 'world_knowledge': 3}
production equivalence: 210 query runs match the real SemanticSearchService exactly

## Overall

| configuration | limit | pool recall | retriever P@10 | end-to-end P@10 | filtered queries empty | mean fit (page) | in-process p50 / p95 ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| hash (production) | 10 | 0.45 | 0.46 | 0.46 | 5/6 | 77.6 | 1.65 / 2.80 |
| hash (production) | 25 | 0.64 | 0.51 | 0.34 | 3/6 | 80.3 | 2.84 / 4.60 |
| hash (production) | 50 | 0.85 | 0.60 | 0.35 | 0/6 | 81.5 | 4.05 / 6.84 |
| lexical (production fallback) | 10 | 0.54 | 0.54 | 0.54 | 6/6 | 76.4 | 0.75 / 1.36 |
| lexical (production fallback) | 25 | 0.72 | 0.60 | 0.36 | 4/6 | 80.1 | 1.92 / 3.56 |
| lexical (production fallback) | 50 | 0.85 | 0.66 | 0.30 | 2/6 | 81.3 | 3.43 / 5.87 |
| hash + clean docs | 10 | 0.58 | 0.58 | 0.58 | 6/6 | 76.6 | 1.53 / 2.70 |
| hash + clean docs | 25 | 0.86 | 0.72 | 0.47 | 1/6 | 80.4 | 2.52 / 4.41 |
| hash + clean docs | 50 | 0.93 | 0.75 | 0.35 | 0/6 | 81.6 | 4.25 / 6.38 |
| lexical + clean docs | 10 | 0.67 | 0.67 | 0.67 | 6/6 | 76.6 | 0.85 / 1.74 |
| lexical + clean docs | 25 | 0.81 | 0.73 | 0.38 | 4/6 | 80.2 | 1.86 / 3.14 |
| lexical + clean docs | 50 | 0.90 | 0.78 | 0.30 | 2/6 | 81.3 | 3.29 / 5.20 |
| lexical + clean + filter first | 10 | 0.84 | 0.84 | 0.84 | 0/6 | 77.6 | 1.06 / 2.16 |
| lexical + clean + filter first | 25 | 0.93 | 0.84 | 0.49 | 0/6 | 80.6 | 2.32 / 3.51 |
| lexical + clean + filter first | 50 | 0.95 | 0.84 | 0.35 | 0/6 | 81.5 | 3.80 / 5.92 |
| lexical + clean + filter first + relevance order | 10 | 0.84 | 0.84 | 0.84 | 0/6 | 77.6 | 0.94 / 1.64 |
| lexical + clean + filter first + relevance order | 25 | 0.93 | 0.84 | 0.86 | 0/6 | 79.5 | 1.88 / 3.79 |
| lexical + clean + filter first + relevance order | 50 | 0.95 | 0.84 | 0.86 | 0/6 | 79.8 | 3.83 / 6.77 |
| lexical + clean + filter first + matched then fit | 10 | 0.84 | 0.84 | 0.84 | 0/6 | 77.6 | 0.98 / 1.82 |
| lexical + clean + filter first + matched then fit | 25 | 0.93 | 0.84 | 0.68 | 0/6 | 80.0 | 2.02 / 3.05 |
| lexical + clean + filter first + matched then fit | 50 | 0.95 | 0.84 | 0.60 | 0/6 | 80.6 | 3.89 / 5.91 |

## End-to-end P@10 by query category, candidate limit 50

| configuration | exact_vocabulary | filtered | state_name | structured_only | synonym | world_knowledge |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| hash (production) | 0.20 | 1.00 | 0.32 | 0.21 | 0.16 | 0.21 |
| lexical (production fallback) | 0.23 | 0.67 | 0.28 | 0.18 | 0.26 | 0.00 |
| hash + clean docs | 0.23 | 1.00 | 0.26 | 0.18 | 0.17 | 0.21 |
| lexical + clean docs | 0.23 | 0.67 | 0.28 | 0.18 | 0.26 | 0.00 |
| lexical + clean + filter first | 0.23 | 1.00 | 0.28 | 0.18 | 0.26 | 0.00 |
| lexical + clean + filter first + relevance order | 0.94 | 1.00 | 1.00 | 0.74 | 0.93 | 0.00 |
| lexical + clean + filter first + matched then fit | 0.77 | 1.00 | 0.31 | 0.24 | 0.66 | 0.00 |

## Per query

| configuration | limit | query | category | relevant | pool | pool recall | retriever P@10 | end-to-end P@10 | empty |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| hash (production) | 10 | tx-engineering | state_name | 5 | 10 | 0.80 | 0.80 | 0.80 |  |
| hash (production) | 10 | ca-computer-science | state_name | 3 | 10 | 0.67 | 0.67 | 0.67 |  |
| hash (production) | 10 | fl-business | state_name | 7 | 10 | 0.14 | 0.14 | 0.14 |  |
| hash (production) | 10 | ma-private | state_name | 6 | 10 | 0.17 | 0.17 | 0.17 |  |
| hash (production) | 10 | tx-health | state_name | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| hash (production) | 10 | ga-psychology | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash (production) | 10 | midwest-public | exact_vocabulary | 9 | 10 | 0.89 | 0.89 | 0.89 |  |
| hash (production) | 10 | south-suburban | exact_vocabulary | 8 | 10 | 0.75 | 0.75 | 0.75 |  |
| hash (production) | 10 | small-private | exact_vocabulary | 6 | 10 | 0.67 | 0.67 | 0.67 |  |
| hash (production) | 10 | town-setting | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash (production) | 10 | northeast-mathematics | exact_vocabulary | 5 | 10 | 0.80 | 0.80 | 0.80 |  |
| hash (production) | 10 | agriculture | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash (production) | 10 | legal-studies | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash (production) | 10 | education | exact_vocabulary | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| hash (production) | 10 | criminal-justice | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash (production) | 10 | performing-arts | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash (production) | 10 | division-three | synonym | 9 | 10 | 0.22 | 0.22 | 0.22 |  |
| hash (production) | 10 | division-two | synonym | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| hash (production) | 10 | fl-nursing | synonym | 5 | 10 | 0.40 | 0.40 | 0.40 |  |
| hash (production) | 10 | oh-big-state | synonym | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| hash (production) | 10 | ga-tech-focused | synonym | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| hash (production) | 10 | midwest-coding | synonym | 6 | 10 | 0.33 | 0.33 | 0.33 |  |
| hash (production) | 10 | film-theater | synonym | 5 | 10 | 0.20 | 0.20 | 0.20 |  |
| hash (production) | 10 | bay-area-cs | world_knowledge | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| hash (production) | 10 | hbcu | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| hash (production) | 10 | ivy-league | world_knowledge | 8 | 10 | 0.12 | 0.12 | 0.12 |  |
| hash (production) | 10 | tx-cheap-public | structured_only | 4 | 10 | 0.25 | 0.25 | 0.25 |  |
| hash (production) | 10 | small-classes | structured_only | 17 | 10 | 0.12 | 0.20 | 0.20 |  |
| hash (production) | 10 | south-selective-private | structured_only | 6 | 10 | 0.33 | 0.33 | 0.33 |  |
| hash (production) | 10 | filter-or-engineering | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| hash (production) | 10 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash (production) | 10 | filter-ut-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| hash (production) | 10 | filter-dc-social-sciences | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| hash (production) | 10 | filter-ms-health | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| hash (production) | 10 | filter-private-affordable-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| hash (production) | 25 | tx-engineering | state_name | 5 | 25 | 1.00 | 0.80 | 0.40 |  |
| hash (production) | 25 | ca-computer-science | state_name | 3 | 25 | 1.00 | 0.67 | 1.00 |  |
| hash (production) | 25 | fl-business | state_name | 7 | 25 | 0.29 | 0.14 | 0.14 |  |
| hash (production) | 25 | ma-private | state_name | 6 | 25 | 0.67 | 0.17 | 0.17 |  |
| hash (production) | 25 | tx-health | state_name | 2 | 25 | 1.00 | 0.50 | 0.00 |  |
| hash (production) | 25 | ga-psychology | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| hash (production) | 25 | midwest-public | exact_vocabulary | 9 | 25 | 1.00 | 0.89 | 0.56 |  |
| hash (production) | 25 | south-suburban | exact_vocabulary | 8 | 25 | 1.00 | 0.75 | 0.50 |  |
| hash (production) | 25 | small-private | exact_vocabulary | 6 | 25 | 0.83 | 0.67 | 0.50 |  |
| hash (production) | 25 | town-setting | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| hash (production) | 25 | northeast-mathematics | exact_vocabulary | 5 | 25 | 1.00 | 0.80 | 0.80 |  |
| hash (production) | 25 | agriculture | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| hash (production) | 25 | legal-studies | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| hash (production) | 25 | education | exact_vocabulary | 2 | 25 | 1.00 | 0.50 | 0.00 |  |
| hash (production) | 25 | criminal-justice | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| hash (production) | 25 | performing-arts | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 0.20 |  |
| hash (production) | 25 | division-three | synonym | 9 | 25 | 0.33 | 0.22 | 0.22 |  |
| hash (production) | 25 | division-two | synonym | 2 | 25 | 0.00 | 0.00 | 0.00 |  |
| hash (production) | 25 | fl-nursing | synonym | 5 | 25 | 0.60 | 0.40 | 0.00 |  |
| hash (production) | 25 | oh-big-state | synonym | 2 | 25 | 0.00 | 0.00 | 0.00 |  |
| hash (production) | 25 | ga-tech-focused | synonym | 2 | 25 | 0.50 | 0.50 | 0.50 |  |
| hash (production) | 25 | midwest-coding | synonym | 6 | 25 | 0.50 | 0.33 | 0.50 |  |
| hash (production) | 25 | film-theater | synonym | 5 | 25 | 0.20 | 0.20 | 0.00 |  |
| hash (production) | 25 | bay-area-cs | world_knowledge | 2 | 25 | 0.50 | 0.50 | 0.50 |  |
| hash (production) | 25 | hbcu | world_knowledge | 2 | 25 | 0.00 | 0.00 | 0.00 |  |
| hash (production) | 25 | ivy-league | world_knowledge | 8 | 25 | 0.50 | 0.12 | 0.25 |  |
| hash (production) | 25 | tx-cheap-public | structured_only | 4 | 25 | 0.75 | 0.25 | 0.00 |  |
| hash (production) | 25 | small-classes | structured_only | 17 | 25 | 0.24 | 0.20 | 0.20 |  |
| hash (production) | 25 | south-selective-private | structured_only | 6 | 25 | 0.67 | 0.33 | 0.50 |  |
| hash (production) | 25 | filter-or-engineering | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| hash (production) | 25 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash (production) | 25 | filter-ut-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| hash (production) | 25 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash (production) | 25 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash (production) | 25 | filter-private-affordable-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| hash (production) | 50 | tx-engineering | state_name | 5 | 50 | 1.00 | 0.80 | 0.40 |  |
| hash (production) | 50 | ca-computer-science | state_name | 3 | 50 | 1.00 | 0.67 | 0.33 |  |
| hash (production) | 50 | fl-business | state_name | 7 | 50 | 0.86 | 0.14 | 0.00 |  |
| hash (production) | 50 | ma-private | state_name | 6 | 50 | 1.00 | 0.17 | 0.17 |  |
| hash (production) | 50 | tx-health | state_name | 2 | 50 | 1.00 | 0.50 | 0.00 |  |
| hash (production) | 50 | ga-psychology | state_name | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| hash (production) | 50 | midwest-public | exact_vocabulary | 9 | 50 | 1.00 | 0.89 | 0.33 |  |
| hash (production) | 50 | south-suburban | exact_vocabulary | 8 | 50 | 1.00 | 0.75 | 0.12 |  |
| hash (production) | 50 | small-private | exact_vocabulary | 6 | 50 | 0.83 | 0.67 | 0.17 |  |
| hash (production) | 50 | town-setting | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| hash (production) | 50 | northeast-mathematics | exact_vocabulary | 5 | 50 | 1.00 | 0.80 | 0.20 |  |
| hash (production) | 50 | agriculture | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| hash (production) | 50 | legal-studies | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| hash (production) | 50 | education | exact_vocabulary | 2 | 50 | 1.00 | 0.50 | 0.00 |  |
| hash (production) | 50 | criminal-justice | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| hash (production) | 50 | performing-arts | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 0.20 |  |
| hash (production) | 50 | division-three | synonym | 9 | 50 | 0.67 | 0.22 | 0.11 |  |
| hash (production) | 50 | division-two | synonym | 2 | 50 | 0.00 | 0.00 | 0.00 |  |
| hash (production) | 50 | fl-nursing | synonym | 5 | 50 | 0.80 | 0.40 | 0.00 |  |
| hash (production) | 50 | oh-big-state | synonym | 2 | 50 | 0.00 | 0.00 | 0.00 |  |
| hash (production) | 50 | ga-tech-focused | synonym | 2 | 50 | 1.00 | 0.50 | 0.50 |  |
| hash (production) | 50 | midwest-coding | synonym | 6 | 50 | 1.00 | 0.33 | 0.50 |  |
| hash (production) | 50 | film-theater | synonym | 5 | 50 | 0.60 | 0.20 | 0.00 |  |
| hash (production) | 50 | bay-area-cs | world_knowledge | 2 | 50 | 1.00 | 0.50 | 0.50 |  |
| hash (production) | 50 | hbcu | world_knowledge | 2 | 50 | 0.00 | 0.00 | 0.00 |  |
| hash (production) | 50 | ivy-league | world_knowledge | 8 | 50 | 0.88 | 0.12 | 0.12 |  |
| hash (production) | 50 | tx-cheap-public | structured_only | 4 | 50 | 0.75 | 0.25 | 0.00 |  |
| hash (production) | 50 | small-classes | structured_only | 17 | 50 | 0.59 | 0.20 | 0.30 |  |
| hash (production) | 50 | south-selective-private | structured_only | 6 | 50 | 0.83 | 0.33 | 0.33 |  |
| hash (production) | 50 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash (production) | 50 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash (production) | 50 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash (production) | 50 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash (production) | 50 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash (production) | 50 | filter-private-affordable-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical (production fallback) | 10 | tx-engineering | state_name | 5 | 10 | 0.80 | 0.80 | 0.80 |  |
| lexical (production fallback) | 10 | ca-computer-science | state_name | 3 | 10 | 0.67 | 0.67 | 0.67 |  |
| lexical (production fallback) | 10 | fl-business | state_name | 7 | 10 | 0.86 | 0.86 | 0.86 |  |
| lexical (production fallback) | 10 | ma-private | state_name | 6 | 10 | 0.17 | 0.17 | 0.17 |  |
| lexical (production fallback) | 10 | tx-health | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical (production fallback) | 10 | ga-psychology | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical (production fallback) | 10 | midwest-public | exact_vocabulary | 9 | 10 | 0.56 | 0.56 | 0.56 |  |
| lexical (production fallback) | 10 | south-suburban | exact_vocabulary | 8 | 10 | 0.62 | 0.62 | 0.62 |  |
| lexical (production fallback) | 10 | small-private | exact_vocabulary | 6 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical (production fallback) | 10 | town-setting | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical (production fallback) | 10 | northeast-mathematics | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical (production fallback) | 10 | agriculture | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical (production fallback) | 10 | legal-studies | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical (production fallback) | 10 | education | exact_vocabulary | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical (production fallback) | 10 | criminal-justice | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical (production fallback) | 10 | performing-arts | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical (production fallback) | 10 | division-three | synonym | 9 | 10 | 0.11 | 0.11 | 0.11 |  |
| lexical (production fallback) | 10 | division-two | synonym | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| lexical (production fallback) | 10 | fl-nursing | synonym | 5 | 10 | 0.80 | 0.80 | 0.80 |  |
| lexical (production fallback) | 10 | oh-big-state | synonym | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| lexical (production fallback) | 10 | ga-tech-focused | synonym | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| lexical (production fallback) | 10 | midwest-coding | synonym | 6 | 10 | 0.67 | 0.67 | 0.67 |  |
| lexical (production fallback) | 10 | film-theater | synonym | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical (production fallback) | 10 | bay-area-cs | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| lexical (production fallback) | 10 | hbcu | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| lexical (production fallback) | 10 | ivy-league | world_knowledge | 8 | 10 | 0.00 | 0.00 | 0.00 |  |
| lexical (production fallback) | 10 | tx-cheap-public | structured_only | 4 | 10 | 0.75 | 0.75 | 0.75 |  |
| lexical (production fallback) | 10 | small-classes | structured_only | 17 | 10 | 0.24 | 0.40 | 0.40 |  |
| lexical (production fallback) | 10 | south-selective-private | structured_only | 6 | 10 | 0.67 | 0.67 | 0.67 |  |
| lexical (production fallback) | 10 | filter-or-engineering | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical (production fallback) | 10 | filter-wa-computer-science | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical (production fallback) | 10 | filter-ut-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical (production fallback) | 10 | filter-dc-social-sciences | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical (production fallback) | 10 | filter-ms-health | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical (production fallback) | 10 | filter-private-affordable-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical (production fallback) | 25 | tx-engineering | state_name | 5 | 25 | 0.80 | 0.80 | 0.20 |  |
| lexical (production fallback) | 25 | ca-computer-science | state_name | 3 | 25 | 0.67 | 0.67 | 0.67 |  |
| lexical (production fallback) | 25 | fl-business | state_name | 7 | 25 | 1.00 | 0.86 | 0.43 |  |
| lexical (production fallback) | 25 | ma-private | state_name | 6 | 25 | 1.00 | 0.17 | 0.33 |  |
| lexical (production fallback) | 25 | tx-health | state_name | 2 | 25 | 1.00 | 1.00 | 0.00 |  |
| lexical (production fallback) | 25 | ga-psychology | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical (production fallback) | 25 | midwest-public | exact_vocabulary | 9 | 25 | 1.00 | 0.56 | 0.67 |  |
| lexical (production fallback) | 25 | south-suburban | exact_vocabulary | 8 | 25 | 1.00 | 0.62 | 0.50 |  |
| lexical (production fallback) | 25 | small-private | exact_vocabulary | 6 | 25 | 1.00 | 1.00 | 0.50 |  |
| lexical (production fallback) | 25 | town-setting | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| lexical (production fallback) | 25 | northeast-mathematics | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 0.80 |  |
| lexical (production fallback) | 25 | agriculture | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical (production fallback) | 25 | legal-studies | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| lexical (production fallback) | 25 | education | exact_vocabulary | 2 | 25 | 1.00 | 1.00 | 0.00 |  |
| lexical (production fallback) | 25 | criminal-justice | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| lexical (production fallback) | 25 | performing-arts | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 0.20 |  |
| lexical (production fallback) | 25 | division-three | synonym | 9 | 25 | 0.11 | 0.11 | 0.11 |  |
| lexical (production fallback) | 25 | division-two | synonym | 2 | 25 | 0.50 | 0.00 | 0.50 |  |
| lexical (production fallback) | 25 | fl-nursing | synonym | 5 | 25 | 0.80 | 0.80 | 0.00 |  |
| lexical (production fallback) | 25 | oh-big-state | synonym | 2 | 25 | 0.50 | 0.50 | 0.50 |  |
| lexical (production fallback) | 25 | ga-tech-focused | synonym | 2 | 25 | 0.50 | 0.50 | 0.50 |  |
| lexical (production fallback) | 25 | midwest-coding | synonym | 6 | 25 | 1.00 | 0.67 | 1.00 |  |
| lexical (production fallback) | 25 | film-theater | synonym | 5 | 25 | 1.00 | 1.00 | 0.20 |  |
| lexical (production fallback) | 25 | bay-area-cs | world_knowledge | 2 | 25 | 0.50 | 0.00 | 0.50 |  |
| lexical (production fallback) | 25 | hbcu | world_knowledge | 2 | 25 | 0.50 | 0.00 | 0.00 |  |
| lexical (production fallback) | 25 | ivy-league | world_knowledge | 8 | 25 | 0.12 | 0.00 | 0.00 |  |
| lexical (production fallback) | 25 | tx-cheap-public | structured_only | 4 | 25 | 0.75 | 0.75 | 0.00 |  |
| lexical (production fallback) | 25 | small-classes | structured_only | 17 | 25 | 0.29 | 0.40 | 0.30 |  |
| lexical (production fallback) | 25 | south-selective-private | structured_only | 6 | 25 | 1.00 | 0.67 | 0.67 |  |
| lexical (production fallback) | 25 | filter-or-engineering | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical (production fallback) | 25 | filter-wa-computer-science | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical (production fallback) | 25 | filter-ut-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical (production fallback) | 25 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical (production fallback) | 25 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical (production fallback) | 25 | filter-private-affordable-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical (production fallback) | 50 | tx-engineering | state_name | 5 | 50 | 1.00 | 0.80 | 0.40 |  |
| lexical (production fallback) | 50 | ca-computer-science | state_name | 3 | 50 | 1.00 | 0.67 | 0.00 |  |
| lexical (production fallback) | 50 | fl-business | state_name | 7 | 50 | 1.00 | 0.86 | 0.14 |  |
| lexical (production fallback) | 50 | ma-private | state_name | 6 | 50 | 1.00 | 0.17 | 0.17 |  |
| lexical (production fallback) | 50 | tx-health | state_name | 2 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical (production fallback) | 50 | ga-psychology | state_name | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical (production fallback) | 50 | midwest-public | exact_vocabulary | 9 | 50 | 1.00 | 0.56 | 0.33 |  |
| lexical (production fallback) | 50 | south-suburban | exact_vocabulary | 8 | 50 | 1.00 | 0.62 | 0.25 |  |
| lexical (production fallback) | 50 | small-private | exact_vocabulary | 6 | 50 | 1.00 | 1.00 | 0.33 |  |
| lexical (production fallback) | 50 | town-setting | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical (production fallback) | 50 | northeast-mathematics | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 0.20 |  |
| lexical (production fallback) | 50 | agriculture | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical (production fallback) | 50 | legal-studies | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical (production fallback) | 50 | education | exact_vocabulary | 2 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical (production fallback) | 50 | criminal-justice | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical (production fallback) | 50 | performing-arts | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 0.20 |  |
| lexical (production fallback) | 50 | division-three | synonym | 9 | 50 | 0.67 | 0.11 | 0.11 |  |
| lexical (production fallback) | 50 | division-two | synonym | 2 | 50 | 1.00 | 0.00 | 0.50 |  |
| lexical (production fallback) | 50 | fl-nursing | synonym | 5 | 50 | 1.00 | 0.80 | 0.00 |  |
| lexical (production fallback) | 50 | oh-big-state | synonym | 2 | 50 | 0.50 | 0.50 | 0.00 |  |
| lexical (production fallback) | 50 | ga-tech-focused | synonym | 2 | 50 | 0.50 | 0.50 | 0.50 |  |
| lexical (production fallback) | 50 | midwest-coding | synonym | 6 | 50 | 1.00 | 0.67 | 0.50 |  |
| lexical (production fallback) | 50 | film-theater | synonym | 5 | 50 | 1.00 | 1.00 | 0.20 |  |
| lexical (production fallback) | 50 | bay-area-cs | world_knowledge | 2 | 50 | 0.50 | 0.00 | 0.00 |  |
| lexical (production fallback) | 50 | hbcu | world_knowledge | 2 | 50 | 1.00 | 0.00 | 0.00 |  |
| lexical (production fallback) | 50 | ivy-league | world_knowledge | 8 | 50 | 0.25 | 0.00 | 0.00 |  |
| lexical (production fallback) | 50 | tx-cheap-public | structured_only | 4 | 50 | 0.75 | 0.75 | 0.00 |  |
| lexical (production fallback) | 50 | small-classes | structured_only | 17 | 50 | 0.59 | 0.40 | 0.20 |  |
| lexical (production fallback) | 50 | south-selective-private | structured_only | 6 | 50 | 1.00 | 0.67 | 0.33 |  |
| lexical (production fallback) | 50 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical (production fallback) | 50 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical (production fallback) | 50 | filter-ut-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical (production fallback) | 50 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical (production fallback) | 50 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical (production fallback) | 50 | filter-private-affordable-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| hash + clean docs | 10 | tx-engineering | state_name | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 10 | ca-computer-science | state_name | 3 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 10 | fl-business | state_name | 7 | 10 | 0.86 | 0.86 | 0.86 |  |
| hash + clean docs | 10 | ma-private | state_name | 6 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 10 | tx-health | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 10 | ga-psychology | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 10 | midwest-public | exact_vocabulary | 9 | 10 | 0.67 | 0.67 | 0.67 |  |
| hash + clean docs | 10 | south-suburban | exact_vocabulary | 8 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 10 | small-private | exact_vocabulary | 6 | 10 | 0.67 | 0.67 | 0.67 |  |
| hash + clean docs | 10 | town-setting | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 10 | northeast-mathematics | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 10 | agriculture | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 10 | legal-studies | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 10 | education | exact_vocabulary | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| hash + clean docs | 10 | criminal-justice | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 10 | performing-arts | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 10 | division-three | synonym | 9 | 10 | 0.67 | 0.67 | 0.67 |  |
| hash + clean docs | 10 | division-two | synonym | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| hash + clean docs | 10 | fl-nursing | synonym | 5 | 10 | 0.80 | 0.80 | 0.80 |  |
| hash + clean docs | 10 | oh-big-state | synonym | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| hash + clean docs | 10 | ga-tech-focused | synonym | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 10 | midwest-coding | synonym | 6 | 10 | 0.17 | 0.17 | 0.17 |  |
| hash + clean docs | 10 | film-theater | synonym | 5 | 10 | 0.20 | 0.20 | 0.20 |  |
| hash + clean docs | 10 | bay-area-cs | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| hash + clean docs | 10 | hbcu | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| hash + clean docs | 10 | ivy-league | world_knowledge | 8 | 10 | 0.00 | 0.00 | 0.00 |  |
| hash + clean docs | 10 | tx-cheap-public | structured_only | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 10 | small-classes | structured_only | 17 | 10 | 0.18 | 0.30 | 0.30 |  |
| hash + clean docs | 10 | south-selective-private | structured_only | 6 | 10 | 0.50 | 0.50 | 0.50 |  |
| hash + clean docs | 10 | filter-or-engineering | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| hash + clean docs | 10 | filter-wa-computer-science | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| hash + clean docs | 10 | filter-ut-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| hash + clean docs | 10 | filter-dc-social-sciences | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| hash + clean docs | 10 | filter-ms-health | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| hash + clean docs | 10 | filter-private-affordable-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| hash + clean docs | 25 | tx-engineering | state_name | 5 | 25 | 1.00 | 1.00 | 0.40 |  |
| hash + clean docs | 25 | ca-computer-science | state_name | 3 | 25 | 1.00 | 1.00 | 0.33 |  |
| hash + clean docs | 25 | fl-business | state_name | 7 | 25 | 1.00 | 0.86 | 0.71 |  |
| hash + clean docs | 25 | ma-private | state_name | 6 | 25 | 1.00 | 1.00 | 0.33 |  |
| hash + clean docs | 25 | tx-health | state_name | 2 | 25 | 1.00 | 1.00 | 0.00 |  |
| hash + clean docs | 25 | ga-psychology | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 25 | midwest-public | exact_vocabulary | 9 | 25 | 0.89 | 0.67 | 0.56 |  |
| hash + clean docs | 25 | south-suburban | exact_vocabulary | 8 | 25 | 1.00 | 1.00 | 0.50 |  |
| hash + clean docs | 25 | small-private | exact_vocabulary | 6 | 25 | 1.00 | 0.67 | 0.50 |  |
| hash + clean docs | 25 | town-setting | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| hash + clean docs | 25 | northeast-mathematics | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 0.80 |  |
| hash + clean docs | 25 | agriculture | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 25 | legal-studies | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| hash + clean docs | 25 | education | exact_vocabulary | 2 | 25 | 1.00 | 0.50 | 0.00 |  |
| hash + clean docs | 25 | criminal-justice | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| hash + clean docs | 25 | performing-arts | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 0.40 |  |
| hash + clean docs | 25 | division-three | synonym | 9 | 25 | 0.89 | 0.67 | 0.44 |  |
| hash + clean docs | 25 | division-two | synonym | 2 | 25 | 1.00 | 0.50 | 0.50 |  |
| hash + clean docs | 25 | fl-nursing | synonym | 5 | 25 | 1.00 | 0.80 | 0.00 |  |
| hash + clean docs | 25 | oh-big-state | synonym | 2 | 25 | 0.50 | 0.50 | 0.50 |  |
| hash + clean docs | 25 | ga-tech-focused | synonym | 2 | 25 | 1.00 | 1.00 | 0.50 |  |
| hash + clean docs | 25 | midwest-coding | synonym | 6 | 25 | 0.83 | 0.17 | 0.67 |  |
| hash + clean docs | 25 | film-theater | synonym | 5 | 25 | 0.60 | 0.20 | 0.20 |  |
| hash + clean docs | 25 | bay-area-cs | world_knowledge | 2 | 25 | 0.50 | 0.00 | 0.50 |  |
| hash + clean docs | 25 | hbcu | world_knowledge | 2 | 25 | 0.00 | 0.00 | 0.00 |  |
| hash + clean docs | 25 | ivy-league | world_knowledge | 8 | 25 | 0.25 | 0.00 | 0.12 |  |
| hash + clean docs | 25 | tx-cheap-public | structured_only | 4 | 25 | 1.00 | 1.00 | 0.25 |  |
| hash + clean docs | 25 | small-classes | structured_only | 17 | 25 | 0.47 | 0.30 | 0.60 |  |
| hash + clean docs | 25 | south-selective-private | structured_only | 6 | 25 | 1.00 | 0.50 | 0.67 |  |
| hash + clean docs | 25 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 25 | filter-wa-computer-science | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| hash + clean docs | 25 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 25 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 25 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 25 | filter-private-affordable-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 50 | tx-engineering | state_name | 5 | 50 | 1.00 | 1.00 | 0.40 |  |
| hash + clean docs | 50 | ca-computer-science | state_name | 3 | 50 | 1.00 | 1.00 | 0.00 |  |
| hash + clean docs | 50 | fl-business | state_name | 7 | 50 | 1.00 | 0.86 | 0.00 |  |
| hash + clean docs | 50 | ma-private | state_name | 6 | 50 | 1.00 | 1.00 | 0.17 |  |
| hash + clean docs | 50 | tx-health | state_name | 2 | 50 | 1.00 | 1.00 | 0.00 |  |
| hash + clean docs | 50 | ga-psychology | state_name | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 50 | midwest-public | exact_vocabulary | 9 | 50 | 1.00 | 0.67 | 0.33 |  |
| hash + clean docs | 50 | south-suburban | exact_vocabulary | 8 | 50 | 1.00 | 1.00 | 0.25 |  |
| hash + clean docs | 50 | small-private | exact_vocabulary | 6 | 50 | 1.00 | 0.67 | 0.33 |  |
| hash + clean docs | 50 | town-setting | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| hash + clean docs | 50 | northeast-mathematics | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 0.20 |  |
| hash + clean docs | 50 | agriculture | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 50 | legal-studies | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| hash + clean docs | 50 | education | exact_vocabulary | 2 | 50 | 1.00 | 0.50 | 0.00 |  |
| hash + clean docs | 50 | criminal-justice | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| hash + clean docs | 50 | performing-arts | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 0.20 |  |
| hash + clean docs | 50 | division-three | synonym | 9 | 50 | 1.00 | 0.67 | 0.22 |  |
| hash + clean docs | 50 | division-two | synonym | 2 | 50 | 1.00 | 0.50 | 0.50 |  |
| hash + clean docs | 50 | fl-nursing | synonym | 5 | 50 | 1.00 | 0.80 | 0.00 |  |
| hash + clean docs | 50 | oh-big-state | synonym | 2 | 50 | 1.00 | 0.50 | 0.00 |  |
| hash + clean docs | 50 | ga-tech-focused | synonym | 2 | 50 | 1.00 | 1.00 | 0.00 |  |
| hash + clean docs | 50 | midwest-coding | synonym | 6 | 50 | 0.83 | 0.17 | 0.50 |  |
| hash + clean docs | 50 | film-theater | synonym | 5 | 50 | 0.60 | 0.20 | 0.00 |  |
| hash + clean docs | 50 | bay-area-cs | world_knowledge | 2 | 50 | 0.50 | 0.00 | 0.50 |  |
| hash + clean docs | 50 | hbcu | world_knowledge | 2 | 50 | 0.00 | 0.00 | 0.00 |  |
| hash + clean docs | 50 | ivy-league | world_knowledge | 8 | 50 | 1.00 | 0.00 | 0.12 |  |
| hash + clean docs | 50 | tx-cheap-public | structured_only | 4 | 50 | 1.00 | 1.00 | 0.00 |  |
| hash + clean docs | 50 | small-classes | structured_only | 17 | 50 | 0.65 | 0.30 | 0.20 |  |
| hash + clean docs | 50 | south-selective-private | structured_only | 6 | 50 | 1.00 | 0.50 | 0.33 |  |
| hash + clean docs | 50 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 50 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 50 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 50 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 50 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash + clean docs | 50 | filter-private-affordable-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 10 | tx-engineering | state_name | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 10 | ca-computer-science | state_name | 3 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 10 | fl-business | state_name | 7 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 10 | ma-private | state_name | 6 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 10 | tx-health | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 10 | ga-psychology | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 10 | midwest-public | exact_vocabulary | 9 | 10 | 0.78 | 0.78 | 0.78 |  |
| lexical + clean docs | 10 | south-suburban | exact_vocabulary | 8 | 10 | 0.62 | 0.62 | 0.62 |  |
| lexical + clean docs | 10 | small-private | exact_vocabulary | 6 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 10 | town-setting | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 10 | northeast-mathematics | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 10 | agriculture | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 10 | legal-studies | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 10 | education | exact_vocabulary | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 10 | criminal-justice | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 10 | performing-arts | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 10 | division-three | synonym | 9 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 10 | division-two | synonym | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 10 | fl-nursing | synonym | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 10 | oh-big-state | synonym | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| lexical + clean docs | 10 | ga-tech-focused | synonym | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 10 | midwest-coding | synonym | 6 | 10 | 0.50 | 0.50 | 0.50 |  |
| lexical + clean docs | 10 | film-theater | synonym | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 10 | bay-area-cs | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| lexical + clean docs | 10 | hbcu | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| lexical + clean docs | 10 | ivy-league | world_knowledge | 8 | 10 | 0.00 | 0.00 | 0.00 |  |
| lexical + clean docs | 10 | tx-cheap-public | structured_only | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 10 | small-classes | structured_only | 17 | 10 | 0.24 | 0.40 | 0.40 |  |
| lexical + clean docs | 10 | south-selective-private | structured_only | 6 | 10 | 0.67 | 0.67 | 0.67 |  |
| lexical + clean docs | 10 | filter-or-engineering | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical + clean docs | 10 | filter-wa-computer-science | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical + clean docs | 10 | filter-ut-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical + clean docs | 10 | filter-dc-social-sciences | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical + clean docs | 10 | filter-ms-health | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical + clean docs | 10 | filter-private-affordable-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical + clean docs | 25 | tx-engineering | state_name | 5 | 25 | 1.00 | 1.00 | 0.40 |  |
| lexical + clean docs | 25 | ca-computer-science | state_name | 3 | 25 | 1.00 | 1.00 | 0.67 |  |
| lexical + clean docs | 25 | fl-business | state_name | 7 | 25 | 1.00 | 1.00 | 0.43 |  |
| lexical + clean docs | 25 | ma-private | state_name | 6 | 25 | 1.00 | 1.00 | 0.33 |  |
| lexical + clean docs | 25 | tx-health | state_name | 2 | 25 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean docs | 25 | ga-psychology | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 25 | midwest-public | exact_vocabulary | 9 | 25 | 1.00 | 0.78 | 0.67 |  |
| lexical + clean docs | 25 | south-suburban | exact_vocabulary | 8 | 25 | 1.00 | 0.62 | 0.50 |  |
| lexical + clean docs | 25 | small-private | exact_vocabulary | 6 | 25 | 1.00 | 1.00 | 0.50 |  |
| lexical + clean docs | 25 | town-setting | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean docs | 25 | northeast-mathematics | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 0.60 |  |
| lexical + clean docs | 25 | agriculture | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 25 | legal-studies | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean docs | 25 | education | exact_vocabulary | 2 | 25 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean docs | 25 | criminal-justice | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean docs | 25 | performing-arts | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 0.20 |  |
| lexical + clean docs | 25 | division-three | synonym | 9 | 25 | 1.00 | 1.00 | 0.44 |  |
| lexical + clean docs | 25 | division-two | synonym | 2 | 25 | 1.00 | 1.00 | 0.50 |  |
| lexical + clean docs | 25 | fl-nursing | synonym | 5 | 25 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean docs | 25 | oh-big-state | synonym | 2 | 25 | 1.00 | 0.50 | 0.50 |  |
| lexical + clean docs | 25 | ga-tech-focused | synonym | 2 | 25 | 1.00 | 1.00 | 0.50 |  |
| lexical + clean docs | 25 | midwest-coding | synonym | 6 | 25 | 1.00 | 0.50 | 1.00 |  |
| lexical + clean docs | 25 | film-theater | synonym | 5 | 25 | 1.00 | 1.00 | 0.20 |  |
| lexical + clean docs | 25 | bay-area-cs | world_knowledge | 2 | 25 | 0.50 | 0.00 | 0.50 |  |
| lexical + clean docs | 25 | hbcu | world_knowledge | 2 | 25 | 0.50 | 0.00 | 0.00 |  |
| lexical + clean docs | 25 | ivy-league | world_knowledge | 8 | 25 | 0.12 | 0.00 | 0.00 |  |
| lexical + clean docs | 25 | tx-cheap-public | structured_only | 4 | 25 | 1.00 | 1.00 | 0.25 |  |
| lexical + clean docs | 25 | small-classes | structured_only | 17 | 25 | 0.29 | 0.40 | 0.30 |  |
| lexical + clean docs | 25 | south-selective-private | structured_only | 6 | 25 | 1.00 | 0.67 | 0.67 |  |
| lexical + clean docs | 25 | filter-or-engineering | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical + clean docs | 25 | filter-wa-computer-science | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical + clean docs | 25 | filter-ut-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical + clean docs | 25 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 25 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 25 | filter-private-affordable-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical + clean docs | 50 | tx-engineering | state_name | 5 | 50 | 1.00 | 1.00 | 0.40 |  |
| lexical + clean docs | 50 | ca-computer-science | state_name | 3 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean docs | 50 | fl-business | state_name | 7 | 50 | 1.00 | 1.00 | 0.14 |  |
| lexical + clean docs | 50 | ma-private | state_name | 6 | 50 | 1.00 | 1.00 | 0.17 |  |
| lexical + clean docs | 50 | tx-health | state_name | 2 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean docs | 50 | ga-psychology | state_name | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 50 | midwest-public | exact_vocabulary | 9 | 50 | 1.00 | 0.78 | 0.33 |  |
| lexical + clean docs | 50 | south-suburban | exact_vocabulary | 8 | 50 | 1.00 | 0.62 | 0.25 |  |
| lexical + clean docs | 50 | small-private | exact_vocabulary | 6 | 50 | 1.00 | 1.00 | 0.33 |  |
| lexical + clean docs | 50 | town-setting | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean docs | 50 | northeast-mathematics | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 0.20 |  |
| lexical + clean docs | 50 | agriculture | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 50 | legal-studies | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean docs | 50 | education | exact_vocabulary | 2 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean docs | 50 | criminal-justice | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean docs | 50 | performing-arts | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 0.20 |  |
| lexical + clean docs | 50 | division-three | synonym | 9 | 50 | 1.00 | 1.00 | 0.11 |  |
| lexical + clean docs | 50 | division-two | synonym | 2 | 50 | 1.00 | 1.00 | 0.50 |  |
| lexical + clean docs | 50 | fl-nursing | synonym | 5 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean docs | 50 | oh-big-state | synonym | 2 | 50 | 1.00 | 0.50 | 0.00 |  |
| lexical + clean docs | 50 | ga-tech-focused | synonym | 2 | 50 | 1.00 | 1.00 | 0.50 |  |
| lexical + clean docs | 50 | midwest-coding | synonym | 6 | 50 | 1.00 | 0.50 | 0.50 |  |
| lexical + clean docs | 50 | film-theater | synonym | 5 | 50 | 1.00 | 1.00 | 0.20 |  |
| lexical + clean docs | 50 | bay-area-cs | world_knowledge | 2 | 50 | 0.50 | 0.00 | 0.00 |  |
| lexical + clean docs | 50 | hbcu | world_knowledge | 2 | 50 | 1.00 | 0.00 | 0.00 |  |
| lexical + clean docs | 50 | ivy-league | world_knowledge | 8 | 50 | 0.25 | 0.00 | 0.00 |  |
| lexical + clean docs | 50 | tx-cheap-public | structured_only | 4 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean docs | 50 | small-classes | structured_only | 17 | 50 | 0.59 | 0.40 | 0.20 |  |
| lexical + clean docs | 50 | south-selective-private | structured_only | 6 | 50 | 1.00 | 0.67 | 0.33 |  |
| lexical + clean docs | 50 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 50 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 50 | filter-ut-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical + clean docs | 50 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 50 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean docs | 50 | filter-private-affordable-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical + clean + filter first | 10 | tx-engineering | state_name | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | ca-computer-science | state_name | 3 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | fl-business | state_name | 7 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | ma-private | state_name | 6 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | tx-health | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | ga-psychology | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | midwest-public | exact_vocabulary | 9 | 10 | 0.78 | 0.78 | 0.78 |  |
| lexical + clean + filter first | 10 | south-suburban | exact_vocabulary | 8 | 10 | 0.62 | 0.62 | 0.62 |  |
| lexical + clean + filter first | 10 | small-private | exact_vocabulary | 6 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | town-setting | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | northeast-mathematics | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | agriculture | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | legal-studies | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | education | exact_vocabulary | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | criminal-justice | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | performing-arts | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | division-three | synonym | 9 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | division-two | synonym | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | fl-nursing | synonym | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | oh-big-state | synonym | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| lexical + clean + filter first | 10 | ga-tech-focused | synonym | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | midwest-coding | synonym | 6 | 10 | 0.50 | 0.50 | 0.50 |  |
| lexical + clean + filter first | 10 | film-theater | synonym | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | bay-area-cs | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| lexical + clean + filter first | 10 | hbcu | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| lexical + clean + filter first | 10 | ivy-league | world_knowledge | 8 | 10 | 0.00 | 0.00 | 0.00 |  |
| lexical + clean + filter first | 10 | tx-cheap-public | structured_only | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | small-classes | structured_only | 17 | 10 | 0.24 | 0.40 | 0.40 |  |
| lexical + clean + filter first | 10 | south-selective-private | structured_only | 6 | 10 | 0.67 | 0.67 | 0.67 |  |
| lexical + clean + filter first | 10 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 10 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 25 | tx-engineering | state_name | 5 | 25 | 1.00 | 1.00 | 0.40 |  |
| lexical + clean + filter first | 25 | ca-computer-science | state_name | 3 | 25 | 1.00 | 1.00 | 0.67 |  |
| lexical + clean + filter first | 25 | fl-business | state_name | 7 | 25 | 1.00 | 1.00 | 0.43 |  |
| lexical + clean + filter first | 25 | ma-private | state_name | 6 | 25 | 1.00 | 1.00 | 0.33 |  |
| lexical + clean + filter first | 25 | tx-health | state_name | 2 | 25 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean + filter first | 25 | ga-psychology | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 25 | midwest-public | exact_vocabulary | 9 | 25 | 1.00 | 0.78 | 0.67 |  |
| lexical + clean + filter first | 25 | south-suburban | exact_vocabulary | 8 | 25 | 1.00 | 0.62 | 0.50 |  |
| lexical + clean + filter first | 25 | small-private | exact_vocabulary | 6 | 25 | 1.00 | 1.00 | 0.50 |  |
| lexical + clean + filter first | 25 | town-setting | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean + filter first | 25 | northeast-mathematics | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 0.60 |  |
| lexical + clean + filter first | 25 | agriculture | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 25 | legal-studies | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean + filter first | 25 | education | exact_vocabulary | 2 | 25 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean + filter first | 25 | criminal-justice | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean + filter first | 25 | performing-arts | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 0.20 |  |
| lexical + clean + filter first | 25 | division-three | synonym | 9 | 25 | 1.00 | 1.00 | 0.44 |  |
| lexical + clean + filter first | 25 | division-two | synonym | 2 | 25 | 1.00 | 1.00 | 0.50 |  |
| lexical + clean + filter first | 25 | fl-nursing | synonym | 5 | 25 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean + filter first | 25 | oh-big-state | synonym | 2 | 25 | 1.00 | 0.50 | 0.50 |  |
| lexical + clean + filter first | 25 | ga-tech-focused | synonym | 2 | 25 | 1.00 | 1.00 | 0.50 |  |
| lexical + clean + filter first | 25 | midwest-coding | synonym | 6 | 25 | 1.00 | 0.50 | 1.00 |  |
| lexical + clean + filter first | 25 | film-theater | synonym | 5 | 25 | 1.00 | 1.00 | 0.20 |  |
| lexical + clean + filter first | 25 | bay-area-cs | world_knowledge | 2 | 25 | 0.50 | 0.00 | 0.50 |  |
| lexical + clean + filter first | 25 | hbcu | world_knowledge | 2 | 25 | 0.50 | 0.00 | 0.00 |  |
| lexical + clean + filter first | 25 | ivy-league | world_knowledge | 8 | 25 | 0.12 | 0.00 | 0.00 |  |
| lexical + clean + filter first | 25 | tx-cheap-public | structured_only | 4 | 25 | 1.00 | 1.00 | 0.25 |  |
| lexical + clean + filter first | 25 | small-classes | structured_only | 17 | 25 | 0.29 | 0.40 | 0.30 |  |
| lexical + clean + filter first | 25 | south-selective-private | structured_only | 6 | 25 | 1.00 | 0.67 | 0.67 |  |
| lexical + clean + filter first | 25 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 25 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 25 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 25 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 25 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 25 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 50 | tx-engineering | state_name | 5 | 50 | 1.00 | 1.00 | 0.40 |  |
| lexical + clean + filter first | 50 | ca-computer-science | state_name | 3 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean + filter first | 50 | fl-business | state_name | 7 | 50 | 1.00 | 1.00 | 0.14 |  |
| lexical + clean + filter first | 50 | ma-private | state_name | 6 | 50 | 1.00 | 1.00 | 0.17 |  |
| lexical + clean + filter first | 50 | tx-health | state_name | 2 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean + filter first | 50 | ga-psychology | state_name | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 50 | midwest-public | exact_vocabulary | 9 | 50 | 1.00 | 0.78 | 0.33 |  |
| lexical + clean + filter first | 50 | south-suburban | exact_vocabulary | 8 | 50 | 1.00 | 0.62 | 0.25 |  |
| lexical + clean + filter first | 50 | small-private | exact_vocabulary | 6 | 50 | 1.00 | 1.00 | 0.33 |  |
| lexical + clean + filter first | 50 | town-setting | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean + filter first | 50 | northeast-mathematics | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 0.20 |  |
| lexical + clean + filter first | 50 | agriculture | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 50 | legal-studies | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean + filter first | 50 | education | exact_vocabulary | 2 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean + filter first | 50 | criminal-justice | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean + filter first | 50 | performing-arts | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 0.20 |  |
| lexical + clean + filter first | 50 | division-three | synonym | 9 | 50 | 1.00 | 1.00 | 0.11 |  |
| lexical + clean + filter first | 50 | division-two | synonym | 2 | 50 | 1.00 | 1.00 | 0.50 |  |
| lexical + clean + filter first | 50 | fl-nursing | synonym | 5 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean + filter first | 50 | oh-big-state | synonym | 2 | 50 | 1.00 | 0.50 | 0.00 |  |
| lexical + clean + filter first | 50 | ga-tech-focused | synonym | 2 | 50 | 1.00 | 1.00 | 0.50 |  |
| lexical + clean + filter first | 50 | midwest-coding | synonym | 6 | 50 | 1.00 | 0.50 | 0.50 |  |
| lexical + clean + filter first | 50 | film-theater | synonym | 5 | 50 | 1.00 | 1.00 | 0.20 |  |
| lexical + clean + filter first | 50 | bay-area-cs | world_knowledge | 2 | 50 | 0.50 | 0.00 | 0.00 |  |
| lexical + clean + filter first | 50 | hbcu | world_knowledge | 2 | 50 | 1.00 | 0.00 | 0.00 |  |
| lexical + clean + filter first | 50 | ivy-league | world_knowledge | 8 | 50 | 0.25 | 0.00 | 0.00 |  |
| lexical + clean + filter first | 50 | tx-cheap-public | structured_only | 4 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean + filter first | 50 | small-classes | structured_only | 17 | 50 | 0.59 | 0.40 | 0.20 |  |
| lexical + clean + filter first | 50 | south-selective-private | structured_only | 6 | 50 | 1.00 | 0.67 | 0.33 |  |
| lexical + clean + filter first | 50 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 50 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 50 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 50 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 50 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first | 50 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | tx-engineering | state_name | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | ca-computer-science | state_name | 3 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | fl-business | state_name | 7 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | ma-private | state_name | 6 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | tx-health | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | ga-psychology | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | midwest-public | exact_vocabulary | 9 | 10 | 0.78 | 0.78 | 0.78 |  |
| lexical + clean + filter first + relevance order | 10 | south-suburban | exact_vocabulary | 8 | 10 | 0.62 | 0.62 | 0.62 |  |
| lexical + clean + filter first + relevance order | 10 | small-private | exact_vocabulary | 6 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | town-setting | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | northeast-mathematics | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | agriculture | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | legal-studies | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | education | exact_vocabulary | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | criminal-justice | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | performing-arts | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | division-three | synonym | 9 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | division-two | synonym | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | fl-nursing | synonym | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | oh-big-state | synonym | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| lexical + clean + filter first + relevance order | 10 | ga-tech-focused | synonym | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | midwest-coding | synonym | 6 | 10 | 0.50 | 0.50 | 0.50 |  |
| lexical + clean + filter first + relevance order | 10 | film-theater | synonym | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | bay-area-cs | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| lexical + clean + filter first + relevance order | 10 | hbcu | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| lexical + clean + filter first + relevance order | 10 | ivy-league | world_knowledge | 8 | 10 | 0.00 | 0.00 | 0.00 |  |
| lexical + clean + filter first + relevance order | 10 | tx-cheap-public | structured_only | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | small-classes | structured_only | 17 | 10 | 0.24 | 0.40 | 0.40 |  |
| lexical + clean + filter first + relevance order | 10 | south-selective-private | structured_only | 6 | 10 | 0.67 | 0.67 | 0.67 |  |
| lexical + clean + filter first + relevance order | 10 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 10 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | tx-engineering | state_name | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | ca-computer-science | state_name | 3 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | fl-business | state_name | 7 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | ma-private | state_name | 6 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | tx-health | state_name | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | ga-psychology | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | midwest-public | exact_vocabulary | 9 | 25 | 1.00 | 0.78 | 0.67 |  |
| lexical + clean + filter first + relevance order | 25 | south-suburban | exact_vocabulary | 8 | 25 | 1.00 | 0.62 | 0.75 |  |
| lexical + clean + filter first + relevance order | 25 | small-private | exact_vocabulary | 6 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | town-setting | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | northeast-mathematics | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | agriculture | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | legal-studies | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | education | exact_vocabulary | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | criminal-justice | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | performing-arts | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | division-three | synonym | 9 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | division-two | synonym | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | fl-nursing | synonym | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | oh-big-state | synonym | 2 | 25 | 1.00 | 0.50 | 0.50 |  |
| lexical + clean + filter first + relevance order | 25 | ga-tech-focused | synonym | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | midwest-coding | synonym | 6 | 25 | 1.00 | 0.50 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | film-theater | synonym | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | bay-area-cs | world_knowledge | 2 | 25 | 0.50 | 0.00 | 0.00 |  |
| lexical + clean + filter first + relevance order | 25 | hbcu | world_knowledge | 2 | 25 | 0.50 | 0.00 | 0.00 |  |
| lexical + clean + filter first + relevance order | 25 | ivy-league | world_knowledge | 8 | 25 | 0.12 | 0.00 | 0.00 |  |
| lexical + clean + filter first + relevance order | 25 | tx-cheap-public | structured_only | 4 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | small-classes | structured_only | 17 | 25 | 0.29 | 0.40 | 0.40 |  |
| lexical + clean + filter first + relevance order | 25 | south-selective-private | structured_only | 6 | 25 | 1.00 | 0.67 | 0.83 |  |
| lexical + clean + filter first + relevance order | 25 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 25 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | tx-engineering | state_name | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | ca-computer-science | state_name | 3 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | fl-business | state_name | 7 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | ma-private | state_name | 6 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | tx-health | state_name | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | ga-psychology | state_name | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | midwest-public | exact_vocabulary | 9 | 50 | 1.00 | 0.78 | 0.67 |  |
| lexical + clean + filter first + relevance order | 50 | south-suburban | exact_vocabulary | 8 | 50 | 1.00 | 0.62 | 0.75 |  |
| lexical + clean + filter first + relevance order | 50 | small-private | exact_vocabulary | 6 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | town-setting | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | northeast-mathematics | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | agriculture | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | legal-studies | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | education | exact_vocabulary | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | criminal-justice | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | performing-arts | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | division-three | synonym | 9 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | division-two | synonym | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | fl-nursing | synonym | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | oh-big-state | synonym | 2 | 50 | 1.00 | 0.50 | 0.50 |  |
| lexical + clean + filter first + relevance order | 50 | ga-tech-focused | synonym | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | midwest-coding | synonym | 6 | 50 | 1.00 | 0.50 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | film-theater | synonym | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | bay-area-cs | world_knowledge | 2 | 50 | 0.50 | 0.00 | 0.00 |  |
| lexical + clean + filter first + relevance order | 50 | hbcu | world_knowledge | 2 | 50 | 1.00 | 0.00 | 0.00 |  |
| lexical + clean + filter first + relevance order | 50 | ivy-league | world_knowledge | 8 | 50 | 0.25 | 0.00 | 0.00 |  |
| lexical + clean + filter first + relevance order | 50 | tx-cheap-public | structured_only | 4 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | small-classes | structured_only | 17 | 50 | 0.59 | 0.40 | 0.40 |  |
| lexical + clean + filter first + relevance order | 50 | south-selective-private | structured_only | 6 | 50 | 1.00 | 0.67 | 0.83 |  |
| lexical + clean + filter first + relevance order | 50 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + relevance order | 50 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | tx-engineering | state_name | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | ca-computer-science | state_name | 3 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | fl-business | state_name | 7 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | ma-private | state_name | 6 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | tx-health | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | ga-psychology | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | midwest-public | exact_vocabulary | 9 | 10 | 0.78 | 0.78 | 0.78 |  |
| lexical + clean + filter first + matched then fit | 10 | south-suburban | exact_vocabulary | 8 | 10 | 0.62 | 0.62 | 0.62 |  |
| lexical + clean + filter first + matched then fit | 10 | small-private | exact_vocabulary | 6 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | town-setting | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | northeast-mathematics | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | agriculture | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | legal-studies | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | education | exact_vocabulary | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | criminal-justice | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | performing-arts | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | division-three | synonym | 9 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | division-two | synonym | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | fl-nursing | synonym | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | oh-big-state | synonym | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| lexical + clean + filter first + matched then fit | 10 | ga-tech-focused | synonym | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | midwest-coding | synonym | 6 | 10 | 0.50 | 0.50 | 0.50 |  |
| lexical + clean + filter first + matched then fit | 10 | film-theater | synonym | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | bay-area-cs | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| lexical + clean + filter first + matched then fit | 10 | hbcu | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| lexical + clean + filter first + matched then fit | 10 | ivy-league | world_knowledge | 8 | 10 | 0.00 | 0.00 | 0.00 |  |
| lexical + clean + filter first + matched then fit | 10 | tx-cheap-public | structured_only | 4 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | small-classes | structured_only | 17 | 10 | 0.24 | 0.40 | 0.40 |  |
| lexical + clean + filter first + matched then fit | 10 | south-selective-private | structured_only | 6 | 10 | 0.67 | 0.67 | 0.67 |  |
| lexical + clean + filter first + matched then fit | 10 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 10 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 25 | tx-engineering | state_name | 5 | 25 | 1.00 | 1.00 | 0.40 |  |
| lexical + clean + filter first + matched then fit | 25 | ca-computer-science | state_name | 3 | 25 | 1.00 | 1.00 | 0.67 |  |
| lexical + clean + filter first + matched then fit | 25 | fl-business | state_name | 7 | 25 | 1.00 | 1.00 | 0.43 |  |
| lexical + clean + filter first + matched then fit | 25 | ma-private | state_name | 6 | 25 | 1.00 | 1.00 | 0.33 |  |
| lexical + clean + filter first + matched then fit | 25 | tx-health | state_name | 2 | 25 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean + filter first + matched then fit | 25 | ga-psychology | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 25 | midwest-public | exact_vocabulary | 9 | 25 | 1.00 | 0.78 | 0.67 |  |
| lexical + clean + filter first + matched then fit | 25 | south-suburban | exact_vocabulary | 8 | 25 | 1.00 | 0.62 | 0.50 |  |
| lexical + clean + filter first + matched then fit | 25 | small-private | exact_vocabulary | 6 | 25 | 1.00 | 1.00 | 0.50 |  |
| lexical + clean + filter first + matched then fit | 25 | town-setting | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 25 | northeast-mathematics | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 0.60 |  |
| lexical + clean + filter first + matched then fit | 25 | agriculture | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 25 | legal-studies | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 25 | education | exact_vocabulary | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 25 | criminal-justice | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 25 | performing-arts | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 25 | division-three | synonym | 9 | 25 | 1.00 | 1.00 | 0.44 |  |
| lexical + clean + filter first + matched then fit | 25 | division-two | synonym | 2 | 25 | 1.00 | 1.00 | 0.50 |  |
| lexical + clean + filter first + matched then fit | 25 | fl-nursing | synonym | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 25 | oh-big-state | synonym | 2 | 25 | 1.00 | 0.50 | 0.50 |  |
| lexical + clean + filter first + matched then fit | 25 | ga-tech-focused | synonym | 2 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 25 | midwest-coding | synonym | 6 | 25 | 1.00 | 0.50 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 25 | film-theater | synonym | 5 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 25 | bay-area-cs | world_knowledge | 2 | 25 | 0.50 | 0.00 | 0.00 |  |
| lexical + clean + filter first + matched then fit | 25 | hbcu | world_knowledge | 2 | 25 | 0.50 | 0.00 | 0.00 |  |
| lexical + clean + filter first + matched then fit | 25 | ivy-league | world_knowledge | 8 | 25 | 0.12 | 0.00 | 0.00 |  |
| lexical + clean + filter first + matched then fit | 25 | tx-cheap-public | structured_only | 4 | 25 | 1.00 | 1.00 | 0.25 |  |
| lexical + clean + filter first + matched then fit | 25 | small-classes | structured_only | 17 | 25 | 0.29 | 0.40 | 0.40 |  |
| lexical + clean + filter first + matched then fit | 25 | south-selective-private | structured_only | 6 | 25 | 1.00 | 0.67 | 0.67 |  |
| lexical + clean + filter first + matched then fit | 25 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 25 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 25 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 25 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 25 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 25 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 50 | tx-engineering | state_name | 5 | 50 | 1.00 | 1.00 | 0.40 |  |
| lexical + clean + filter first + matched then fit | 50 | ca-computer-science | state_name | 3 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean + filter first + matched then fit | 50 | fl-business | state_name | 7 | 50 | 1.00 | 1.00 | 0.14 |  |
| lexical + clean + filter first + matched then fit | 50 | ma-private | state_name | 6 | 50 | 1.00 | 1.00 | 0.33 |  |
| lexical + clean + filter first + matched then fit | 50 | tx-health | state_name | 2 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean + filter first + matched then fit | 50 | ga-psychology | state_name | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 50 | midwest-public | exact_vocabulary | 9 | 50 | 1.00 | 0.78 | 0.33 |  |
| lexical + clean + filter first + matched then fit | 50 | south-suburban | exact_vocabulary | 8 | 50 | 1.00 | 0.62 | 0.25 |  |
| lexical + clean + filter first + matched then fit | 50 | small-private | exact_vocabulary | 6 | 50 | 1.00 | 1.00 | 0.50 |  |
| lexical + clean + filter first + matched then fit | 50 | town-setting | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 50 | northeast-mathematics | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 0.60 |  |
| lexical + clean + filter first + matched then fit | 50 | agriculture | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 50 | legal-studies | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 50 | education | exact_vocabulary | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 50 | criminal-justice | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 50 | performing-arts | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 50 | division-three | synonym | 9 | 50 | 1.00 | 1.00 | 0.11 |  |
| lexical + clean + filter first + matched then fit | 50 | division-two | synonym | 2 | 50 | 1.00 | 1.00 | 0.50 |  |
| lexical + clean + filter first + matched then fit | 50 | fl-nursing | synonym | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 50 | oh-big-state | synonym | 2 | 50 | 1.00 | 0.50 | 0.00 |  |
| lexical + clean + filter first + matched then fit | 50 | ga-tech-focused | synonym | 2 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 50 | midwest-coding | synonym | 6 | 50 | 1.00 | 0.50 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 50 | film-theater | synonym | 5 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 50 | bay-area-cs | world_knowledge | 2 | 50 | 0.50 | 0.00 | 0.00 |  |
| lexical + clean + filter first + matched then fit | 50 | hbcu | world_knowledge | 2 | 50 | 1.00 | 0.00 | 0.00 |  |
| lexical + clean + filter first + matched then fit | 50 | ivy-league | world_knowledge | 8 | 50 | 0.25 | 0.00 | 0.00 |  |
| lexical + clean + filter first + matched then fit | 50 | tx-cheap-public | structured_only | 4 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical + clean + filter first + matched then fit | 50 | small-classes | structured_only | 17 | 50 | 0.59 | 0.40 | 0.40 |  |
| lexical + clean + filter first + matched then fit | 50 | south-selective-private | structured_only | 6 | 50 | 1.00 | 0.67 | 0.33 |  |
| lexical + clean + filter first + matched then fit | 50 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 50 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 50 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 50 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 50 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical + clean + filter first + matched then fit | 50 | filter-private-affordable-business | filtered | 1 | 4 | 1.00 | 1.00 | 1.00 |  |
