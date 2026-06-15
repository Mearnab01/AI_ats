---
tags:
- sentence-transformers
- sentence-similarity
- feature-extraction
- generated_from_trainer
- dataset_size:6790
- loss:CosineSimilarityLoss
base_model: sentence-transformers/all-mpnet-base-v2
widget:
- source_sentence: Lead Data Scientist bringing over 8 years of industry experience
    along with a verified Masters degree. Expert competencies cover Python data ecosystems,
    custom Pandas metrics, NumPy, and advanced SQL matrices. Proven success track
    record in building high-dimension feature distributions to trace underlying statistical
    variations.
  sentences:
  - Seeking a skilled Algo-Trading Research Associate to join our growing team. Key
    responsibilities include modeling volatile financial vectors to predict historical
    risk exposure trends. Must be fully comfortable handling tools like Time-series
    variance tracking analytics, econometric models, and asset liquidity formulas
    in a fast-paced environment.
  - 'We are looking for a Infrastructure Platform Architect with a minimum of 4+ years
    of experience. The core technical stack requirements involve deep knowledge in:
    OCI Containers, Container Orchestration Engine, AWS Cloud Platform, Terraform,
    Python3. Must be highly capable of executing product deliverables in a fast paced
    workspace environment.'
  - Seeking a skilled Senior iOS/Android Mobile Developer to join our growing team.
    Key responsibilities include managing offline caching synchronization pipelines
    and publishing builds across app marketplaces. Must be fully comfortable handling
    tools like Swift UI frameworks, core mobile animations, Kotlin, and Gradle scripts
    in a fast-paced environment.
- source_sentence: 'Analytics Engineer with 5 years working across active teams. Demonstrated
    technical execution and history background includes: Theoretical knowledge of
    Python, Worked with Statistical Modeling in minor capacity, Deep Learning Architectures,
    AWS Cloud Platform. Seeking an engineering position to scale architectural patterns.'
  sentences:
  - 'We are looking for a Lead Product Analyst with a minimum of 8+ years of experience.
    The core technical stack requirements involve deep knowledge in: Python, Postgres,
    Statistical Modeling, Deep Learning Architectures, Cloud Infrastructure (AWS).
    Must be highly capable of executing product deliverables in a fast paced workspace
    environment.'
  - 'We are looking for a AI Infrastructure Architect with a minimum of 7+ years of
    experience. The core technical stack requirements involve deep knowledge in: Python3,
    ML, Artificial Intelligence, Container Orchestration Engine, Docker, Cloud Infrastructure
    (AWS). Must be highly capable of executing product deliverables in a fast paced
    workspace environment.'
  - Seeking a skilled Senior iOS/Android Mobile Developer to join our growing team.
    Key responsibilities include building highly responsive mobile applications featuring
    custom touch gestures. Must be fully comfortable handling tools like App Store
    deployment pathways, mobile push notification setups, and local SQLite syncs in
    a fast-paced environment.
- source_sentence: 'Terraform Engineer with 8 years working across active teams. Demonstrated
    technical execution and history background includes: Architected distributed pipelines
    via Docker Containers, Subject matter expert in Kubernetes, Cloud Infrastructure
    (AWS), Terraform, Architected distributed pipelines via Py3 Engine. Seeking an
    engineering position to scale architectural patterns.'
  sentences:
  - 'We are looking for a DevOps Cloud Engineer with a minimum of 6+ years of experience.
    The core technical stack requirements involve deep knowledge in: Docker Containers,
    K8s, Amazon Web Services, Terraform, Py3 Engine. Must be highly capable of executing
    product deliverables in a fast paced workspace environment.'
  - 'We are looking for a AI Infrastructure Architect with a minimum of 6+ years of
    experience. The core technical stack requirements involve deep knowledge in: Py3
    Engine, Predictive AI, AI, K8s, Docker Containers, Cloud Infrastructure (AWS).
    Must be highly capable of executing product deliverables in a fast paced workspace
    environment.'
  - Seeking a skilled Risk Asset Modeler to join our growing team. Key responsibilities
    include authoring algorithmic pricing code architectures driven by statistical
    signal anomalies. Must be fully comfortable handling tools like Time-series variance
    tracking analytics, econometric models, and asset liquidity formulas in a fast-paced
    environment.
