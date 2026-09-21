# VerseNet: A Visual Neo4j-Based Bible Knowledge Network

**Students:** Martin Liu
**Supervisor:** Eric Araújo
**Term:** Spring 2026 to Fall 2026
**Status:** In progress

## Abstract

Theologians have spent millennia trying to understand the Bible, its historical figures, and the relations between its books. That task has accelerated with recent advances in computer science and mathematics. The field of complex systems in particular has changed how we model the world mathematically, bringing in graphs as a way of organizing reality into theoretical, and now computational, models. In a graph, nodes and edges are the main actors in the way reality presents itself. For this project the nodes are the 31,102 verses of a Protestant Bible, and new relationships derived from them are built to enrich the study of Scripture.

Moving from a linear or two-dimensional cross-reference between verses to a complex network requires tools that fit the new model. For that reason we use Neo4j to store the verses and, from there, create new edges based on factors such as sentiment, style, the main actor of a verse, and the presence of similar phrasal structures. The work involves (1) setting up a Neo4j dataset based on the viz.Bible project (https://viz.bible/), (2) becoming skilled in Neo4j, able to perform queries, insertions, and deletions, (3) creating a web interface that runs basic queries against Neo4j and presents the results in a friendly way to the user, (4) providing an AI agent to build more advanced queries, and (5) presenting the student's own reflection on the outcomes and on the new features added to the database.

The tool could be used by theologians and lay readers alike to take their investigation of the Bible further.
