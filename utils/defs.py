import pandas as pd
import numpy as np
import statistics as st
import matplotlib.pyplot as plt
from dateutil.parser import parse
from datetime import datetime

from masks import *


def year(x): #def for taking YEAR from date (when I created this version, I didn't know that it was possible to parse dates
    y = str(x)
    yr = y.split('-')[0]
    return yr


def month(x): #def for taking MONTH from date (when I created this version, I didn't know that it was possible to parse dates
    x = str(x)
    mnth = x.split('-')[1]
    return mnth


def week_name(dfr): #def for taking name of Week from Days list of my diary and mark 'del' weeks which didn't happen yet
    dfr.DATE = str(dfr.DATE)
    try:
        dfr.DATE = dfr.DATE.split(' ')[1]
        dfr.DATE = int(dfr.DATE)
    except:
        dfr.DATE = 'del'
    return dfr


def month_name(dfr):
        dfr.DATE = str(dfr.DATE)
        try:
            dfr.DATE = dfr.DATE.split(' ')[3]
            dfr.DATE = int(dfr.DATE)
        except:
            dfr.DATE = 'del'
        return dfr


def pivot(dt,ind,val,fun):
    pvt = pd.pivot_table(dt,
                         index=ind,
                         values=val,
                         aggfunc=fun)
    return pvt


def new_points(dfr,columnis,p):
    maxim = p
    top = dfr.loc[0,columnis].round(3)

    if dfr[columnis].name == 'ALCOTIME':
        for n in range(len(dfr[columnis])):
            if dfr.loc[n, columnis] == top:
                dfr.loc[n, columnis] = maxim
                p -= 1
            elif p > 0:
                try:
                    nexus = dfr.loc[n + 1, columnis]
                    if dfr.loc[n, columnis] == nexus:
                        dfr.loc[n, columnis] = p
                    else:
                        dfr.loc[n, columnis] = p
                        p -= 1
                except:
                    dfr.loc[n, columnis] = 0
            else:
                dfr.loc[n, columnis] = 0

    else:
        for n in range(len(dfr[columnis])):
            if dfr.loc[n, columnis] == 0:
                dfr.loc[n, columnis] = 0
            else:
                if dfr.loc[n, columnis] == top:
                    dfr.loc[n, columnis] = maxim
                    p -= 1
                elif p > 0:
                    try:
                        nexus = dfr.loc[n + 1, columnis]
                        if dfr.loc[n, columnis] == nexus:
                            dfr.loc[n, columnis] = p
                        else:
                            dfr.loc[n, columnis] = p
                            p -= 1
                    except:
                        dfr.loc[n, columnis] = 0
                else:
                    dfr.loc[n, columnis] = 0

    return dfr


def top_rating(df,col_set,p):
    for c in col_set:
        df = df.sort_values(by=c, ascending=False)
        df = df.reset_index(drop=True)
        df = new_points(df, c, p)

    summa = df.sum(axis=1, numeric_only=True)
    df.insert(0, 'TOTAL_SUM', summa)
    df.sort_values(by='TOTAL_SUM', ascending=False, inplace = True)

    return df


def pts(dfr, clmn):

    temp = dfr[clmn].std()

    if dfr[clmn].mean() < 0:
        for n in range(len(dfr[clmn])):
            if dfr.loc[n, clmn] < 0:
                dfr.loc[n, clmn] = 0
            else:
                dfr.loc[n, clmn] = 1
    elif dfr[clmn].std() <= 1:

        for n in range(len(dfr[clmn])):
            if dfr.loc[n, clmn] > 0:
                dfr.loc[n, clmn] = 1
            else:
                dfr.loc[n, clmn] = 0

    else:
        for n in range(len(dfr[clmn])):
            if dfr.loc[n, clmn] >= temp:
                dfr.loc[n, clmn] = 1
            else:
                dfr.loc[n, clmn] = 0

    return dfr


