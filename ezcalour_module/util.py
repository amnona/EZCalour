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


def get_res_file_name(filename):
    '''Get the full path to a resource file
    We put it in util so we'll get the absolute path

    Parameters
    ----------
    filename : str
        file name of the resource

    Returns
    -------
    res_file : str
        full path to the resource file
    '''
    res_file = resource_filename(__name__, filename)
    logger.debug('full path for file %s is %s' % (filename, res_file))
    return res_file
