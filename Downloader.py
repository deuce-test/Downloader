from pytube import YouTube, Playlist
import argparse
import concurrent.futures


class Downloader:

    def __init__(self):
        self.url = self.argument_parser().url
        self.only_video = self.argument_parser().only_video
        self.only_audio = self.argument_parser().only_audio
        self.is_playlist = self.argument_parser().is_playlist

    def argument_parser(self):
        parser = argparse.ArgumentParser(description='Videos downloader')
        parser.add_argument('url', type=str)
        parser.add_argument('--only_video', '-v', type=bool)
        parser.add_argument('--only_audio', '-a', type=bool)
        parser.add_argument('--is_playlist', '-p', type=bool)
        args = parser.parse_args()
        return args

    def _basic_audio_download(self, url):
        yt_object = YouTube(url)
        yt_object.streams.get_audio_only().download(filename_prefix='audio_')
        return yt_object.title

    def _basic_video_download(self, url):
        yt_object = YouTube(url)
        yt_object.streams.get_highest_resolution().download()
        return yt_object.title

    def _download(self, yt_object):
        if self.only_video:
            yt_object.streams.get_highest_resolution().download()
        elif self.only_audio:
            yt_object.streams.get_audio_only().download()
        else:
            yt_object.streams.get_audio_only().download(filename_prefix='audio_')
            yt_object.streams.get_highest_resolution().download()

        return yt_object.title

    def _download_parallel(self, url):
        if self.only_video:
            title = self._basic_video_download(url)
        elif self.only_audio:
            title = self._basic_audio_download(url)
        else:
            with concurrent.futures.ProcessPoolExecutor() as executor:
                result1 = executor.submit(self._basic_audio_download, url)
                result2 = executor.submit(self._basic_video_download, url)
                for process in concurrent.futures.as_completed([result1, result2]):
                    title = process.result()
        return title


    def download(self):
        titles_list = []
        if self.is_playlist:
            pl = Playlist(self.url)
            url_list = pl.video_urls
            with concurrent.futures.ProcessPoolExecutor() as executor:
                # processes = [executor.submit(self._download, video) for video in pl]
                processes = [executor.submit(self._download_parallel, url) for url in url_list]
                for process in concurrent.futures.as_completed(processes):
                    titles_list.append(process.result())
        else:
            titles_list = [self._download_parallel(self.url)]
        return titles_list



if __name__ == '__main__':
    downloader = Downloader()
    downloaded_titles = []
    try:
        downloaded_titles = downloader.download()
    except:
        pass
    if downloaded_titles:
        for title in downloaded_titles:
            print(f'\n Video clip "{title}" was downloaded successfully')
    elif not downloaded_titles:
        print('\nAAA! Something went wrong!')