def top27(df):
    years = df.YEAR.unique()
    months = df.MONTH.unique()
    df['DAY#'] = df['DAY#'].astype('str')
    df['WEEK#'] = df['WEEK#'].astype('str')
    df['MONTH#'] = df['MONTH#'].astype('str')
    list_of_columns = key_columns # all key columns from mask file
    list_of_dates = ['DATE', 'YEAR', 'MONTH', 'WEEK_DAY', 'EVENT', 'DAY#', 'WEEK#',
                                 'WEEK_EVENT', 'MONTH#', 'MONTH_EVENT']
    total_sum_list = ['TOTAL_SUM']
    for_pointing = list_of_dates + list_of_columns
    necessary = total_sum_list + list_of_dates + list_of_columns
    best = pd.DataFrame(columns=necessary)

    for y in years:
        try:
            for m in months:
                mask1 = df.YEAR == y
                mask2 = df.MONTH == m
                data_frame = df[mask1 & mask2]
                pointing = data_frame.loc[:, for_pointing]
                setting = list_of_columns
                for c in setting:
                    pointing = pointing.sort_values(by=c, ascending=False)
                    pointing = pointing.reset_index(drop=True)
                    pointing = new_points(pointing,c,27)
                sums = pointing.sum(axis=1, numeric_only = True)
                pointing.insert(0, 'TOTAL_SUM', sums)
                pointing = pointing.sort_values(by='TOTAL_SUM', ascending=False)
                best = pd.concat([best, pointing.head(27)])

        except:

            temp = best.loc[:, ['EVENT', 'TOTAL_SUM']]
            df = pd.merge(df, temp, on='EVENT', how='right')

            writer = pd.ExcelWriter('Mega.xlsx', engine='xlsxwriter')
            best.to_excel(writer, sheet_name='1')
            writer.close()

    return df


def get_key(d, value):
    for k,v in d.items():
        if v == value:
            return k


def up_to_day(df):

    dtfr = df.copy()

    # convert the Date column to datetime type
    #dtfr['DATE'] = pd.to_datetime(dtfr['DATE'], format='%d.%m.%Y')

    # get the end date of each year (i.e. today's date with the year replaced by the year of each row's date)
    years = list(dtfr['YEAR'].unique())
    end_dates = [datetime(int(year), datetime.today().month, datetime.today().day - 1) for year in years]

    # filter the dataframe using boolean indexing
    new_df = pd.concat([dtfr[(dtfr['DATE'] >= datetime(int(year), 1, 1)) & (dtfr['DATE'] <= end_date)] for year, end_date in
                        zip(years, end_dates)], ignore_index=True)
    return new_df


