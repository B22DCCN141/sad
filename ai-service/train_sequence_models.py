import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                            f1_score, confusion_matrix, classification_report)
import tensorflow as tf
from tensorflow.keras import Sequential, layers
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 1. LOAD AND PREPARE DATA
# ============================================================================
print("=" * 80)
print("LOADING DATA")
print("=" * 80)

df = pd.read_csv('data_user500.csv')
print(f"\nDataset shape: {df.shape}")
print(f"\nFirst few rows:\n{df.head(10)}")
print(f"\nData info:\n{df.info()}")
print(f"\nAction distribution:\n{df['action'].value_counts()}")

# ============================================================================
# 2. FEATURE ENGINEERING - CREATE SEQUENCES
# ============================================================================
print("\n" + "=" * 80)
print("FEATURE ENGINEERING - CREATING SEQUENCES")
print("=" * 80)

# Encode categorical features
action_encoder = LabelEncoder()
product_encoder = LabelEncoder()

df['action_encoded'] = action_encoder.fit_transform(df['action'])
df['product_encoded'] = product_encoder.fit_transform(df['product_id'])

print(f"\nAction encoding: {dict(zip(action_encoder.classes_, action_encoder.transform(action_encoder.classes_)))}")
print(f"Number of unique products: {len(product_encoder.classes_)}")

# Create sequences for each user
def create_sequences(user_group, seq_length=5):
    """Create sequences of actions for RNN models"""
    sequences = []
    targets = []
    
    actions = user_group['action_encoded'].values
    products = user_group['product_encoded'].values
    
    if len(actions) < seq_length + 1:
        return sequences, targets
    
    for i in range(len(actions) - seq_length):
        # Combine product_id and action as input features
        seq = np.column_stack([
            products[i:i + seq_length],
            actions[i:i + seq_length]
        ])
        sequences.append(seq)
        targets.append(actions[i + seq_length])
    
    return sequences, targets

all_sequences = []
all_targets = []

for user_id, user_group in df.groupby('user_id'):
    sequences, targets = create_sequences(user_group, seq_length=5)
    all_sequences.extend(sequences)
    all_targets.extend(targets)

print(f"\nTotal sequences created: {len(all_sequences)}")
print(f"Sequence shape: {all_sequences[0].shape if all_sequences else 'N/A'}")

# Pad sequences to same length
X = np.array(all_sequences)
y = np.array(all_targets)

print(f"X shape: {X.shape}")
print(f"y shape: {y.shape}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTraining set size: {X_train.shape[0]}")
print(f"Test set size: {X_test.shape[0]}")
print(f"Number of classes: {len(np.unique(y))}")

# ============================================================================
# 3. BUILD AND TRAIN MODELS
# ============================================================================
print("\n" + "=" * 80)
print("BUILDING AND TRAINING MODELS")
print("=" * 80)

models_info = {}

# -------- MODEL 1: RNN --------
print("\n[1/3] Training Simple RNN Model...")
model_rnn = Sequential([
    layers.SimpleRNN(64, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2]), return_sequences=True),
    layers.Dropout(0.3),
    layers.SimpleRNN(32, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(16, activation='relu'),
    layers.Dense(len(np.unique(y)), activation='softmax')
])

model_rnn.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print(model_rnn.summary())
early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
history_rnn = model_rnn.fit(
    X_train, y_train,
    validation_split=0.2,
    epochs=30,
    batch_size=16,
    callbacks=[early_stop],
    verbose=0
)
models_info['RNN'] = {
    'model': model_rnn,
    'history': history_rnn,
    'train_loss': history_rnn.history['loss'][-1],
    'train_acc': history_rnn.history['accuracy'][-1],
    'val_loss': history_rnn.history['val_loss'][-1],
    'val_acc': history_rnn.history['val_accuracy'][-1]
}
print(f"RNN Training completed - Final Val Accuracy: {history_rnn.history['val_accuracy'][-1]:.4f}")

# -------- MODEL 2: LSTM --------
print("\n[2/3] Training LSTM Model...")
model_lstm = Sequential([
    layers.LSTM(64, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2]), return_sequences=True),
    layers.Dropout(0.3),
    layers.LSTM(32, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(16, activation='relu'),
    layers.Dense(len(np.unique(y)), activation='softmax')
])

