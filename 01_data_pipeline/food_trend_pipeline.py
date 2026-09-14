"""
코멘토 1차 과제: 식품 트렌드 키워드 발견 파이프라인

흐름:
  1) 여러 시드 키워드(food, snack, dessert 등)로 Google Trends의
     rising(급상승) 연관 검색어를 수집
  2) 식품 트렌드와 무관한 단어가 포함된 검색어 필터링
  3) 결과를 CSV로 백업하고 SQLite DB에 저장

실행 전 준비:
  pip install pytrends pandas
"""

import time
import sqlite3
import pandas as pd
from pytrends.request import TrendReq

# ---------- 설정값 (필요에 따라 수정하세요) ----------

SEED_KEYWORDS = [
    'snack', 'dessert', 'drink', 'beverage',
    'fast food', 'organic food'
]
# 'food'는 범위가 너무 넓고, 'restaurant'은 지역 이벤트성 검색어 위주,
# 'cafe'는 429 에러로 데이터가 거의 안 잡혔고,
# 'healthy food'는 스팸성 사이트명이 많이 섞여서 이번엔 제외했습니다.

# 검색어에 아래 단어가 포함되면 식품 트렌드와 무관하다고 보고 제외합니다.
# 실행 결과를 보면서 필요한 단어를 자유롭게 추가/삭제하세요.
EXCLUDE_TERMS = [
    'pet', 'dog', 'cat', 'puppy', 'kitten', 'recall', 'hummingbird',
    # 구글 트렌드에 종종 섞여 들어오는 스팸/피싱성 사이트명
    'justalittlebite', 'whatutalkingboutwillis', 'traveltweaks', 'levvvel',
]

TIMEFRAME = 'today 3-m'   # 최근 3개월 기준
SLEEP_SECONDS = 15        # 요청 사이 대기 시간 (너무 짧으면 429 에러 발생)
import os
from datetime import datetime

# 스크립트 파일이 있는 폴더를 기준으로 삼아서, 어디서 실행하든 항상 같은 위치에 저장되게 합니다.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(SCRIPT_DIR, 'food_trends.db')

# CSV는 실행한 날짜를 파일명에 붙여서, 매번 덮어써지지 않고 날짜별로 쌓이게 합니다.
# (DB는 원래부터 누적 저장되니 그대로 두고, CSV만 이렇게 바꿉니다.)
today_str = datetime.now().strftime('%Y%m%d')
CSV_PATH = os.path.join(SCRIPT_DIR, f'food_trends_rising_{today_str}.csv')

MIN_VALUE = 300           # 이 값보다 낮은 급상승 지표는 노이즈로 보고 제외 (기존 60 -> 300으로 상향)
TOP_N_PER_SEED = 5        # 시드 키워드 하나당 최대 몇 개까지 남길지 (기존 8 -> 5로 축소, 신호 강한 것만 유지)

MAX_RETRIES = 3           # 429 에러 발생 시 최대 재시도 횟수
RETRY_BACKOFF_SECONDS = 60  # 재시도 전 대기 시간 (재시도할수록 이 값의 배수로 점점 길어짐)


def fetch_rising_for_keyword(pytrends, kw):
    """키워드 하나에 대한 rising 데이터를 가져옵니다.
    429(Too Many Requests) 에러가 나면 점점 더 오래 쉬면서 최대 MAX_RETRIES번 재시도합니다.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            pytrends.build_payload(kw_list=[kw], timeframe=TIMEFRAME)
            related = pytrends.related_queries()
            return related.get(kw, {}).get('rising')

        except Exception as e:
            is_rate_limit = '429' in str(e) or 'TooManyRequests' in type(e).__name__

            if is_rate_limit and attempt < MAX_RETRIES:
                wait_time = RETRY_BACKOFF_SECONDS * attempt  # 재시도할수록 대기시간 증가
                print(f"  -> '{kw}' 429 에러 (시도 {attempt}/{MAX_RETRIES}). "
                      f"{wait_time}초 대기 후 재시도합니다.")
                time.sleep(wait_time)
                continue

            # 429가 아니거나, 재시도 횟수를 다 썼으면 포기하고 에러를 알립니다.
            print(f"  -> '{kw}' 수집 중 오류 발생 (시도 {attempt}/{MAX_RETRIES}): {e}")
            return None

    return None


def collect_rising_queries(pytrends, seed_keywords):
    """시드 키워드별로 rising 연관 검색어를 수집해서 하나의 데이터프레임으로 합칩니다."""
    all_rising = []

    for kw in seed_keywords:
        print(f"수집 중: {kw}")
        df = fetch_rising_for_keyword(pytrends, kw)

        if df is not None and not df.empty:
            df = df.copy()
            df['seed'] = kw
            all_rising.append(df)
        else:
            print(f"  -> '{kw}'에 대한 rising 데이터 없음")

        time.sleep(SLEEP_SECONDS)  # 다음 요청 전 대기 (429 방지)

    if not all_rising:
        return pd.DataFrame(columns=['query', 'value', 'seed'])

    return pd.concat(all_rising, ignore_index=True)


def filter_irrelevant(df, exclude_terms):
    """검색어에 무관한 단어가 포함된 행을 제외합니다."""
    if df.empty:
        return df

    pattern = '|'.join(exclude_terms)
    mask = ~df['query'].str.contains(pattern, case=False, na=False)
    return df[mask].reset_index(drop=True)


def clean_and_rank(df, min_value, top_n_per_seed):
    """노이즈를 줄이고 보기 좋게 정리합니다.
    - value가 너무 낮은 행 제외
    - 시드 키워드별 상위 N개만 유지
    - value 기준 내림차순 정렬
    """
    if df.empty:
        return df

    df = df[df['value'] >= min_value].copy()
    df = df.sort_values('value', ascending=False)
    df = df.groupby('seed', group_keys=False).head(top_n_per_seed)
    df = df.sort_values(['seed', 'value'], ascending=[True, False]).reset_index(drop=True)
    return df


def save_to_sqlite(df, db_path):
    """결과를 SQLite DB의 rising_keywords 테이블에 저장합니다 (누적 저장)."""
    conn = sqlite3.connect(db_path)
    df = df.copy()
    df['collected_at'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    df.to_sql('rising_keywords', conn, if_exists='append', index=False)
    conn.close()
    print(f"SQLite DB에 {len(df)}건 저장 완료: {db_path}")


def main():
    pytrends = TrendReq(hl='en-US', tz=360)

    raw_df = collect_rising_queries(pytrends, SEED_KEYWORDS)
    print(f"\n수집된 원본 데이터: {len(raw_df)}건")

    filtered_df = filter_irrelevant(raw_df, EXCLUDE_TERMS)
    filtered_df = clean_and_rank(filtered_df, MIN_VALUE, TOP_N_PER_SEED)
    print(f"필터링 및 정리 후 데이터: {len(filtered_df)}건\n")
    print(filtered_df)

    if not filtered_df.empty:
        filtered_df.to_csv(CSV_PATH, index=False)
        print(f"\nCSV 백업 저장 완료: {CSV_PATH}")

        save_to_sqlite(filtered_df, DB_PATH)
    else:
        print("\n저장할 데이터가 없습니다. 시드 키워드나 EXCLUDE_TERMS를 확인해보세요.")


if __name__ == '__main__':
    main()