def prep_one(file_name):
    total = pd.read_excel(file_name, sheet_name='health')

    days_total = total.loc[:, health_columns]
    more = pd.read_excel(file_name, sheet_name='lang')
    days = pd.read_excel(file_name, sheet_name='days')
    week = pd.read_excel(file_name, sheet_name='week')
    week = week.loc[:, ['DATE', 'DAY#', 'WEEK#', 'MONTH#']]

    my_days = days.loc[:, ['Type', 'DATE', 'EVENT']]
    my_days = my_days.loc[my_days['Type'] == 'D'].set_index('DATE')


    name_weeks = days.loc[:, ['Type', 'DATE', 'EVENT']]
    my_weeks = name_weeks.loc[name_weeks['Type'] == 'W']
    my_weeks = my_weeks.apply(week_name, axis='columns')
    my_weeks = my_weeks.loc[:,['DATE','EVENT']]
    my_weeks = my_weeks.loc[my_weeks['DATE'] != 'del']
    my_weeks = my_weeks.rename(columns={'DATE':'WEEK#','EVENT':'WEEK_EVENT'})
    my_weeks = my_weeks.set_index('WEEK#')
    name_monthes = days.loc[:, ['Type', 'DATE', 'EVENT']]
    my_monthes = name_monthes.loc[name_monthes['Type'] == 'M']
    my_monthes = my_monthes.apply(month_name, axis='columns')
    my_monthes = my_monthes.loc[:,['DATE','EVENT']]
    my_monthes = my_monthes.loc[my_monthes['DATE'] != 'del']
    my_monthes = my_monthes.rename(columns={'DATE':'MONTH#','EVENT':'MONTH_EVENT'})
    my_monthes = my_monthes.set_index('MONTH#')

    days_total = days_total.set_index('DATE')
    days_total = days_total.join(my_days)

    weeks = week.set_index('DATE')
    days_total = days_total.join(weeks, lsuffix='1', rsuffix='2')
    days_total = days_total.reset_index()
    days_total = pd.merge(days_total,
                          my_weeks,
                          on ='WEEK#',
                          how ='inner')
    days_total = pd.merge(days_total,
                          my_monthes,
                          on ='MONTH#',
                          how ='inner')
    days_total = days_total.loc[:, health_columns_with_date]
    full = days_total.join(more.set_index('DATE'),on='DATE', rsuffix='_more')

    def year(x):
        y = str(x)
        yr = y.split('-')[0]
        return yr

    def month(x):
        x = str(x)
        mnth = x.split('-')[1]
        return mnth

    years = full['DATE'].apply(lambda x: year(x))
    monthes = full.DATE.apply(lambda x: month(x))
    full.insert(1, 'MONTH', monthes)
    full.insert(1, 'YEAR', years)
    full['LIGHT'] = full['BEER'] + full['WINE'] + full['COCTAIL']
    full['STRONG'] = full['VODKA'] + full['WHISKY'] + full['BRANDY']
    full['NFOOD'] = full['FASTFOOD'] + full['SWEETS']
    full['ACTIVE'] = full.BREATH + full.CTRAINING * 5 +  full.SPORT_TIME + full.MK * 11 + full.PT * 7
    full['HEALTH'] = full.ACTIVE + full.MEDITAITON + full.OUTSIDE + full.EYES * 10 + full.ALCOTIME + full.SLEEP
    full['STRENGHT_POINTS'] = full.PUSH_UPS + full.PULL_UPS * 3 + full.SKID * 2 + full.SQUATING + full.ABS + full.PLANK / 2 + full.WATER / 4 + full.RUN * 50 + full.CYCLE * 20 + full.WALK * 50 + full.GOALS * 10 + full.DUMBBELLS / 2
    full['WRITING'] = full.WRITE_ENG + full.WRITE_RUS
    full['READING'] = full.READ_ENG + full.READ_RUS + full.READ_DUT + full.READ_SPA
    full['LISTENING'] = full.LISTEN_ENG + full.LISTEN_SPA + full.LISTEN_DUT + full.LISTEN_RUS
    full['ALW'] = full['ALCOTIME'].apply(lambda x: 1 if x == 0 else 0)

    full['WEEK#'] = full['WEEK#'].astype('str')
    full['MONTH#'] = full['MONTH#'].astype('str')

    days_competition = full.loc[:, days_df_all_columns]

    up_today = input('Do you want to have data from the beginnig of the year up to date for each year? Type: "y" :')

    if up_today == 'y':
        days_competition = up_to_day(days_competition)

    return days, full, days_competition


def target_achievements(df, left_month, left_year, period, choice):
    overal = df.copy()
    try:
        this_year = overal[overal['YEAR'] == '2023']
    except:
        this_year = overal.copy()


    this_months = overal.tail(1)
    this_months = this_months.loc[:, my_choices[choice]]
    overal_m = overal.loc[:, my_choices[choice]]
    this_year_m = this_year.loc[:, my_choices[choice]]

    overal_max = {}
    this_year_max = {}

    for c in overal_m.columns:
        overal_max[c] = overal_m[c].max()
        this_year_max[c] = this_year_m[c].max()

    overal_max = pd.DataFrame.from_dict(overal_max, orient='index').transpose().rename(index={0: 'overal_max'})
    this_year_max = pd.DataFrame.from_dict(this_year_max, orient='index').transpose().rename(index={0: 'this_year_max'})

    this_year_m = pd.concat([this_year_m, this_year_max], ignore_index=False)
    this_year_m_last = this_year_m.tail(2)
    this_year_m_difference = this_year_m_last.diff(axis=0).tail(1).rename(index={'this_year_max': 'daily_goal'})

    overal_m = pd.concat([overal_m, overal_max], ignore_index=False)
    overal_m_last = overal_m.tail(2)
    overal_m_difference = overal_m_last.diff(axis=0).tail(1).rename(index={'overal_max': 'golden_goal'})

    this_year_max = this_year_max.round(0)
    overal_max = overal_max.round(0)

    if period == 'months_sum':
        this_year_m_difference = round(this_year_m_difference / left_month, 2)
        overal_m_difference = round(overal_m_difference / left_month, 2)
        final = pd.concat([this_year_max, overal_max, this_year_m_difference, overal_m_difference])
        final = final.transpose()
        return final

    elif period == 'years_sum':
        overal_m_difference = round(overal_m_difference / left_year, 2)
        final = pd.concat([overal_max, overal_m_difference])
        final = final.transpose()
        return final

    elif period == 'weeks':
        day_this_week_left = int(input('How many days left this week?'))
        overal_m_difference = round(overal_m_difference / day_this_week_left, 2)
        final = pd.concat([overal_max, overal_m_difference])
        final = final.transpose()
        return final


    else:
        'There is some mistake!'


