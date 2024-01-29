
class Selectors:
    bb_all_matches = "[id^='g_3']"   #
    scoreline = '.smh__template'
    team_home = 'div.participant__participantName:nth-child(2)'
    team_away = 'div.participant__participantName:nth-child(1)'
    tournament = '.tournamentHeader__country'
    date_and_time = '.duelParticipant__startTime'
    final_score = '.detailScore__wrapper'
    show_more = '.event__more.event__more--static'
    fulltime_score = '.detailScore__fullTime'

    class CustomIndexedList(list):
        '''
        TAKE CARE !!!
        To ensure that quarters in basketball, periods in hockey, and halves in football and handball
        correspond to their actual values rather than the standard indexing, an offset of 1 is applied.
        '''
        def __getitem__(self, index):
            if 1 <= index <= 5:
                # Adjust the index to start from 1 instead of 0
                return super().__getitem__(index - 1)
            else:
                raise IndexError("Index must be between 1 and 5 inclusive.")

    home_part = CustomIndexedList(map(lambda i: f'.smh__part.smh__home.smh__part--{i}', range(1, 6)))
    away_part = CustomIndexedList(map(lambda i: f'.smh__part.smh__away.smh__part--{i}', range(1, 6)))

    total_button = '[title="Over/Under"]'
    handicap_button = '[title="Asian handicap"]'
    home_away = '[title="Home/Away"]'

    coef_box = '.ui-table__body'

    # This selectors often change by site owners
    odds_on_bar = 'button._tab_33oei_5:has-text("Odds")'
    handicap_quarter1 = 'button._tab_33oei_5:has-text("1st Qrt")'



