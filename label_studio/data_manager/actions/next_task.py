"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import logging
import subprocess
import os


from rest_framework.exceptions import NotFound
from data_manager.functions import filters_ordering_selected_items_exist, get_prepared_queryset_simple
from projects.functions.next_task import get_next_task
from core.permissions import all_permissions
from tasks.serializers import NextTaskSerializer

from tasks.models import Task

logger = logging.getLogger(__name__)


def create_new_task():
    # TODO make this not hardcoded
    python_file = "/Users/sebca/PycharmProjects/research/landcoveranalysis" + os.sep + "insertCyclingAnnotationTasks.py"
    assert os.path.exists(python_file)
    # Call the function in Python file as a subprocess

    # TODO make this not hardcoded
    assert os.path.exists("/opt/homebrew/Caskroom/miniconda/base/envs/mixedint/bin/python")
    exitCode = os.system(f"/opt/homebrew/Caskroom/miniconda/base/envs/mixedint/bin/python {python_file}")
    areMoreTasks = True
    if os.WIFEXITED(exitCode):
        realStatus = os.WEXITSTATUS(exitCode)
        print(realStatus)

        if realStatus == 5:
            areMoreTasks = False
        return areMoreTasks

def next_task(project, queryset, **kwargs):
    """ Generate next task for labeling stream

    :param project: project
    :param queryset: task ids to sample from
    :param kwargs: arguments from api request
    """

    request = kwargs['request']
    dm_queue = filters_ordering_selected_items_exist(request.data)

    next_task, queue_info = get_next_task(request.user, queryset, project, dm_queue)
    if next_task is None:
        areMoreTasks = create_new_task()
        if areMoreTasks:
            next_task, queue_info = get_next_task(request.user, queryset, project, dm_queue)
        else:
            raise NotFound(
            f' There are still some tasks to complete for the user={request.user}, '
            f'but they seem to be locked by another user.')

    # serialize task
    context = {'request': request, 'project': project, 'resolve_uri': True, 'annotations': False}
    serializer = NextTaskSerializer(next_task, context=context)
    response = serializer.data
    response['queue'] = queue_info
    return response


actions = [
    {
        'entry_point': next_task,
        'permission': all_permissions.projects_view,
        'title': 'Generate Next Task',
        'order': 0,
        'hidden': True
    }
]
