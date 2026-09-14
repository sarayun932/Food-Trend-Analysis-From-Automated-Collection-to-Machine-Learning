"""
미국(US) 기준, 식품 카테고리 6개의 최근 5년간 주별 검색 관심도(interest_over_time) 수집

related_queries()(급상승 연관 검색어 발견용)와는 다른 함수입니다.
interest_over_time()은 특정 키워드를 정해두고, Google이 이미 가지고 있는
과거 데이터를 그 즉시 통째로 가져오는 함수라 별도 자동화(cron) 없이
한 번 실행으로 5년치가 바로 나옵니다.

5년치를 한 번에 요청하면, 0~100 점수의 기준(가장 높았던 주=100)이
5년 전체에서 통일되기 때문에, 계절성(예: 매년 4월에 반복되는 피크)이
실제로 매년 반복되는지 같은 기준으로 비교할 수 있습니다.

실행 전 준비:
  pip install pytrends pandas
"""

import time
import pandas as pd
from pytrends.request import TrendReq

# ---------- 설정값 ----------

CATEGORIES = ['snack', 'dessert', 'drink', 'beverage', 'fast food', 'organic food', 'food delivery']

GEO = 'US'                 # 미국으로 범위 한정
TIMEFRAME = 'today 5-y'    # 최근 5년 — Google Trends가 정식으로 지원하는 표현입니다
SLEEP_SECONDS = 15         # 요청 사이 대기 시간 (429 방지)

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 60

OUTPUT_CSV = 'food_categories_5yr_trend_US.csv'


def fetch_interest_for_keyword(pytrends, kw):
    """키워드 하나의 5년치 주별 관심도 시계열을 가져옵니다.
    429 에러가 나면 점점 더 오래 쉬면서 최대 MAX_RETRIES번 재시도합니다.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            pytrends.build_payload(kw_list=[kw], geo=GEO, timeframe=TIMEFRAME)
            df = pytrends.interest_over_time()

            if df is None or df.empty:
                return None

            # isPartial(마지막 주 데이터가 아직 확정 안 됐다는 표시) 컬럼은 분석에 불필요하므로 제거
            if 'isPartial' in df.columns:
                df = df.drop(columns=['isPartial'])

            df = df.reset_index()  # date를 컬럼으로 꺼냄
            df = df.rename(columns={kw: 'interest_score', 'date': 'week'})
            df['category'] = kw
            return df

        except Exception as e:
            is_rate_limit = '429' in str(e) or 'TooManyRequests' in type(e).__name__

            if is_rate_limit and attempt < MAX_RETRIES:
                wait_time = RETRY_BACKOFF_SECONDS * attempt
                print(f"  -> '{kw}' 429 에러 (시도 {attempt}/{MAX_RETRIES}). "
                      f"{wait_time}초 대기 후 재시도합니다.")
                time.sleep(wait_time)
                continue

            print(f"  -> '{kw}' 수집 중 오류 발생 (시도 {attempt}/{MAX_RETRIES}): {e}")
            return None

    return None


def main():
    pytrends = TrendReq(hl='en-US', tz=360)

    all_data = []
    for kw in CATEGORIES:
        print(f"수집 중: {kw} (US, 최근 5년)")
        df = fetch_interest_for_keyword(pytrends, kw)

        if df is not None and not df.empty:
            all_data.append(df)
            print(f"  -> {len(df)}주 분량 수집 완료")
        else:
            print(f"  -> '{kw}' 데이터 없음")

        time.sleep(SLEEP_SECONDS)

    if not all_data:
        print("수집된 데이터가 없습니다.")
        return

    result = pd.concat(all_data, ignore_index=True)
    result = result[['week', 'category', 'interest_score']]  # 컬럼 순서 정리
    result = result.sort_values(['category', 'week']).reset_index(drop=True)

    print(f"\n총 {len(result)}행 수집 완료 (카테고리 {result['category'].nunique()}개)")
    print(result.head(10))

    result.to_csv(OUTPUT_CSV, index=False)
    print(f"\nCSV 저장 완료: {OUTPUT_CSV}")


if __name__ == '__main__':
    main()