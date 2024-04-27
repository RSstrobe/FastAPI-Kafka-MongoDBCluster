#!/bin/bash
sleep 10

mongosh --host mongors1n1:27017 <<EOF
  var cfg = {_id: "mongors1", members: [{_id: 0, host: "mongors1n1"}, {_id: 1, host: "mongors1n2"}, {_id: 2, host: "mongors1n3"}]};
  rs.initiate(cfg);
  rs.status();
EOF
