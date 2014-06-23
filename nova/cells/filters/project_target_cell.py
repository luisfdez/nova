# Copyright (c) 2014 CERN
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Project target cell filter.

Route a build form a project to a particular cell(s)
"""

from distutils import versionpredicate
from oslo.config import cfg

from nova.cells import filters
from nova import exception
from nova.openstack.common.gettextutils import _
from nova.openstack.common import log as logging

cell_project_target_cell_opts = [
        cfg.ListOpt('default_cells',
               default=[],
               help='list of default cells'),
        cfg.ListOpt('project_to_cell',
               default=[],
               help='list of cells and projects')

]

LOG = logging.getLogger(__name__)

CONF = cfg.CONF
CONF.register_opts(cell_project_target_cell_opts, group='cells')


class ProjectTargetCell(filters.BaseCellFilter):
    """Project target cell filter"""

    def filter_all(self, cells, filter_properties):
        """Override filter_all() which operates on the full list
        of cells
        """
        request_spec = filter_properties.get('request_spec', {})
        instance_properties = request_spec['instance_properties']
        instance_project_id = instance_properties['project_id']

        cells = list(cells)
        cells_projects = {}
        selected_cells = set()

        scheduler = filter_properties['scheduler']
        if len(cells) == 1 and\
           cells[0].name == scheduler.state_manager.get_my_state().name:
            return cells

        try:
            for x in CONF.cells.project_to_cell:
                cell, project = x.strip().split('_')
                if project not in cells_projects:
                    cells_projects[project.lower()] = set()
                cells_projects[project.lower()].add(cell.lower())

            if instance_project_id in cells_projects.keys():
                selected_cells = cells_projects[instance_project_id]
            else:
                for x in CONF.cells.default_cells:
                    selected_cells.add(x.strip())
        except Exception as e:
            LOG.error(_("Cells setup wrong"))
            raise exception.CernProjectTargetCell()

        filtered_cells = [x for x in cells if x.name in selected_cells]

        return filtered_cells

    def _matches_version(self, version, version_requires):
        predicate = versionpredicate.VersionPredicate(
                             'prop (%s)' % version_requires)
        return predicate.satisfied_by(version)