def frq(dfr, clmn):
    if dfr.loc[0, clmn] != 0:
        dfr.loc[0, clmn] == 1
    else:
        dfr.loc[0, clmn] == 0

    for n in range(1, len(dfr[clmn])):
        if dfr.loc[n, clmn] > 0:
            dfr.loc[n, clmn] = int(dfr.loc[n - 1, clmn]) + 1
        else:
            dfr.loc[n, clmn] = 0

    return dfr


def prep_two(d_c,left_month,left_year):


    snp = np.sum
    anp = np.average

    pivot_weeks = pivot(d_c, ind_week, all_mask, snp)
    pivot_weeks_avg = pivot(d_c, ind_week, all_mask, anp)
    pivot_months = pivot(d_c, ind_month, all_mask, anp)
    pivot_months_sum = pivot(d_c, ind_month, all_mask, snp)
    pivot_years = pivot(d_c, ind_year, all_mask, anp)
    pivot_years_sum = pivot(d_c, ind_year, all_mask, snp)


    MY_PERIOD = '''Choose period for top rating:

        - 'weeks' - for weeks in totals
        - 'months' - for months in average
        - 'months_sum' - for months in totals
        - 'years' - for years in average
        - 'years_sum' - for years in totals

        My choice : '''

    W_INTERVAL = '''Time period:

        - '52' - last 52 weeks
        - '2' - last 2 years
        - 'all' - full history

        My choice : '''

    M_INTERVAL = '''Time period:

        - '12' - last 12 months
        - '36' - last 3 years in months
        - 'all' - full history

        My choice : '''

    Y_INTERVAL = '''Time period:

        - '3' - last 3 years
        - '5' - last 5 years
        - '10' - last 10 years
        - 'all' - full history


        My choice : '''



    my_period_s = input(MY_PERIOD)
    my_choice_s = input(MY_CHOICE)

    if my_period_s == 'weeks':

        if my_choice_s in ('a', 'h', 's', 'l', 't', 'w', 'p'):
            target_frame = pivot_weeks[my_choices[my_choice_s]].reset_index()
            last = input(W_INTERVAL)

            achievemnts = target_achievements(target_frame, left_month, left_year, my_period_s, my_choice_s)

            writer = pd.ExcelWriter(f'my_goals_avg_per_day_{my_period_s}_{my_choice_s}.xlsx', engine='xlsxwriter')
            achievemnts.to_excel(writer, sheet_name='Achieve_this!')
            writer.close()



            return target_frame, last,my_choice_s,my_period_s

        else:
            print('Please choose a valid command.')



    elif my_period_s == 'months':

        if my_choice_s in ('a', 'h', 's', 'l', 't', 'w', 'p'):
            target_frame = pivot_months[my_choices[my_choice_s]].round(3).reset_index()
            last = input(M_INTERVAL)
            return target_frame, last,my_choice_s, my_period_s

        else:
            print('Please choose a valid command.')

    elif my_period_s == 'months_sum':

        if my_choice_s in ('a', 'h', 's', 'l', 't', 'w', 'p'):
            target_frame = pivot_months_sum[my_choices[my_choice_s]].round(0).reset_index()
            last = input(M_INTERVAL)
            achievemnts = target_achievements(target_frame, left_month, left_year, my_period_s, my_choice_s)

            writer = pd.ExcelWriter(f'my_goals_avg_per_day_{my_period_s}_{my_choice_s}.xlsx', engine='xlsxwriter')
            achievemnts.to_excel(writer, sheet_name='Achieve_this!')
            writer.close()

            return target_frame, last,my_choice_s, my_period_s

        else:
            print('Please choose a valid command.')



    elif my_period_s == 'years':

        if my_choice_s in ('a', 'h', 's', 'l', 't', 'w', 'p'):
            target_frame = pivot_years[my_choices[my_choice_s]].round(3).reset_index()
            last = input(Y_INTERVAL)
            return target_frame, last,my_choice_s,my_period_s
        else:
            print('Please choose a valid command.')

    elif my_period_s == 'years_sum':

        if my_choice_s in ('a', 'h', 's', 'l', 't', 'w', 'p'):
            target_frame = pivot_years_sum[my_choices[my_choice_s]].round(0).reset_index()
            last = input(Y_INTERVAL)
            achievemnts = target_achievements(target_frame, left_month, left_year, my_period_s, my_choice_s)

            writer = pd.ExcelWriter(f'my_goals_avg_per_day_{my_period_s}_{my_choice_s}.xlsx', engine='xlsxwriter')
            achievemnts.to_excel(writer, sheet_name='Achieve_this!')
            writer.close()

            return target_frame, last, my_choice_s, my_period_s
        else:
            print('Please choose a valid command.')


    else:
        print('Please choose a valid command.') # #


