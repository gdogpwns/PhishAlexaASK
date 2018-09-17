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
URL = "http://phish.in/api/v1"


@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    speech_text = "Welcome to Phish Stream. What is the date of the show you would like to listen to?"
    card_text = "What is the date of the show?"
    display_text = "Phish Stream"
    handler_input.response_builder.speak(speech_text).set_card(
         SimpleCard(display_text, card_text)).set_should_end_session(
         False)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input):
    speech_text = "You can ask for me to play a Phish show."
    card_text = "Ask me to play a Phish show."
    handler_input.response_builder.speak(speech_text).set_card(
         SimpleCard(card_text, speech_text)).set_should_end_session(
         True)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.FallbackIntent"))
def fallback_handler(handler_input):
    speech_text = "I'm sorry, Dave. I'm afraid I can't do that."
    card_text = "I can't do that yet."
    handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard(card_text, speech_text)).set_should_end_session(
        True)
    return handler_input.response_builder.response


@sb.request_handler(
    can_handle_func=lambda input :
        is_intent_name("AMAZON.CancelIntent")(input) or
        is_intent_name("AMAZON.StopIntent")(input))
def cancel_and_stop_intent_handler(handler_input):
    speech_text = "Goodbye! Whatever you do, take care of your shoe."
    card_text = "Goodbye!"
    handler_input.response_builder.speak(speech_text).set_card(
         SimpleCard(card_text, speech_text)).set_should_end_session(
         True)
    return handler_input.response_builder.response

# Exception handler
'''
@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    # Log the exception in CloudWatch Logs
    print(exception)
    speech_text = "Sorry, I didn't get that. Can you please say it again?"
    display_text = speech_text
    handler_input.response_builder.speak(speech_text).ask(speech_text).set_card(
            SimpleCard("Phish Stream", display_text)).set_should_end_session(
            True)
    return handler_input.response_builder.response
'''

@sb.request_handler(can_handle_func=is_intent_name("ShowIntent"))
def get_date(handler_input):
    global track
    track = TrackData()
    # Gets date from end user and converts it to a string
    user_date = handler_input.request_envelope.request.intent.slots
    alexa_date = user_date["DateInput"].value
    print(alexa_date)
    show_date = (URL + "/shows/" + alexa_date)
    # Pulls .json from Phish.in
    try:
        response = requests.get(show_date)
    except ConnectionError:
        speech_text = ("It appears that the fish dot in website is down. Please try again later.")
        display_text = ("Please try again later.")
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Phish Stream", display_text)).set_should_end_session(
            True)
        return handler_input.response_builder.response
    # Converts byte type to list
    info = response.json()
    # Gets only the data list within info
    data = info.get("data")
    # Gets only the tracks list within data
    try:
        tracks = data.get("tracks")
    except:
        print("ERROR: Cannot find show.")
        speech_text = ("I can't find this show right now. Double check that you said the date correctly.")
        display_text = ("I can't find this show.")
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Phish Stream", display_text)).set_should_end_session(
            True)
        return handler_input.response_builder.response
    # An increment to see if the track exists
    i = 0
    while True:
        try:
            phishin_dict = tracks[i]
        except:
            break
        else:
            mp3 = phishin_dict.get("mp3")
            track_title = phishin_dict.get("title")
            track_set = phishin_dict.get("set")
            track_position = phishin_dict.get("position")
            track_list = [mp3, track_title, track_set]
            track.track_dict[track_position] = track_list
            i += 1
    # Make track.position changable if user wants to start somewhere else
    track.position = 1
    return play_music(replace=True)


