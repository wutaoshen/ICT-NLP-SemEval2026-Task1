## ICT-NLP System for SemEval-2026 Task 1: Humor Generation Joke in Chinese
This repository contains the implementation of team ICT-NLP for SemEval-2026 Task 1: Humor Generation, Subtask A-Joke in Chinese.

### Repository Structure

- Root 
  - README.md: This file
  - raw_data
    - mwahaha_test: Original Dataset File
  - data
    - eval.json: Formatted Dataset
  - script
    - step1.json: data augmentation
    - step2.json: keyword extraction and association
    - step3.json: candidate joke generation
    - step4.json: multi-model internal voting
    - step5.json: external voting

### Requirements
- openai
- opencc
- dashscope
