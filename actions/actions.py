# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from datetime import datetime
from definitions import (DATABASE_HOST, DATABASE_PASSWORD, 
                         DATABASE_PORT, DATABASE_USER)
from rasa_sdk import Action, FormValidationAction, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import FollowupAction, SlotSet
from typing import Any, Dict, List, Optional, Text

import collections
import logging
import math
import mysql.connector
import random


class ActionEndDialog(Action):
    """Action to cleanly terminate the dialog."""
    # ATM this action just call the default restart action
    # but this can be used to perform actions that might be needed
    # at the end of each dialog
    def name(self):
        return "action_end_dialog"

    async def run(self, dispatcher, tracker, domain):

        return [FollowupAction('action_restart')]
    

class ActionDefaultFallbackEndDialog(Action):
    """Executes the fallback action and goes back to the previous state
    of the dialogue"""

    def name(self) -> Text:
        return "action_default_fallback_end_dialog"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(template="utter_default")
        dispatcher.utter_message(template="utter_default_close_session")

        # End the dialog, which leads to a restart.
        return [FollowupAction('action_end_dialog')]


def get_latest_bot_utterance(events) -> Optional[Any]:
    """
       Get the latest utterance sent by the VC.
        Args:
            events: the events list, obtained from tracker.events
        Returns:
            The name of the latest utterance
    """
    events_bot = []

    for event in events:
        if event['event'] == 'bot':
            events_bot.append(event)

    if (len(events_bot) != 0
            and 'metadata' in events_bot[-1]
            and 'utter_action' in events_bot[-1]['metadata']):
        last_utterance = events_bot[-1]['metadata']['utter_action']
    else:
        last_utterance = None

    return last_utterance


def check_session_not_done_before(cur, prolific_id):
    
    query = ("SELECT * FROM sessiondata WHERE prolific_id = %s")
    cur.execute(query, [prolific_id])
    done_before_result = cur.fetchone()
    
    not_done_before = True

    # user has done the session before
    if done_before_result is not None:
        not_done_before = False
        
    return not_done_before
    


class ActionLoadSessionFirst(Action):
    
    def name(self) -> Text:
        return "action_load_session_first"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    
        prolific_id = tracker.current_state()['sender_id']
        
        conn = mysql.connector.connect(
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_HOST,
            port=DATABASE_PORT,
            database='db'
        )
        cur = conn.cursor(prepared=True)

        ## commented out for debugging
        
        # session_loaded = check_session_not_done_before(cur, prolific_id)
        
        conn.close()

        ## changd to True for debugging

        return [SlotSet("session_loaded", True)]

def round_to_nearest_5(n):
    return 5 * round(n / 5)


