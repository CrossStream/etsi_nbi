#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# For those usages not covered by the Apache License, Version 2.0 please
# contact: esousa@whitestack.com or alfonso.tiernosepulveda@telefonica.com
##

"""Contains database content needed for tests"""


db_vim_accounts_text = """
---
-   _admin:
        created: 1566818150.3024442
        current_operation: 0
        deployed:
            RO: dc51ce6c-c7f2-11e9-b9c0-02420aff0004
            RO-account: dc5c67fa-c7f2-11e9-b9c0-02420aff0004
        detailed-status: Done
        modified: 1566818150.3024442
        operationalState: ENABLED
        operations:
        -   detailed-status: Done
            lcmOperationType: create
            operationParams: null
            operationState: COMPLETED
            startTime: 1566818150.3025382
            statusEnteredTime: 1566818150.3025382
            worker: 86434c2948e2
        projects_read:
        - 25b5aebf-3da1-49ed-99de-1d2b4a86d6e4
        projects_write:
        - 25b5aebf-3da1-49ed-99de-1d2b4a86d6e4
    _id: ea958ba5-4e58-4405-bf42-6e3be15d4c3a
    description: Openstack site 2, based on Mirantis, also called DSS9000-1, with
        tenant tid
    name: ost2-mrt-tid
    schema_version: '1.1'
    vim_password: 5g0yGX86qIhprX86YTMcpg==
    vim_tenant_name: osm
    vim_type: openstack
    vim_url: http://10.95.87.162:5000/v2.0
    vim_user: osm
"""

db_vnfds_text = """
---
-   _admin:
        created: 1566823352.7154346
        modified: 1566823353.9295402
        onboardingState: ONBOARDED
        operationalState: ENABLED
        projects_read:
        - 25b5aebf-3da1-49ed-99de-1d2b4a86d6e4
        projects_write:
        - 25b5aebf-3da1-49ed-99de-1d2b4a86d6e4
        storage:
            descriptor: hackfest_3charmed_vnfd/hackfest_3charmed_vnfd.yaml
            folder: 7637bcf8-cf14-42dc-ad70-c66fcf1e6e77
            fs: local
            path: /app/storage/
            pkg-dir: hackfest_3charmed_vnfd
            zipfile: package.tar.gz
        type: vnfd
        usageState: NOT_IN_USE
        userDefinedData: {}
    _id: 7637bcf8-cf14-42dc-ad70-c66fcf1e6e77
    connection-point:
    -   id: vnf-mgmt
        name: vnf-mgmt
        short-name: vnf-mgmt
        type: VPORT
    -   id: vnf-data
        name: vnf-data
        short-name: vnf-data
        type: VPORT
    description: A VNF consisting of 2 VDUs connected to an internal VL, and one VDU
        with cloud-init
    id: hackfest3charmed-vnf
    internal-vld:
    -   id: internal
        internal-connection-point:
        -   id-ref: mgmtVM-internal
        -   id-ref: dataVM-internal
        name: internal
        short-name: internal
        type: ELAN
    logo: osm.png
    mgmt-interface:
        cp: vnf-mgmt
    monitoring-param:
    -   aggregation-type: AVERAGE
        id: monitor1
        name: monitor1
        vdu-monitoring-param:
            vdu-monitoring-param-ref: dataVM_cpu_util
            vdu-ref: dataVM
    -   id: dataVM_users
        aggregation-type: AVERAGE
        name: dataVM_users
        vdu-metric:
            vdu-metric-name-ref: users
            vdu-ref: dataVM
    -   id: dataVM_load
        aggregation-type: AVERAGE
        name: dataVM_load
        vdu-metric:
            vdu-metric-name-ref: load
            vdu-ref: dataVM
    name: hackfest3charmed-vnf
    scaling-group-descriptor:
    -   max-instance-count: 10
        name: scale_dataVM
        scaling-config-action:
        -   trigger: post-scale-out
            vnf-config-primitive-name-ref: touch
        -   trigger: pre-scale-in
            vnf-config-primitive-name-ref: touch
        scaling-policy:
        -   cooldown-time: 60
            name: auto_cpu_util_above_threshold
            scaling-criteria:
            -   name: cpu_util_above_threshold
                scale-in-relational-operation: LE
                scale-in-threshold: '15.0000000000'
                scale-out-relational-operation: GE
                scale-out-threshold: '60.0000000000'
                vnf-monitoring-param-ref: monitor1
            scaling-type: automatic
            threshold-time: 0
        vdu:
        -   count: 1
            vdu-id-ref: dataVM
    short-name: hackfest3charmed-vnf
    vdu:
    -   count: '1'
        cloud-init-file: cloud-config.txt
        id: mgmtVM
        image: hackfest3-mgmt
        interface:
        -   external-connection-point-ref: vnf-mgmt
            name: mgmtVM-eth0
            position: 1
            type: EXTERNAL
            virtual-interface:
                type: VIRTIO
        -   internal-connection-point-ref: mgmtVM-internal
            name: mgmtVM-eth1
            position: 2
            type: INTERNAL
            virtual-interface:
                type: VIRTIO
        internal-connection-point:
        -   id: mgmtVM-internal
            name: mgmtVM-internal
            short-name: mgmtVM-internal
            type: VPORT
        name: mgmtVM
        vm-flavor:
            memory-mb: '1024'
            storage-gb: '10'
            vcpu-count: 1
    -   count: '1'
        id: dataVM
        image: hackfest3-mgmt
        interface:
        -   internal-connection-point-ref: dataVM-internal
            name: dataVM-eth0
            position: 1
            type: INTERNAL
            virtual-interface:
                type: VIRTIO
        -   external-connection-point-ref: vnf-data
            name: dataVM-xe0
            position: 2
            type: EXTERNAL
            virtual-interface:
                type: VIRTIO
        internal-connection-point:
        -   id: dataVM-internal
            name: dataVM-internal
            short-name: dataVM-internal
            type: VPORT
        monitoring-param:
        -   id: dataVM_cpu_util
            nfvi-metric: cpu_utilization
        name: dataVM
        vdu-configuration:
          initial-config-primitive:
          -   parameter:
              -   value: "<rw_mgmt_ip>"
                  name: ssh-hostname
              -   value: ubuntu
                  name: ssh-username
              -   value: osm2018
                  name: ssh-password
              name: config
              seq: '1'
          metrics:
          -   name: users
          -   name: load
          juju:
            proxy: true
            charm: testmetrics
        vm-flavor:
            memory-mb: '1024'
            storage-gb: '10'
            vcpu-count: 1
    version: '1.0'
    vnf-configuration:
        config-primitive:
        -   name: touch
            parameter:
            -   data-type: STRING
                default-value: <touch_filename2>
                name: filename
        initial-config-primitive:
        -   name: config
            parameter:
            -   name: ssh-hostname
                value: <rw_mgmt_ip>
            -   name: ssh-username
                value: ubuntu
            -   name: ssh-password
                value: osm4u
            seq: '1'
        -   name: touch
            parameter:
            -   name: filename
                value: <touch_filename>
            seq: '2'
        juju:
            charm: simple
"""

