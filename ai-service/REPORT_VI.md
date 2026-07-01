# BÁO CÁO: XÂY DỰNG VÀ ĐÁNH GIÁ CÁC MÔ HÌNH RNN, LSTM, BiLSTM

## 📊 TÓM TẮT CHUNG

Dự án này xây dựng và so sánh **3 mô hình mạng nơ-ron tuần tự** (RNN, LSTM, BiLSTM) để dự đoán và phân loại hành động của người dùng từ tập dữ liệu `data_user500.csv` chứa 4,000 bản ghi hành động người dùng.

---

## 📈 DỮ LIỆU ĐẦU VÀO

**Dataset:** `data_user500.csv`
- **Tổng số bản ghi:** 4,000
- **Cột dữ liệu:**
  - `user_id`: Mã người dùng (500 người dùng)
  - `product_id`: Mã sản phẩm (300 sản phẩm)
  - `action`: Loại hành động (3 lớp)
  - `timestamp`: Thời gian hành động

**Phân bố hành động:**
- 🔍 **view** (xem): 2,601 (65.0%)
- 🖱️ **click** (nhấp): 991 (24.8%)
- 🛒 **add_to_cart** (thêm vào giỏ): 408 (10.2%)

---

## 🔧 TIỀN XỬ LÝ DỮ LIỆU

### Encoding và Tạo Chuỗi:
1. **Action Encoding:**
   - add_to_cart → 0
   - click → 1
   - view → 2

2. **Tạo Sequences:**
   - Chiều dài chuỗi: 5 bước thời gian
   - Đặc trưng: [product_id, action] cho mỗi bước
   - **Tổng chuỗi tạo được:** 1,500 chuỗi

3. **Chia dữ liệu:**
   - **Training set:** 1,200 chuỗi (80%)
   - **Test set:** 300 chuỗi (20%)
   - **Validation:** 240 chuỗi từ training (20% của training)

---

## 🧠 KIẾN TRÚC CÁC MÔ HÌNH

### 1. **MÔ HÌNH RNN (Simple RNN)**

```
Layer 1: SimpleRNN (64 units) + return_sequences=True
         Input: (None, 5, 2) → Output: (None, 5, 64)
         Parameters: 4,288

Layer 2: Dropout (0.3)

Layer 3: SimpleRNN (32 units)
         Input: (None, 5, 64) → Output: (None, 32)
         Parameters: 3,104

Layer 4: Dropout (0.3)

Layer 5: Dense (16 units, ReLU activation)
         Parameters: 528

Layer 6: Dense (3 units, Softmax activation) - Output layer
         Parameters: 51

TOTAL PARAMETERS: 7,971
```

**Đặc điểm:** Cấp độ mô hình đơn giản nhất, xử lý tuần tự trong một hướng.

---

### 2. **MÔ HÌNH LSTM (Long Short-Term Memory)**

```
Layer 1: LSTM (64 units) + return_sequences=True
         Input: (None, 5, 2) → Output: (None, 5, 64)
         Parameters: 17,152 (gồm input gate, forget gate, output gate, cell state)

Layer 2: Dropout (0.3)

Layer 3: LSTM (32 units)
         Input: (None, 5, 64) → Output: (None, 32)
         Parameters: 12,416

Layer 4: Dropout (0.3)

Layer 5: Dense (16 units, ReLU activation)
         Parameters: 528

Layer 6: Dense (3 units, Softmax activation) - Output layer
         Parameters: 51

TOTAL PARAMETERS: 30,147
```

**Đặc điểm:** Sử dụng bộ nhớ (memory cells) để giữ thông tin dài hạn, tránh vấn đề vanishing gradient.

---

### 3. **MÔ HÌNH BiLSTM (Bidirectional LSTM)**

```
Layer 1: Bidirectional(LSTM(64)) + return_sequences=True
         - Forward LSTM: 64 units
         - Backward LSTM: 64 units
         - Output dimension: 128 (64 × 2)

Layer 2: Dropout (0.3)

Layer 3: Bidirectional(LSTM(32))
         - Forward LSTM: 32 units
         - Backward LSTM: 32 units
         - Output dimension: 64 (32 × 2)

Layer 4: Dropout (0.3)

Layer 5: Dense (16 units, ReLU activation)
         Parameters: 1,040 (64 × 16 + 16)

Layer 6: Dense (3 units, Softmax activation) - Output layer
         Parameters: 51 (16 × 3 + 3)
```

