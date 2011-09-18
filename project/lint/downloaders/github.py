import os
import re
import requests

from subprocess import Popen

from django.core.exceptions import ValidationError
from django.utils import simplejson as json

from .base import BaseDownloader, DownloadError


regexps = (
    re.compile(r'^https:\/\/(?:[-\w]+@|)github\.com\/([-\w]+\/[-.\w]+?)(?:\.git|)$'),
    re.compile(r'^git:\/\/github\.com\/([-\w]+\/[-.\w]+?)\.git$'),
    re.compile(r'^git@github\.com:([-\w]+\/[-.\w]+?)\.git$'),
)


class GitHubDownloader(BaseDownloader):

    def __init__(self, repo_url):
        super(GitHubDownloader, self).__init__(repo_url)
        self.github_url = None

    def can_process(self):
        for regexp in regexps:
            match = regexp.match(self.repo_url)
            if match:
                self.github_url = match.group(1)
                return True
        return False

    def validate(self):
        if self.github_url is None and not self.can_process():
            return ValidationError("This downloader can't process passed url")
        r = requests.get('https://api.github.com/repos/%s/languages' % self.github_url,
                         timeout=self.timeout)
        if not r.ok or r.status_code != 200:
            raise ValidationError("Repo not found, 404")
        data = json.loads(r.content)
        if not 'Python' in data.keys():
            raise ValidationError("Repo language hasn't Python code")

    def download(self, repo_path):
        # Get branch to download
        r = requests.get('https://api.github.com/repos/%s' % self.github_url,
                         timeout=self.timeout)
        if not r.ok or r.status_code != 200:
            raise DownloadError('Cannot fetch information about repo')
        data = json.loads(r.content)
        branch = data['master_branch'] or 'master'
        tarball = 'https://github.com/%s/tarball/%s' % (self.github_url, branch)
        # Donwload tarball with curl
        if not os.path.exists(repo_path):
            os.makedirs(repo_path)
        filepath = os.path.join(repo_path, 'archive.tar.gz')
        curl_string = 'curl %s --connect-timeout %d --max-filesize %d -L -s -o %s' % (
            tarball, self.timeout, self.max_size, filepath
        )
        if Popen(curl_string.split()).wait():
            raise DownloadError("Can't download tarball")
        if Popen(['tar', 'xf', filepath, '-C', repo_path]).wait():
            raise DownloadError("Can't extract tarball")
        os.unlink(filepath)
