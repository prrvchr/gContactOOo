#!/bin/bash

WorkBench=CloudContactOOo
OOoProgram=/usr/lib/libreoffice/program
Path=$(dirname "${0}")

rm ${Path}/${WorkBench}/types.rdb

./rdb/make_rdb.sh ${WorkBench} com/sun/star/auth/RestRequestTokenType
./rdb/make_rdb.sh ${WorkBench} com/sun/star/auth/XRestKeyMap
./rdb/make_rdb.sh ${WorkBench} com/sun/star/auth/XRestDataParser
./rdb/make_rdb.sh ${WorkBench} com/sun/star/sdbc/XRestProvider
./rdb/make_rdb.sh ${WorkBench} com/sun/star/sdbc/XRestDataSource
./rdb/make_rdb.sh ${WorkBench} com/sun/star/sdbc/XRestUser

read -p "Press enter to continue"

${OOoProgram}/regview ${Path}/${WorkBench}/types.rdb