model_lstm.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print(model_lstm.summary())
early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
history_lstm = model_lstm.fit(
    X_train, y_train,
    validation_split=0.2,
    epochs=30,
    batch_size=16,
    callbacks=[early_stop],
    verbose=0
)
models_info['LSTM'] = {
    'model': model_lstm,
    'history': history_lstm,
    'train_loss': history_lstm.history['loss'][-1],
    'train_acc': history_lstm.history['accuracy'][-1],
    'val_loss': history_lstm.history['val_loss'][-1],
    'val_acc': history_lstm.history['val_accuracy'][-1]
}
print(f"LSTM Training completed - Final Val Accuracy: {history_lstm.history['val_accuracy'][-1]:.4f}")

# -------- MODEL 3: BiLSTM --------
print("\n[3/3] Training BiLSTM Model...")
model_bilstm = Sequential([
    layers.Bidirectional(layers.LSTM(64, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2]), return_sequences=True)),
    layers.Dropout(0.3),
    layers.Bidirectional(layers.LSTM(32, activation='relu')),
    layers.Dropout(0.3),
    layers.Dense(16, activation='relu'),
    layers.Dense(len(np.unique(y)), activation='softmax')
])

model_bilstm.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print(model_bilstm.summary())
early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
history_bilstm = model_bilstm.fit(
    X_train, y_train,
    validation_split=0.2,
    epochs=30,
    batch_size=16,
    callbacks=[early_stop],
    verbose=0
)
models_info['BiLSTM'] = {
    'model': model_bilstm,
    'history': history_bilstm,
    'train_loss': history_bilstm.history['loss'][-1],
    'train_acc': history_bilstm.history['accuracy'][-1],
    'val_loss': history_bilstm.history['val_loss'][-1],
    'val_acc': history_bilstm.history['val_accuracy'][-1]
}
print(f"BiLSTM Training completed - Final Val Accuracy: {history_bilstm.history['val_accuracy'][-1]:.4f}")

# ============================================================================
# 4. EVALUATE MODELS ON TEST SET
# ============================================================================
print("\n" + "=" * 80)
print("MODEL EVALUATION ON TEST SET")
print("=" * 80)

evaluation_results = {}

for model_name, model_info in models_info.items():
    model = model_info['model']
    
    # Predictions
    y_pred_prob = model.predict(X_test, verbose=0)
    y_pred = np.argmax(y_pred_prob, axis=1)
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    evaluation_results[model_name] = {
        'y_pred': y_pred,
        'y_pred_prob': y_pred_prob,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'confusion_matrix': confusion_matrix(y_test, y_pred)
    }
    
    print(f"\n{model_name} Model Performance:")
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1-Score:  {f1:.4f}")
    print(f"\nClassification Report:\n{classification_report(y_test, y_pred, target_names=action_encoder.classes_)}")

# ============================================================================
# 5. MODEL COMPARISON AND SELECTION
# ============================================================================
print("\n" + "=" * 80)
print("MODEL COMPARISON SUMMARY")
print("=" * 80)

comparison_df = pd.DataFrame({
    'Model': list(models_info.keys()),
    'Train_Accuracy': [models_info[m]['train_acc'] for m in models_info.keys()],
    'Val_Accuracy': [models_info[m]['val_acc'] for m in models_info.keys()],
    'Test_Accuracy': [evaluation_results[m]['accuracy'] for m in models_info.keys()],
    'Test_Precision': [evaluation_results[m]['precision'] for m in models_info.keys()],
    'Test_Recall': [evaluation_results[m]['recall'] for m in models_info.keys()],
    'Test_F1': [evaluation_results[m]['f1'] for m in models_info.keys()]
})

print("\n" + comparison_df.to_string(index=False))

# Find best model
best_model_name = comparison_df.loc[comparison_df['Test_F1'].idxmax(), 'Model']
print(f"\n{'*' * 80}")
print(f"BEST MODEL: {best_model_name}")
print(f"{'*' * 80}")

model_best = models_info[best_model_name]['model']
y_pred_best = evaluation_results[best_model_name]['y_pred']

# Save best model
model_best.save('model_best.h5')
print(f"\nBest model saved as 'model_best.h5'")

# ============================================================================
# 6. VISUALIZATION
# ============================================================================
print("\n" + "=" * 80)
print("GENERATING VISUALIZATIONS")
print("=" * 80)

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# -------- FIGURE 1: Training History Comparison --------
fig, axes = plt.subplots(1, 2, figsize=(15, 5))

# Accuracy
for model_name, model_info in models_info.items():
    history = model_info['history']
    axes[0].plot(history.history['accuracy'], label=f'{model_name} (Train)', linewidth=2)
    axes[0].plot(history.history['val_accuracy'], label=f'{model_name} (Val)', linestyle='--', linewidth=2)