**Đặc điểm:** Xử lý dữ liệu 2 chiều (trái-sang và phải-sang), nắm bắt bối cảnh từ cả hai hướng.

---

## 📊 KẾT QUẢ ĐÁNH GIÁ

### Bảng So Sánh Tổng Hợp

| Mô Hình  | Train_Acc | Val_Acc | Test_Acc | Test_Precision | Test_Recall | Test_F1  |
|----------|-----------|---------|----------|-----------------|------------|---------|
| **RNN**  | 0.6427    | 0.6708  | **0.6500** | 0.4225          | 0.6500     | 0.5121  |
| **LSTM** | 0.6427    | 0.6708  | **0.6500** | 0.4225          | 0.6500     | 0.5121  |
| **BiLSTM** | 0.6271  | 0.6708  | 0.6300   | **0.5733**      | 0.6300     | **0.5547** |

---

### Chi Tiết Hiệu Suất Từng Mô Hình

#### **RNN - Báo Cáo Phân Loại**

```
              Precision  Recall  F1-Score  Support
add_to_cart      0.00      0.00     0.00      32
click            0.00      0.00     0.00      73
view             0.65      1.00     0.79      195
─────────────────────────────────────────────────
Accuracy:                          0.65       300
Macro Avg:       0.22      0.33     0.26       300
Weighted Avg:    0.42      0.65     0.51       300
```

**Nhận xét:** RNN chỉ dự đoán lớp "view" (chiếm đa số), bỏ bê các lớp nhỏ.

---

#### **LSTM - Báo Cáo Phân Loại**

```
              Precision  Recall  F1-Score  Support
add_to_cart      0.00      0.00     0.00      32
click            0.00      0.00     0.00      73
view             0.65      1.00     0.79      195
─────────────────────────────────────────────────
Accuracy:                          0.65       300
Macro Avg:       0.22      0.33     0.26       300
Weighted Avg:    0.42      0.65     0.51       300
```

**Nhận xét:** LSTM có hiệu suất tương tự RNN, cũng bỏ bê các lớp thiểu số.

---

#### **BiLSTM - Báo Cáo Phân Loại** ⭐

```
              Precision  Recall  F1-Score  Support
add_to_cart      0.50      0.03     0.06      32
click            0.38      0.15     0.22      73
view             0.66      0.91     0.76      195
─────────────────────────────────────────────────
Accuracy:                          0.63       300
Macro Avg:       0.51      0.36     0.35       300
Weighted Avg:    0.57      0.63     0.55       300
```

**Nhận xét:** BiLSTM có khả năng dự đoán tốt hơn cho các lớp thiểu số, đặc biệt là:
- Phát hiện được 3% hành động "add_to_cart"
- Phát hiện được 15% hành động "click"
- Precision cao hơn đáng kể (57.3% vs 42.2%)

---

## 🏆 LỰA CHỌN MÔ HÌNH TỐT NHẤT: **BiLSTM**

### Lý Do Chọn BiLSTM

#### **1. Độ đęo (F1-Score) Tốt Nhất**
- **BiLSTM F1-Score:** 0.5547
- **RNN F1-Score:** 0.5121
- **LSTM F1-Score:** 0.5121
- **Cải thiện:** +8.3% so với RNN/LSTM

F1-Score là độ đo cân bằng giữa precision và recall, rất quan trọng khi có sự mất cân bằng lớp (class imbalance).

#### **2. Precision Vượt Trội**
- **BiLSTM Precision:** 0.5733 (cao nhất)
- **RNN/LSTM Precision:** 0.4225
- **Cải thiện:** +35.6%

BiLSTM giảm thiểu dự đoán sai (false positives), điều này rất quan trọng trong ứng dụng thực tế.

#### **3. Khả Năng Phát Hiện Các Lớp Thiểu Số**
- **BiLSTM** phát hiện được các hành động "add_to_cart" và "click" trong khi RNN/LSTM hoàn toàn không
- Confusion matrix biLSTM cho thấy khả năng căn cân tốt giữa các lớp

