import pandas as pd
import re
from pathlib import Path
import typer

def clean_election_data(input_file):
    """
    乱れた選挙データCSVを整理する
    """
    # CSVを読み込み
    df = pd.read_csv(input_file, header=None)
    
    # すべてのセルを文字列に変換して結合
    all_text = ' '.join(df.astype(str).values.flatten())
    
    # 各項目を抽出
    result = {}
    
    # 投票日
    vote_date = re.search(r'投票日[,\s]*(\d{4}年\d{2}月\d{2}日)', all_text)
    result['投票日'] = vote_date.group(1) if vote_date else ''
    
    # 告示日
    announce_date = re.search(r'告示日[,\s]*(\d{4}年\d{2}月\d{2}日)', all_text)
    result['告示日'] = announce_date.group(1) if announce_date else ''
    
    # 投票率
    vote_rate = re.search(r'投票率[,\s]*([\d.]+%)', all_text)
    result['投票率'] = vote_rate.group(1) if vote_rate else ''
    
    # 前回投票率
    prev_rate = re.search(r'前回投票率[,\s]*([\d.]+%)', all_text)
    result['前回投票率'] = prev_rate.group(1) if prev_rate else ''
    
    # 定数/候補者数
    quota = re.search(r'定数/候補者数[,\s]*(\d+\s*/\s*\d+)', all_text)
    result['定数/候補者数'] = quota.group(1).replace(' ', '') if quota else ''
    
    # 有権者数（カンマ区切りの数値に対応）
    voters = re.search(r'有権者数[,\s]*["\']?([\d,]+)人', all_text)
    result['有権者数'] = voters.group(1) if voters else ''
    
    # 男性有権者数
    male = re.search(r'男性[,\s]*([\d,]+)人', all_text)
    result['男性'] = male.group(1) if male else ''
    
    # 女性有権者数
    female = re.search(r'女性[,\s]*([\d,]+)人', all_text)
    result['女性'] = female.group(1) if female else ''
    
    # 前回より
    diff = re.search(r'前回より[,\s]*([+-]?[\d,]+)人', all_text)
    result['前回より'] = diff.group(1) if diff else ''
    
    return pd.DataFrame([result])

def main(input_file: str, output_file: str = ""):
    """
    選挙データを整理する
    """
    input_path = Path(input_file)
    
    if not output_file:
        output_file = str(input_path.parent / f"{input_path.stem}_cleaned.csv")
    
    # データを整理
    cleaned_df = clean_election_data(input_path)
    
    # 保存
    cleaned_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"整理完了: {output_file}")
    print("\n整理後のデータ:")
    print(cleaned_df.to_string())

if __name__ == "__main__":
    typer.run(main)