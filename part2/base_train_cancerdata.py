# base_train.py
import joblib
from sklearn.datasets import load_breast_cancer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# breast_cancer 데이터 가져오기.
X, y = load_breast_cancer(return_X_y=True, as_frame=True)
X_train, X_valid, y_train, y_valid = train_test_split(X, y, train_size=0.8, random_state=1010)

# 2. model development and train
scaler = StandardScaler()
classifier = SVC() #Support Vector Classification 사용

scaled_X_train = scaler.fit_transform(X_train)
scaled_X_valid = scaler.transform(X_valid)

# fit
classifier.fit(scaled_X_train, y_train)

train_pred = classifier.predict(scaled_X_train)
valid_pred = classifier.predict(scaled_X_valid)

train_acc = accuracy_score(y_true=y_train, y_pred=train_pred)
valid_acc = accuracy_score(y_true=y_valid, y_pred=valid_pred)

print("Train Accuracy :", train_acc)
print("Valid Accuracy :", valid_acc)

# 3. save model
joblib.dump(scaler, "scaler.joblib")
joblib.dump(classifier, "classifier.joblib")