35 queries over 92 schools; candidate limits [10, 25, 50]
queries per category: {'exact_vocabulary': 10, 'filtered': 6, 'state_name': 6, 'structured_only': 3, 'synonym': 7, 'world_knowledge': 3}

## Overall

| arm | candidate_limit | pool recall | retriever P@10 | end-to-end P@10 | filtered: empty (post) | filtered: empty (pre) | filtered: recall post -> pre | in-process p50 / p95 ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| hash | 10 | 0.45 | 0.46 | 0.46 | 5/6 | 0/6 | 0.17 -> 1.00 | 1.82 / 3.43 |
| hash | 25 | 0.64 | 0.51 | 0.34 | 3/6 | 0/6 | 0.50 -> 1.00 | 2.85 / 5.04 |
| hash | 50 | 0.85 | 0.60 | 0.35 | 0/6 | 0/6 | 1.00 -> 1.00 | 4.83 / 7.69 |
| lexical | 10 | 0.54 | 0.54 | 0.54 | 6/6 | 0/6 | 0.00 -> 1.00 | 3.87 / 6.53 |
| lexical | 25 | 0.72 | 0.60 | 0.36 | 4/6 | 0/6 | 0.33 -> 1.00 | 4.96 / 7.62 |
| lexical | 50 | 0.85 | 0.66 | 0.30 | 2/6 | 0/6 | 0.67 -> 1.00 | 6.57 / 9.56 |

## Retriever P@10 by query category

| arm | candidate_limit | exact_vocabulary | filtered | state_name | structured_only | synonym | world_knowledge |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| hash | 10 | 0.86 | 0.17 | 0.55 | 0.26 | 0.24 | 0.21 |
| hash | 25 | 0.86 | 0.50 | 0.55 | 0.26 | 0.24 | 0.21 |
| hash | 50 | 0.86 | 1.00 | 0.55 | 0.26 | 0.24 | 0.21 |
| lexical | 10 | 0.92 | 0.00 | 0.75 | 0.61 | 0.51 | 0.00 |
| lexical | 25 | 0.92 | 0.33 | 0.75 | 0.61 | 0.51 | 0.00 |
| lexical | 50 | 0.92 | 0.67 | 0.75 | 0.61 | 0.51 | 0.00 |

## Per query

