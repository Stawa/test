from typing import List, Dict, Union, Optional
import discord


class MusicProperty(object):
    def __init__(self, **kwargs):
        self.queue = []
        self.history = []
        self.audio_url = kwargs.get("audio_url")
        self.video_id = kwargs.get("video_id")
        self.video_url = kwargs.get("video_url")
        self.title = kwargs.get("title")
        self.duration = kwargs.get("duration")
        self.current_duration = kwargs.get("current_duration")
        self.thumbnails = kwargs.get("thumbnails")
        self.is_live = kwargs.get("is_live")
        self.requester = kwargs.get("requester")
        self.volume = kwargs.get("volume")
        self.start_time = kwargs.get("start_time")
        self.loop = kwargs.get("loop")

    @property
    def queue(self) -> Optional[List]:
        return self._queue

    @queue.setter
    def queue(self, value) -> None:
        self._queue = value

    @property
    def history(self) -> Optional[List]:
        return self._history

    @history.setter
    def history(self, value) -> None:
        self._history = value

    @property
    def audio_url(self) -> Optional[str]:
        return self._audio_url

    @audio_url.setter
    def audio_url(self, value) -> None:
        self._audio_url = value

    @property
    def video_id(self) -> Optional[str]:
        return self._video_id

    @video_id.setter
    def video_id(self, value) -> None:
        self._video_id = value

    @property
    def video_url(self) -> Optional[str]:
        return self._video_url

    @video_url.setter
    def video_url(self, value) -> None:
        self._video_url = value

    @property
    def title(self) -> Optional[str]:
        return self._title

    @title.setter
    def title(self, value) -> None:
        self._title = value

    @property
    def duration(self) -> Optional[int]:
        return self._duration

    @duration.setter
    def duration(self, value) -> None:
        self._duration = value

    @property
    def current_duration(self) -> Optional[float]:
        return self._current_duration

    @current_duration.setter
    def current_duration(self, value) -> None:
        self._current_duration = value

    @property
    def thumbnails(self) -> List[Dict]:
        return self._thumbnails

    @thumbnails.setter
    def thumbnails(self, value) -> None:
        self._thumbnails = value

    @property
    def is_live(self) -> Optional[bool]:
        return self._is_live

    @is_live.setter
    def is_live(self, value) -> None:
        self._is_live = value

    @property
    def requester(self) -> Union[discord.User, discord.Member]:
        return self._requester

    @requester.setter
    def requester(self, value) -> None:
        self._requester = value

    @property
    def volume(self) -> Optional[int]:
        return self._volume

    @volume.setter
    def volume(self, value) -> None:
        self._volume = value

    @property
    def start_time(self) -> Optional[float]:
        return self._start_time

    @start_time.setter
    def start_time(self, value) -> None:
        self._start_time = value

    @property
    def loop(self) -> Optional[float]:
        return self._loop

    @loop.setter
    def loop(self, value) -> None:
        self._loop = value
