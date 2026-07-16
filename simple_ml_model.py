import sys
import time

# Cek apakah scikit-learn terinstal, jika belum kita beri tahu cara instalnya
try:
    from sklearn.tree import DecisionTreeClassifier
except ImportError:
    print("=========================================================")
    print("[!] Library 'scikit-learn' belum terinstal.")
    print("    Silakan instal terlebih dahulu dengan menjalankan:")
    print("    pip install scikit-learn")
    print("=========================================================")
    sys.exit(1)

def main():
    print("=========================================================")
    print("  MEMBUAT MODEL MACHINE LEARNING PERTAMA ANDA (AI)       ")
    print("=========================================================")
    print("Skenario: Memprediksi kondisi Programmer (Stres atau Happy)")
    print("berdasarkan Jam Tidur dan Gelas Kopi yang diminum.")
    print("---------------------------------------------------------")
    
    # 1. MENYIAPKAN DATA LATIH (Training Data)
    # Fitur [Jam Tidur, Gelas Kopi]
    X_train = [
        [8, 0],  # Tidur cukup, tidak minum kopi -> Happy
        [7, 1],  # Tidur cukup, kopi sedikit -> Happy
        [4, 4],  # Kurang tidur, kopi banyak -> Stres
        [3, 5],  # Kurang tidur, kopi sangat banyak -> Stres
        [9, 1],  # Tidur sangat cukup, kopi sedikit -> Happy
        [5, 3],  # Kurang tidur, kopi sedang -> Stres
        [6, 2],  # Tidur sedang, kopi sedang -> Happy
        [5, 4]   # Kurang tidur, kopi banyak -> Stres
    ]
    
    # Label: 1 = Happy, 0 = Stres
    y_train = [1, 1, 0, 0, 1, 0, 1, 0]
    
    print("1. Melatih Model (Decision Tree Classifier)...")
    time.sleep(1)
    
    # 2. MEMBUAT DAN MELATIH MODEL AI
    model = DecisionTreeClassifier()
    model.fit(X_train, y_train)
    
    print("[✓] Model AI berhasil dilatih secara lokal!")
    print("---------------------------------------------------------")
    
    # 3. INTERAKSI PREDIKSI
    print("Cobalah prediksi kondisi Anda saat ini:")
    try:
        sleep_hours = float(input("-> Berapa jam Anda tidur semalam? (contoh: 7): "))
        coffee_cups = float(input("-> Berapa gelas kopi yang Anda minum hari ini? (contoh: 2): "))
        
        # Lakukan prediksi
        prediction = model.predict([[sleep_hours, coffee_cups]])
        probability = model.predict_proba([[sleep_hours, coffee_cups]])
        
        print("\n---------------------------------------------------------")
        print("HASIL ANALISIS MODEL AI:")
        if prediction[0] == 1:
            print(f"😊 Model memprediksi Anda: HAPPY! (Keyakinan: {probability[0][1]*100:.1f}%)")
        else:
            print(f"🤯 Model memprediksi Anda: STRES/LELAH! (Keyakinan: {probability[0][0]*100:.1f}%)")
        print("=========================================================")
        
    except ValueError:
        print("[X] Input tidak valid. Harap masukkan angka.")

if __name__ == "__main__":
    main()