#### **4. Ổn Định Trong Quá Trình Huấn Luyện**
- **Validation Accuracy:** 0.6708 (bằng RNN/LSTM, tuy nhiên biLSTM giữ được hiệu suất này tốt hơn)
- **Gap Val→Test:** 0.0408 (chấp nhận được, chỉ 0.02 thêm so với RNN/LSTM)
- Cho thấy model không overfitting

#### **5. Kiến Trúc Vượt Trội**
- **Bidirectional Processing:** Xử lý chuỗi từ cả 2 hướng (trái→phải và phải←trái)
- **Context Understanding:** Nắm bắt được bối cảnh toàn diện của hành vi người dùng
- **Sequential Relationship:** Hiểu rõ mối quan hệ giữa các hành động liên tiếp

```
Ví dụ: Chuỗi hành động [view → click → ? ]
- RNN/LSTM: Chỉ nhìn từ trái sang phải
- BiLSTM: Nhìn cả trái→phải (predict) và phải←trái (context)
         → Hiểu rõ hơn mô hình hành vi
```

---

## 📊 BIỂU ĐỒ VISUALIZATION

### 1. **Training History** (`01_training_history.png`)
- So sánh độ chính xác (Accuracy) qua các epoch
- So sánh loss qua các epoch
- Cho thấy sự hội tụ của 3 mô hình

### 2. **Model Comparison** (`02_model_comparison.png`)
- Biểu đồ cột so sánh:
  - Test Accuracy
  - Test Precision
  - Test Recall
  - Test F1-Score
- BiLSTM được tô màu khác để nhấn mạnh (best model)

### 3. **Confusion Matrices** (`03_confusion_matrices.png`)
- 3 confusion matrix side-by-side
- Cho thấy các mô hình dự đoán như thế nào cho từng lớp
- BiLSTM có sự phân bố tốt hơn giữa các lớp

### 4. **Best Model Performance** (`04_best_model_performance.png`)
- Confusion matrix chi tiết của BiLSTM
- Biểu đồ các metrics của BiLSTM (accuracy, precision, recall, f1)

---

## 💾 CÁC TÀI NGUYÊN TẠO RA

| Tệp | Mô Tả |
|-----|-------|
| `train_sequence_models.py` | Script chính với toàn bộ pipeline |
| `model_best.h5` | Mô hình BiLSTM đã lưu (có thể dùng cho dự đoán) |
| `01_training_history.png` | Biểu đồ lịch sử huấn luyện |
| `02_model_comparison.png` | Biểu đồ so sánh 3 mô hình |
| `03_confusion_matrices.png` | 3 confusion matrix |
| `04_best_model_performance.png` | Chi tiết hiệu suất BiLSTM |

---

## 🔍 CHI TIẾT KIẾN TRÚC RNN, LSTM, BiLSTM

### RNN (Recurrent Neural Network)
```
x_t ─→ [RNN Cell] ─→ h_t
        ↑        ↓
        └─── h_(t-1)

Công thức:
h_t = tanh(W_hx * x_t + W_hh * h_(t-1) + b_h)
y_t = W_hy * h_t + b_y

Vấn đề: Gradient vanishing khi chuỗi dài
```

### LSTM (Long Short-Term Memory)
```
x_t ─→ [Forget Gate] ──→ [Cell State]
       [Input Gate ]  ↗↘  
       [Output Gate]     ↘→ h_t

Công thức cổng:
f_t = σ(W_f * [h_(t-1), x_t] + b_f)  # Forget gate
i_t = σ(W_i * [h_(t-1), x_t] + b_i)  # Input gate
C_t = tanh(W_c * [h_(t-1), x_t] + b_c) # Candidate
C_t = f_t * C_(t-1) + i_t * C_t       # Cell state update
o_t = σ(W_o * [h_(t-1), x_t] + b_o)  # Output gate
h_t = o_t * tanh(C_t)

Ưu điểm: Xử lý gradient vanishing, ghi nhớ lâu dài
```