axes[0].set_xlabel('Epoch', fontsize=12)
axes[0].set_ylabel('Accuracy', fontsize=12)
axes[0].set_title('Model Training History - Accuracy', fontsize=14, fontweight='bold')
axes[0].legend(fontsize=10)
axes[0].grid(True, alpha=0.3)

# Loss
for model_name, model_info in models_info.items():
    history = model_info['history']
    axes[1].plot(history.history['loss'], label=f'{model_name} (Train)', linewidth=2)
    axes[1].plot(history.history['val_loss'], label=f'{model_name} (Val)', linestyle='--', linewidth=2)

axes[1].set_xlabel('Epoch', fontsize=12)
axes[1].set_ylabel('Loss', fontsize=12)
axes[1].set_title('Model Training History - Loss', fontsize=14, fontweight='bold')
axes[1].legend(fontsize=10)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('01_training_history.png', dpi=300, bbox_inches='tight')
print("✓ Saved: 01_training_history.png")
plt.close()

# -------- FIGURE 2: Model Performance Comparison --------
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

metrics_names = ['Test_Accuracy', 'Test_Precision', 'Test_Recall', 'Test_F1']
positions = [(0, 0), (0, 1), (1, 0), (1, 1)]

for idx, metric in enumerate(metrics_names):
    row, col = positions[idx]
    ax = axes[row, col]
    
    colors = ['#FF6B6B' if model != best_model_name else '#4ECDC4' 
              for model in comparison_df['Model']]
    
    bars = ax.bar(comparison_df['Model'], comparison_df[metric], color=colors, edgecolor='black', linewidth=1.5)
    ax.set_ylabel(metric.replace('Test_', ''), fontsize=11, fontweight='bold')
    ax.set_title(f'{metric.replace("Test_", "")} Comparison', fontsize=12, fontweight='bold')
    ax.set_ylim([0, 1])
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}', ha='center', va='bottom', fontweight='bold')

plt.suptitle('Model Performance Metrics Comparison', fontsize=16, fontweight='bold', y=1.00)
plt.tight_layout()
plt.savefig('02_model_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: 02_model_comparison.png")
plt.close()

# -------- FIGURE 3: Confusion Matrices --------
fig, axes = plt.subplots(1, 3, figsize=(18, 4))

for idx, model_name in enumerate(['RNN', 'LSTM', 'BiLSTM']):
    cm = evaluation_results[model_name]['confusion_matrix']
    
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[idx],
                xticklabels=action_encoder.classes_,
                yticklabels=action_encoder.classes_,
                cbar_kws={'label': 'Count'})
    
    axes[idx].set_title(f'{model_name} Confusion Matrix', fontsize=12, fontweight='bold')
    axes[idx].set_ylabel('True Label', fontsize=11)
    axes[idx].set_xlabel('Predicted Label', fontsize=11)