def medals(df):
    medal = df.copy()
    mx = int(medal.iloc[:, -1].max())
    for i in range(len(medal)):
        medal.loc[i, 'Gold'] = (medal.loc[i, :] == mx).sum()
        medal.loc[i, 'Silver'] = (medal.loc[i, :] == int(mx - 1)).sum()
        medal.loc[i, 'Bronze'] = (medal.loc[i, :] == int(mx - 2)).sum()
    medal['medal pts'] = medal['Gold'] * 3 + medal['Silver'] * 2 + medal['Bronze'] * 1
    return medal


def top_pts(target_frame,last,my_choice_s,my_period_s):

    pointing = target_frame.copy()
    reserve = target_frame.copy()

    if last in ('52', '2', '12', '36', '3', '5', '10'):
        pointing = pointing.tail(my_int[last])
        p = my_int[last] - 1
    else:
        pointing = pointing
        p = int(input('Please, decide number of points for the best: '))

    pointing = top_rating(pointing, my_choices[my_choice_s], p)

    pm = medals(pointing)

    writer = pd.ExcelWriter(f'top_pts_{my_choice_s}_{my_period_s}_{last}.xlsx', engine='xlsxwriter')
    pointing.to_excel(writer, sheet_name=f'top_points_{my_period_s}')
    pm.to_excel(writer, sheet_name=f'top_points_{my_period_s}_wm')
    reserve.to_excel(writer, sheet_name='reserve')
    writer.close()


def system_one_(days_competition):

    days_competition_s = days_competition.copy()
    days_competition_s = days_competition_s.reset_index()
    my_choice_s = input(MY_CHOICE)

    for_system_one = ['DATE', 'YEAR', 'MONTH', 'EVENT', 'WEEK#', 'WEEK_EVENT'] + my_choices[my_choice_s]
    system_one = days_competition_s.loc[:, for_system_one]
    reserve = days_competition_s.loc[:, for_system_one]
    cols = my_choices[my_choice_s]
    for n in cols:
        pts(system_one, n)
    total_sum = system_one.sum(axis=1)
    system_one.insert(5, 'SUM', total_sum)
    system_one = system_one.sort_values(by='SUM', ascending=False)
    pivot_weeks_system_one = pd.pivot_table(system_one,
                                 index=['WEEK#','WEEK_EVENT'],
                                 values=['SUM'], aggfunc=np.sum)
    pivot_weeks_system_one.sort_values(by='SUM', ascending=False, inplace = True)
    pivot_months_system_one = pd.pivot_table(system_one,
                                            index=['YEAR','MONTH'],
                                            values=['SUM'], aggfunc=np.average)
    pivot_months_system_one.reset_index(inplace=True)
    pivot_months_system_one.sort_values(by='SUM', ascending=False, inplace = True)

    writer = pd.ExcelWriter(f'System_1_{my_choice_s}.xlsx', engine='xlsxwriter')
    system_one.to_excel(writer, sheet_name='S')
    pivot_weeks_system_one.to_excel(writer, sheet_name='W')
    pivot_months_system_one.to_excel(writer, sheet_name='M')
    reserve.to_excel(writer, sheet_name='initial')
    writer.close()


