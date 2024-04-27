#!/bin/bash
sleep 10

mongosh --host mongos1:27017 <<EOF
  var cfg = "mongors1/mongors1n1";
  sh.addShard(cfg);
  sh.status();
EOF
