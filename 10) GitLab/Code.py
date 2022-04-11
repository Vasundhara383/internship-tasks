"""
Hi Samyak,

We will need data (commits, developers' details, etc.) for every repo in the following GitLab orgs:
https://gitlab.com/tezos
https://gitlab.com/bitcoin-cash-node
https://gitlab.com/NebulousLabs

I have attached the GitHub code I used to get the data from GitHub repositories.

Please keep in mind that an org has multiple repos, you will need to fetch the orgs for the repos before going to the
final step of getting commits data.

I have also attached sample dataset of how the final data should look like.

Regards,
Vasundhara
"""


# IMPORTS:

from requests import Session, RequestException
from time import perf_counter, sleep
from itertools import count
from json import dumps


start_time = perf_counter()


# ATTRIBUTES:

HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'}
GROUP_IDS = ('tezos', 'bitcoin-cash-node', 'NebulousLabs')[2:]  # The ID or URL-encoded path of the group owned by the authenticated user
BASE_URL = 'https://gitlab.com/api/v4'
WITH_SHARED = False  # Include projects shared to this group. Default is true
INCLUDE_SUBGROUPS = True  # Include projects in subgroups of this group. Default is false
MAX_ITEMS_PER_PAGE = 100  # Number of items to list per page (default: 20, max: 100).


# MAIN:

# Session Init:
with Session() as session:

    session.headers = HEADERS
    session.stream = False  # stream off for all the requests of this session

    for i, group_id in enumerate(GROUP_IDS, start=1):

        print('\n' + f'Group {i}) {group_id}')

        # 1) List a group’s projects: https://docs.gitlab.com/ee/api/groups.html#list-a-groups-projects

        # Pagination: https://docs.gitlab.com/ee/api/index.html#pagination
        project_count = None
        projects = []
        for page in count(start=1):

            # Getting Request's Response:
            while True:
                try:
                    response = session.get(url=f'{BASE_URL}/groups/{group_id}/projects?simple=true&with_shared={WITH_SHARED}&include_subgroups={INCLUDE_SUBGROUPS}&pagination=keyset&page={page}&per_page={MAX_ITEMS_PER_PAGE}')
                except RequestException as e:
                    print(f'{type(e).__name__}:', e.__doc__.split('\n')[0], 'TRYING AGAIN...')
                    sleep(1)  # take a breath
                else:
                    if response.status_code == 200:
                        break
                    else:  # bad response
                        print(f'{response.status_code}: {response.reason} TRYING AGAIN...')
                        sleep(1)  # take a breath

            projects.extend(response.json())  # save this page's data

            # https://docs.gitlab.com/ee/api/index.html#other-pagination-headers:
            # print(response.headers)  # debugging
            if project_count is None:
                project_count = response.headers['X-Total']
                print('Project Count:', project_count)
            if response.headers['X-Next-Page'] == '':
                break  # stop when no more pages left

        # print(dumps(projects, indent=4))  # debugging

        for project in projects:
            print(project['id'])

        break


print('\n' + f'Successfully finished in {int(perf_counter()-start_time)}s.')