| arm | limit | query | category | relevant | pool | pool recall | retriever P@10 | end-to-end P@10 | empty |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| hash | 10 | tx-engineering | state_name | 5 | 10 | 0.80 | 0.80 | 0.80 |  |
| hash | 10 | ca-computer-science | state_name | 3 | 10 | 0.67 | 0.67 | 0.67 |  |
| hash | 10 | fl-business | state_name | 7 | 10 | 0.14 | 0.14 | 0.14 |  |
| hash | 10 | ma-private | state_name | 6 | 10 | 0.17 | 0.17 | 0.17 |  |
| hash | 10 | tx-health | state_name | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| hash | 10 | ga-psychology | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash | 10 | midwest-public | exact_vocabulary | 9 | 10 | 0.89 | 0.89 | 0.89 |  |
| hash | 10 | south-suburban | exact_vocabulary | 8 | 10 | 0.75 | 0.75 | 0.75 |  |
| hash | 10 | small-private | exact_vocabulary | 6 | 10 | 0.67 | 0.67 | 0.67 |  |
| hash | 10 | town-setting | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash | 10 | northeast-mathematics | exact_vocabulary | 5 | 10 | 0.80 | 0.80 | 0.80 |  |
| hash | 10 | agriculture | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash | 10 | legal-studies | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash | 10 | education | exact_vocabulary | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| hash | 10 | criminal-justice | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash | 10 | performing-arts | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| hash | 10 | division-three | synonym | 9 | 10 | 0.22 | 0.22 | 0.22 |  |
| hash | 10 | division-two | synonym | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| hash | 10 | fl-nursing | synonym | 5 | 10 | 0.40 | 0.40 | 0.40 |  |
| hash | 10 | oh-big-state | synonym | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| hash | 10 | ga-tech-focused | synonym | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| hash | 10 | midwest-coding | synonym | 6 | 10 | 0.33 | 0.33 | 0.33 |  |
| hash | 10 | film-theater | synonym | 5 | 10 | 0.20 | 0.20 | 0.20 |  |
| hash | 10 | bay-area-cs | world_knowledge | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| hash | 10 | hbcu | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| hash | 10 | ivy-league | world_knowledge | 8 | 10 | 0.12 | 0.12 | 0.12 |  |
| hash | 10 | tx-cheap-public | structured_only | 4 | 10 | 0.25 | 0.25 | 0.25 |  |
| hash | 10 | small-classes | structured_only | 17 | 10 | 0.12 | 0.20 | 0.20 |  |
| hash | 10 | south-selective-private | structured_only | 6 | 10 | 0.33 | 0.33 | 0.33 |  |
| hash | 10 | filter-or-engineering | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| hash | 10 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash | 10 | filter-ut-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| hash | 10 | filter-dc-social-sciences | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| hash | 10 | filter-ms-health | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| hash | 10 | filter-private-affordable-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| hash | 25 | tx-engineering | state_name | 5 | 25 | 1.00 | 0.80 | 0.40 |  |
| hash | 25 | ca-computer-science | state_name | 3 | 25 | 1.00 | 0.67 | 1.00 |  |
| hash | 25 | fl-business | state_name | 7 | 25 | 0.29 | 0.14 | 0.14 |  |
| hash | 25 | ma-private | state_name | 6 | 25 | 0.67 | 0.17 | 0.17 |  |
| hash | 25 | tx-health | state_name | 2 | 25 | 1.00 | 0.50 | 0.00 |  |
| hash | 25 | ga-psychology | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| hash | 25 | midwest-public | exact_vocabulary | 9 | 25 | 1.00 | 0.89 | 0.56 |  |
| hash | 25 | south-suburban | exact_vocabulary | 8 | 25 | 1.00 | 0.75 | 0.50 |  |
| hash | 25 | small-private | exact_vocabulary | 6 | 25 | 0.83 | 0.67 | 0.50 |  |
| hash | 25 | town-setting | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| hash | 25 | northeast-mathematics | exact_vocabulary | 5 | 25 | 1.00 | 0.80 | 0.80 |  |
| hash | 25 | agriculture | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| hash | 25 | legal-studies | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| hash | 25 | education | exact_vocabulary | 2 | 25 | 1.00 | 0.50 | 0.00 |  |
| hash | 25 | criminal-justice | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| hash | 25 | performing-arts | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 0.20 |  |
| hash | 25 | division-three | synonym | 9 | 25 | 0.33 | 0.22 | 0.22 |  |
| hash | 25 | division-two | synonym | 2 | 25 | 0.00 | 0.00 | 0.00 |  |
| hash | 25 | fl-nursing | synonym | 5 | 25 | 0.60 | 0.40 | 0.00 |  |
| hash | 25 | oh-big-state | synonym | 2 | 25 | 0.00 | 0.00 | 0.00 |  |
| hash | 25 | ga-tech-focused | synonym | 2 | 25 | 0.50 | 0.50 | 0.50 |  |
| hash | 25 | midwest-coding | synonym | 6 | 25 | 0.50 | 0.33 | 0.50 |  |
| hash | 25 | film-theater | synonym | 5 | 25 | 0.20 | 0.20 | 0.00 |  |
| hash | 25 | bay-area-cs | world_knowledge | 2 | 25 | 0.50 | 0.50 | 0.50 |  |
| hash | 25 | hbcu | world_knowledge | 2 | 25 | 0.00 | 0.00 | 0.00 |  |
| hash | 25 | ivy-league | world_knowledge | 8 | 25 | 0.50 | 0.12 | 0.25 |  |
| hash | 25 | tx-cheap-public | structured_only | 4 | 25 | 0.75 | 0.25 | 0.00 |  |
| hash | 25 | small-classes | structured_only | 17 | 25 | 0.24 | 0.20 | 0.20 |  |
| hash | 25 | south-selective-private | structured_only | 6 | 25 | 0.67 | 0.33 | 0.50 |  |
| hash | 25 | filter-or-engineering | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| hash | 25 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash | 25 | filter-ut-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| hash | 25 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash | 25 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash | 25 | filter-private-affordable-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| hash | 50 | tx-engineering | state_name | 5 | 50 | 1.00 | 0.80 | 0.40 |  |
| hash | 50 | ca-computer-science | state_name | 3 | 50 | 1.00 | 0.67 | 0.33 |  |
| hash | 50 | fl-business | state_name | 7 | 50 | 0.86 | 0.14 | 0.00 |  |
| hash | 50 | ma-private | state_name | 6 | 50 | 1.00 | 0.17 | 0.17 |  |
| hash | 50 | tx-health | state_name | 2 | 50 | 1.00 | 0.50 | 0.00 |  |
| hash | 50 | ga-psychology | state_name | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| hash | 50 | midwest-public | exact_vocabulary | 9 | 50 | 1.00 | 0.89 | 0.33 |  |
| hash | 50 | south-suburban | exact_vocabulary | 8 | 50 | 1.00 | 0.75 | 0.12 |  |
| hash | 50 | small-private | exact_vocabulary | 6 | 50 | 0.83 | 0.67 | 0.17 |  |
| hash | 50 | town-setting | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| hash | 50 | northeast-mathematics | exact_vocabulary | 5 | 50 | 1.00 | 0.80 | 0.20 |  |
| hash | 50 | agriculture | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| hash | 50 | legal-studies | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| hash | 50 | education | exact_vocabulary | 2 | 50 | 1.00 | 0.50 | 0.00 |  |
| hash | 50 | criminal-justice | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| hash | 50 | performing-arts | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 0.20 |  |
| hash | 50 | division-three | synonym | 9 | 50 | 0.67 | 0.22 | 0.11 |  |
| hash | 50 | division-two | synonym | 2 | 50 | 0.00 | 0.00 | 0.00 |  |
| hash | 50 | fl-nursing | synonym | 5 | 50 | 0.80 | 0.40 | 0.00 |  |
| hash | 50 | oh-big-state | synonym | 2 | 50 | 0.00 | 0.00 | 0.00 |  |
| hash | 50 | ga-tech-focused | synonym | 2 | 50 | 1.00 | 0.50 | 0.50 |  |
| hash | 50 | midwest-coding | synonym | 6 | 50 | 1.00 | 0.33 | 0.50 |  |
| hash | 50 | film-theater | synonym | 5 | 50 | 0.60 | 0.20 | 0.00 |  |
| hash | 50 | bay-area-cs | world_knowledge | 2 | 50 | 1.00 | 0.50 | 0.50 |  |
| hash | 50 | hbcu | world_knowledge | 2 | 50 | 0.00 | 0.00 | 0.00 |  |
| hash | 50 | ivy-league | world_knowledge | 8 | 50 | 0.88 | 0.12 | 0.12 |  |
| hash | 50 | tx-cheap-public | structured_only | 4 | 50 | 0.75 | 0.25 | 0.00 |  |
| hash | 50 | small-classes | structured_only | 17 | 50 | 0.59 | 0.20 | 0.30 |  |
| hash | 50 | south-selective-private | structured_only | 6 | 50 | 0.83 | 0.33 | 0.33 |  |
| hash | 50 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash | 50 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash | 50 | filter-ut-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash | 50 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash | 50 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| hash | 50 | filter-private-affordable-business | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical | 10 | tx-engineering | state_name | 5 | 10 | 0.80 | 0.80 | 0.80 |  |
| lexical | 10 | ca-computer-science | state_name | 3 | 10 | 0.67 | 0.67 | 0.67 |  |
| lexical | 10 | fl-business | state_name | 7 | 10 | 0.86 | 0.86 | 0.86 |  |
| lexical | 10 | ma-private | state_name | 6 | 10 | 0.17 | 0.17 | 0.17 |  |
| lexical | 10 | tx-health | state_name | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical | 10 | ga-psychology | state_name | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical | 10 | midwest-public | exact_vocabulary | 9 | 10 | 0.56 | 0.56 | 0.56 |  |
| lexical | 10 | south-suburban | exact_vocabulary | 8 | 10 | 0.62 | 0.62 | 0.62 |  |
| lexical | 10 | small-private | exact_vocabulary | 6 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical | 10 | town-setting | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical | 10 | northeast-mathematics | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical | 10 | agriculture | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical | 10 | legal-studies | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical | 10 | education | exact_vocabulary | 2 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical | 10 | criminal-justice | exact_vocabulary | 1 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical | 10 | performing-arts | exact_vocabulary | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical | 10 | division-three | synonym | 9 | 10 | 0.11 | 0.11 | 0.11 |  |
| lexical | 10 | division-two | synonym | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| lexical | 10 | fl-nursing | synonym | 5 | 10 | 0.80 | 0.80 | 0.80 |  |
| lexical | 10 | oh-big-state | synonym | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| lexical | 10 | ga-tech-focused | synonym | 2 | 10 | 0.50 | 0.50 | 0.50 |  |
| lexical | 10 | midwest-coding | synonym | 6 | 10 | 0.67 | 0.67 | 0.67 |  |
| lexical | 10 | film-theater | synonym | 5 | 10 | 1.00 | 1.00 | 1.00 |  |
| lexical | 10 | bay-area-cs | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| lexical | 10 | hbcu | world_knowledge | 2 | 10 | 0.00 | 0.00 | 0.00 |  |
| lexical | 10 | ivy-league | world_knowledge | 8 | 10 | 0.00 | 0.00 | 0.00 |  |
| lexical | 10 | tx-cheap-public | structured_only | 4 | 10 | 0.75 | 0.75 | 0.75 |  |
| lexical | 10 | small-classes | structured_only | 17 | 10 | 0.24 | 0.40 | 0.40 |  |
| lexical | 10 | south-selective-private | structured_only | 6 | 10 | 0.67 | 0.67 | 0.67 |  |
| lexical | 10 | filter-or-engineering | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical | 10 | filter-wa-computer-science | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical | 10 | filter-ut-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical | 10 | filter-dc-social-sciences | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical | 10 | filter-ms-health | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical | 10 | filter-private-affordable-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical | 25 | tx-engineering | state_name | 5 | 25 | 0.80 | 0.80 | 0.20 |  |
| lexical | 25 | ca-computer-science | state_name | 3 | 25 | 0.67 | 0.67 | 0.67 |  |
| lexical | 25 | fl-business | state_name | 7 | 25 | 1.00 | 0.86 | 0.43 |  |
| lexical | 25 | ma-private | state_name | 6 | 25 | 1.00 | 0.17 | 0.33 |  |
| lexical | 25 | tx-health | state_name | 2 | 25 | 1.00 | 1.00 | 0.00 |  |
| lexical | 25 | ga-psychology | state_name | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical | 25 | midwest-public | exact_vocabulary | 9 | 25 | 1.00 | 0.56 | 0.67 |  |
| lexical | 25 | south-suburban | exact_vocabulary | 8 | 25 | 1.00 | 0.62 | 0.50 |  |
| lexical | 25 | small-private | exact_vocabulary | 6 | 25 | 1.00 | 1.00 | 0.50 |  |
| lexical | 25 | town-setting | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| lexical | 25 | northeast-mathematics | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 0.80 |  |
| lexical | 25 | agriculture | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 1.00 |  |
| lexical | 25 | legal-studies | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| lexical | 25 | education | exact_vocabulary | 2 | 25 | 1.00 | 1.00 | 0.00 |  |
| lexical | 25 | criminal-justice | exact_vocabulary | 1 | 25 | 1.00 | 1.00 | 0.00 |  |
| lexical | 25 | performing-arts | exact_vocabulary | 5 | 25 | 1.00 | 1.00 | 0.20 |  |
| lexical | 25 | division-three | synonym | 9 | 25 | 0.11 | 0.11 | 0.11 |  |
| lexical | 25 | division-two | synonym | 2 | 25 | 0.50 | 0.00 | 0.50 |  |
| lexical | 25 | fl-nursing | synonym | 5 | 25 | 0.80 | 0.80 | 0.00 |  |
| lexical | 25 | oh-big-state | synonym | 2 | 25 | 0.50 | 0.50 | 0.50 |  |
| lexical | 25 | ga-tech-focused | synonym | 2 | 25 | 0.50 | 0.50 | 0.50 |  |
| lexical | 25 | midwest-coding | synonym | 6 | 25 | 1.00 | 0.67 | 1.00 |  |
| lexical | 25 | film-theater | synonym | 5 | 25 | 1.00 | 1.00 | 0.20 |  |
| lexical | 25 | bay-area-cs | world_knowledge | 2 | 25 | 0.50 | 0.00 | 0.50 |  |
| lexical | 25 | hbcu | world_knowledge | 2 | 25 | 0.50 | 0.00 | 0.00 |  |
| lexical | 25 | ivy-league | world_knowledge | 8 | 25 | 0.12 | 0.00 | 0.00 |  |
| lexical | 25 | tx-cheap-public | structured_only | 4 | 25 | 0.75 | 0.75 | 0.00 |  |
| lexical | 25 | small-classes | structured_only | 17 | 25 | 0.29 | 0.40 | 0.30 |  |
| lexical | 25 | south-selective-private | structured_only | 6 | 25 | 1.00 | 0.67 | 0.67 |  |
| lexical | 25 | filter-or-engineering | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical | 25 | filter-wa-computer-science | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical | 25 | filter-ut-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical | 25 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical | 25 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical | 25 | filter-private-affordable-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical | 50 | tx-engineering | state_name | 5 | 50 | 1.00 | 0.80 | 0.40 |  |
| lexical | 50 | ca-computer-science | state_name | 3 | 50 | 1.00 | 0.67 | 0.00 |  |
| lexical | 50 | fl-business | state_name | 7 | 50 | 1.00 | 0.86 | 0.14 |  |
| lexical | 50 | ma-private | state_name | 6 | 50 | 1.00 | 0.17 | 0.17 |  |
| lexical | 50 | tx-health | state_name | 2 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical | 50 | ga-psychology | state_name | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical | 50 | midwest-public | exact_vocabulary | 9 | 50 | 1.00 | 0.56 | 0.33 |  |
| lexical | 50 | south-suburban | exact_vocabulary | 8 | 50 | 1.00 | 0.62 | 0.25 |  |
| lexical | 50 | small-private | exact_vocabulary | 6 | 50 | 1.00 | 1.00 | 0.33 |  |
| lexical | 50 | town-setting | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical | 50 | northeast-mathematics | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 0.20 |  |
| lexical | 50 | agriculture | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 1.00 |  |
| lexical | 50 | legal-studies | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical | 50 | education | exact_vocabulary | 2 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical | 50 | criminal-justice | exact_vocabulary | 1 | 50 | 1.00 | 1.00 | 0.00 |  |
| lexical | 50 | performing-arts | exact_vocabulary | 5 | 50 | 1.00 | 1.00 | 0.20 |  |
| lexical | 50 | division-three | synonym | 9 | 50 | 0.67 | 0.11 | 0.11 |  |
| lexical | 50 | division-two | synonym | 2 | 50 | 1.00 | 0.00 | 0.50 |  |
| lexical | 50 | fl-nursing | synonym | 5 | 50 | 1.00 | 0.80 | 0.00 |  |
| lexical | 50 | oh-big-state | synonym | 2 | 50 | 0.50 | 0.50 | 0.00 |  |
| lexical | 50 | ga-tech-focused | synonym | 2 | 50 | 0.50 | 0.50 | 0.50 |  |
| lexical | 50 | midwest-coding | synonym | 6 | 50 | 1.00 | 0.67 | 0.50 |  |
| lexical | 50 | film-theater | synonym | 5 | 50 | 1.00 | 1.00 | 0.20 |  |
| lexical | 50 | bay-area-cs | world_knowledge | 2 | 50 | 0.50 | 0.00 | 0.00 |  |
| lexical | 50 | hbcu | world_knowledge | 2 | 50 | 1.00 | 0.00 | 0.00 |  |
| lexical | 50 | ivy-league | world_knowledge | 8 | 50 | 0.25 | 0.00 | 0.00 |  |
| lexical | 50 | tx-cheap-public | structured_only | 4 | 50 | 0.75 | 0.75 | 0.00 |  |
| lexical | 50 | small-classes | structured_only | 17 | 50 | 0.59 | 0.40 | 0.20 |  |
| lexical | 50 | south-selective-private | structured_only | 6 | 50 | 1.00 | 0.67 | 0.33 |  |
| lexical | 50 | filter-or-engineering | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical | 50 | filter-wa-computer-science | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical | 50 | filter-ut-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
| lexical | 50 | filter-dc-social-sciences | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical | 50 | filter-ms-health | filtered | 1 | 1 | 1.00 | 1.00 | 1.00 |  |
| lexical | 50 | filter-private-affordable-business | filtered | 1 | 0 | 0.00 | 0.00 | 0.00 | yes |
