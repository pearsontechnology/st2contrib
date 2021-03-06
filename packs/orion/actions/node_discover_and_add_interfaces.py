# Licensed to the StackStorm, Inc ('StackStorm') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from lib.actions import OrionBaseAction


class NodeDiscoverAndAddInterfaces(OrionBaseAction):
    def run(self, node, platform, whitelist=[], blacklist=[]):
        """
        Discover and add interfaces on an Orion node
        """
        results = {'added': [], 'existing': []}

        self.connect(platform)

        NodeId = self.get_node_id(node)

        Discoverdinterfaces = self.invoke('Orion.NPM.Interfaces',
                                          'DiscoverInterfacesOnNode',
                                          NodeId)

        add_interfaces = []
        for interface in Discoverdinterfaces['DiscoveredInterfaces']:
            # Unmonitored interfaces have an InterfaceID of 0.
            if not interface['InterfaceID'] == 0:
                self.logger.info("Skipping {} as monitored (I:{})".format(
                    interface['Caption'],
                    interface['InterfaceID']))
                results['existing'].append(
                    {interface['Caption']: interface['InterfaceID']})
                continue

            if interface['Caption'] in blacklist:
                self.logger.info("Skipping {} as in blacklist".format(
                    interface['Caption']))
                continue
            elif interface['Caption'] in whitelist:
                self.logger.info("Adding {} as in whitelist".format(
                    interface['Caption']))
                add_interfaces.append(interface)
            elif not whitelist:
                add_interfaces.append(interface)
            else:
                continue

        additions = self.invoke('Orion.NPM.Interfaces',
                                'AddInterfacesOnNode',
                                NodeId,
                                add_interfaces,
                                'AddDefaultPollers')

        for i in additions['DiscoveredInterfaces']:
            results['added'].append({i['Caption']: i['InterfaceID']})

        return results
