"""
Comento 폴더 안의 food_trends_rising_YYYYMMDD.csv 파일을 전부 찾아서
하나로 병합하고, id / collected_date(YYYYMMDD) / keyword / category / trend_score
컬럼 구조로 정리합니다.

날짜를 하나하나 적지 않고 glob으로 패턴에 맞는 파일을 전부 자동으로 찾기 때문에,
나중에 파일이 더 늘어나도 이 스크립트를 그대로 다시 실행하면 됩니다.

실행 전 준비:
  pip install pandas
"""

import re
import glob
import pandas as pd

FILE_PATTERN = 'food_trends_rising_*.csv'
OUTPUT_CSV = 'food_trends_merged.csv'


def main():
    files = sorted(glob.glob(FILE_PATTERN))

    if not files:
        print(f"'{FILE_PATTERN}' 패턴에 맞는 파일을 찾지 못했습니다. "
              f"이 스크립트를 CSV 파일들과 같은 폴더에서 실행하고 있는지 확인해주세요.")
        return

    print(f"찾은 파일 {len(files)}개:")
    for f in files:
        print(f"  - {f}")

    dfs = []
    for f in files:
        # 파일명에서 YYYYMMDD 날짜만 뽑아냅니다 (예: food_trends_rising_20260819.csv -> 20260819)
        match = re.search(r'(\d{8})', f)
        if not match:
            print(f"  경고: '{f}'에서 날짜를 못 찾아 건너뜁니다.")
            continue

        date_str = match.group(1)
        d = pd.read_csv(f)
        d['collected_date'] = date_str
        dfs.append(d)

    merged = pd.concat(dfs, ignore_index=True)

    # 컬럼명 정리 (query -> keyword, seed -> category, value -> trend_score)
    merged = merged.rename(columns={'query': 'keyword', 'seed': 'category', 'value': 'trend_score'})

    # id 컬럼을 맨 앞에 추가
    merged.insert(0, 'id', range(1, len(merged) + 1))

    # 컬럼 순서 정리
    merged = merged[['id', 'collected_date', 'keyword', 'category', 'trend_score']]

    print(f"\n총 {len(merged)}행, 날짜 {merged['collected_date'].nunique()}일치 병합 완료")
    print("날짜 목록:", sorted(merged['collected_date'].unique()))

    merged.to_csv(OUTPUT_CSV, index=False)
    print(f"\n저장 완료: {OUTPUT_CSV}")


if __name__ == '__main__':
    main()