db_nsds_text = """
---
-   _admin:
        created: 1566823353.971486
        modified: 1566823353.971486
        onboardingState: ONBOARDED
        operationalState: ENABLED
        projects_read:
        - 25b5aebf-3da1-49ed-99de-1d2b4a86d6e4
        projects_write:
        - 25b5aebf-3da1-49ed-99de-1d2b4a86d6e4
        storage:
            descriptor: hackfest_3charmed_nsd/hackfest_3charmed_nsd.yaml
            folder: 8c2f8b95-bb1b-47ee-8001-36dc090678da
            fs: local
            path: /app/storage/
            pkg-dir: hackfest_3charmed_nsd
            zipfile: package.tar.gz
        usageState: NOT_IN_USE
        userDefinedData: {}
    _id: 8c2f8b95-bb1b-47ee-8001-36dc090678da
    constituent-vnfd:
    -   member-vnf-index: '1'
        vnfd-id-ref: hackfest3charmed-vnf
    -   member-vnf-index: '2'
        vnfd-id-ref: hackfest3charmed-vnf
    description: NS with 2 VNFs hackfest3charmed-vnf connected by datanet and mgmtnet
        VLs
    id: hackfest3charmed-ns
    logo: osm.png
    name: hackfest3charmed-ns
    short-name: hackfest3charmed-ns
    version: '1.0'
    vld:
    -   id: mgmt
        mgmt-network: true
        name: mgmt
        short-name: mgmt
        type: ELAN
        vim-network-name: mgmt
        vnfd-connection-point-ref:
        -   member-vnf-index-ref: '1'
            vnfd-connection-point-ref: vnf-mgmt
            vnfd-id-ref: hackfest3charmed-vnf
        -   member-vnf-index-ref: '2'
            vnfd-connection-point-ref: vnf-mgmt
            vnfd-id-ref: hackfest3charmed-vnf
    -   id: datanet
        name: datanet
        short-name: datanet
        type: ELAN
        vnfd-connection-point-ref:
        -   member-vnf-index-ref: '1'
            vnfd-connection-point-ref: vnf-data
            vnfd-id-ref: hackfest3charmed-vnf
        -   member-vnf-index-ref: '2'
            vnfd-connection-point-ref: vnf-data
            vnfd-id-ref: hackfest3charmed-vnf
"""

