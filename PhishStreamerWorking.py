import requests
import pprint
from ask_sdk_core.skill_builder import SkillBuilder
import ask_sdk_model
from ask_sdk_model.ui import SimpleCard
from ask_sdk_model.interfaces import audioplayer
from ask_sdk_core.utils import is_request_type, is_intent_name

sb = SkillBuilder()
pp = pprint.PrettyPrinter(indent=4)
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
    print(handler_input.response_builder.response)
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
    # Gets only the data list within info
    data = info.get("data")
    # Gets only the tracks list within data
    tracks = data.get("tracks")
    # An increment to see if the track exists
    i = 0
    track_dict = {}
    while True:
        try:
            tracks_dict = tracks[i]
        except:
            break
        else:
            mp3 = tracks_dict.get("mp3")
            track_title = tracks_dict.get("title")
            track_set = tracks_dict.get("set")
            track_position = tracks_dict.get("position")
            track_list = [mp3, track_title, track_set]
            track_dict[track_position] = track_list
            i += 1

'''
    while True:
        try:
            tracks_dict = tracks[i]
        except:
            break
        else:
            mp3 = tracks_dict.get("mp3")
            mp3_list.append(mp3)
            i += 1
'''
    #play_music("https://phish.in/audio/000/031/552/31552.mp3")
    url = track_dict
    return play_music(url)

def play_music(url):
    card = ask_sdk_model.ui.SimpleCard(title="Mike's Song")
    output_speech = ask_sdk_model.ui.PlainTextOutputSpeech(text="Now playing")
    stream = audioplayer.Stream(token="31552", url=url, offset_in_milliseconds=0)
    metadata = audioplayer.AudioItemMetadata(title="Mike's Song")
    audio_item = audioplayer.AudioItem(stream=stream, metadata=metadata)
    play_behavior = audioplayer.PlayBehavior("REPLACE_ALL")
    directives = (audioplayer.PlayDirective(play_behavior=play_behavior,audio_item=audio_item))
    return ask_sdk_model.Response(card=card, output_speech=output_speech, directives=[directives], should_end_session=True)