def write_all(full,days_competition):
    writer = pd.ExcelWriter('initial_full_stat_days.xlsx', engine='xlsxwriter')
    full.to_excel(writer, sheet_name='all_stat')
    days_competition.to_excel(writer, sheet_name='competition_cols')
    writer.close()


def spheres(days):
    inter1 = days.loc[days.Type == 'D']
    inter2 = inter1.loc[:, ['DATE', 'SPHERE']]
    working = inter2.dropna()

    working['pt'] = 1
    years = working['DATE'].apply(lambda x: year(x))
    monthes = working['DATE'].apply(lambda x: month(x))
    working.insert(1, 'MONTH', monthes)
    working.insert(1, 'YEAR', years)
    pvt = pd.pivot_table(working,
                         index=['SPHERE'],
                         columns=['YEAR'],
                         values='pt',
                         aggfunc=np.sum)
    pvt.reset_index()
    summ = pvt.sum(axis=1, numeric_only=True)
    pvt['total'] = summ
    pvt = pvt.sort_values(by='total', ascending=False)


    writer = pd.ExcelWriter('Spheres.xlsx', engine='xlsxwriter')
    pvt.to_excel(writer, sheet_name='Spheres')
    writer.close()


def days_left(df): #full data frame from Days file is necessary Days_competition
    mnt = str(df.tail(1).iloc[0, 2])
    yer = str(df.tail(1).iloc[0, 1])
    l_yer = str(int(yer) - 1)


    len_this_year = len(df[df['YEAR'] == yer])
    last_year_lenght = len(df[(df['YEAR'] == l_yer)])
    left_this_year = last_year_lenght - len(df[df['YEAR'] == yer])
    len_this_month = len(df[(df['YEAR'] == yer) & (df['MONTH'] == mnt)])
    last_year_month = len(df[(df['YEAR'] == l_yer) & (df['MONTH'] == mnt)])
    left_this_month = last_year_month - len_this_month

    print('')
    print(f'Today: {len_this_year} from {last_year_lenght}, left for achievement {left_this_year} this year!')
    print(f'Today: {len_this_month} from {last_year_month}, left for achievement {left_this_month} this month!')
    print('')

    return [left_this_month, left_this_year]


def clean_sport(my_df):
    df = my_df.copy()
    xl = df.loc[(df.SPORT_TIME > 0) & (df.ALCOTIME == 0)]
    pivot_s = pd.pivot_table(xl,
                             index=['YEAR', 'MONTH'],
                             values='SPORT_TIME', aggfunc=np.sum)
    pivot_s = pivot_s.reset_index()

    xs = df.loc[(df.SPORT_TIME > 0)]

    pivot_sx = pd.pivot_table(xs,
                              index=['YEAR', 'MONTH'],
                              values='SPORT_TIME', aggfunc=np.sum)
    pivot_sx = pivot_sx.reset_index()

    pivot_sx = pivot_sx.rename(columns={'SPORT_TIME': 'SPORT_TIME_F'})

    m = pd.merge(pivot_s, pivot_sx, how='inner')
    m['Share, %'] = round((m['SPORT_TIME'] / m['SPORT_TIME_F']) * 100, 1)

    writer = pd.ExcelWriter('Cleansport.xlsx', engine='xlsxwriter')
    m.to_excel(writer, sheet_name='cs')
    writer.close()
    print('clean_sport - done')


def series(my_df):

    df = my_df.copy()

    m_or_y = input('Choose what period to use - "year", "monthes" or "no": ')
    if m_or_y == 'year':
        inp = input('What year (four digits)? - ')
        mask_year = df['YEAR'] == inp
        dft = df[mask_year]
    elif m_or_y == 'monthes':
        inp_2 = input('What month (in numbers)? - ')
        mask_month = df['MONTH'] == inp_2
        dft = df[mask_month]
    elif m_or_y == 'no':
        dft = df.copy()


    for_series = dft.copy()
    my_choice_s = input(MY_CHOICE)
    cols = my_choices[my_choice_s]

    for c in cols:
        for_series[c] = for_series[c].apply(lambda x: 0 if x == 0 else 1)
        #for_series[c] = for_series[c].apply(lambda x: 0 if x == 0 else (1 if x > 0 else -1))

    for_series = for_series.reset_index() #нужно сбросить индекс, для функции frq

    for c in cols:
        seria = frq(for_series, c)

    last_line = seria.tail(1).transpose()

    mxm = {}
    for c in cols:
        print(c, '= ', seria[c].max(), 'days in a row')
        mxm[c] = seria[c].max()

    seria_mxm = pd.DataFrame.from_dict(mxm, orient='index').rename(columns={0: 'Seria_Max'})
    writer = pd.ExcelWriter('Seria.xlsx', engine='xlsxwriter')
    seria_mxm.to_excel(writer, sheet_name='Seria')
    last_line.to_excel(writer, sheet_name='Last_line')
    writer.close()


