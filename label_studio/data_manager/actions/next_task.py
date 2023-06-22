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

    print("BEGIN CREATE NEW PROJECT")
    python_file = 'C:\\Users\\nsf2023\\repos\\landcoveranalysis\\getJsonWithId.py'
    annotatedPath = "C:\\Users\\nsf2023\\repos\\annotation\\"
    imagePath = "C:\\Users\\nsf2023\\repos\\imagePath\\"
    # Call the function in Python file as a subprocess
    os.system(f"C:\\Users\\nsf2023\\.conda\\envs\\researchEnv\\python.exe {python_file} {annotatedPath} {imagePath} C:\\Users\\nsf2023\\repos\\completedPath\\")
    # create_new_task_in_file {str(project.id)}")


def next_task(project, queryset, **kwargs):
    """ Generate next task for labeling stream

    :param project: project
    :param queryset: task ids to sample from
    :param kwargs: arguments from api request
    """

    print('NEXT TASK project:',project,'as type', type(project))
    #print("Functions and methods:", dir(project))
    print('LABEL CONFIG: ', project.label_config)
    request = kwargs['request']
    dm_queue = filters_ordering_selected_items_exist(request.data)

    print("NEXT TASK: request: ", request)
    print("NEXT TASK: dm_queue: ", dm_queue)
    next_task, queue_info = get_next_task(request.user, queryset, project, dm_queue)

    print("INITIAL QUERYSET: ", queryset)
    print(type(queryset))
    print('QUEUE INFO: ', queue_info)
    # a = 1/0  # break here :)
    if next_task is None:
        # inputs task formed from getJsonWithId
        create_new_task()


        queryset = Task.prepared.only_filtered_simple(project.id) # placeholder hardcoded value since project is
                                                                         # a class object
        print('ONLY FILTERED SIMPLE QUERY', queryset) # adds new task to queryset..

        next_task, queue_info = get_next_task(request.user, queryset, project, dm_queue)
        print("NEXT TASK TO ANNOTATE:", next_task)

        # raise NotFound(
        #      f' There are still some tasks to complete for the user={request.user}, '
        #      f'but they seem to be locked by another user.')

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
