# KGDS
**Knowledge-Grounded Discussion Summarization (KGDS)** is a novel task designed to produce a **supplementary background summary** and a **clear opinion summary** by integrating shared background knowledge with the discussion content. The goal is to create reader-centered summaries by bridging knowledge gaps with necessary background-supporting information and presenting clear participant opinions with clarified implicit references.

![An illustration of the KGDS task, showing how shared knowledge and discussion content are used to generate a background summary and an opinion summary.](./figures/task_formulation.png)

## 📊 Benchmark Dataset
The official dataset is available at `benchmark/KGDS.json`. The file contains a list of JSON objects, where each object has the following fields:
* `SBK`: **S**hared **B**ackground **K**nowledge (news domain).
* `KGD`: **K**nowledge-**G**rounded **D**iscussion.
* `BSP`: **B**ackground-**S**upporting **P**aragraphs.
* `CAO`: **C**lear **A**tomic **O**pinions.
* `BSPAF`: **B**ackground-**S**upporting **P**aragraph **A**tomic **F**acts. Those annotated with `"type": 1` are **Key Background-Supporting Atomic Facts**.
* `BNPAF`: **B**ackground-**N**onsupporting **P**aragraph **A**tomic **F**acts. Those labeled with `"type": 0` are **Background-Nonsupporting Atomic Facts**.

## ⚙️ Evaluation Framework
Our evaluation framework provides a comprehensive and hierarchical assessment of the generated summaries. It independently evaluates the sub-summaries (background and opinion) using fine-grained, interpretable metrics and then aggregates these scores to determine the overall quality at the paradigm level.

![The hierarchical evaluation framework for KGDS.](./figures/evaluation_framework.png)

🚀 *Now, you can reproduce the results reported in our paper by following the steps below:*

**Step 1:** Download the `outputs.zip` file from either [**Baidu Netdisk**](https://pan.baidu.com/s/1uPcbjQcOQmnEKfpXFBFMXw?pwd=a8x9) (Password: `a8x9`) or [**Google Drive**](https://drive.google.com/file/d/1UcYQ6ZyNq1i1QDI7iSKsscuHR4AHiU4N/view?usp=share_link) and unzip it into the root directory of this project.