def all_graphs(df, column, years, last_year, current_year, last_year_2, last_year_3, last_year_4):
    df = df.loc[:, ['DATE', 'YEAR', 'MONTH', column]]
    lst = []
    dct = {}
    df['day'] = 0
    for y in years:

        data = df.loc[df.YEAR == y, :]
        data.iloc[0, 3] = data.iloc[0, 3]
        data.iloc[0, 4] = 1
        for i in range(1, len(data)):
            data.iloc[i, 4] = i + 1
            data.iloc[i, 3] = data.iloc[i, 3] + data.iloc[i - 1, 3]
        lst.append(data)
        dct[y] = data[column][-1:].values[0]

    dct2 = {}
    for i in dct.keys():
        if dct[i] != 0.0:
            dct2[i] = dct[i]


    dct_without_current_year = {}
    for y in dct2.keys():
        if y != current_year:
            dct_without_current_year[y] = dct2[y]

    # exlusion all '0' lines from graph and changing it for current year graph only
    if len(dct_without_current_year) < 2:
        min_year = last_year = last_year_2 = last_year_3 = last_year_4 = current_year
    else:
        for i, yr in enumerate([last_year, last_year_2, last_year_3, last_year_4]):
            if dct[yr] == 0:
                if i == 0:
                    last_year = current_year
                elif i == 1:
                    last_year_2 = current_year
                elif i == 2:
                    last_year_3 = current_year
                elif i == 3:
                    last_year_4 = current_year

    min_year = get_key(dct_without_current_year, min(dct_without_current_year.values()))
    max_year = get_key(dct, max(dct2.values()))

    df = pd.concat(lst)
    mycolors = ['tab:red', 'gold', 'tab:blue', 'tab:green', 'tab:brown', 'firebrick', 'tab:pink', 'tab:olive',
                'deeppink', 'steelblue', 'firebrick', 'mediumseagreen', 'firebrick', 'mediumseagreen']
    plt.figure(figsize=(16, 10), dpi=80)


    years = [min_year, max_year, last_year, current_year, last_year_2, last_year_3, last_year_4]

    for i, y in enumerate(years):
        plt.plot('day', column, data=df.loc[df.YEAR == y, :], color=mycolors[i], label=y)
        plt.text(df.loc[df.YEAR == y, :].shape[0] - .9, df.loc[df.YEAR == y, column][-1:].values[0], y, fontsize=14,
                 color=mycolors[i])
        plt.grid(color='grey', linestyle='-', linewidth=.5)

    # plt.ylim(0, max(dct.values()))
    plt.xlim(0, 366)
    plt.title(column, fontsize=22)
    plt.grid(axis='y', alpha=.3)

    # Remove borders
    plt.gca().spines["top"].set_alpha(0.0)
    plt.gca().spines["bottom"].set_alpha(0.5)
    plt.gca().spines["right"].set_alpha(0.0)
    plt.gca().spines["left"].set_alpha(0.5)
    # plt.legend(loc='lower right', ncol=2, fontsize=12)
    current_time = datetime.now().strftime("%d_%m_%Y")
    plt.savefig(f'data_files/{column}_{current_time}.png', dpi=300, bbox_inches='tight')
    # plt.show()

def graphs(my_df):
    # Import Data
    df = my_df.copy()
    years = df['YEAR'].unique()
    current_year = years[len(years) - 1]
    last_year = years[len(years) - 2]
    last_year_2 = years[len(years) - 3]
    last_year_3 = years[len(years) - 4]
    last_year_4 = years[len(years) - 5]
    key_columns = top_priority_mask
    #column = input(COLUMN_CHOICE)

    for column in all_mask:
        all_graphs(df, column, years, last_year, current_year, last_year_2, last_year_3, last_year_4)
    print('Done')


