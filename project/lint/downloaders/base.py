from django.core.exceptions import ValidationError

from ..settings import CONFIG


class BaseDownloader(object):

    timeout = CONFIG['TIMEOUT']
    max_size = CONFIG['MAX_SIZE']

    def __init__(self, repo_url):
        self.repo_url = repo_url

    def is_valid(self):
        try:
            self.validate()
        except ValidationError:
            return False
        return True

    def can_process(self):
        raise NotImplementedError('Subclasses must implement this method')

    def validate(self):
        raise NotImplementedError('Subclasses must implement this method')

    def download(self):
        raise NotImplementedError('Subclasses must implement this method')


class DownloadError(Exception):
    pass
