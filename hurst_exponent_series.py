import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from hurst import compute_Hc

# CSV 파일에서 데이터 읽어오기 (파일명과 경로를 지정하세요)
file_path = 'df_world.csv'  # 실제 CSV 파일 경로로 수정하세요.
df = pd.read_csv(file_path, parse_dates=['Date'], index_col='Date')

# 로그 리턴 계산
df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))

# Hurst exponent를 계산할 창(window)의 크기 설정 (252 거래일 = 1년)
window_size = 250

# Hurst exponent를 저장할 리스트
hurst_series = []

# 날짜를 저장할 리스트
dates_series = []

# 슬라이딩 윈도우를 통해 Hurst exponent 계산
for i in range(window_size, len(df)):
    window_data = df['Log_Return'].iloc[i-window_size:i].dropna()
    H, _, _ = compute_Hc(window_data, kind='change', simplified=True)
    hurst_series.append(H)
    dates_series.append(df.index[i])

# 결과를 시계열 데이터로 변환
hurst_df = pd.DataFrame(data={'Hurst': hurst_series}, index=dates_series)

# 서브플롯을 설정
fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# 색상 변경 시점 추적을 위한 변수
prev_color = 'blue'
color_changes = []
num_prev_colors = 7

# 색상 변경 점선 없는 서브플롯
for i in range(10, len(hurst_df)):
    recent_10_days = hurst_df['Hurst'].iloc[i-10:i]
    
    count_above_55 = (recent_10_days >= 0.55).sum()
    count_between_45_and_55 = ((recent_10_days < 0.55) & (recent_10_days >= 0.45)).sum()
    count_below_45 = (recent_10_days < 0.45).sum()
    
    if count_above_55 >= num_prev_colors:
        color = 'red'
    elif count_between_45_and_55 >= num_prev_colors:
        color = 'blue'
    elif count_below_45 >= num_prev_colors:
        color = 'green'
    else:
        color = prev_color
    
    axs[0].plot(hurst_df.index[i-1:i+1], hurst_df['Hurst'].iloc[i-1:i+1], color=color)
    
    # 색상 변경 시점 기록
    if color != prev_color:
        color_changes.append(hurst_df.index[i])
        prev_color = color

# 색상 변경 점선 있는 서브플롯
prev_color = 'blue'
for i in range(10, len(hurst_df)):
    recent_10_days = hurst_df['Hurst'].iloc[i-10:i]
    
    count_above_55 = (recent_10_days >= 0.55).sum()
    count_between_45_and_55 = ((recent_10_days < 0.55) & (recent_10_days >= 0.45)).sum()
    count_below_45 = (recent_10_days < 0.45).sum()
    
    if count_above_55 >= num_prev_colors:
        color = 'red'
    elif count_between_45_and_55 >= num_prev_colors:
        color = 'blue'
    elif count_below_45 >= num_prev_colors:
        color = 'green'
    else:
        color = prev_color
    
    axs[1].plot(hurst_df.index[i-1:i+1], hurst_df['Hurst'].iloc[i-1:i+1], color=color)
    
    # 색상 변경 시점에 점선 추가
    if color != prev_color:
        axs[1].axvline(hurst_df.index[i], color='black', linestyle='--', linewidth=1)
        prev_color = color

# 기준선 추가
for ax in axs:
    ax.axhline(0.5, color='black', linestyle='--', label='H = 0.5 (Random Walk)')
    ax.axhline(0.55, color='red', linestyle='--', label='H = 0.55 (Trending Threshold)')
    ax.axhline(0.45, color='green', linestyle='--', label='H = 0.45 (Mean-Reverting Threshold)')
    ax.set_xlabel('Date')
    ax.set_ylabel('Hurst Exponent')
    ax.legend()

# 서브플롯 제목
axs[0].set_title('Hurst Exponent Over Time (No Change Points)')
axs[1].set_title('Hurst Exponent Over Time (With Change Points)')

# 그래프 설정
plt.tight_layout()
plt.show()