def all_graphs_m(df, years, months, column, current_year, current_month, last_year):
    df = df.loc[:, ['DATE', 'YEAR', 'MONTH', column, 'D']]
    lst = []
    dct = {}
    df['day'] = 0

    for y in years:
        for m in months:
            try:
                data = df.loc[(df.YEAR == y) & (df.MONTH == m), :]
                data.iloc[0, 5] = 1
                data.iloc[0, 3] = data.iloc[0, 3]
                for i in range(1, len(data)):
                    data.iloc[i, 5] = i + 1
                    data.iloc[i, 3] = data.iloc[i, 3] + data.iloc[i - 1, 3]
                lst.append(data)
                dct[(y, m)] = data[column][-1:].values[0]
            except:
                continue

    dct2 = {}
    for i in dct.keys():
        if dct[i] != 0.0:
            dct2[i] = dct[i]

    dct3 = {}
    for j in dct2.keys():
        if j[1] == current_month:
            dct3[j] = dct2[j]


    min_year = get_key(dct2, min(dct2.values()))[0]
    min_year_month = get_key(dct2, min(dct2.values()))[1]
    max_year = get_key(dct2, max(dct2.values()))[0]
    max_year_month = get_key(dct2, max(dct2.values()))[1]
    try:
        max_current_year = get_key(dct3, max(dct3.values()))[0]
        max_current_year_month = get_key(dct3, max(dct3.values()))[1]
        min_current_year = get_key(dct3, min(dct3.values()))[0]
        min_current_year_month = get_key(dct3, min(dct3.values()))[1]
    except:
        max_current_year = current_year
        max_current_year_month = current_month
        min_current_year = current_year
        min_current_year_month = current_month


    df = pd.concat(lst)
    mycolors = ['tab:red', 'gold', 'tab:blue', 'tab:green', 'tab:olive', 'firebrick', 'tab:pink', 'tab:olive',
                'deeppink', 'steelblue', 'firebrick', 'mediumseagreen', 'firebrick', 'mediumseagreen']
    plt.figure(figsize=(16, 10), dpi=80)

    test_tuple = [(min_year, min_year_month), (max_year, max_year_month), (current_year, current_month),
                  (last_year, current_month), (max_current_year, max_current_year_month), (min_current_year, min_current_year_month)]

    for i, (y, m) in enumerate(test_tuple):
        plt.plot('day', column, data=df.loc[(df.YEAR == y) & (df.MONTH == m), :], color=mycolors[i], label=y)
        plt.text(df.loc[(df.YEAR == y) & (df.MONTH == m), :].shape[0] - .9,
                 df.loc[(df.YEAR == y) & (df.MONTH == m), column][-1:].values[0], f'{m},{y}', fontsize=14,
                 color=mycolors[i])
        plt.grid(color='grey', linestyle='-', linewidth=.5)

    # plt.ylim(0, max(dct2.values()))
    # plt.xlim(0, 366)
    plt.title(column, fontsize=22)
    plt.grid(axis='y', alpha=.3)

    # Remove borders
    plt.gca().spines["top"].set_alpha(0.0)
    plt.gca().spines["bottom"].set_alpha(0.5)
    plt.gca().spines["right"].set_alpha(0.0)
    plt.gca().spines["left"].set_alpha(0.5)
    # plt.legend(loc='lower right', ncol=2, fontsize=12)
    current_time = datetime.now().strftime("%d_%m_%Y")
    plt.savefig(f'data_files/months/{column}_{current_time}.png', dpi=300, bbox_inches='tight')
    #plt.show()


def graphs_m(my_df):
    # Import Data
    df = my_df.copy()
    df.DATE = df.DATE.astype('str')
    df['D'] = [parse(d).strftime('%d') for d in df.DATE]
    years = df['YEAR'].unique()
    months = df['MONTH'].unique()
    current_month = df.loc[:, 'MONTH'][-1:].values[0]
    current_year = years[len(years) - 1]
    last_year = years[len(years) - 2]
    last_year_2 = years[len(years) - 3]
    last_year_3 = years[len(years) - 4]
    last_year_4 = years[len(years) - 5]
    #column = input(COLUMN_CHOICE)

    for column in all_mask:
        all_graphs_m(df, years, months, column, current_year, current_month, last_year)
    print('Done')