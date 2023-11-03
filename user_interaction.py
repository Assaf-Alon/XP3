from typing import Any, List, Optional

from colorama import Back, Fore

from music_api import ReleaseRecording


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
    if default:
        if str(default).lower() == "y":
            prompt = f"{prompt} [Y/n]"
        elif str(default).lower() == "n":
            prompt = f"{prompt} [y/N]"
        else:
            prompt = f"{prompt} [{default}]"
    user_input = input(prompt + ": ")

    if not user_input and default:
        return default

    return user_input


# TODO - consider changing this with `pick`
def print_suggestions(
    recordings: List[ReleaseRecording],
    artist: str,
    title: str,
    suggested_recording: int,
):
    """Prints the suggestions recordings.

    Args:
        recordings List[str, int, int]: The suggested recordings to print
        artist (str): The artist of the track
        title (str): The title of the track
        suggested_recording (int): The default recording to choose.
    """
    print("--------------------")
    print(f"Choose the correct album for {artist} - {title}:")
    print(" -1: Skip album metadata")
    print("--------------------")
    print(" 0 : Type metadata manually")
    print("--------------------")
    for index, recording in enumerate(recordings):
        if suggested_recording == index:  # Highlight suggested album
            print(Fore.BLUE, Back.WHITE, end="")
        print(f"{index + 1} : {recording.album}")
        print(f" >> year : {recording.year}, track : {recording.track}" + Fore.RESET + Back.RESET)
        print("--------------------")


def choose_recording(recordings: List[ReleaseRecording], suggested_recording: int) -> Optional[ReleaseRecording]:
    """Chooses a recording interactivly using user input.

    Args:
        recordings (List[ReleaseRecording]): List of suggested recordings.
        suggested_recording (int): Default index for recording from the recordings list.

    Returns:
        ReleaseRecording: Chosen Recording
    """
    recording_index = get_user_input("Enter the correct album number", default=suggested_recording + 1)
    recording_index = int(recording_index)
    # TODO - validate recording_index
    if not recordings:
        return None
    if recording_index == -1:
        return None  # No album information needed
    if recording_index == 0:
        # TODO - validate input
        album = get_user_input("Enter album name", default=recordings[suggested_recording].album)
        year = int(get_user_input("Enter album year", default=recordings[suggested_recording].year))
        track = int(get_user_input("Enter album track", default=recordings[suggested_recording].track))
        return ReleaseRecording(album, year, "", track, "")
    return recordings[recording_index - 1]
