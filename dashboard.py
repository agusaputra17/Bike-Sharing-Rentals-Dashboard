import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# function

def create_weekday_df(df):
    # Daftar urutan hari
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    df.set_index('date', inplace=True)
    
    weekday_df = df.resample('D').agg({
        'weekday': 'first',
        'casual': 'sum',
        'registered': 'sum',
        'count': 'sum',
    }).groupby('weekday').agg({
        'casual': 'sum',
        'registered': 'sum',
        'count': 'mean'})

    # Lakukan pengurutan berdasarkan urutan hari
    weekday_df = weekday_df.reindex(days_order, level=1)

    # Reindeks DataFrame agar urutan hari menjadi sesuai
    weekday_df = weekday_df.reset_index()
    
    return weekday_df

def create_grouped_df(df, group_col, agg_col):
    grouped_df = df.groupby(group_col).agg({
        'casual': 'mean',
        'registered': 'mean',
        'count': 'mean'
    }).reset_index()
    
    return grouped_df

# ------------------------------------------------------------------------

# membaca dataset
df = pd.read_csv("dashboard/main_data.csv")

df.sort_values(by="date", inplace=True)
df.reset_index(inplace=True)

df['date'] = pd.to_datetime(df['date'])

min_date = df['date'].min()
max_date = df['date'].max()

# membuat sidebar
with st.sidebar:
    # mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
main_df = df[(df['date'] >= str(start_date)) &
             (df['date'] <= str(end_date))]

weekday_df = create_weekday_df(main_df)
# Create grouped DataFrames
grouped_dfs = {
    'weekday': create_grouped_df(main_df, 'weekday', ['casual', 'registered', 'count']),
    'time_range': create_grouped_df(main_df, 'time_range', ['casual', 'registered', 'count']),
    'season': create_grouped_df(main_df, 'season', ['casual', 'registered', 'count']),
    'weathersit': create_grouped_df(main_df, 'weathersit', ['casual', 'registered', 'count']),
    'workingday': create_grouped_df(main_df, 'workingday', ['casual', 'registered', 'count']),
    'holiday': create_grouped_df(main_df, 'holiday', ['casual', 'registered', 'count']),
    
    'month': create_grouped_df(main_df.resample('M').agg({
        'casual': 'sum',
        'registered': 'sum',
        'count': 'sum',
    }), 'date', ['casual', 'registered', 'count'])
}
weekday_users = weekday_df[['weekday','casual','registered']]
time_range_users = grouped_dfs['time_range'][['time_range','casual','registered']]
season_users = grouped_dfs['season'][['season','casual','registered']]
weathersit_users = grouped_dfs['weathersit'][['weathersit','casual','registered']]
workingday_users= grouped_dfs['workingday'][['workingday','casual','registered']]
holiday_users = grouped_dfs['holiday'][['holiday','casual','registered']]


# membuat judul
st.header('Bike-Sharing Rental Dashboard')
# sub judul
st.subheader('daily Users')

col1, col2, col3 = st.columns(3)

with col1:
    registered_users = weekday_df.registered.sum()
    st.metric("Total Registered users", value=registered_users)
    
with col2:
    casual_users = weekday_df.casual.sum()
    st.metric("Total Casual users", value=casual_users)
    
with col3:
    count_users = registered_users + casual_users
    st.metric("Total users", value=count_users)
    
st.write('---')
# visualisasi data
# Membuat subplot
fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(6, 4))

# Bar plot berdasarkan Hari
sns.barplot(
    x='weekday',
    y='count',
    data= weekday_df,
    ax=ax[0]
)
ax[0].set_xticklabels(ax[0].get_xticklabels(), fontsize=8)
ax[0].set_yticklabels(ax[0].get_yticklabels(), fontsize=8)
ax[0].set_title('Average Daily User', fontsize=10)
ax[0].set_xlabel(None)
ax[0].set_ylabel(None)

# Bar plot berdasarkan time range
sns.barplot(
    x='time_range',
    y='count',
    data= grouped_dfs['time_range'],
    ax=ax[1]
)
ax[1].set_xticklabels(ax[1].get_xticklabels(), fontsize=8)
ax[1].set_yticklabels(ax[1].get_yticklabels(), fontsize=8)
ax[1].set_title('Average User by time of day', fontsize=10)
ax[1].set_xlabel(None)
ax[1].set_ylabel(None)

plt.tight_layout()

# Menampilkan plot
st.pyplot(fig)

st.subheader("Season vs Weather")
colors = ["#B2B377", "#EADFB4", "#EADFB4", "#EADFB4", "#EADFB4"]
# Membuat subplot
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(15, 5))

sns.barplot(
    x="season", 
    y="count",
    data=grouped_dfs['season'].sort_values(by="count", ascending=False),
    palette=colors,
    ax=ax[0]
)
ax[0].set_title("Number of Users by Season", loc="center", fontsize=12)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)

sns.barplot(
    y="count",
    x="weathersit", 
    data=grouped_dfs['weathersit'].sort_values(by="count", ascending=False),
    palette=colors,
    ax=ax[1]
)
ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=10, fontsize=8)
ax[1].set_title("Number of Users by Weather", loc="center", fontsize=12)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)

