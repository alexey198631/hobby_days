from utils.defs import *


USER_CHOICE = '''Assessment system:

- 'sp' - spheres of life in total
- 'tp' - rank of the best
- 's1' - system of "1"
- 'cs' - clean sport
- 'sr' - seria
- 'w' - all initial frames
- 'gr' - year graphs
- 'grm' - month graphs
- 'q' - exit

Enter your choice: '''


USER_FILE = '''File name:  '''


user_choices = {
    'sp': spheres,
    's1': system_one_,
    'tp': top_pts,
    'cs': clean_sport,
    'sr': series,
    'w': write_all,
    'gr': graphs,
    'grm': graphs_m
}


def menu():

    file_name = 'data_files/Days.xlsx'
    days, full, days_competition = prep_one(file_name)

    lefts = days_left(days_competition)
    ltm = lefts[0]
    lty = lefts[1]

    user_input = input(USER_CHOICE)
    while user_input != 'q':
        if user_input in ('sp','tp','s1','w','cs','sr','gr','grm'):
            if user_input == 'sp':
                user_choices[user_input](days)
            elif user_input == 'tp':
                best_27 = input('Do you need to prepare 27 best days of each month? - "yes" or "no" : ')
                if best_27 == 'yes':
                    days_competition_tp = top27(days_competition)
                m_or_y = input('Choose what period to use - "year", "monthes" or "no": ')
                if m_or_y == 'year':
                    inp = str(input('What year (four digits)? - '))
                    mask_year = days_competition['YEAR'] == inp
                    days_competition_tp = days_competition[mask_year]
                elif m_or_y == 'monthes':
                    inp_2 = str(input('What month (in numbers)? - '))
                    mask_month = days_competition['MONTH'] == inp_2
                    days_competition_tp = days_competition[mask_month]
                elif m_or_y == 'no':
                    days_competition_tp = days_competition.loc[:,:]
                target_frame, last, my_choice_s, my_period_s = prep_two(days_competition_tp,ltm,lty)
                user_choices[user_input](target_frame, last, my_choice_s, my_period_s)
            elif user_input == 's1':
               user_choices[user_input](days_competition)
            elif user_input == 'w':
               user_choices[user_input](full,days_competition)
            elif user_input == 'cs':
               user_choices[user_input](days_competition)
            elif user_input == 'sr':
               user_choices[user_input](days_competition)
            elif user_input == 'gr':
               user_choices[user_input](days_competition)
            elif user_input == 'grm':
               user_choices[user_input](days_competition)
        else:
            print('Please choose a valid command.')
        user_input = input(USER_CHOICE)


menu()