from celery.task import task

from django.conf import settings
from django.utils import simplejson as json

from .analyzers.loader import get_analyzers
from .downloaders.base import DownloadError
from .downloaders.loader import get_downloaders
from .models import Fix
from .parsers import Parser
from .settings import CONFIG


def download(url, repo_path):
    for downloader_class in get_downloaders():
        downloader = downloader_class(url)
        if downloader.can_process() and downloader.is_valid():
            downloader.download(repo_path)
            return
    raise DownloadError("Can't process this url: %s" % url)


def parse(path):
    return Parser(path).parse()


def analyze(code, path):
    results = []
    for analyzer in get_analyzers():
        results.extend(analyzer(code, path).analyze())
    return results


def save_results(report, results):
    for result in results:
        source = json.dumps(result.source)
        solution = json.dumps(result.solution)
        # Remove archive dir name from result path
        path = '/'.join(result.path.split('/')[1:]) 
        Fix.objects.create(
            report=report, line=result.line, description=result.description,
            path=path, source=source, solution=solution
        )


def exception_handle(func):
    def decorator(report):
        try:
            func(report)
        except Exception, e:
            report.error = '%s: %s' % (e.__class__.__name__, unicode(e))
            report.save()
    decorator.__name__ = func.__name__
    return decorator


@task()
@exception_handle
def process_report(report):
    report.stage = 'cloning'
    report.save()
    path = report.get_repo_path()
    download(report.url, path)

    report.stage = 'parsing'
    report.save()
    parsed_code = parse(path)

    report.stage = 'analyzing'
    report.save()
    save_results(report, analyze(parsed_code, path))
    report.stage = 'done'
    report.save()
