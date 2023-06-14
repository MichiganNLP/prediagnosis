# Prediagnosis-depression

This is the impelmenation for the paper [Improving Mental Health Classifier Generalization with Pre-diagnosis Data](https://ojs.aaai.org/index.php/ICWSM/article/view/22169).

## Abstract
Recent work has shown that classifiers for depression detection often fail to generalize to new datasets. Most NLP models for this task are built on datasets that use textual reports of a depression diagnosis (e.g., statements on social media) to identify diagnosed users; this approach allows for collection of large-scale datasets, but leads to poor generalization to out-of-domain data. Notably, models tend to capture features that typify direct discussion of mental health rather than more subtle indications of depression symptoms. In this paper, we explore the hypothesis that building classifiers using exclusively social media posts from before a user’s diagnosis will lead to less reliance on shortcuts and better generalization. We test our classifiers on a dataset that is based on an external survey rather than textual self-reports, and find that using pre-diagnosis data for training yields improved performance with many types of classifiers.

## Requirements
### Environment
Install conda environment by running
```
conda env create -f environment.yml
conda activate prediagnosis
```

Please follow the [instruction here](https://github.com/FraBle/python-sutime) to install Java dependencies for SUTime.

## Usage
### Extract diagnosis timestamp
To extract diagnosis timestamp for a self-report, you can run
```
python scripts/extract_diagnosis_time.py:
    --input_file:   The file that stores the self-reports to be processed.
    --output_file:  The output file. 
```
Here is an example run using provided data sample:

```python scripts/extract_diagnosis_time.py --input_file data/example_data.json --output_file output/example_diagnosis_time.json```

Extracted diagnosis timestamp is stored in the field `diagnosis_time_value`, and its corresponding text expression is stored in `diagnosis_time_text`.

### Depression detection
Coming soon...

## Reference
If you find our work useful for your research, please consider citing our paper:
```
@article{Liu_Biester_Mihalcea_2023,
        title={Improving Mental Health Classifier Generalization with Pre-diagnosis Data},
        volume={17},
        url={https://ojs.aaai.org/index.php/ICWSM/article/view/22169},
        DOI={10.1609/icwsm.v17i1.22169},
        number={1},
        journal={Proceedings of the International AAAI Conference on Web and Social Media},
        author={Liu, Yujian and Biester, Laura and Mihalcea, Rada},
        year={2023},
        month={Jun.},
        pages={566-577}
}
```