db_nsrs_text = """
---
-   _admin:
        created: 1566823354.3716335
        modified: 1566823354.3716335
        nsState: NOT_INSTANTIATED
        nslcmop: null
        projects_read:
        - 25b5aebf-3da1-49ed-99de-1d2b4a86d6e4
        projects_write:
        - 25b5aebf-3da1-49ed-99de-1d2b4a86d6e4
    _id: f48163a6-c807-47bc-9682-f72caef5af85
    additionalParamsForNs: null
    admin-status: ENABLED
    config-status: init
    constituent-vnfr-ref:
    - 88d90b0c-faff-4b9f-bccd-017f33985984
    - 1ca3bb1a-b29b-49fe-bed6-5f3076d77434
    create-time: 1566823354.36234
    datacenter: ea958ba5-4e58-4405-bf42-6e3be15d4c3a
    description: default description
    detailed-status: 'ERROR executing proxy charm initial primitives for member_vnf_index=1
        vdu_id=None: charm error executing primitive verify-ssh-credentials for member_vnf_index=1
        vdu_id=None: ''timeout after 600 seconds'''
    id: f48163a6-c807-47bc-9682-f72caef5af85
    instantiate_params:
        nsDescription: default description
        nsName: ALF
        nsdId: 8c2f8b95-bb1b-47ee-8001-36dc090678da
        vimAccountId: ea958ba5-4e58-4405-bf42-6e3be15d4c3a
    name: ALF
    name-ref: ALF
    ns-instance-config-ref: f48163a6-c807-47bc-9682-f72caef5af85
    nsd:
        _admin:
            created: 1566823353.971486
            modified: 1566823353.971486
            onboardingState: ONBOARDED
            operationalState: ENABLED
            projects_read:
            - 25b5aebf-3da1-49ed-99de-1d2b4a86d6e4
            projects_write:
            - 25b5aebf-3da1-49ed-99de-1d2b4a86d6e4
            storage:
                descriptor: hackfest_3charmed_nsd/hackfest_3charmed_nsd.yaml
                folder: 8c2f8b95-bb1b-47ee-8001-36dc090678da
                fs: local
                path: /app/storage/
                pkg-dir: hackfest_3charmed_nsd
                zipfile: package.tar.gz
            usageState: NOT_IN_USE
            userDefinedData: {}
        _id: 8c2f8b95-bb1b-47ee-8001-36dc090678da
        constituent-vnfd:
        -   member-vnf-index: '1'
            vnfd-id-ref: hackfest3charmed-vnf
        -   member-vnf-index: '2'
            vnfd-id-ref: hackfest3charmed-vnf
        description: NS with 2 VNFs hackfest3charmed-vnf connected by datanet and
            mgmtnet VLs
        id: hackfest3charmed-ns
        logo: osm.png
        name: hackfest3charmed-ns
        short-name: hackfest3charmed-ns
        version: '1.0'
        vld:
        -   id: mgmt
            mgmt-network: true
            name: mgmt
            short-name: mgmt
            type: ELAN
            vim-network-name: mgmt
            vnfd-connection-point-ref:
            -   member-vnf-index-ref: '1'
                vnfd-connection-point-ref: vnf-mgmt
                vnfd-id-ref: hackfest3charmed-vnf
            -   member-vnf-index-ref: '2'
                vnfd-connection-point-ref: vnf-mgmt
                vnfd-id-ref: hackfest3charmed-vnf
        -   id: datanet
            name: datanet
            short-name: datanet
            type: ELAN
            vnfd-connection-point-ref:
            -   member-vnf-index-ref: '1'
                vnfd-connection-point-ref: vnf-data
                vnfd-id-ref: hackfest3charmed-vnf
            -   member-vnf-index-ref: '2'
                vnfd-connection-point-ref: vnf-data
                vnfd-id-ref: hackfest3charmed-vnf
    nsd-id: 8c2f8b95-bb1b-47ee-8001-36dc090678da
    nsd-name-ref: hackfest3charmed-ns
    nsd-ref: hackfest3charmed-ns
    operational-events: []
    operational-status: failed
    orchestration-progress: {}
    resource-orchestrator: osmopenmano
    short-name: ALF
    ssh-authorized-key: null
    vld:
    -   id: mgmt
        name: null
        status: ACTIVE
        status-detailed: null
        vim-id: f99ae780-0e2f-4985-af41-574eae6919c0
        vim-network-name: mgmt
    -   id: datanet
        name: ALF-datanet
        status: ACTIVE
        status-detailed: null
        vim-id: c31364ba-f573-4ab6-bf1a-fed30ede39a8
    vnfd-id:
    - 7637bcf8-cf14-42dc-ad70-c66fcf1e6e77
"""

