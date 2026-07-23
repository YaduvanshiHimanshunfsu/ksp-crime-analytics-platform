# Train the place-based risk model

## Goal

Train a time-aware model for weekly reported-incident volume by H3-like grid cell and crime category. The model is decision support, not a directive to target a person or community.

## Inputs

- `data/synthetic/cases.csv` or an authorised extract with the same approved columns.
- At least 12 months of incident history is preferred. With less history, retain the seasonal baseline only.

## Procedure

1. Generate daily cell/category counts from reported FIR and citizen-source records only.
2. Create lag-7, lag-14, lag-28, rolling-28, weekday, month, and festival features.
3. Split chronologically: training period, validation period, then final held-out period. Never randomly split dates.
4. Compare the baseline with a count model using MAE and top-area hit rate.
5. Save the model only if it improves on the baseline and has acceptable calibration.
6. Export feature metadata, evaluation metrics, and model version beside the model file.

## Colab limit

Use CPU runtime. The model is small tabular data; a T4 GPU is unnecessary. It should train in minutes, comfortably below three hours.

