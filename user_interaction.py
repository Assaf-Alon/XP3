"""Functions for interaction with users, such as get_user_input"""
import logging
from typing import Any, List, Optional

from colorama import Back, Fore

from config import IS_DEBUG
from music_api import ReleaseRecording

logging.basicConfig()
logger = logging.getLogger("XP3")
logger.setLevel(logging.DEBUG if IS_DEBUG else logging.INFO)


def get_user_input(prompt: str, default: Any) -> str:
    """Handles user input for functions that require interactivity

    Args:
        prompt (str): The message who'll be shown to the user
        default (Any): The default value to be suggested to the user

    Returns:
        str: The chosen user input
    """
    if prompt.endswith(":"):
        prompt = prompt[:-1]
    prompt = prompt.strip()
    if default or default == 0:
        if str(default).lower() == "true":
            prompt = f"{prompt} [Y/n]"
        elif str(default).lower() == "false":
            prompt = f"{prompt} [y/N]"
        else:
            prompt = f"{prompt} [{default}]"
    user_input = input(prompt + ": ")

    if not user_input:
        return default
    chosen_option = user_input

    # Convert to booleans
    if chosen_option.lower() in ("y", "yes"):
        chosen_option = True
    if chosen_option.lower() in ("n", "no"):
        chosen_option = False

    return chosen_option


# TODO - consider changing this with `pick`
def print_suggestions(
    recordings: List[ReleaseRecording],
    artist: str,
    title: str,
    suggested_recording_index: int,
):
    """Prints the suggestions recordings.

    Args:
        recordings List[str, int, int]: The suggested recordings to print
        artist (str): The artist of the track
        title (str): The title of the track
        suggested_recording_index (int): The default recording to choose.
    """
    print("--------------------")
    print(f"Choose the correct album for {artist} - {title}:")
    print(" -1: Skip album metadata")
    print("--------------------")
    if suggested_recording_index == -1:
        print(Fore.BLUE, Back.WHITE, end="")
    print(" 0 : Type metadata manually" + Fore.RESET + Back.RESET)
    print("--------------------")
    for index, recording in enumerate(recordings):
        if suggested_recording_index == index:  # Highlight suggested album
            print(Fore.BLUE, Back.WHITE, end="")
        print(f"{index + 1} : {recording.album}")
        print(f" >> year : {recording.year}, track : {recording.track}" + Fore.RESET + Back.RESET)
        print("--------------------")


def choose_recording(recordings: List[ReleaseRecording], suggested_recording_index: int) -> Optional[ReleaseRecording]:
    """Chooses a recording interactivly using user input.

    Args:
        recordings (List[ReleaseRecording]): List of suggested recordings.
        suggested_recording_index (int): Default index for recording from the recordings list.

    Returns:
        ReleaseRecording: Chosen Recording
    """

    recording_index = None
    while not isinstance(recording_index, int):
        recording_index = get_user_input("Enter the correct album number", default=suggested_recording_index + 1)
        try:
            recording_index = int(recording_index)
        except ValueError:
            logger.error("Failed to convert input '%d' to an int. Please try again.", recording_index)
            recording_index = ""
        if not -1 <= recording_index <= len(recordings):
            logger.error("Index %d out of range. Recording length: %d", recording_index, len(recordings))
            recording_index = ""

    # No album information needed
    if recording_index == -1:
        return None

    # Manually enter the album information
    if recording_index == 0:
        is_info_valid = False
        defaults = (
            (
                recordings[suggested_recording_index].album,
                recordings[suggested_recording_index].year,
                recordings[suggested_recording_index].track,
            )
            if recordings
            else (
                None,
                None,
                None,
            )
        )
        while not is_info_valid:
            try:
                album = get_user_input("Enter album name", default=defaults[0])
                year = int(get_user_input("Enter album year", default=defaults[1]))
                track = int(get_user_input("Enter album track", default=defaults[1]))
                is_info_valid = True
            except ValueError:
                print("Invalid input. Please try again.")

        return ReleaseRecording(album, year, "", track, "")
    return recordings[recording_index - 1]