st.pyplot(fig)



st.subheader("Workingday vs Holiday")
# Membuat subplot
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(7, 4))

workingday_df = grouped_dfs['workingday']
# Diagram lingkaran untuk hari kerja
ax[0].pie(workingday_df['count'], labels=workingday_df['workingday'], autopct='%1.1f%%', colors=['#DD5746', '#4793AF'], wedgeprops={'width': 0.6})
ax[0].set_title("Comparison of Users by Working Day", loc="center", fontsize=10)

holiday_df = grouped_dfs['holiday']
# Diagram lingkaran untuk hari libur
ax[1].pie(holiday_df['count'], labels=holiday_df['holiday'], autopct='%1.1f%%', colors=['#5356FF', '#E8751A'], wedgeprops={'width': 0.6})
ax[1].set_title("Comparison of Users by Holiday", loc="center", fontsize=10)

plt.tight_layout()
st.pyplot(fig)


st.subheader("Casual users vs Registered")
# Buat diagram garis untuk memvisualisasikan tren
# Membuat subplot
fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(15, 10))

# Berdasarkan hari
sns.lineplot(x='weekday', y='value', hue='variable', data=pd.melt(weekday_users, ['weekday']), ax=ax[0,0])
ax[0,0].set_xticklabels(ax[0,0].get_xticklabels(), rotation=10, fontsize=12)
ax[0,0].set_title('User Trends in a Week', fontsize=16)
ax[0,0].set_xlabel(None)
ax[0,0].set_ylabel('User count', fontsize=12)
ax[0,0].set_xticks(range(7))
ax[0,0].legend(title='User types', loc='upper left', bbox_to_anchor=(1, 1))

# Berdasarkan time range
sns.lineplot(x='time_range', y='value', hue='variable', data=pd.melt(time_range_users, ['time_range']), ax=ax[0,1])
ax[0,1].set_xticklabels(ax[0,1].get_xticklabels(), fontsize=12)
ax[0,1].set_title('User Trends in a day', fontsize=16)
ax[0,1].set_xlabel(None)
ax[0,1].set_ylabel(None)
ax[0,1].legend().remove()
plt.tight_layout()

# Berdasarkan musim
sns.barplot(x='season', y='value', hue='variable', data=pd.melt(season_users, ['season']), ax=ax[1,0])
ax[1,0].set_xticklabels(ax[1,0].get_xticklabels(), fontsize=12)
ax[1,0].set_title('Average users by Season', fontsize=16)
ax[1,0].set_xlabel(None)
ax[1,0].set_ylabel('User count', fontsize=12)
ax[1,0].legend(title='User types', loc='upper left', bbox_to_anchor=(1, 1))
plt.tight_layout()

# Berdasarkan cuaca
sns.barplot(x='weathersit', y='value', hue='variable', data=pd.melt(weathersit_users, ['weathersit']), ax=ax[1,1])
ax[1,1].set_xticklabels(ax[1,1].get_xticklabels(), rotation=10, fontsize=12)
ax[1,1].set_title('Average users by Weather', fontsize=16)
ax[1,1].set_xlabel(None)
ax[1,1].set_ylabel(None)
ax[1,1].set_xticklabels(weathersit_users['weathersit'], rotation=10)
ax[1,1].legend().remove()
plt.tight_layout()

plt.subplots_adjust(hspace=0.5, wspace=0.3)
st.pyplot(fig)


fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10, 4))

# Berdasarkan cuaca
sns.barplot(x='workingday', y='value', hue='variable', data=pd.melt(workingday_users, ['workingday']), ax=ax[0])
ax[0].set_title('average users on a working day', fontsize=12)
ax[0].set_xlabel(None)
ax[0].set_ylabel('User count', fontsize=10)
ax[0].legend(title='User type', loc='upper left', bbox_to_anchor=(1, 1))
plt.tight_layout()

# Berdasarkan cuaca
sns.barplot(x='holiday', y='value', hue='variable', data=pd.melt(holiday_users, ['holiday']), ax=ax[1])
ax[1].set_title('average users on Holiday', fontsize=12)
ax[1].set_xlabel(None)
ax[1].set_ylabel(None)
ax[1].legend().remove()
plt.tight_layout()

st.pyplot(fig)


st.subheader("Annual trend")
# Membuat plot
fig, ax = plt.subplots(figsize=(15, 6))

month_df = grouped_dfs['month']
# Menggunakan seaborn untuk membuat plot garis dengan tren
sns.lineplot(data=month_df, x=month_df['date'].dt.strftime('%B'), y='count', hue=month_df['date'].dt.strftime('%Y'), estimator='mean')

# Memberi judul dan label sumbu
ax.set_title('Annual User Number Trend', fontsize=16)
ax.set_xlabel(None)
ax.set_ylabel('User count', fontsize=14)

# Menampilkan legenda
ax.legend(title='Year')

# Menyertakan grid
plt.grid(True)

# Menampilkan plot
st.pyplot(fig)

st.write('---')

st.caption('Copyright (c) Agus Saputra Kambea 2024')