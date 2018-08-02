import json
import re
from datetime import date
import logging
import requests
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_model.ui import SimpleCard
from ask_sdk_model.interfaces import audioplayer
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.services.directive import directive_service_client
sb = SkillBuilder()
handler = sb.lambda_handler()
intent = sb.request_handler(can_handle_func=is_intent_name({}))
URL = "http://phish.in/api/v1"


def alexa_say(handler_input, speech_text):
    handler_input.response_builder.speak(speech_text).ask(speech_text).set_card(
        SimpleCard("Phish Stream", speech_text))
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    speech_text = "Welcome to Phish Stream. What is the date of the show you would like to listen to?"

    handler_input.response_builder.speak(speech_text).set_card(
         SimpleCard("Phish Stream", speech_text)).set_should_end_session(
         False)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input):
    speech_text = "You can ask for me to play a Phish show."
    return alexa_say(handler_input, speech_text)


@sb.request_handler(
    can_handle_func=lambda input :
        is_intent_name("AMAZON.CancelIntent")(input) or
        is_intent_name("AMAZON.StopIntent")(input))
def cancel_and_stop_intent_handler(handler_input):
    speech_text = "Goodbye! Whatever you do, take care of your shoe."
    #handler_input.response_builder.speak(speech_text).set_card(
    #    SimpleCard("Phish Stream", speech_text))
    #return handler_input.response_builder.response
    return alexa_say(handler_input, speech_text)


@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    # Log the exception in CloudWatch Logs
    print(exception)

    speech = "Sorry, I didn't get that. Can you please say it again!"
    handler_input.response_builder.speak(speech).ask(speech)
    return handler_input.response_builder.response

@sb.request_handler(can_handle_func=is_intent_name("ShowIntent"))
def get_date(handler_input):
    # Gets date from end user and converts it to a string
    user_date = handler_input.request_envelope.request.intent.slots
    alexa_date = user_date["DateInput"].value
    print (alexa_date)
    show_date = (URL + "/shows/" + alexa_date)
    # Pulls .json from Phish.in
    response = requests.get(show_date)
    # Converts byte type to list
    info = response.json()
    print (info)
    # Gets only the data list within info
    data = info.get("data")
    # Gets only the tracks list within data
    tracks = data.get("tracks")
    # An increment to see if the track exists
    i = 0
    mp3_list = []
    while True:
        try:
            tracks_dict = tracks[i]
        except:
            break
        else:
            mp3 = tracks_dict.get("mp3")
            mp3_list.append(mp3)
            i += 1
    speech_text = "Got it."
    #return alexa_say(handler_input, speech_text)
    from ask_sdk_model.interfaces.audioplayer import play_directive
    audio_file = audioplayer.Stream(url="https://phish.in/audio/000/031/552/31552.mp3")
    play_directive.PlayDirective(audio_item=audio_file)
    #return handler_input.request_envelope audioplayer.stream.Stream(url=mp3_list[0])
#print (audioplayer.Stream(url="https://phish.in/audio/000/031/552/31552.mp3"))