class ActionCreateInitialPlan(Action):

    def name(self) -> Text:
        return "action_create_initial_plan"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # goal

        goal = f"{tracker.get_slot('goal')}"

        # free times

        monday_morning = bool(tracker.get_slot('monday_morning'))
        monday_midday = bool(tracker.get_slot('monday_midday'))
        monday_afternoon = bool(tracker.get_slot('monday_afternoon'))
        monday_evening = bool(tracker.get_slot('monday_evening'))

        tuesday_morning = bool(tracker.get_slot('tuesday_morning'))
        tuesday_midday = bool(tracker.get_slot('tuesday_midday'))
        tuesday_afternoon = bool(tracker.get_slot('tuesday_afternoon'))
        tuesday_evening = bool(tracker.get_slot('tuesday_evening'))

        wednesday_morning = bool(tracker.get_slot('wednesday_morning'))
        wednesday_midday = bool(tracker.get_slot('wednesday_midday'))
        wednesday_afternoon = bool(tracker.get_slot('wednesday_afternoon'))
        wednesday_evening = bool(tracker.get_slot('wednesday_evening'))

        thursday_morning = bool(tracker.get_slot('thursday_morning'))
        thursday_midday = bool(tracker.get_slot('thursday_midday'))
        thursday_afternoon = bool(tracker.get_slot('thursday_afternoon'))
        thursday_evening = bool(tracker.get_slot('thursday_evening'))

        friday_morning = bool(tracker.get_slot('friday_morning'))
        friday_midday = bool(tracker.get_slot('friday_midday'))
        friday_afternoon = bool(tracker.get_slot('friday_afternoon'))
        friday_evening = bool(tracker.get_slot('friday_evening'))

        saturday_morning = bool(tracker.get_slot('saturday_morning'))
        saturday_midday = bool(tracker.get_slot('saturday_midday'))
        saturday_afternoon = bool(tracker.get_slot('saturday_afternoon'))
        saturday_evening = bool(tracker.get_slot('saturday_evening'))

        sunday_morning = bool(tracker.get_slot('sunday_morning'))
        sunday_midday = bool(tracker.get_slot('sunday_midday'))
        sunday_afternoon = bool(tracker.get_slot('sunday_afternoon'))
        sunday_evening = bool(tracker.get_slot('sunday_evening'))

        # energy levels

        weekdays_morning = tracker.get_slot('weekdays_morning')
        weekdays_midday = tracker.get_slot('weekdays_midday')
        weekdays_afternoon = tracker.get_slot('weekdays_afternoon')
        weekdays_evening = tracker.get_slot('weekdays_evening')

        
        weekends_morning = tracker.get_slot('weekends_morning')
        weekends_midday = tracker.get_slot('weekends_midday')
        weekends_afternoon = tracker.get_slot('weekends_afternoon')
        weekends_evening = tracker.get_slot('weekends_evening')

        # "day_time" : [free_at_time, energetic_at_time]
        days = {
        "monday_morning" : [monday_morning, weekdays_morning],
        "monday_midday" : [monday_midday, weekdays_midday],
        "monday_afternoon" : [monday_afternoon, weekdays_afternoon],
        "monday_evening" : [monday_evening, weekdays_evening],

        "tuesday_morning" : [tuesday_morning, weekdays_morning],
        "tuesday_midday" : [tuesday_midday, weekdays_midday],
        "tuesday_afternoon" : [tuesday_afternoon, weekdays_afternoon],
        "tuesday_evening" : [tuesday_evening, weekdays_evening],

        "wednesday_morning" : [wednesday_morning, weekdays_morning],
        "wednesday_midday" : [wednesday_midday, weekdays_midday],
        "wednesday_afternoon" : [wednesday_afternoon, weekdays_afternoon],
        "wednesday_evening" : [wednesday_evening, weekdays_evening],

        "thursday_morning" : [thursday_morning, weekdays_morning],
        "thursday_midday" : [thursday_midday, weekdays_midday],
        "thursday_afternoon" : [thursday_afternoon, weekdays_afternoon],
        "thursday_evening" : [thursday_evening, weekdays_evening],

        "friday_morning" : [friday_morning, weekdays_morning],
        "friday_midday" : [friday_midday, weekdays_midday],
        "friday_afternoon" : [friday_afternoon, weekdays_afternoon],
        "friday_evening" : [friday_evening, weekdays_evening],

        "saturday_morning" : [saturday_morning, weekends_morning],
        "saturday_midday" : [saturday_midday, weekends_midday],
        "saturday_afternoon" : [saturday_afternoon, weekends_afternoon],
        "saturday_evening" : [saturday_evening, weekends_evening],

        "sunday_morning" : [sunday_morning, weekends_morning],
        "sunday_midday" : [sunday_midday, weekends_midday],
        "sunday_afternoon" : [sunday_afternoon, weekends_afternoon],
        "sunday_evening" : [sunday_evening, weekends_evening]
        }

        available_timeslots = [[day, days[day][1]] for day in days if days[day][0] == True]

        number_of_timeslots = len(available_timeslots) 

        high_energy_timeslots = [[available, energy] for [available, energy] in available_timeslots if energy == '3']

        medium_energy_timeslots = [[available, energy] for [available, energy] in available_timeslots if energy == '2']

        low_energy_timeslots = [[available, energy] for [available, energy] in available_timeslots if energy == '1']

        number_of_high_energy_timeslots = len(high_energy_timeslots)

        number_of_medium_energy_timeslots = len(medium_energy_timeslots)

        number_of_low_energy_timeslots = len(low_energy_timeslots)

        minutes_week_1 = 120

        if goal == "8000":
            weekly_increase = 20
        elif goal == "9000":
            weekly_increase = 22
        elif goal == "10000":
            weekly_increase = 25

        if number_of_timeslots < 4:
            
            dispatcher.utter_message(text=f"I'm afraid you would have to do a bit too much activity all at once if we were to plan with your current schedule in mind… Let's think again about the times when you are available. Even if you're free for only 30 minutes or so at that time, that should still be enough to take a short walk.  [Handle this case later by going back to selecting time slots].")
            
            return []

        elif number_of_timeslots == 4:

            selected =  available_timeslots

        else: 

            select_slots = 4

            if number_of_high_energy_timeslots > select_slots:

                selected = random.sample(high_energy_timeslots, select_slots)

            else: 

                selected = high_energy_timeslots

                select_slots -= number_of_high_energy_timeslots

                if number_of_medium_energy_timeslots > select_slots:

                    selected += random.sample(medium_energy_timeslots, select_slots)

                else:

                    selected += medium_energy_timeslots

                    select_slots -= number_of_medium_energy_timeslots

                    if select_slots is not 0:
                        
                        selected += random.sample(low_energy_timeslots, select_slots)


        # dispatcher.utter_message(text=f"Available slots: {available_timeslots},  Selected slots: {selected}")

        duration_per_timeslot_week_1 = math.ceil(minutes_week_1/4)

        selected_times = [time_energy[0] for time_energy in selected]

        message = f"""Plan: Week 1 - {round_to_nearest_5(duration_per_timeslot_week_1)} minutes at these time slots: {selected_times}. Week 2 - {round_to_nearest_5(math.ceil((minutes_week_1 + weekly_increase)/4))} minutes at these time slots: {selected_times}. Week 3 - Walking for {round_to_nearest_5(minutes_week_1 + 2* weekly_increase)} minutes across 4 days. Week 4 - Walking for {round_to_nearest_5(minutes_week_1 + 3* weekly_increase)} minutes across 4 days. Month 2 - Walking for up to {round_to_nearest_5(minutes_week_1 + 7* weekly_increase)} minutes per week across 5 days. Month 3 - Walking for up to {round_to_nearest_5(minutes_week_1 + 11* weekly_increase)} minutes per week across 6 days."""

        dispatcher.utter_message(text=message)

        return [SlotSet("plan_1", message)]

    
    
