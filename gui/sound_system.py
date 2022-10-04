from random import choice

import pygame

from game.game import Game


class SoundSystem:
    """
    A class to manage sounds and music

    Attributes
    ----------
    _sounds_dict : dict
        dictionary that stores playable sounds
    """

    def __init__(self) -> None:
        """
        initialises pygame.mixer and creates helper variables
        """
        pygame.mixer.init()
        self.playing_music = False
        self.muted = False

        self.load_song("summer_samba.mp3")
        self.play_song()
        self.toggle_music()

        self._sounds_dict: dict[str, tuple | pygame.Sound] = {}
        self.load_sound("croak", "croak.ogg")
        self.load_multi_sound(
            "step",
            (
                "low_bongo.wav",
                "mid_bongo.wav",
                "open_bongo.wav",
            ),
        )

    def load_sound(self, sound_name: str, sound_file: str) -> None:
        """Adds sound from file to sound_dict.

        Args:
            sound_name: key for sound_dict
            sound_file: filename of sound
        """

        path_to_sound = "assets/sounds/" + sound_file
        self._sounds_dict[sound_name] = pygame.mixer.Sound(path_to_sound)

    def load_multi_sound(self, sound_name: str, sound_files: tuple) -> None:
        """
        Adds multi_sound from files to sound_dict.

        A multi_sound is a tuple of sounds
        (for when you want to randomly pick a sound from a selection)

        Args:
            sound_name: key for sound_dict
            sound_files: filename of sound
        """

        sounds = []
        for file in sound_files:
            path_to_sound = "assets/sounds/" + file
            sounds.append(pygame.mixer.Sound(path_to_sound))
        sounds = tuple(sounds)
        self._sounds_dict[sound_name] = sounds

    def set_sound_volume(self, sound_name: str, volume: float) -> None:
        """sets the volume for all sounds associated with the key sound_name

        Args:
            sound_name: key for sound_dict
            volume: float between 0.0 and 1.0 inclusive
        """

        sound = self._sounds_dict[sound_name]
        if type(sound) == tuple:
            for s in sound:
                s.set_volume(volume)

        else:
            assert isinstance(sound, pygame.mixer.Sound)
            sound.set_volume(volume)

    def play_sound(self, sound_name: str) -> None:
        """plays the sound, or if the sound is a multi_sound, chooses and plays a sound

        Args:
            sound_name: key for sound_dict
        """

        if type(self._sounds_dict[sound_name]) == tuple:
            sound = choice(self._sounds_dict[sound_name])

        else:
            sound = self._sounds_dict[sound_name]

        sound.play()

    def toggle_mute(self) -> None:
        """toggles volume between 0 and 1"""
        if self.muted:
            for sound in self._sounds_dict:
                self.set_sound_volume(sound, 1.0)
            pygame.mixer.music.set_volume(1.0)
            self.muted = False
        else:
            for sound in self._sounds_dict:
                self.set_sound_volume(sound, 0.0)
            pygame.mixer.music.set_volume(0.0)
            self.muted = True

    @staticmethod
    def load_song(song_name: str) -> None:
        """loads a song from file, if that song exists"""

        path_to_song = "assets/sounds/" + song_name
        pygame.mixer.music.load(path_to_song)

    def play_song(self) -> None:
        """plays the currently loaded song on loop indefinitely"""
        # ToDo: check to see if music is loaded

        pygame.mixer.music.play(loops=-1)
        self.playing_music = True

    def toggle_music(self) -> None:
        """toggles play/pause state for music"""

        if self.playing_music:
            pygame.mixer.music.pause()
            self.playing_music = False

        else:
            pygame.mixer.music.unpause()
            self.playing_music = True

    @staticmethod
    def adjust_step_volume(game: Game):
        # ToDo: implement max step amount instead of hard coding 25
        if not sound_system.muted:
            volume = 1 - (game.get_steps_remaining() / 25)
            sound_system.set_sound_volume("step", volume)


sound_system = SoundSystem()