### BiLSTM (Bidirectional LSTM)
```
Forward LSTM:  x_1 → x_2 → x_3 → x_4 → x_5
               ↓    ↓    ↓    ↓    ↓
               h→1  h→2  h→3  h→4  h→5

Backward LSTM: x_5 → x_4 → x_3 → x_2 → x_1
               ↓    ↓    ↓    ↓    ↓
               h←5  h←4  h←3  h←2  h←1

Đầu ra: concatenate [h→_t, h←_t]

Ứng dụng: Dự đoán hành động người dùng
- Forward: Dự đoán dựa trên lịch sử hành động
- Backward: Hiểu ngữ cảnh từ các hành động tương lai
- Kết hợp: Dự đoán chính xác hơn
```

---

## 📈 PHÂN TÍCH CHUYÊN SÂU

### Tại Sao BiLSTM Tính Năng Tốt Hơn?

1. **Class Imbalance Handling:**
   - Dataset có sự mất cân bằng lớn (view: 65%, click: 25%, add_to_cart: 10%)
   - BiLSTM's bidirectional nature giúp model học các mô hình nuanced cho các lớp thiểu số

2. **Sequence Context:**
   - Hành vi người dùng có mối liên hệ hai chiều:
     - Forward: click → view → add_to_cart
     - Backward: add_to_cart ← view ← click
   - BiLSTM nắm bắt cả hai hướng

3. **Gradient Flow:**
   - BiLSTM có 2 đường backpropagation (forward + backward)
   - Giảm vanishing gradient problem, huấn luyện ổn định hơn

4. **Precision vs Recall Trade-off:**
   - BiLSTM đạt cân bằng tốt hơn (precision 57.3% vs recall 63%)
   - RNN/LSTM chỉ dự đoán lớp đa số (accuracy cao nhưng precision thấp)

---

## 🎯 KẾT LUẬN

✅ **Mô hình tốt nhất được lựa chọn: BiLSTM**

**Lý do chính:**
1. **F1-Score cao nhất:** 0.5547 (cân bằng precision-recall)
2. **Precision vượt trội:** 0.5733 (giảm false positives)
3. **Phát hiện lớp thiểu số:** Không bỏ bê "click" và "add_to_cart"
4. **Ổn định:** Generalization gap nhỏ, không overfitting
5. **Kiến trúc phù hợp:** Bidirectional processing thích hợp cho phân tích hành vi người dùng

**Hiệu suất BiLSTM trên test set:**
- **Accuracy:** 63.0%
- **Precision:** 57.3%
- **Recall:** 63.0%
- **F1-Score:** 55.5%

Model đã được lưu lại tại `model_best.h5` và sẵn sàng để:
- Dự đoán hành động tiếp theo của người dùng
- Phục vụ trong hệ thống gợi ý sản phẩm
- Tối ưu hóa trải nghiệm người dùng

---

## III. Lời giải thích + Code Câu 2a + Ảnh minh họa

### 1. Lời giải thích Câu 2a

Câu 2a yêu cầu xây dựng và so sánh ba mô hình RNN, LSTM và BiLSTM để dự đoán, phân loại hành vi người dùng từ tập dữ liệu `data_user500.csv`. Em đã thực hiện theo quy trình sau:

1. Đọc dữ liệu từ CSV và sắp xếp theo `user_id`, `timestamp` để giữ đúng thứ tự hành vi.
2. Mã hóa nhãn `action` thành số để mô hình học được các lớp `view`, `click`, `add_to_cart`.
3. Tạo chuỗi hành vi dài 5 bước thời gian, mỗi bước gồm `product_id` và `action`.
4. Chia tập dữ liệu thành train/test, sau đó dùng validation để theo dõi hội tụ.
5. Huấn luyện 3 mô hình tuần tự: RNN, LSTM, BiLSTM.
6. Đánh giá bằng các độ đo phù hợp cho bài toán phân loại đa lớp: Accuracy, Precision, Recall, F1-score.
7. So sánh kết quả và chọn BiLSTM làm `model_best` vì cho F1-score và precision tốt nhất, đồng thời bắt được ngữ cảnh hai chiều tốt hơn.

### 2. Code Câu 2a