db_nslcmops_text = """
---
-   _admin:
        created: 1566823354.4148262
        modified: 1566823354.4148262
        projects_read:
        - 25b5aebf-3da1-49ed-99de-1d2b4a86d6e4
        projects_write:
        - 25b5aebf-3da1-49ed-99de-1d2b4a86d6e4
        worker: 86434c2948e2
    _id: a639fac7-e0bb-4225-8ecb-c1f8efcc125e
    detailed-status: 'FAILED executing proxy charm initial primitives for member_vnf_index=1
        vdu_id=None: charm error executing primitive verify-ssh-credentials for member_vnf_index=1
        vdu_id=None: ''timeout after 600 seconds'''
    id: a639fac7-e0bb-4225-8ecb-c1f8efcc125e
    isAutomaticInvocation: false
    isCancelPending: false
    lcmOperationType: instantiate
    links:
        nsInstance: /osm/nslcm/v1/ns_instances/f48163a6-c807-47bc-9682-f72caef5af85
        self: /osm/nslcm/v1/ns_lcm_op_occs/a639fac7-e0bb-4225-8ecb-c1f8efcc125e
    nsInstanceId: f48163a6-c807-47bc-9682-f72caef5af85
    operationParams:
        additionalParamsForVnf:
        -   additionalParams:
                touch_filename: /home/ubuntu/first-touch-1
                touch_filename2: /home/ubuntu/second-touch-1
            member-vnf-index: '1'
        -   additionalParams:
                touch_filename: /home/ubuntu/first-touch-2
                touch_filename2: /home/ubuntu/second-touch-2
            member-vnf-index: '2'
        lcmOperationType: instantiate
        nsDescription: default description
        nsInstanceId: f48163a6-c807-47bc-9682-f72caef5af85
        nsName: ALF
        nsdId: 8c2f8b95-bb1b-47ee-8001-36dc090678da
        vimAccountId: ea958ba5-4e58-4405-bf42-6e3be15d4c3a
    operationState: FAILED
    startTime: 1566823354.414689
    statusEnteredTime: 1566824534.5112448
"""