- source_sentence: 'Statistical Researcher with 6 years working across active teams.
    Demonstrated technical execution and history background includes: Python, Relational
    DB Engine, Deep Learning Architectures, Basic understanding of AWS Cloud Platform.
    Seeking an engineering position to scale architectural patterns.'
  sentences:
  - Seeking a skilled Risk Asset Modeler to join our growing team. Key responsibilities
    include authoring algorithmic pricing code architectures driven by statistical
    signal anomalies. Must be fully comfortable handling tools like Advanced quantitative
    modeling systems, predictive alpha signals generation, and mathematical metrics
    in a fast-paced environment.
  - 'We are looking for a Senior Data Scientist with a minimum of 5+ years of experience.
    The core technical stack requirements involve deep knowledge in: Py3 Engine, Relational
    DB Engine, ML, Artificial Intelligence, Cloud Infrastructure (AWS). Must be highly
    capable of executing product deliverables in a fast paced workspace environment.'
  - 'We are looking for a Lead Product Analyst with a minimum of 4+ years of experience.
    The core technical stack requirements involve deep knowledge in: Python3, PgSQL,
    Machine Learning, Deep Learning Architectures, Cloud Infrastructure (AWS). Must
    be highly capable of executing product deliverables in a fast paced workspace
    environment.'
- source_sentence: 'Data Scientist with 1 years working across active teams. Demonstrated
    technical execution and history background includes: Py3 Engine, PostgreSQL, Theoretical
    knowledge of ML, GenAI. Seeking an engineering position to scale architectural
    patterns.'
  sentences:
  - Seeking a skilled Senior React Native Mobile Architect to join our growing team.
    Key responsibilities include building robust declarative modular application structures
    that map perfectly across target runtime layers. Must be fully comfortable handling
    tools like Mobile UI render optimization configurations, component lifecycles,
    and component scaling metrics in a fast-paced environment.
  - 'We are looking for a Quantitative Analytics Expert with a minimum of 4+ years
    of experience. The core technical stack requirements involve deep knowledge in:
    Python, PgSQL, Predictive AI, AI, Cloud Infrastructure (AWS). Must be highly capable
    of executing product deliverables in a fast paced workspace environment.'
  - 'We are looking for a Quantitative Analytics Expert with a minimum of 4+ years
    of experience. The core technical stack requirements involve deep knowledge in:
    Py3 Engine, Postgres, Machine Learning, GenAI, Amazon Web Services. Must be highly
    capable of executing product deliverables in a fast paced workspace environment.'
pipeline_tag: sentence-similarity
library_name: sentence-transformers
metrics:
- pearson_cosine
- spearman_cosine
model-index:
- name: SentenceTransformer based on sentence-transformers/all-mpnet-base-v2
  results:
  - task:
      type: semantic-similarity
      name: Semantic Similarity
    dataset:
      name: ats val
      type: ats-val
    metrics:
    - type: pearson_cosine
      value: 0.9459617705192965
      name: Pearson Cosine
    - type: spearman_cosine
      value: 0.925793716302145
      name: Spearman Cosine
---

# SentenceTransformer based on sentence-transformers/all-mpnet-base-v2

