#!/bin/bash
sleep 10

mongosh --host mongocfg1:27017 <<EOF
  var cfg = {_id: "mongors1conf", configsvr: true, members: [{_id: 0, host: "mongocfg1"}]};
  rs.initiate(cfg);
  rs.status();
EOF
