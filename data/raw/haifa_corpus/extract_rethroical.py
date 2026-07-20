from pathlib import Path
import pandas as pd
import sys

def extract_balanced_datasets(merged_csv: Path, master_poetry_csv: Path, out_tashbeeh: Path, out_negative: Path, seed: int = 42):
    # 1. تحميل وترتيب ملف الأشعار الرئيسي (Master)
    try:
        master_df = pd.read_csv(master_poetry_csv, encoding="utf-8-sig")
    except UnicodeDecodeError:
        master_df = pd.read_csv(master_poetry_csv, encoding="utf-8")

    # ترقيم الأبيات آلياً ودمج الصدر والعجز
    master_df['البيت_رقم'] = master_df.groupby('Poem Title').cumcount() + 1
    master_df['البيت_الكامل'] = master_df['Sadr'].fillna('') + " " + master_df['Ajuz'].fillna('')

    # 2. تحميل ملف البيانات المدمجة (Analyzed Data)
    try:
        df = pd.read_csv(merged_csv, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(merged_csv, encoding="utf-8")

    df['البيت'] = pd.to_numeric(df['البيت'], errors='coerce')
    col_balagha = "العنصر البلاغي المستعمل"

    # 3. فصل البيانات إلى تشبيه وغير تشبيه
    mask_tashbeeh = df[col_balagha].fillna("").astype(str).str.contains("مجاز", na=False)
    
    df_tashbeeh_raw = df.loc[mask_tashbeeh].copy()
    df_negative_raw = df.loc[~mask_tashbeeh].copy()

    if df_tashbeeh_raw.empty:
        print("تنبيه: لم يتم العثور على أي 'تشبيه' في الملف.")
        return

    # 4. دالة مساعدة لربط النصوص وترتيب الأعمدة
    def attach_full_verses(target_df):
        merged = pd.merge(
            target_df,
            master_df[['Poem Title', 'البيت_رقم', 'البيت_الكامل']],
            left_on=['القصيدة', 'البيت'],
            right_on=['Poem Title', 'البيت_رقم'],
            how='left'
        )
        # إعادة ترتيب الأعمدة (وضع البيت_الكامل بعد التعبير البلاغي)
        cols = list(merged.columns)
        if 'البيت_الكامل' in cols:
            target_idx = cols.index('التعبير البلاغي') + 1 if 'التعبير البلاغي' in cols else 0
            cols.insert(target_idx, cols.pop(cols.index('البيت_الكامل')))
        
        # تنظيف أعمدة الربط الزائدة
        final_cols = [c for c in cols if c not in ['Poem Title', 'البيت_رقم']]
        return merged[final_cols]

    # 5. معالجة ملف التشبيه
    final_tashbeeh = attach_full_verses(df_tashbeeh_raw)

    # 6. معالجة ملف العينة العشوائية (Negative Sample)
    # نأخذ عينة بنفس حجم ملف التشبيه
    n_samples = len(final_tashbeeh)
    if len(df_negative_raw) >= n_samples:
        df_negative_sampled = df_negative_raw.sample(n=n_samples, random_state=seed)
    else:
        df_negative_sampled = df_negative_raw.copy()
        print(f"تنبيه: عدد الأبيات غير التشبيهية أقل من المطلوبة. تم تصدير {len(df_negative_sampled)} بيت.")

    final_negative = attach_full_verses(df_negative_sampled)

    # 7. حفظ الملفات
    out_tashbeeh.parent.mkdir(parents=True, exist_ok=True)
    
    final_tashbeeh.to_csv(out_tashbeeh, index=False, encoding="utf-8-sig")
    final_negative.to_csv(out_negative, index=False, encoding="utf-8-sig")

    print("-" * 30)
    print(f"✅ تم الحفظ بنجاح:")
    print(f"1. ملف التشبيه: {out_tashbeeh} ({len(final_tashbeeh)} سطر)")
    print(f"2. ملف العينة العشوائية: {out_negative} ({len(final_negative)} سطر)")

def main():
    # إعدادات المسارات
    input_merged = Path("merged_poets_data.csv")
    input_master = Path("Analyzed_Poetry_Master.csv")
    
    output_tashbeeh = Path("majaz_dataset.csv")
    output_negative = Path("non_majaz_random_sample.csv")

    if not input_merged.exists() or not input_master.exists():
        print("❌ خطأ: لم يتم العثور على الملفات الأصلية. تأكد من وجودها في نفس المجلد.")
        sys.exit(1)

    extract_balanced_datasets(input_merged, input_master, output_tashbeeh, output_negative)

if __name__ == "__main__":
    main()