def save_sessiondata_entry(cur, conn, prolific_id, time, event):
    query = "INSERT INTO sessiondata(prolific_id, time, event) VALUES(%s, %s, %s)"
    cur.execute(query, [prolific_id, time, event])
    conn.commit()
    

class ActionSaveEventState(Action):
    def name(self):
        return "action_save_event_state"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        conn = mysql.connector.connect(
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_HOST,
            port=DATABASE_PORT,
            database='db'
        )
        cur = conn.cursor(prepared=True)
        
        prolific_id = tracker.current_state()['sender_id']

        ch = tracker.get_slot("changes_to_plan")

        c = tracker.get_slot("confidence")

        pu = tracker.get_slot("perceived_usefulness")

        a = tracker.get_slot("attitude")

        explain_planning = tracker.get_slot("explain_planning")

        identify_barriers = tracker.get_slot("identify_barriers")

        deal_with_barriers = tracker.get_slot("deal_with_barriers")

        show_testimonials = tracker.get_slot("show_testimonials")

        state = f"{ch}, {c}, {pu}, {a}, {explain_planning}, {identify_barriers}, {deal_with_barriers}, {show_testimonials}"

        save_sessiondata_entry(cur, conn, prolific_id, formatted_date, f"state: {state}")

        conn.close()
        
        return []

