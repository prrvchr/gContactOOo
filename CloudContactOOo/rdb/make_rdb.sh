#!/bin/bash

OOoPath=/usr/lib/libreoffice
Path=$(dirname "${0}")

rm -f ${Path}/types.rdb

${Path}/merge_rdb.sh ${OOoPath} com/sun/star/auth/RestRequestTokenType
${Path}/merge_rdb.sh ${OOoPath} com/sun/star/auth/XRestKeyMap
${Path}/merge_rdb.sh ${OOoPath} com/sun/star/auth/OAuth2Request
${Path}/merge_rdb.sh ${OOoPath} com/sun/star/auth/XInteractionUserName
${Path}/merge_rdb.sh ${OOoPath} com/sun/star/auth/XRestDataParser
${Path}/merge_rdb.sh ${OOoPath} com/sun/star/sdbc/XRestProvider
${Path}/merge_rdb.sh ${OOoPath} com/sun/star/sdbc/XRestDataBase
${Path}/merge_rdb.sh ${OOoPath} com/sun/star/sdbc/XRestDataSource
${Path}/merge_rdb.sh ${OOoPath} com/sun/star/sdbc/XRestUser
${Path}/merge_rdb.sh ${OOoPath} com/sun/star/sdbc/XRestReplicator

read -p "Press enter to continue"

if test -f "${Path}/types.rdb"; then
    ${OOoPath}/program/regview ${Path}/types.rdb
    read -p "Press enter to continue"
fi
