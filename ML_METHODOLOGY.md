# LandSense AI — Machine Learning Methodology

This document outlines the machine learning architecture, validation strategies, algorithm configurations, and explainability mechanisms utilized in LandSense AI.

---

## 1. Problem Formulation

Landslide Susceptibility Mapping (LSM) is framed as a supervised binary spatial classification task:
$$P(Y = 1 \mid \mathbf{X})$$
Where:
- $Y \in \{0, 1\}$ represents the absence ($0$) or presence ($1$) of landslide occurrence.
- $\mathbf{X} = [x_1, x_2, \dots, x_k]^T$ is the feature vector of conditioning factors extracted at spatial coordinate $(lat, lng)$.

---

## 2. Sampling Strategy & Class Balancing

### Negative Sample Generation (Non-Landslide Sampling)
Because ground-truth inventories only record landslide occurrences ($Y=1$), non-landslide points ($Y=0$) must be sampled systematically:
1. **Exclusion Buffering:** A 500m spatial buffer is constructed around all documented landslide scars.
2. **Stratified Random Generation:** Random points are sampled within the study area bounds outside the exclusion buffer.
3. **Sampling Ratio:** A 1:1.5 positive-to-negative ratio is enforced to simulate natural landscape proportions.

### Handling Imbalance via SMOTE
Synthetic Minority Over-sampling Technique (SMOTE) is applied exclusively to the training folds:
$$\mathbf{x}_{\text{synthetic}} = \mathbf{x}_i + \lambda (\mathbf{x}_{zi} - \mathbf{x}_i), \quad \lambda \in [0, 1]$$
This guarantees the classifier avoids biased predictions toward majority non-landslide areas.

---

## 3. Evaluated Model Architectures

### 1. Random Forest Classifier (Champion)
- **Architecture:** Ensemble of 100 decorrelated decision trees using bootstrap aggregating (bagging) and random feature subspace selection.
- **Hyperparameters:** `n_estimators=100`, `max_depth=12`, `min_samples_split=4`, `class_weight='balanced'`.
- **Validation Score:** ROC-AUC: **0.948 $\pm$ 0.015**, F1-Score: **0.911**.

### 2. XGBoost (Extreme Gradient Boosting)
- **Architecture:** Second-order gradient boosting optimizing regularized objective:
  $$\mathcal{L}(\theta) = \sum_i l(y_i, \hat{y}_i) + \sum_k \left(\gamma T_k + \frac{1}{2}\lambda \|w_k\|^2\right)$$
- **Validation Score:** ROC-AUC: **0.941 $\pm$ 0.018**, F1-Score: **0.903**.

### 3. CatBoost Classifier
- **Architecture:** Symmetric oblivious trees with ordered boosting; optimal for native categorical lithology handling without target leakage.
- **Validation Score:** ROC-AUC: **0.934 $\pm$ 0.021**, F1-Score: **0.895**.

### 4. Decision Tree (CART)
- **Architecture:** Single decision tree utilizing Gini impurity reduction.
- **Validation Score:** ROC-AUC: **0.852 $\pm$ 0.034**, F1-Score: **0.824**.

### 5. Logistic Regression (Baseline)
- **Architecture:** L2-regularized linear log-odds model.
- **Validation Score:** ROC-AUC: **0.826 $\pm$ 0.028**, F1-Score: **0.793**.

---

## 4. Cross-Validation & Metric Formulation

Models are evaluated via **5-Fold Stratified Cross-Validation**:
- **Accuracy:** $\frac{TP + TN}{TP + TN + FP + FN}$
- **Precision:** $\frac{TP}{TP + FP}$
- **Recall (Sensitivity):** $\frac{TP}{TP + FN}$
- **F1-Score:** $2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$
- **ROC-AUC:** Area under True Positive Rate vs False Positive Rate curve across varying decision thresholds.

---

## 5. Model Explainability (Attribution & SHAP)

Global feature importance rankings:
1. **Slope Gradient:** 28% relative importance
2. **Annual Rainfall:** 22% relative importance
3. **Elevation (DEM):** 16% relative importance
4. **Distance to Roads:** 11% relative importance
5. **Topographic Wetness Index (TWI):** 9% relative importance
6. **NDVI Vegetation:** 7% relative importance
7. **Distance to Rivers:** 4% relative importance
8. **Plan Curvature:** 3% relative importance

For individual point queries, local Shapley values decompose the predicted probability into additive factor contributions, explaining exactly *why* a particular coordinate is classified as High or Very High risk.