def do_action(action):

    if action == "explain_planning":

        dispatcher.utter_message(text="Maybe it would be useful to look again at why planning can help you do more physical activity.")
        
        buttons = []

        buttons.append({"title": "Motivation"})
        buttons.append({"title": "Routine"})
        buttons.append({"title": "Visualising the road towards the goal"})
        buttons.append({"title": "Realistic expectations"})
        
        dispatcher.utter_message(text="First off, why do you think planning can help you do more physical activity?", buttons=buttons)
        dispatcher.utter_message(text="That's right!")
        dispatcher.utter_message(text="Ultimately, the plan is meant to help you stay committed to your goal.")
        dispatcher.utter_message(text="By creating a plan that is consistent across different weeks, it will be easier for you to form a habit of doing physical activity regularly.")
        dispatcher.utter_message(text="Besides this, the plan shows you what you will be able to achieve in the end, so you have an idea of the goal you are working towards.")
        dispatcher.utter_message(text="It might also help you set realistic expectations.")
        dispatcher.utter_message(text="By seeing the plan, you can picture yourself doing the exercises each week, and think if that is feasible for you.")
    
    elif action == "identify_barriers":

        dispatcher.utter_message(text="I think it might be useful to think of some barriers, or things that might stop or prevent you from doing more physical activity.")

        dispatcher.utter_message(text="Let's first think of what the barriers are and then we'll see how we can deal with them.")

        buttons = []

        buttons.append({"title": "Lack of time"})
        buttons.append({"title": "Lack of energy"})
        buttons.append({"title": "Disliking being in the presence of others when exercising"})
        buttons.append({"title": "Lack of equipment"})
        buttons.append({"title": "Family obligations"})

        ispatcher.utter_message(text="Which of these do you think might be a common barrier?", buttons=buttons)

        dispatcher.utter_message(text="You're right!")
        dispatcher.utter_message(text="A common barrier is that you may not always have time to exercise or you may be tired at the end of the day.")
        dispatcher.utter_message(text="On the other hand, maybe you do not enjoy other people being there when you exercise.")
        dispatcher.utter_message(text="Maybe you don't have shoes that are comfortable to take longer walks in.")
        dispatcher.utter_message(text="It could also be that you have young children to take care of and that leaves you with little time.")
        dispatcher.utter_message(text="All of these are barriers which could prevent you from doing more physical activity.")
        dispatcher.utter_message(text="Think if these apply to you specifically.")
        dispatcher.utter_message(text="You can also try to come up with some things that you know have been barriers in the past.")
        dispatcher.utter_message(text="Write down all the barriers for yourself and let me know when you are ready to proceed.")

    elif action == "deal_with_barriers":

        dispatcher.utter_message(text="We've previously thought of barriers which might prevent you from being physically active.")
        dispatcher.utter_message(text="Now, let's try to think how you could overcome those barriers.")
        dispatcher.utter_message(text="Keep in mind that, while I can provide suggestions, it's really up to you to come up with the solution that works best for you.")
        dispatcher.utter_message(text="Let's first see what you think would be a good way of dealing with a certain barrier.")

        buttons = []

        buttons.append({"title": "Lack of time"})
        buttons.append({"title": "Lack of energy"})
        buttons.append({"title": "Disliking being in the presence of others when exercising"})
        buttons.append({"title": "Lack of equipment"})
        buttons.append({"title": "Family obligations"})
        
        dispatcher.utter_message(text="Pick one of the barriers that we've talked about before and let me know how you would deal with it.", buttons=buttons)
        dispatcher.utter_message(text="How would you overcome this barrier? Think for yourself and write it down next to the barrier you previously wrote down.")
        
        buttons = []

        buttons.append({"title": "Let's move further."})
        buttons.append({"title": "Let's proceed."})

        dispatcher.utter_message(text="Let me know when you are ready to go on.", buttons = buttons)

        dispatcher.utter_message(text="Okay. Now, you have your approach to this barrier. Here are the straegies for common barriers that I thought about.")
        dispatcher.utter_message(text="If you lack the time to do physical activity, you could try taking a short walk when you have some free time (during your lunch break, for example).")
        dispatcher.utter_message(text="In terms of energy, think back to when we talked about when you feel most energetic during the day. Aim to schedule activities at those times, since it will be easier for you that way.")
        dispatcher.utter_message(text="Try to go to the gym when it's a bit quieter if you don't like it when other people can see you doing physical activity. It is not absolutely necessary to go to a gym, especially if you're only taking walks. Try walking in a park nearby or simply on the sidewalk.")
        dispatcher.utter_message(text="Another common barrier is not having the right equipment. For walking in particular, the only thing you really need are shoes that are comfortable for you, so putting aside some money for that can be a relatively simple strategy.")
        dispatcher.utter_message(text="If you have children to take care of, it might be a good idea to take them on regular walks with you. That way you can fulfill your family obligations and make progress towards your goal.")

    elif action == "show_testimonials":

        #TODO

        dispatcher.utter_message(text="Testimonial")

    elif action == "changes_to_plan":

        #TODO

        dispatcher.utter_message(text="Change plan")