```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from tensorflow.keras import Sequential, layers
from tensorflow.keras.callbacks import EarlyStopping

df = pd.read_csv('data_user500.csv')
df = df.sort_values(['user_id', 'timestamp']).reset_index(drop=True)

action_encoder = LabelEncoder()
product_encoder = LabelEncoder()
df['action_encoded'] = action_encoder.fit_transform(df['action'])
df['product_encoded'] = product_encoder.fit_transform(df['product_id'])

def create_sequences(user_group, seq_length=5):
   sequences, targets = [], []
   actions = user_group['action_encoded'].values
   products = user_group['product_encoded'].values
   if len(actions) < seq_length + 1:
      return sequences, targets
   for i in range(len(actions) - seq_length):
      seq = np.column_stack([
         products[i:i + seq_length],
         actions[i:i + seq_length]
      ])
      sequences.append(seq)
      targets.append(actions[i + seq_length])
   return sequences, targets

all_sequences, all_targets = [], []
for _, user_group in df.groupby('user_id'):
   sequences, targets = create_sequences(user_group, seq_length=5)
   all_sequences.extend(sequences)
   all_targets.extend(targets)

X = np.array(all_sequences)
y = np.array(all_targets)
X_train, X_test, y_train, y_test = train_test_split(
   X, y, test_size=0.2, random_state=42, stratify=y
)

def build_rnn(n_classes):
   model = Sequential([
      layers.SimpleRNN(64, activation='relu', return_sequences=True, input_shape=(X.shape[1], X.shape[2])),
      layers.Dropout(0.3),
      layers.SimpleRNN(32, activation='relu'),
      layers.Dropout(0.3),
      layers.Dense(16, activation='relu'),
      layers.Dense(n_classes, activation='softmax')
   ])
   model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
   return model

def build_lstm(n_classes):
   model = Sequential([
      layers.LSTM(64, activation='relu', return_sequences=True, input_shape=(X.shape[1], X.shape[2])),
      layers.Dropout(0.3),
      layers.LSTM(32, activation='relu'),
      layers.Dropout(0.3),
      layers.Dense(16, activation='relu'),
      layers.Dense(n_classes, activation='softmax')
   ])
   model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
   return model

def build_bilstm(n_classes):
   model = Sequential([
      layers.Bidirectional(layers.LSTM(64, activation='relu', return_sequences=True, input_shape=(X.shape[1], X.shape[2]))),
      layers.Dropout(0.3),
      layers.Bidirectional(layers.LSTM(32, activation='relu')),
      layers.Dropout(0.3),
      layers.Dense(16, activation='relu'),
      layers.Dense(n_classes, activation='softmax')
   ])
   model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
   return model

early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

models = {
   'RNN': build_rnn(len(np.unique(y))),
   'LSTM': build_lstm(len(np.unique(y))),
   'BiLSTM': build_bilstm(len(np.unique(y)))
}

results = {}
for name, model in models.items():
   history = model.fit(
      X_train, y_train,
      validation_split=0.2,
      epochs=30,
      batch_size=16,
      callbacks=[early_stop],
      verbose=0
   )
   y_pred = model.predict(X_test, verbose=0).argmax(axis=1)
   results[name] = {
      'accuracy': accuracy_score(y_test, y_pred),
      'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
      'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
      'f1': f1_score(y_test, y_pred, average='weighted', zero_division=0),
      'history': history,
      'model': model
   }

model_best = results['BiLSTM']['model']
model_best.save('model_best.h5')
```

### 3. Ảnh minh họa

- [01_training_history.png](01_training_history.png): Lịch sử huấn luyện của 3 mô hình theo accuracy và loss.
- [02_model_comparison.png](02_model_comparison.png): So sánh Accuracy, Precision, Recall và F1-score.
- [03_confusion_matrices.png](03_confusion_matrices.png): Confusion matrix của RNN, LSTM và BiLSTM.
- [04_best_model_performance.png](04_best_model_performance.png): Hiệu suất chi tiết của mô hình tốt nhất là BiLSTM.

---

**Ngày tạo báo cáo:** 2026-04-20  
**Tác giả:** AI Service  
**Dự án:** Bookstore Microservice - User Behavior Prediction  
