# KGDS
**Knowledge-Grounded Discussion Summarization (KGDS)** is a novel task designed to produce a **supplementary background summary** and a **clear opinion summary** by integrating shared background knowledge with the discussion content. The goal is to create reader-centered summaries by bridging knowledge gaps with necessary background-supporting information and presenting clear participant opinions with clarified implicit references.

![](./figures/task_formulation.png)

## Benchmark Dataset
The official dataset is available at `benchmark/KGDS.json`. The file contains a list of JSON objects, where each object has the following fields:
+ `SBK`: **Shared Background Knowledge** (news domain).
+ `KGD`: **Knowledge-Grounded Discussion**.
+ `BSP`: **Background-Supporting Paragraphs**.
+ `CAO`: **Clear Atomic Opinions**.
+ `BSPAF`: Background-Supporting Paragraph Atomic Facts. Those annotated with `"type": 1` are **Key Background-Supporting Atomic Facts**.
+ `BNPAF`: Background-Nonsupporting Paragraph Atomic Facts. Those labeled with `"type": 0` are **Background-Nonsupporting Atomic Facts**.

## Evaluation Framework
Our evaluation framework provides a comprehensive and hierarchical assessment of the generated summaries. It independently evaluates the sub-summaries (background and opinion) using fine-grained, interpretable metrics and then aggregates these scores to determine the overall quality at the paradigm level.

![](./figures/evaluation_framework.png)