db_vnfrs_text = """
---
-   _admin:
        created: 1566823354.3668208
        modified: 1566823354.3668208
        nsState: NOT_INSTANTIATED
        projects_read:
        - 25b5aebf-3da1-49ed-99de-1d2b4a86d6e4
        projects_write:
        - 25b5aebf-3da1-49ed-99de-1d2b4a86d6e4
    _id: 88d90b0c-faff-4b9f-bccd-017f33985984
    additionalParamsForVnf:
        touch_filename: /home/ubuntu/first-touch-1
        touch_filename2: /home/ubuntu/second-touch-1
    connection-point:
    -   connection-point-id: vnf-mgmt
        id: vnf-mgmt
        name: vnf-mgmt
    -   connection-point-id: vnf-data
        id: vnf-data
        name: vnf-data
    created-time: 1566823354.36234
    id: 88d90b0c-faff-4b9f-bccd-017f33985984
    ip-address: 10.205.1.46
    member-vnf-index-ref: '1'
    nsr-id-ref: f48163a6-c807-47bc-9682-f72caef5af85
    vdur:
    -   _id: f0e7d7ce-2443-4dcb-ad0b-5ab9f3b13d37
        count-index: 0
        interfaces:
        -   ip-address: 10.205.1.46
            mac-address: fa:16:3e:b4:3e:b1
            mgmt-vnf: true
            name: mgmtVM-eth0
            ns-vld-id: mgmt
        -   ip-address: 192.168.54.2
            mac-address: fa:16:3e:6e:7e:78
            name: mgmtVM-eth1
            vnf-vld-id: internal
        internal-connection-point:
        -   connection-point-id: mgmtVM-internal
            id: mgmtVM-internal
            name: mgmtVM-internal
        ip-address: 10.205.1.46
        name: ALF-1-mgmtVM-1
        status: ACTIVE
        status-detailed: null
        vdu-id-ref: mgmtVM
        vim-id: c2538499-4c30-41c0-acd5-80cb92f48061
    -   _id: ab453219-2d9a-45c2-864d-2c0788385028
        count-index: 0
        interfaces:
        -   ip-address: 192.168.54.3
            mac-address: fa:16:3e:d9:7a:5d
            name: dataVM-eth0
            vnf-vld-id: internal
        -   ip-address: 192.168.24.3
            mac-address: fa:16:3e:d1:6c:0d
            name: dataVM-xe0
            ns-vld-id: datanet
        internal-connection-point:
        -   connection-point-id: dataVM-internal
            id: dataVM-internal
            name: dataVM-internal
        ip-address: null
        name: ALF-1-dataVM-1
        status: ACTIVE
        status-detailed: null
        vdu-id-ref: dataVM
        vim-id: 87973c3f-365d-4227-95c2-7a8abc74349c
    vim-account-id: ea958ba5-4e58-4405-bf42-6e3be15d4c3a
    vld:
    -   id: internal
        name: ALF-internal
        status: ACTIVE
        status-detailed: null
        vim-id: ff181e6d-2597-4244-b40b-bb0174bdfeb6
    vnfd-id: 7637bcf8-cf14-42dc-ad70-c66fcf1e6e77
    vnfd-ref: hackfest3charmed-vnf
-   _admin:
        created: 1566823354.3703845
        modified: 1566823354.3703845
        nsState: NOT_INSTANTIATED
        projects_read:
        - 25b5aebf-3da1-49ed-99de-1d2b4a86d6e4
        projects_write:
        - 25b5aebf-3da1-49ed-99de-1d2b4a86d6e4
    _id: 1ca3bb1a-b29b-49fe-bed6-5f3076d77434
    additionalParamsForVnf:
        touch_filename: /home/ubuntu/first-touch-2
        touch_filename2: /home/ubuntu/second-touch-2
    connection-point:
    -   connection-point-id: vnf-mgmt
        id: vnf-mgmt
        name: vnf-mgmt
    -   connection-point-id: vnf-data
        id: vnf-data
        name: vnf-data
    created-time: 1566823354.36234
    id: 1ca3bb1a-b29b-49fe-bed6-5f3076d77434
    ip-address: 10.205.1.47
    member-vnf-index-ref: '2'
    nsr-id-ref: f48163a6-c807-47bc-9682-f72caef5af85
    vdur:
    -   _id: 190b4a2c-4f85-4cfe-9406-4cef7ffb1e67
        count-index: 0
        interfaces:
        -   ip-address: 10.205.1.47
            mac-address: fa:16:3e:cb:9f:c7
            mgmt-vnf: true
            name: mgmtVM-eth0
            ns-vld-id: mgmt
        -   ip-address: 192.168.231.1
            mac-address: fa:16:3e:1a:89:24
            name: mgmtVM-eth1
            vnf-vld-id: internal
        internal-connection-point:
        -   connection-point-id: mgmtVM-internal
            id: mgmtVM-internal
            name: mgmtVM-internal
        ip-address: 10.205.1.47
        name: ALF-2-mgmtVM-1
        status: ACTIVE
        status-detailed: null
        vdu-id-ref: mgmtVM
        vim-id: 248077b2-e3b8-4a37-8b72-575abb8ed912
    -   _id: 889b874d-e1c3-4e75-aa45-53a9b0ddabd9
        count-index: 0
        interfaces:
        -   ip-address: 192.168.231.3
            mac-address: fa:16:3e:7e:ba:8c
            name: dataVM-eth0
            vnf-vld-id: internal
        -   ip-address: 192.168.24.4
            mac-address: fa:16:3e:d2:e1:f5
            name: dataVM-xe0
            ns-vld-id: datanet
        internal-connection-point:
        -   connection-point-id: dataVM-internal
            id: dataVM-internal
            name: dataVM-internal
        ip-address: null
        name: ALF-2-dataVM-1
        status: ACTIVE
        status-detailed: null
        vdu-id-ref: dataVM
        vim-id: a4ce4372-e0ad-4ae3-8f9f-1c969f32e77b
    vim-account-id: ea958ba5-4e58-4405-bf42-6e3be15d4c3a
    vld:
    -   id: internal
        name: ALF-internal
        status: ACTIVE
        status-detailed: null
        vim-id: ff181e6d-2597-4244-b40b-bb0174bdfeb6
    vnfd-id: 7637bcf8-cf14-42dc-ad70-c66fcf1e6e77
    vnfd-ref: hackfest3charmed-vnf
"""
