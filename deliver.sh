#!/bin/bash

# Identify release tag

function last_tag_minor()
{
    git tag -l $1"*" | sort -rV | head -n 1 | cut -c 7
}

function get_new_tag()
{
    MAJOR=$( date +%y%m%d )

    MINOR=$( last_tag_minor ${MAJOR} )
    MINOR=${MINOR:=-1}
    let 'MINOR=MINOR+1'

    echo ${MAJOR}${MINOR}
}

function is_index_clean()
{
    test -z "$( git status -s )"
}

function fail()
{
    echo "Aborting delivery: $1"
    exit 0
}

###

TAG=$( get_new_tag )

is_index_clean || fail "repository shall be clean before delivery"

read -p "Do you really want to create a new version (${TAG})? [y/N] " -n 1
[ ${#REPLY} -ne 0 ] && echo ""
[[ ! ${REPLY} =~ ^[yY]$ ]] && fail "exiting"

COMMIT_MSG="RELEASE ${TAG}"

echo "Releasing version ${TAG} ... "

BUILDROOT=$( mktemp -d )
mkdir -p ${BUILDROOT}/perky-${TAG}/Src
rsync -vaH Src ${BUILDROOT}/perky-${TAG} --exclude=prk --exclude=__pycache__
pushd $BUILDROOT
tar cjvf perky-${TAG}.tar.bz2 perky-${TAG}
popd
mv ${BUILDROOT}/perky-${TAG}.tar.bz2 Dist
rm -Rf ${BUILDROOT}
git add Dist/perky-${TAG}.tar.bz2

BUILDROOT=$( mktemp -d )
rsync -vaH Rpm/perky.spec ${BUILDROOT}
sed -i -e "s,<VERSION>,${TAG},g" Rpm/perky.spec
git add Rpm/perky.spec

git commit -q -m "${COMMIT_MSG}"
git tag ${TAG}

rsync -vaH ${BUILDROOT}/perky.spec Rpm
git add Rpm/perky.spec

git commit -q -m "Switch back to development environment"

echo "done."