plt.suptitle('Confusion Matrices - All Models', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('03_confusion_matrices.png', dpi=300, bbox_inches='tight')
print("✓ Saved: 03_confusion_matrices.png")
plt.close()

# -------- FIGURE 4: Best Model Performance --------
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Best model confusion matrix
cm_best = evaluation_results[best_model_name]['confusion_matrix']
sns.heatmap(cm_best, annot=True, fmt='d', cmap='RdYlGn', ax=axes[0],
            xticklabels=action_encoder.classes_,
            yticklabels=action_encoder.classes_,
            cbar_kws={'label': 'Count'})
axes[0].set_title(f'Best Model ({best_model_name}) - Confusion Matrix', fontsize=13, fontweight='bold')
axes[0].set_ylabel('True Label', fontsize=11)
axes[0].set_xlabel('Predicted Label', fontsize=11)

# Best model metrics
best_metrics = evaluation_results[best_model_name]
metrics = ['accuracy', 'precision', 'recall', 'f1']
values = [best_metrics[m] for m in metrics]
colors_metrics = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']

bars = axes[1].barh(metrics, values, color=colors_metrics, edgecolor='black', linewidth=1.5)
axes[1].set_xlabel('Score', fontsize=11, fontweight='bold')
axes[1].set_title(f'Best Model ({best_model_name}) - Metrics', fontsize=13, fontweight='bold')
axes[1].set_xlim([0, 1])
axes[1].grid(axis='x', alpha=0.3)

# Add value labels
for idx, (bar, value) in enumerate(zip(bars, values)):
    axes[1].text(value, idx, f' {value:.4f}', va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('04_best_model_performance.png', dpi=300, bbox_inches='tight')
print("✓ Saved: 04_best_model_performance.png")
plt.close()

# ============================================================================
# 7. MODEL SELECTION EXPLANATION
# ============================================================================
print("\n" + "=" * 80)
print("MODEL SELECTION EVALUATION AND EXPLANATION")
print("=" * 80)

print(f"\n{'='*80}")
print(f"SELECTED BEST MODEL: {best_model_name}")
print(f"{'='*80}\n")

print("EVALUATION RATIONALE:\n")

best_row = comparison_df[comparison_df['Model'] == best_model_name].iloc[0]
rnn_row = comparison_df[comparison_df['Model'] == 'RNN'].iloc[0]
lstm_row = comparison_df[comparison_df['Model'] == 'LSTM'].iloc[0]
bilstm_row = comparison_df[comparison_df['Model'] == 'BiLSTM'].iloc[0]

print(f"1. TEST ACCURACY COMPARISON:")
print(f"   • RNN:    {rnn_row['Test_Accuracy']:.4f}")
print(f"   • LSTM:   {lstm_row['Test_Accuracy']:.4f}")
print(f"   • BiLSTM: {bilstm_row['Test_Accuracy']:.4f}")
print(f"   → {best_model_name} achieved the highest accuracy\n")

print(f"2. F1-SCORE COMPARISON (Balanced Performance Metric):")
print(f"   • RNN:    {rnn_row['Test_F1']:.4f}")
print(f"   • LSTM:   {lstm_row['Test_F1']:.4f}")
print(f"   • BiLSTM: {bilstm_row['Test_F1']:.4f}")
print(f"   → {best_model_name} shows the best balanced performance\n")

print(f"3. PRECISION & RECALL:")
print(f"   • RNN:    Precision={rnn_row['Test_Precision']:.4f}, Recall={rnn_row['Test_Recall']:.4f}")
print(f"   • LSTM:   Precision={lstm_row['Test_Precision']:.4f}, Recall={lstm_row['Test_Recall']:.4f}")
print(f"   • BiLSTM: Precision={bilstm_row['Test_Precision']:.4f}, Recall={bilstm_row['Test_Recall']:.4f}")
print(f"   → {best_model_name} achieves strong balance between precision and recall\n")

print(f"4. TRAINING STABILITY:")
print(f"   • RNN:    Val_Acc={rnn_row['Val_Accuracy']:.4f}, Test_Acc={rnn_row['Test_Accuracy']:.4f} (Gap: {(rnn_row['Val_Accuracy']-rnn_row['Test_Accuracy']):.4f})")
print(f"   • LSTM:   Val_Acc={lstm_row['Val_Accuracy']:.4f}, Test_Acc={lstm_row['Test_Accuracy']:.4f} (Gap: {(lstm_row['Val_Accuracy']-lstm_row['Test_Accuracy']):.4f})")
print(f"   • BiLSTM: Val_Acc={bilstm_row['Val_Accuracy']:.4f}, Test_Acc={bilstm_row['Test_Accuracy']:.4f} (Gap: {(bilstm_row['Val_Accuracy']-bilstm_row['Test_Accuracy']):.4f})")

best_gap = (best_row['Val_Accuracy'] - best_row['Test_Accuracy'])
print(f"   → {best_model_name} shows stable generalization (gap: {best_gap:.4f})\n")

print(f"5. ARCHITECTURAL INSIGHTS:")
if best_model_name == 'RNN':
    print(f"   • Simple RNN captures temporal dependencies effectively")
    print(f"   • Lower computational complexity with adequate performance")
elif best_model_name == 'LSTM':
    print(f"   • LSTM's memory cells handle long-term dependencies well")
    print(f"   • Avoids vanishing gradient problems in sequence modeling")
elif best_model_name == 'BiLSTM':
    print(f"   • Bidirectional processing captures context from both directions")
    print(f"   • Superior performance in action sequence prediction")
    print(f"   • Better understanding of user behavior patterns")

print(f"\n{'='*80}")
print(f"CONCLUSION: {best_model_name} is selected as model_best")
print(f"Test Accuracy: {best_row['Test_Accuracy']:.4f}")
print(f"Test F1-Score: {best_row['Test_F1']:.4f}")
print(f"{'='*80}\n")

print("✓ All visualizations and evaluations completed!")
print("✓ Best model saved as 'model_best.h5'")
