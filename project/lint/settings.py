import os
from django.conf import settings


CONFIG = {
    'REPORT_EXPIRATION_DAYS': 30,
    'CLONES_ROOT': os.path.join(settings.PROJECT_ROOT, 'cloned_repos'),
    'MAX_SIZE': 26214400,
    'TIMEOUT': 30.0,
}
CONFIG.update(getattr(settings, 'LINT_CONFIG', {}))
