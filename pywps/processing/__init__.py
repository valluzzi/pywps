##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import pywps.configuration as config
from pywps.processing.basic import MultiProcessing, DetachProcessing, k8sProcessing
from pywps.processing.scheduler import Scheduler
# api only
from pywps.processing.basic import Processing  # noqa: F401
from pywps.processing.job import Job  # noqa: F401

import logging
LOGGER = logging.getLogger("PYWPS")

MULTIPROCESSING = 'multiprocessing'
DETACHPROCESSING = 'detachprocessing'
SCHEDULER = 'scheduler'
KUBERNETES = 'kubernetes'
DEFAULT = MULTIPROCESSING


def Process(process, wps_request, wps_response):
    """
    Factory method (looking like a class) to return the
    configured processing class.

    :return: instance of :class:`pywps.processing.Processing`
    """
    mode = config.get_config_value("processing", "mode")
    LOGGER.info("Processing mode: {}".format(mode))
    if mode == SCHEDULER:
        process = Scheduler(process, wps_request, wps_response)
    elif mode == DETACHPROCESSING:
        process = DetachProcessing(process, wps_request, wps_response)
    elif process == DEFAULT:
        process = MultiProcessing(process, wps_request, wps_response)
    elif mode == MULTIPROCESSING:
        process = MultiProcessing(process, wps_request, wps_response)   
    elif mode == KUBERNETES:
        process = k8sProcessing(process, wps_request, wps_response)

    return process