def play_music(replace):
    output_speech = ask_sdk_model.ui.PlainTextOutputSpeech(text="Playing.")
    if replace is True and track.position == 1:
        track.previous_token = None
        track.previous_str = None
    elif replace is True:
        track.previous_token = None
        track.previous_str = None
    elif replace is False:
        output_speech = None
        track.position_str = str(track.position)
        track.previous_token = (track.position - 1)
        track.previous_str = str(track.previous_token)

    # Breaks down track_metadata into usable values
    track_metadata = track.track_dict.get(track.position)
    url = track_metadata[0]
    track_title = track_metadata[1]
    offset = track.offset_in_milliseconds
    '''
    if replace is True:
        queue_behavior = "REPLACE_ALL"
        stream = audioplayer.Stream(token=track.position_str, url=url, offset_in_milliseconds=offset)
        metadata = audioplayer.AudioItemMetadata(title=track_title, subtitle="Phish")
        audio_item = audioplayer.AudioItem(stream=stream, metadata=metadata)
        play_behavior = audioplayer.PlayBehavior(queue_behavior)
        directives = (audioplayer.PlayDirective(play_behavior=play_behavior, audio_item=audio_item))
        return ask_sdk_model.Response(output_speech=output_speech, directives=[directives],
                                      should_end_session=True)
    '''
    '''
    elif replace is False:
        queue_behavior = "ENQUEUE"
        stream = audioplayer.Stream(expected_previous_token=track.previous_str, token=track.position_str, url=url,
                                    offset_in_milliseconds=offset)
        metadata = audioplayer.AudioItemMetadata(title=track_title, subtitle="Phish")
        audio_item = audioplayer.AudioItem(stream=stream, metadata=metadata)
        play_behavior = audioplayer.PlayBehavior(queue_behavior)
        directives = (audioplayer.PlayDirective(play_behavior=play_behavior, audio_item=audio_item))
        return ask_sdk_model.Response(directives=[directives], should_end_session=True)
    '''
    if replace is True:
        queue_behavior = "REPLACE_ALL"
    elif replace is False:
        queue_behavior = "ENQUEUE"

    stream = audioplayer.Stream(expected_previous_token=track.previous_str, token=track.position_str, url=url,
                                offset_in_milliseconds=offset)
    metadata = audioplayer.AudioItemMetadata(title=track_title, subtitle="Phish")
    audio_item = audioplayer.AudioItem(stream=stream, metadata=metadata)
    play_behavior = audioplayer.PlayBehavior(queue_behavior)
    directives = (audioplayer.PlayDirective(play_behavior=play_behavior, audio_item=audio_item))
    track.offset_in_milliseconds = 0
    return ask_sdk_model.Response(directives=[directives], should_end_session=True)


@sb.request_handler(can_handle_func=is_request_type("AudioPlayer.PlaybackStarted"))
def send_card(handler_input):
    print("PLAYBACK STARTED")
    track.offset_in_milliseconds = 0


@sb.request_handler(can_handle_func=is_request_type("AudioPlayer.PlaybackNearlyFinished"))
def queue_next_song(handler_input):
    track.position += 1
    print("Position: " + str(track.position))
    return play_music(replace=False)


@sb.request_handler(can_handle_func=is_request_type("AudioPlayer.PlaybackStopped"))
def playback_stopped(handler_input):
    offset_in_milliseconds = handler_input.request_envelope.context.audio_player.offset_in_milliseconds
    track.offset_in_milliseconds = offset_in_milliseconds


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.NextIntent"))
def next_track(handler_input):
    track.position += 1
    print("Position: " + str(track.position))
    return play_music(replace=True)


@sb.request_handler(can_handle_func=is_request_type("PlaybackController.NextCommandIssued"))
def next_track_controller(handler_input):
    track.position += 1
    print("Position: " + str(track.position))
    return play_music(replace=True)


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.PreviousIntent"))
def previous_track(handler_input):
    track.position -= 1
    print("Position: " + str(track.position))
    return play_music(replace=True)


@sb.request_handler(can_handle_func=is_request_type("PlaybackController.PreviousCommandIssued"))
def previous_track_controller(handler_input):
    track.position -= 1
    print("Position: " + str(track.position))
    return play_music(replace=True)


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.PauseIntent"))
def pause(handler_input):
    speech_text = ("Pausing.")
    display_text = ("Pausing.")
    handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard("Phish Stream", display_text)).set_should_end_session(
        True)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.PlayIntent"))
def play(handler_input):
    return play_music(replace=False)


@sb.request_handler(can_handle_func=is_request_type("PlaybackController.PlayCommandIssued"))
def play_controller(handler_input):
    return play_music(replace=False)



@sb.request_handler(can_handle_func=is_intent_name("SetIntent"))
# This code is all broken!
# You were trying to make the code find the first song with the set input then put the position there.
def go_to_set(handler_input):
    user_input = handler_input.request_envelope.request.intent.slots
    input_set = user_input["SetSlot"].value
    i = 1

    def song_search(i):
        track_metadata = track.track_dict.get(i)
        track_set = track_metadata[2]
        if track_set == str(input_set):
            track.position = i
            track.position_str = str(track.position)
            return play_music(replace=True)
        else:
            i += 1
            song_search(i)
    song_search(i)
    return play_music(replace=True)


@sb.request_handler(can_handle_func=is_intent_name("EncoreIntent"))
def go_to_encore(handler_input):
    i = 1

    def song_search(i):
        track_metadata = track.track_dict.get(i)
        track_set = track_metadata[2]
        if track_set == "E":
            track.position = i
            track.position_str = str(track.position)
            return play_music(replace=True)
        else:
            i += 1
            song_search(i)
    song_search(i)
    return play_music(replace=True)


class TrackData:
    def __init__(self):
        self.track_dict = {}
        self.position = 1
        self.position_str = str(self.position)
        self.previous_token = (self.position - 1)
        self.previous_str = str(self.previous_token)
        self.offset_in_milliseconds = 0