class ActionSelectActionSaveToDB(Action):
    def name(self):
        return "action_select_action_and_save"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        conn = mysql.connector.connect(
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_HOST,
            port=DATABASE_PORT,
            database='db'
        )
        cur = conn.cursor(prepared=True)

        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
        
        prolific_id = tracker.current_state()['sender_id']

        changes_to_plan = int(tracker.get_slot("changes_to_plan"))

        explain_planning = tracker.get_slot("explain_planning")

        identify_barriers = tracker.get_slot("identify_barriers")

        deal_with_barriers = tracker.get_slot("deal_with_barriers")

        show_testimonials = tracker.get_slot("show_testimonials")

        last_action = tracker.get_slot("last_action")

        number_actions = changes_to_plan + explain_planning + identify_barriers + deal_with_barriers + show_testimonials

        possible_actions = []

        # this corresponds to having done 3 actions, none of which were changes to the plan
        # if we do the 4th action that is not a change to the plan, then we have to do changes to plans in turns 5 and 6
        # that shouldn't happen, since we don't want to make changes to plans twice in a row
        if number_actions == 3 and changes_to_plan == 0:
            possible_actions = ["changes_to_plan"]
        else:
            # we want to make at most 2 changes to the initial plan and to not change the plan twice in a row
            if last_action != "changes_to_plan" and changes_to_plan<=1:
                possible_actions.append("changes_to_plan")
            # we want to explain planning only once
            if explain_planning == False:
                possible_actions.append("explain_planning")
            # we want to identify barriers only once
            if identify_barriers == False:
                possible_actions.append("identify_barriers")
            # we can only deal with barriers after we have identified them and we want to do this only once
            if deal_with_barriers == False and identify_barriers == True:
                possible_actions.append("deal_with_barriers")
            # we want to show testimonials only once
            if show_testimonials == False:
                possible_actions.append("show_testimonials")

        # there are no actions that we cannot do
        # this means we have already done all the 6 possible actions
        if len(possible_actions) == 0:
            return [SlotSet("actions_done", True)]

        # pick the action that was done the least for this state

        ch = tracker.get_slot("changes_to_plan")

        c = tracker.get_slot("confidence")

        pu = tracker.get_slot("perceived_usefulness")

        a = tracker.get_slot("attitude")

        # build current state
        state = f"{ch}, {c}, {pu}, {a}, {explain_planning}, {identify_barriers}, {deal_with_barriers}, {show_testimonials}"

        query = ("SELECT * FROM state_action_state WHERE state_before = %s")
        
        cur.execute(query, [state])
        
        # retrieve all database entries which have an action taken from this state
        result = cur.fetchall()

        # select only the actions in the database results
        actions = [f"{action}" for (userid,date,state,action,next_state) in result]

        # count how many times each action was done
        count = collections.Counter(actions)

        # order the count such that the most frequently done action is first
        ordered = list(count.most_common())

        cleaned = []

        # remove actions that cannot be done from this state (should never happen, but it's safer this way)
        for (ordered_action, frequency) in ordered:
            if ordered_action in possible_actions:
                cleaned.append((ordered_action, frequency))      

        # if there are possible actions for this state that have never been done, add them to the list with them being done 0 times
        for possible_action in possible_actions:
            if not possible_action in [action for (action,frequency) in cleaned]:
                cleaned.append((possible_action, 0))
        
        # figure out how many times he least frequent action was done
        least_frequent = min(cleaned, key = lambda x: x[1])[1]

        # pick a random action from the ones that have been done the least
        pick_from = [action for (action,frequency) in cleaned if frequency == least_frequent]

        picked = random.choice(pick_from)
        
        # dispatcher.utter_message(text=f"I am going to do the action {picked}.")

        action = picked

        # TODO: do the action that was picked

        do_action(action)

        save_sessiondata_entry(cur, conn, prolific_id, formatted_date, f"action: {action}")

        conn.close()

        if action == "changes_to_plan":
            
            changes_to_plan += 1

            if changes_to_plan == 1:
        
                return [SlotSet("changes_to_plan", f"{changes_to_plan}"), SlotSet("last_action", "changes_to_plan"), SlotSet("plan_2", "placeholder2")]

            if changes_to_plan == 2:

                return [SlotSet("changes_to_plan", f"{changes_to_plan}"), SlotSet("last_action", "changes_to_plan"), SlotSet("plan_3", "placeholder3")]

        else:

            return [SlotSet(picked, True), SlotSet("last_action", picked)]