This is a [sentence-transformers](https://www.SBERT.net) model finetuned from [sentence-transformers/all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2). It maps sentences & paragraphs to a 768-dimensional dense vector space and can be used for retrieval.

## Model Details

### Model Description
- **Model Type:** Sentence Transformer
- **Base model:** [sentence-transformers/all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2) <!-- at revision e8c3b32edf5434bc2275fc9bab85f82640a19130 -->
- **Maximum Sequence Length:** 384 tokens
- **Output Dimensionality:** 768 dimensions
- **Similarity Function:** Cosine Similarity
- **Supported Modality:** Text
<!-- - **Training Dataset:** Unknown -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Documentation:** [Sentence Transformers Documentation](https://sbert.net)
- **Repository:** [Sentence Transformers on GitHub](https://github.com/huggingface/sentence-transformers)
- **Hugging Face:** [Sentence Transformers on Hugging Face](https://huggingface.co/models?library=sentence-transformers)

### Full Model Architecture

```
SentenceTransformer(
  (0): Transformer({'transformer_task': 'feature-extraction', 'modality_config': {'text': {'method': 'forward', 'method_output_name': 'last_hidden_state'}}, 'module_output_name': 'token_embeddings', 'architecture': 'MPNetModel'})
  (1): Pooling({'embedding_dimension': 768, 'pooling_mode': 'mean', 'include_prompt': True})
  (2): Normalize({})
)
```

## Usage

### Direct Usage (Sentence Transformers)

First install the Sentence Transformers library:

```bash
pip install -U sentence-transformers
```
Then you can load this model and run inference.
```python
from sentence_transformers import SentenceTransformer

# Download from the 🤗 Hub
model = SentenceTransformer("sentence_transformers_model_id")
# Run inference
sentences = [
    'Data Scientist with 1 years working across active teams. Demonstrated technical execution and history background includes: Py3 Engine, PostgreSQL, Theoretical knowledge of ML, GenAI. Seeking an engineering position to scale architectural patterns.',
    'We are looking for a Quantitative Analytics Expert with a minimum of 4+ years of experience. The core technical stack requirements involve deep knowledge in: Py3 Engine, Postgres, Machine Learning, GenAI, Amazon Web Services. Must be highly capable of executing product deliverables in a fast paced workspace environment.',
    'Seeking a skilled Senior React Native Mobile Architect to join our growing team. Key responsibilities include building robust declarative modular application structures that map perfectly across target runtime layers. Must be fully comfortable handling tools like Mobile UI render optimization configurations, component lifecycles, and component scaling metrics in a fast-paced environment.',
]
embeddings = model.encode(sentences)
print(embeddings.shape)
# [3, 768]

# Get the similarity scores for the embeddings
similarities = model.similarity(embeddings, embeddings)
print(similarities)
# tensor([[1.0000, 0.4431, 0.1849],
#         [0.4431, 1.0000, 0.4543],
#         [0.1849, 0.4543, 1.0000]])
```
<!--
### Direct Usage (Transformers)

<details><summary>Click to see the direct usage in Transformers</summary>

</details>
-->

<!--
### Downstream Usage (Sentence Transformers)

You can finetune this model on your own dataset.

<details><summary>Click to expand</summary>

</details>
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

## Evaluation

### Metrics

#### Semantic Similarity

* Dataset: `ats-val`
* Evaluated with [<code>EmbeddingSimilarityEvaluator</code>](https://sbert.net/docs/package_reference/sentence_transformer/evaluation.html#sentence_transformers.sentence_transformer.evaluation.EmbeddingSimilarityEvaluator)

| Metric              | Value      |
|:--------------------|:-----------|
| pearson_cosine      | 0.946      |
| **spearman_cosine** | **0.9258** |

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Dataset

#### Unnamed Dataset

* Size: 6,790 training samples
* Columns: <code>sentence_0</code>, <code>sentence_1</code>, and <code>label</code>
* Approximate statistics based on the first 100 samples:
  |          | sentence_0                                                                        | sentence_1                                                                         | label                                                            |
  |:---------|:----------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------|:-----------------------------------------------------------------|
  | type     | string                                                                            | string                                                                             | float                                                            |
  | modality | text                                                                              | text                                                                               |                                                                  |
  | details  | <ul><li>min: 36 tokens</li><li>mean: 57.5 tokens</li><li>max: 75 tokens</li></ul> | <ul><li>min: 58 tokens</li><li>mean: 67.02 tokens</li><li>max: 76 tokens</li></ul> | <ul><li>min: 0.02</li><li>mean: 0.66</li><li>max: 0.99</li></ul> |
* Samples:
  | sentence_0                                                                                                                                                                                                                                                                                                                                                               | sentence_1                                                                                                                                                                                                                                                                                                                                                                                      | label               |
  |:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------|
  | <code>Lead Data Scientist bringing over 8 years of industry experience along with a verified Masters degree. Expert competencies cover Python data ecosystems, custom Pandas metrics, NumPy, and advanced SQL matrices. Proven success track record in optimizing complex optimization layers to surface implicit correlation parameters across structures.</code>       | <code>Seeking a skilled Financial Quantitative Portfolio Analyst to join our growing team. Key responsibilities include modeling volatile financial vectors to predict historical risk exposure trends. Must be fully comfortable handling tools like Advanced quantitative modeling systems, predictive alpha signals generation, and mathematical metrics in a fast-paced environment.</code> | <code>0.8923</code> |
  | <code>Gastronomy Chef Specialist bringing over 9 years of industry experience along with a verified Bachelors degree. Expert competencies cover Kitchen management, menu engineering, and food safety protocols. Proven success track record in authoring seasonal menus while maintaining strict cost-of-goods compliance audits.</code>                                | <code>Seeking a skilled Statistical Modeling Specialist to join our growing team. Key responsibilities include extracting tabular feature data matrices to surface corporate risk exposures. Must be fully comfortable handling tools like dbt data warehousing modeling, Snowflake, Pandas analytics, and statistical hypothesis tracking in a fast-paced environment.</code>                  | <code>0.0229</code> |
  | <code>Modern JavaScript Systems Engineer bringing over 7 years of industry experience along with a verified Masters degree. Expert competencies cover TypeScript application scaling, component modular patterns, and performance tuning. Proven success track record in abstracting core layout state patterns into reusable, contextually driven modular hooks.</code> | <code>Seeking a skilled Cross-Platform Mobile Engineer to join our growing team. Key responsibilities include optimizing responsive visual components to enforce smooth multi-device execution footprints. Must be fully comfortable handling tools like React Native declarative code paradigms, mobile layout state setups, and native bridges in a fast-paced environment.</code>            | <code>0.9061</code> |
* Loss: [<code>CosineSimilarityLoss</code>](https://sbert.net/docs/package_reference/sentence_transformer/losses.html#cosinesimilarityloss) with these parameters:
  ```json
  {
      "loss_fct": "torch.nn.modules.loss.MSELoss",
      "cos_score_transformation": "torch.nn.modules.linear.Identity"
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `per_device_train_batch_size`: 16
- `num_train_epochs`: 4
- `per_device_eval_batch_size`: 16
- `multi_dataset_batch_sampler`: round_robin

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `per_device_train_batch_size`: 16
- `num_train_epochs`: 4
- `max_steps`: -1
- `learning_rate`: 5e-05
- `lr_scheduler_type`: linear
- `lr_scheduler_kwargs`: None
- `warmup_steps`: 0
- `optim`: adamw_torch_fused
- `optim_args`: None
- `weight_decay`: 0.0
- `adam_beta1`: 0.9
- `adam_beta2`: 0.999
- `adam_epsilon`: 1e-08
- `optim_target_modules`: None
- `gradient_accumulation_steps`: 1
- `average_tokens_across_devices`: True
- `max_grad_norm`: 1
- `label_smoothing_factor`: 0.0
- `bf16`: False
- `fp16`: False
- `bf16_full_eval`: False
- `fp16_full_eval`: False
- `tf32`: None
- `gradient_checkpointing`: False
- `gradient_checkpointing_kwargs`: None
- `torch_compile`: False
- `torch_compile_backend`: None
- `torch_compile_mode`: None
- `use_liger_kernel`: False
- `liger_kernel_config`: None
- `use_cache`: False
- `neftune_noise_alpha`: None
- `torch_empty_cache_steps`: None
- `auto_find_batch_size`: False
- `log_on_each_node`: True
- `logging_nan_inf_filter`: True
- `include_num_input_tokens_seen`: no
- `log_level`: passive
- `log_level_replica`: warning
- `disable_tqdm`: False
- `project`: huggingface
- `trackio_space_id`: None
- `trackio_bucket_id`: None
- `trackio_static_space_id`: None
- `per_device_eval_batch_size`: 16
- `prediction_loss_only`: True
- `eval_on_start`: False
- `eval_do_concat_batches`: True
- `eval_use_gather_object`: False
- `eval_accumulation_steps`: None
- `include_for_metrics`: []
- `batch_eval_metrics`: False
- `save_only_model`: False
- `save_on_each_node`: False
- `enable_jit_checkpoint`: False
- `push_to_hub`: False
- `hub_private_repo`: None
- `hub_model_id`: None
- `hub_strategy`: every_save
- `hub_always_push`: False
- `hub_revision`: None
- `load_best_model_at_end`: False
- `ignore_data_skip`: False
- `restore_callback_states_from_checkpoint`: False
- `full_determinism`: False
- `seed`: 42
- `data_seed`: None
- `use_cpu`: False
- `accelerator_config`: {'split_batches': False, 'dispatch_batches': None, 'even_batches': True, 'use_seedable_sampler': True, 'non_blocking': False, 'gradient_accumulation_kwargs': None}
- `parallelism_config`: None
- `dataloader_drop_last`: False
- `dataloader_num_workers`: 0
- `dataloader_pin_memory`: True
- `dataloader_persistent_workers`: False
- `dataloader_prefetch_factor`: None
- `remove_unused_columns`: True
- `label_names`: None
- `train_sampling_strategy`: random
- `length_column_name`: length
- `ddp_find_unused_parameters`: None
- `ddp_bucket_cap_mb`: None
- `ddp_broadcast_buffers`: False
- `ddp_static_graph`: None
- `ddp_backend`: None
- `ddp_timeout`: 1800
- `fsdp`: None
- `fsdp_config`: None
- `deepspeed`: None
- `debug`: []
- `skip_memory_metrics`: True
- `do_predict`: False
- `resume_from_checkpoint`: None
- `warmup_ratio`: None
- `local_rank`: -1
- `prompts`: None
- `batch_sampler`: batch_sampler
- `multi_dataset_batch_sampler`: round_robin
- `router_mapping`: {}
- `learning_rate_mapping`: {}

</details>

### Training Logs
| Epoch  | Step | Training Loss | ats-val_spearman_cosine |
|:------:|:----:|:-------------:|:-----------------------:|
| 1.0    | 425  | -             | 0.9177                  |
| 1.1765 | 500  | 0.0275        | -                       |
| 2.0    | 850  | -             | 0.9181                  |
| 2.3529 | 1000 | 0.0102        | -                       |
| 3.0    | 1275 | -             | 0.9233                  |
| 3.5294 | 1500 | 0.0085        | -                       |
| 4.0    | 1700 | -             | 0.9258                  |


### Training Time
- **Training**: 14.7 minutes

### Framework Versions
- Python: 3.12.13
- Sentence Transformers: 5.5.1
- Transformers: 5.10.2
- PyTorch: 2.11.0+cu128
- Accelerate: 1.13.0
- Datasets: 4.0.0
- Tokenizers: 0.22.2

## Citation

### BibTeX

#### Sentence Transformers
```bibtex
@inproceedings{reimers-2019-sentence-bert,
    title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
    author = "Reimers, Nils and Gurevych, Iryna",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
    month = "11",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/1908.10084",
}
```

<!--
## Glossary

*Clearly define terms in order to be accessible across audiences.*
-->

<!--
## Model Card Authors

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->