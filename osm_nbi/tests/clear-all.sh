#! /bin/bash

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# author: Alfonso Tierno
# Script that uses the test NBI URL to clean database. See usage


function usage(){
    echo -e "usage: $0 [OPTIONS]"
    echo -e "TEST NBI API is used to clean database content, except admin users,projects and roles. Useful for testing."
    echo -e "NOTE: database is cleaned but not the content of other modules as RO or VCA that must be cleaned manually."
    echo -e "  OPTIONS"
    echo -e "     -h --help:   show this help"
    echo -e "     -f --force:  Do not ask for confirmation"
    echo -e "     --completely:  It cleans also admin user/project and roles. It only works for internal" \
            "authentication. NBI will need to be restarted to init database"
    echo -e "     --clean-RO:  clean RO content. RO client (openmano) must be installed and configured"
    echo -e "     --clean-VCA: clean VCA content. juju  must be installed and configured"
    echo -e "  ENV variable 'OSMNBI_URL' is used for the URL of the NBI server. If missing, it uses" \
            "'https://\$OSM_HOSTNAME:9999/osm'. If 'OSM_HOSTNAME' is missing, localhost is used"
}


function ask_user(){
    # ask to the user and parse a response among 'y', 'yes', 'n' or 'no'. Case insensitive.
    # Params: $1 text to ask;   $2 Action by default, can be 'y' for yes, 'n' for no, other or empty for not allowed.
    # Return: true(0) if user type 'yes'; false (1) if user type 'no'
    read -e -p "$1" USER_CONFIRMATION
    while true ; do
        [ -z "$USER_CONFIRMATION" ] && [ "$2" == 'y' ] && return 0
        [ -z "$USER_CONFIRMATION" ] && [ "$2" == 'n' ] && return 1
        [ "${USER_CONFIRMATION,,}" == "yes" ] || [ "${USER_CONFIRMATION,,}" == "y" ] && return 0
        [ "${USER_CONFIRMATION,,}" == "no" ]  || [ "${USER_CONFIRMATION,,}" == "n" ] && return 1
        read -e -p "Please type 'yes' or 'no': " USER_CONFIRMATION
    done
}


while [ -n "$1" ]
do
    option="$1"
    shift
    ( [ "$option" == -h ] || [ "$option" == --help ] ) && usage && exit
    ( [ "$option" == -f ] || [ "$option" == --force ] ) && OSMNBI_CLEAN_FORCE=yes && continue
    [ "$option" == --completely ] && OSMNBI_COMPLETELY=yes && continue
    [ "$option" == --clean-RO ] && OSMNBI_CLEAN_RO=yes && continue
    [ "$option" == --clean-VCA ] && OSMNBI_CLEAN_VCA=yes && continue
    echo "Unknown option '$option'. Type $0 --help" 2>&1 && exit 1
done


[ -n "$OSMNBI_CLEAN_FORCE" ] || ask_user "Clean database content (y/N)?" n || exit
[ -z "$OSM_HOSTNAME" ] && OSM_HOSTNAME=localhost
[ -z "$OSMNBI_URL" ] && OSMNBI_URL="https://${OSM_HOSTNAME}:9999/osm"

if [ -n "$OSMNBI_CLEAN_RO" ]
then
    export OPENMANO_TENANT=osm
    for dc in `openmano datacenter-list | awk '{print $1}'`
    do
        export OPENMANO_DATACENTER=$dc
        for i in instance-scenario scenario vnf
        do
            for f in `openmano $i-list | awk '{print $1}'`
            do
                [[ -n "$f" ]] && [[ "$f" != No ]] && openmano ${i}-delete -f ${f}
            done
        done
    done
fi

for item in vim_accounts wim_accounts sdns nsrs vnfrs nslcmops nsds vnfds pdus nsts nsis nsilcmops # vims
do
    curl --insecure ${OSMNBI_URL}/test/db-clear/${item}
done
curl --insecure ${OSMNBI_URL}/test/fs-clear
if [ -n "$OSMNBI_COMPLETELY" ] ; then
    # delete all users. It will only works for internal backend
    curl --insecure ${OSMNBI_URL}/test/db-clear/users
    curl --insecure ${OSMNBI_URL}/test/db-clear/projects
    curl --insecure ${OSMNBI_URL}/test/db-clear/roles
fi

    [[ -z "$OSM_USER" ]] && OSM_USER=admin
    [[ -z "$OSM_PASSWORD" ]] && OSM_PASSWORD=admin
    [[ -z "$OSM_PROJECT" ]] && OSM_PROJECT=admin

    TOKEN=`curl --insecure -H "Content-Type: application/yaml" -H "Accept: application/yaml" \
        --data "{username: '$OSM_USER', password: '$OSM_PASSWORD', project_id: '$OSM_PROJECT'}" \
        ${OSMNBI_URL}/admin/v1/tokens 2>/dev/null | awk '($1=="_id:"){print $2}'`;
    echo "TOKEN='$TOKEN'"

    echo "delete users, prujects,roles. Ignore response errors due that own user,project cannot be deleted"
    for topic in users projects roles
    do
        elements=`curl --insecure ${OSMNBI_URL}/admin/v1/$topic -H "Authorization: Bearer $TOKEN" \
            -H "Accept: application/yaml" 2>/dev/null | awk '($1=="_id:"){print $2};($2=="_id:"){print $3}'`;
        for element in $elements
        do
            # not needed to check if own user, project, etc; because OSM will deny deletion
            echo deleting $topic _id=$element
            curl --insecure ${OSMNBI_URL}/admin/v1/$topic/$element -H "Authorization: Bearer $TOKEN" \
                -H "Accept: application/yaml" -X DELETE 2>/dev/null
        done
    done


if [ -n "$OSMNBI_CLEAN_RO" ]
then
    for dc in `openmano datacenter-list | awk '{print $1}'` ; do openmano datacenter-detach $dc ; done
    for dc in `openmano datacenter-list --all | awk '{print $1}'` ; do openmano datacenter-delete -f  $dc ; done
    for dc in `openmano sdn-controller-list | awk '{print $1}'` ; do openmano sdn-controller-delete -f $dc ; done
    for dc in `openmano wim-list | awk '{print $1}'` ; do openmano wim-detach $dc ; done
    for dc in `openmano wim-list --all | awk '{print $1}'` ; do openmano wim-delete -f  $dc ; done
fi

if [ -n "$OSMNBI_CLEAN_VCA" ]
then
    for juju_model in `juju models | grep lxd | grep -v controller | grep -v default | awk '{print$1}'`
    do
       echo
       echo juju destroy-model  $juju_model
       juju destroy-model -y $juju_model
    done
    # juju destroy-model -y default
    # juju add-model default
fi