def save_goal_plans_and_reward_to_db(cur, conn, prolific_id, time, goal, plan_1, plan_2, plan_3, reward):
    query = "INSERT INTO users(prolific_id, time, goal, plan_1, plan_2, plan_3, reward) VALUES(%s, %s, %s, %s, %s, %s, %s)"
    cur.execute(query, [prolific_id, time, goal, plan_1, plan_2, plan_3, reward])
    conn.commit()

class ActionSaveGoalPlansAndReward(Action):
    def name(self):
        return "action_save_goal_plans_and_reward"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        conn = mysql.connector.connect(
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_HOST,
            port=DATABASE_PORT,
            database='db'
        )
        cur = conn.cursor(prepared=True)
        
        prolific_id = tracker.current_state()['sender_id']

        goal = tracker.get_slot("goal")

        plan_1 = tracker.get_slot("plan_1")

        plan_2 = tracker.get_slot("plan_2")

        plan_3 = tracker.get_slot("plan_3")

        satisfaction = tracker.get_slot("satisfaction")

        commitment_1 = tracker.get_slot("commitment_1")

        commitment_f = tracker.get_slot("commitment_f")

        confidence_goal = tracker.get_slot("confidence_goal")

        reward = f"Reward: satifaction = {satisfaction}, commitment_1 = {commitment_1}, commitment_f = {commitment_f}, confidence_goal = {confidence_goal}"

        save_goal_plans_and_reward_to_db(cur, conn, prolific_id, formatted_date, goal, plan_1, plan_2, plan_3, reward)

        return []

class ActionConvertDBToStateActionNextState(Action):
    def name(self):
        return "action_rearrange_db"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        conn = mysql.connector.connect(
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_HOST,
            port=DATABASE_PORT,
            database='db'
        )
        cur = conn.cursor(prepared=True)
        
        prolific_id = tracker.current_state()['sender_id']

        query = ("SELECT * FROM sessiondata WHERE prolific_id = %s")
        
        cur.execute(query, [prolific_id])
        
        result = cur.fetchall()

        for row in result[:-1:2]:
    
            i = result.index(row)
            
            state_before = row[2].split("state: ")[1]
            
            action = result[i+1][2].split("action: ")[1]
            
            state_after = result[i+2][2].split("state: ")[1]

            time = result[i+2][1]

            query = "INSERT INTO state_action_state(prolific_id, time, state_before, action, state_after) VALUES(%s, %s, %s, %s, %s)"
            cur.execute(query, [prolific_id, time, state_before, action, state_after])
            conn.commit()


        return []