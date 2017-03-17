from pkg_resources import resource_filename
from logging import getLogger


logger = getLogger(__name__)


def get_ui_file_name(filename):
    '''Get the full path to a ui file name filename

    Parameters
    ----------
    filename : str
        file name of the ui file

    Returns
    -------
    uifile : str
        full path to the ui file filename
    '''
    uifile = resource_filename(__name__, 'ui/%s' % filename)
    logger.debug('full path for ui file %s is %s' % (filename, uifile))
    return uifile
